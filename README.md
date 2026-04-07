## I turn vague user issues into structured, reproducible bugs that engineering teams can act on

In product support, most issues don’t arrive clearly.

Users describe symptoms, not causes.  
Reproducing the issue is often the hardest part.  
Engineering needs precision, not guesswork.

This project focuses on that gap:
taking unclear user reports and turning them into structured, actionable issues.

---

### What this tool does

- Converts messy user input into structured bug reports  
- Guides investigation through hypotheses and checks  
- Outputs:
  - steps to reproduce  
  - expected vs actual behavior  
  - environment details  

---

### What I focus on in support

- Is this actually a bug or expected behavior?  
- Can I reliably reproduce this issue?  
- What variables matter (environment, permissions, state)?  
- How do I communicate this clearly to engineering?  

---

## Sample Support Case

### User Report (Raw)

> “Hey, something’s off with our prototype. Some teammates can open the link, others just see a blank screen. We didn’t change anything.”

---

### Investigation

**Initial read**
- Inconsistent behavior → likely environment, auth, or permissions  

**Hypotheses**
- File permissions changed  
- Browser-specific issue  
- Cached state causing blank screen  
- Invalid or outdated link  

**Steps taken**
- Opened link in:
  - Chrome (logged in)  
  - Chrome (incognito)  
  - Safari  
- Checked file permissions  
- Verified link format  
- Simulated external (logged-out) access  

---

### Final Output

**Steps to Reproduce**
1. Open shared prototype link while logged out  
2. Observe blank screen  

**Expected**  
Users with the link can view the prototype  

**Actual**  
Logged-out users see a blank screen  

**Environment**
- Browser: Chrome, Safari  
- Auth state: logged out  

**Root Cause**  
File restricted to internal team  

**Resolution**  
Updated sharing settings to allow public access  

---

### Edge Cases Considered

- Browser cache causing stale render  
- Extension blocking content  
- Corrupted prototype state  

---

## How the App Works

The Streamlit app mirrors a real support workflow:

1. Intake  
   - user issue  
   - environment  

2. Investigation  
   - hypotheses  
   - notes  

3. Output  
   - structured issue report  

---

## Why this matters

A large part of support work is not fixing bugs — it’s making them understandable.

This project focuses on that translation layer between users and engineering.

---

## Next Improvements

- Attach logs / screenshots  
- Suggest likely root causes  
- Track patterns across issues  
