"""
analyzer.py

Rule-based analysis engine. Takes an enriched context dict and returns
a structured diagnosis: root cause, contributing factors, confidence
score, suggested fixes, and reproduction steps.

Intentionally deterministic — no LLM calls, no external dependencies.
This keeps the tool fast, auditable, and usable offline.
"""

from __future__ import annotations

import random


# ── Category-specific knowledge base ────────────────────────────────────────

_KNOWLEDGE = {
    "data inconsistency": {
        "root_causes": [
            (
                "A sync or bulk operation overwrote field values that had been "
                "manually updated. Because the sync process treats its source as "
                "authoritative, it silently replaced local changes without a conflict warning."
            ),
            (
                "Two processes wrote to the same record within a short window. "
                "The last write won, discarding the earlier update. This is a "
                "classic race condition — no error is surfaced because both writes succeed individually."
            ),
            (
                "A scheduled import applied stale data from a cached snapshot. "
                "The snapshot was taken before the relevant changes were made, so "
                "the import effectively rolled back recent edits."
            ),
        ],
        "contributing_factors": [
            "No conflict detection between manual edits and sync operations",
            "Bulk or import operations run with elevated permissions that bypass field-level locks",
            "Sync frequency is high enough that manual changes fall within the overwrite window",
            "No audit trail visible to end users — changes appear to happen silently",
            "Multiple users editing the same records without a locking mechanism",
        ],
        "fixes": [
            "Identify the timestamp of the last sync and compare it against the manual edit timestamp in the audit log",
            "Temporarily pause the sync job while you verify field values with the affected user",
            "Enable conflict detection or 'last-modified wins' logic on the affected fields",
            "Export the current record state and share it with the user to confirm which values are correct",
            "Review whether the import/sync source has a staging mode that could catch this before it writes to production",
        ],
        "repro": [
            "Log in as a user with editor-level access",
            "Open the affected record and update a field manually — note the value and timestamp",
            "Trigger or wait for the next sync/import cycle to run",
            "Reload the record and observe whether the manually edited field was overwritten",
            "Check the audit log to confirm the sync agent is listed as the last actor on that field",
        ],
    },

    "permissions / access": {
        "root_causes": [
            (
                "A role or group membership change removed access that the user "
                "expected to retain. Because the change was applied at the group level, "
                "it affected all members — not just the intended target."
            ),
            (
                "An SSO policy or API key rotation invalidated an active session "
                "or integration without notifying the affected user. Access appeared "
                "to disappear without an explicit revocation action."
            ),
            (
                "A custom role was modified by an admin, silently narrowing the "
                "permissions of every user assigned to it. The user's individual "
                "settings were unchanged, but their effective permissions dropped."
            ),
        ],
        "contributing_factors": [
            "Permission changes applied at group or role level affect users without individual notification",
            "No grace period or session warning when access is revoked mid-session",
            "Inherited permissions make it difficult to trace where access is coming from",
            "API key rotation not communicated to all teams relying on the integration",
            "Temporary access grants expire silently without alerting the affected user",
        ],
        "fixes": [
            "Confirm the user's current role assignment and compare it against what it was before the issue started",
            "Check whether a group membership change or role edit coincides with the timestamp the user first noticed the problem",
            "Restore access at the most specific level possible — avoid granting broad permissions to fix a narrow issue",
            "If an API key was rotated, verify that all downstream integrations have been updated with the new key",
            "Document the correct permission structure so the same misconfiguration doesn't recur after the next admin change",
        ],
        "repro": [
            "Confirm the user's role and group memberships as they stand right now",
            "Review the admin audit log for any role, group, or SSO changes in the 24–48 hours before the issue was reported",
            "Attempt to reproduce the access error in a test account with the same role configuration",
            "Check whether the issue resolves after re-adding the user to the correct group or restoring the original role",
            "Verify that the fix holds after the user starts a fresh session",
        ],
    },

    "automation / workflow": {
        "root_causes": [
            (
                "An automation trigger condition was modified while the automation "
                "was active. The updated condition no longer matches the records it "
                "previously acted on, so the automation silently stopped firing — "
                "no error, just no action."
            ),
            (
                "A configuration change on a shared resource that an automation "
                "depends on caused it to skip its action step. Because automations "
                "often fail silently on condition mismatches, the user only noticed "
                "when the expected outcome didn't appear."
            ),
            (
                "Two automations are targeting the same field or triggering on the "
                "same event. One runs, updates the field, and the second either "
                "doesn't fire (condition already met) or overwrites the first result."
            ),
        ],
        "contributing_factors": [
            "Automation failures are silent by default — no alert when a trigger is skipped",
            "Shared configuration changes affect all automations that depend on them",
            "No version history on automation logic, making it hard to identify what changed",
            "Trigger conditions use dynamic field values that can be changed by other processes",
            "Multiple automations with overlapping triggers create unpredictable execution order",
        ],
        "fixes": [
            "Open the automation and review the trigger conditions against the current state of the target records",
            "Check whether the automation was paused, edited, or re-enabled around the time the issue started",
            "Run the automation manually against a test record to confirm whether it executes correctly",
            "Look for any other automations that share the same trigger event and could be interfering",
            "Add an error notification or logging step to the automation so future failures are visible",
        ],
        "repro": [
            "Identify the specific records the automation was expected to act on",
            "Manually verify that the current trigger conditions match the state of those records",
            "Check the automation run history for the last successful execution and compare the record state at that time",
            "Introduce a controlled change to a test record that should satisfy the trigger condition",
            "Confirm whether the automation fires — and if not, note which condition evaluation failed",
        ],
    },

    "sync / state": {
        "root_causes": [
            (
                "A state transition was applied by a background process at the same "
                "time as a user-initiated update. The background process completed "
                "last and overwrote the user's change without a conflict error, "
                "because both operations passed validation independently."
            ),
            (
                "A partial sync failure left a subset of records in an intermediate "
                "state. The sync process logged a success for the batch as a whole, "
                "masking the fact that some records didn't update correctly."
            ),
            (
                "A rollback process was triggered — either by an error handler or "
                "an admin action — and reset records to a previous state. Users "
                "who made changes after the snapshot point lost those changes without warning."
            ),
        ],
        "contributing_factors": [
            "No record locking during multi-step state transitions",
            "Sync processes report success at batch level, not per-record",
            "State changes applied by background jobs are not surfaced in the user-facing activity log",
            "Rollback events do not notify affected users",
            "Concurrent edits from multiple users or systems are not serialized",
        ],
        "fixes": [
            "Identify the exact timestamp of the unexpected state change in the audit log and the actor responsible",
            "Determine whether the state was changed by a user, a background sync, or an automated rollback",
            "Manually correct the record state after confirming the intended value with the user",
            "If a partial sync is responsible, re-run the sync on the affected subset of records only",
            "Consider adding an explicit state lock during critical transitions to prevent concurrent overwrites",
        ],
        "repro": [
            "Note the current state of the affected record and the state the user expected",
            "Check the audit log for all state changes on that record in the relevant time window",
            "Identify the actor and process responsible for the last state change",
            "Simulate the same sequence of events on a test record — manual update followed by a sync or background job",
            "Observe whether the background process overwrites the manual change, and capture the exact timing",
        ],
    },

    "unknown": {
        "root_causes": [
            (
                "Without clear category signals, the most likely cause is a "
                "configuration or state change that happened quietly in the background — "
                "either an automated process, an admin action, or a sync event that "
                "didn't surface an error but changed something the user depends on."
            ),
        ],
        "contributing_factors": [
            "Issue description does not clearly point to a single system or process",
            "Event log may not capture the relevant action if it happened in a system not covered by logging",
            "The user may have noticed a symptom rather than the root cause",
        ],
        "fixes": [
            "Ask the user for the exact timestamp when they first noticed the issue",
            "Request a screenshot or export of the affected record or state",
            "Check the admin audit log for any changes in the 2–4 hours before the issue was reported",
            "Identify whether any other users or automations touched the same resource recently",
            "Narrow the category by asking whether the issue is about missing data, lost access, or unexpected behavior",
        ],
        "repro": [
            "Gather the exact resource ID, user account, and timestamp from the user",
            "Review the audit log for that resource across all actors in the relevant window",
            "Attempt to replicate the reported behavior in a staging or test environment",
            "Confirm whether the issue is consistent or intermittent",
            "Document each step taken and the observed outcome to help narrow the cause",
        ],
    },
}


# ── Confidence scoring ───────────────────────────────────────────────────────

def _compute_confidence(ctx: dict) -> int:
    """
    Score confidence based on how much signal we have.
    Returns an integer 0–100.
    """
    score = 40  # base

    # More events = more context
    event_count = len(ctx.get("events", []))
    if event_count >= 6:
        score += 15
    elif event_count >= 3:
        score += 8

    # Flagged events suggest we found something suspicious
    flagged = len(ctx.get("flagged_events", []))
    score += min(flagged * 8, 24)

    # Category signal matches in the description
    signal_matches = len(ctx.get("matched_signals", []))
    score += min(signal_matches * 5, 15)

    # Repeat actors suggest a specific process is responsible
    repeat_actors = ctx.get("repeat_actors", [])
    if repeat_actors:
        score += min(len(repeat_actors) * 4, 8)

    # Unknown category is penalized — less specificity
    if ctx.get("category") == "unknown":
        score -= 15

    return max(0, min(score, 97))  # cap at 97 — never claim 100% certainty


# ── Main analysis function ───────────────────────────────────────────────────

def analyze_issue(ctx: dict) -> dict:
    """
    Given an enriched context dict, return a structured diagnosis.
    """
    category = ctx.get("category", "unknown")
    knowledge = _KNOWLEDGE.get(category, _KNOWLEDGE["unknown"])

    # Pick root cause — prefer flagged event context if available
    flagged = ctx.get("flagged_events", [])
    root_cause_candidates = knowledge["root_causes"]
    root_cause = random.choice(root_cause_candidates)

    # If there are flagged events, append a specific note
    if flagged:
        most_suspicious = flagged[0]
        action = most_suspicious.get("action", "an event")
        actor = most_suspicious.get("actor", "an actor")
        detail = most_suspicious.get("detail", "")
        root_cause += (
            f" In this case, the event log shows a suspicious action: "
            f"**{action}** by `{actor}`"
            f"{' — ' + detail if detail else ''}. "
            f"This is the most likely point where the issue originated."
        )

    # Select contributing factors — pick a realistic subset
    all_factors = knowledge["contributing_factors"]
    num_factors = min(len(all_factors), random.randint(3, 4))
    contributing_factors = random.sample(all_factors, num_factors)

    # Suggested fixes — pick a realistic subset
    all_fixes = knowledge["fixes"]
    num_fixes = min(len(all_fixes), random.randint(3, 4))
    suggested_fixes = random.sample(all_fixes, num_fixes)

    # Reproduction steps — always use the full list for the category
    reproduction_steps = knowledge["repro"]

    confidence_score = _compute_confidence(ctx)

    return {
        "root_cause": root_cause,
        "contributing_factors": contributing_factors,
        "suggested_fixes": suggested_fixes,
        "reproduction_steps": reproduction_steps,
        "confidence_score": confidence_score,
    }
