---
name: systems-review
description: Weekly review of all active systems — GTD, Atomic, PQ, Friction Elimination, Intuitive Eating. Walk through each system spec, check adherence, capture learnings, and update specs.
---

# Systems Review

Interactive weekly review of all active systems. Run on Sundays during the 16:00–17:00 review block.

## Overview

The systems index lives at `References/Systems.md` in the vault. Each system has its own spec in `References/` with routines, principles, and a review log.

## How to Run

This is a **conversational** skill. Walk through each system one at a time with the user. Don't dump everything at once — ask questions, listen, and capture.

### Step 1 — Load the specs

Read the current state of all system specs using the `/obsidian` skill:

```bash
# See /obsidian skill for $OBS and $VAULT setup
$OBS vault=$VAULT read path="References/Systems.md"
$OBS vault=$VAULT read path="References/GTD System.md"
$OBS vault=$VAULT read path="References/Atomic System.md"
$OBS vault=$VAULT read path="References/PQ System.md"
$OBS vault=$VAULT read path="References/Friction Elimination.md"
$OBS vault=$VAULT read path="References/Intuitive Eating System.md"
```

### Step 2 — Walk through each system

For each system, ask:

1. **How did it go this week?** — Did you follow the routines?
2. **What worked?** — Anything to keep or reinforce?
3. **What didn't work?** — What got missed and why?
4. **What needs to change?** — Any tweaks to the spec?

Keep it conversational. Don't interrogate — just ask one question at a time and follow the thread.

#### System order

1. **GTD** — Start here. Check metrics using the `/obsidian` skill's Dataview queries (inbox count, overdue, stale projects, context distribution, completed this week).
   Key questions: inbox at zero? Projects moving? Any stale? Overdue tasks?

2. **Atomic** — Morning and evening routines.
   Key questions: how many days did you do the morning routine? Evening routine? What broke the chain?

3. **PQ** — Mindfulness and refreshes.
   Key questions: did the 08:00/13:00/16:00 happen? Any saboteurs you noticed this week?

4. **Friction Elimination** — Resistance mapping.
   Key questions: what are you avoiding right now? Run the resistance map live if needed. Log any actions taken.

5. **Intuitive Eating** — Weekly check-in.
   Key questions: use the prompts in the spec. How's the relationship with food? Diet mentality creeping in?

### Step 3 — Capture to review logs

After discussing each system, append a dated entry to the **Review Log** section of that system's spec:

```
### YYYY-MM-DD
- [what was discussed, what changed, what to try next week]
```

### Step 4 — Update specs if needed

If the user wants to change a routine, tweak a cue, add or remove something — update the spec directly. The specs are living documents.

### Step 5 — Summary

At the end, give a brief summary:
- Which systems are running well
- Which need attention next week
- Any spec changes made

## Tips

- Don't force all five if the user only has energy for a few — prioritise what needs attention
- If a system is running smoothly, a quick "GTD's solid this week, anything to flag?" is enough
- The Friction Elimination review can double as a live coaching session — help the user break down stuck tasks on the spot
- Keep review log entries short and actionable, not essay-length
