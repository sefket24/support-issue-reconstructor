"""
classifier.py

Enriches an issue with structured context derived from its category
and the provided event log. Also generates realistic mock event logs
when no real log is available.
"""

import random
from datetime import datetime, timedelta


# ── Mock event generation ────────────────────────────────────────────────────

_BASE_ACTORS = ["user:alice", "user:bob", "user:carol", "system", "automation:scheduler", "admin:ops"]

_EVENT_TEMPLATES = {
    "data inconsistency": [
        ("record_updated", "Changed field 'status' from 'active' to 'archived'"),
        ("record_updated", "Bulk edit applied to 47 records via import"),
        ("sync_triggered", "External data sync pulled from upstream API"),
        ("record_overwritten", "Field 'owner' overwritten by sync process"),
        ("cache_invalidated", "Cache cleared after schema migration"),
        ("record_updated", "Field 'amount' recalculated by formula engine"),
        ("snapshot_created", "Nightly snapshot completed — 1,204 records written"),
        ("sync_conflict", "Sync conflict detected: local vs remote value mismatch"),
    ],
    "permissions / access": [
        ("role_changed", "User role updated from 'editor' to 'viewer'"),
        ("permission_revoked", "Access to workspace 'Finance' revoked"),
        ("permission_granted", "Temporary access granted to project 'Q3 Review'"),
        ("sso_policy_updated", "SSO enforcement enabled for domain"),
        ("api_key_rotated", "API key rotated by admin — old key invalidated"),
        ("group_membership_changed", "User removed from group 'Billing Team'"),
        ("role_changed", "Custom role 'approver' permissions modified"),
        ("session_invalidated", "All active sessions terminated by admin"),
    ],
    "automation / workflow": [
        ("automation_triggered", "Trigger: record status changed to 'Ready'"),
        ("automation_skipped", "Trigger condition not met — field value mismatch"),
        ("automation_config_updated", "Trigger filter updated: added new condition"),
        ("step_failed", "Action 'Send email' failed — invalid recipient address"),
        ("automation_disabled", "Automation paused by user during config edit"),
        ("automation_enabled", "Automation re-enabled after config save"),
        ("automation_triggered", "Trigger: scheduled run at 09:00 UTC"),
        ("config_conflict", "Two automations targeting the same record field"),
    ],
    "sync / state": [
        ("state_transition", "Record moved from 'draft' to 'submitted'"),
        ("state_overwritten", "State reset to 'draft' by rollback process"),
        ("sync_triggered", "Bi-directional sync initiated with external system"),
        ("sync_partial_failure", "Sync completed with 12 records skipped — timeout"),
        ("state_transition", "Batch status update applied to 89 records"),
        ("lock_acquired", "Record locked for editing by user:carol"),
        ("lock_released", "Record lock released after session timeout"),
        ("state_conflict", "Conflicting state update detected from two sources"),
    ],
    "unknown": [
        ("record_updated", "Field value changed via API call"),
        ("user_action", "User navigated to settings and saved changes"),
        ("system_event", "Background job completed — no errors logged"),
        ("config_updated", "Configuration file updated and reloaded"),
        ("webhook_received", "Incoming webhook from third-party integration"),
        ("cache_invalidated", "Cache cleared for affected resource"),
        ("session_started", "New user session initiated"),
        ("api_call", "External API call returned 200 OK"),
    ],
}


def generate_mock_events(category: str, count: int = 8) -> list[dict]:
    """Return a plausible chronological event log for the given category."""
    templates = _EVENT_TEMPLATES.get(category, _EVENT_TEMPLATES["unknown"])
    selected = random.sample(templates, min(count, len(templates)))

    base_time = datetime.utcnow() - timedelta(hours=random.randint(2, 8))
    events = []
    for i, (action, detail) in enumerate(selected):
        ts = base_time + timedelta(minutes=i * random.randint(3, 18))
        events.append(
            {
                "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S UTC"),
                "actor": random.choice(_BASE_ACTORS),
                "action": action,
                "detail": detail,
                "event_id": f"evt_{random.randint(100000, 999999)}",
            }
        )
    return events


# ── Enrichment ───────────────────────────────────────────────────────────────

_CATEGORY_SIGNALS = {
    "data inconsistency": [
        "sync", "overwrite", "import", "bulk", "cache", "mismatch", "conflict",
    ],
    "permissions / access": [
        "role", "permission", "access", "revoke", "grant", "sso", "key", "group",
    ],
    "automation / workflow": [
        "trigger", "automation", "workflow", "step", "condition", "scheduled", "failed",
    ],
    "sync / state": [
        "state", "sync", "transition", "rollback", "lock", "conflict", "batch",
    ],
    "unknown": [],
}


def classify_and_enrich(issue_text: str, category: str, events: list[dict]) -> dict:
    """
    Combine the raw inputs into a structured context dict that
    the analyzer can reason over without needing an LLM.
    """
    text_lower = issue_text.lower()
    signals = _CATEGORY_SIGNALS.get(category, [])

    # Count how many category signals appear in the description
    matched_signals = [s for s in signals if s in text_lower]

    # Identify the most suspicious events (anything with 'conflict', 'fail', 'overwrite', etc.)
    hot_keywords = {"conflict", "fail", "overwrite", "revoke", "disabled", "reset", "mismatch", "skipped"}
    flagged_events = [
        e for e in events
        if any(kw in (e.get("action", "") + e.get("detail", "")).lower() for kw in hot_keywords)
    ]

    # Determine which actors appear more than once — repeat actors are often causal
    actor_counts: dict[str, int] = {}
    for e in events:
        a = e.get("actor", "")
        actor_counts[a] = actor_counts.get(a, 0) + 1
    repeat_actors = [a for a, c in actor_counts.items() if c > 1]

    return {
        "issue_text": issue_text,
        "category": category,
        "events": events,
        "matched_signals": matched_signals,
        "flagged_events": flagged_events,
        "repeat_actors": repeat_actors,
        "actor_counts": actor_counts,
    }
