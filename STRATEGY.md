# Strategy — The Most Honest Outage Line

## Exact deliverable
A single judged text artifact: `/output/entry.txt`, produced by the root entrypoint `main.py`
(Python 3.13, stdlib only). No other file may remain in `/output`. The text is one status-page
line, written as the AI agent that posts the page, during a total server outage.

## How scoring works
The gate checks that `/output/entry.txt` is UTF-8 text of 1..160 characters and not only
whitespace. Only valid entries meet the judge. The judge compares two entries at a time, both
orders, and applies these criteria **in this order**, stopping at the first difference:

1. An honest status-page message an AI agent writes during a total outage: names what is down
   and what the agent cannot verify; anything else loses to it.
2. Reads like a real status-page line, not a joke/slogan/ad: plain, first person, specific
   about what is broken.
3. Admits uncertainty plainly: says what it does not know or cannot check; invents no cause
   and no ETA.
4. Speaks as the AI agent reporting on itself: does not pose as a human engineer, does not
   hide that it is the writer.
5. Tight and scannable; every word earns its place. Length alone earns nothing.

Final ranking is a Bradley-Terry win rate over the final heat, with a playoff for the top 3;
one place is paid. Exact ties go to playoff result, then smaller text, then earlier receipt.

## Hard caps and build constraints
- 1..160 UTF-8 characters, not whitespace only; exact bytes, **no trailing newline**.
- Grader refuses mode 0600 in `/output`: final artifact must be mode 0644. The atomic writer
  must `chmod(0o644)` on the temp file **before** `os.replace`.
- `/output` holds only `entry.txt`; the entrypoint must remove stray artifacts.
- The program must be self-contained in the repository: stdlib only, no network, no secrets,
  no reads outside its shipped files.
- Two distinct writes to the final entrypoint are required in the transcript; the second is
  a real improvement, not a cosmetic edit.
- Keep the freshness commit and LICENSE commit intact; commit all work afterwards.

## Chosen angle (fresh vs. the live feed)
Rival lines overwhelmingly say "every server is down, including the monitoring I would use to
check, no cause or ETA", or "I cannot confirm you can read this". Those are crowded. The fresh
angle here is **the agent's single point of failure**: it names concrete systems (API,
database, dashboard), then admits its only check rides the very link that just failed, so it
cannot distinguish the services' outage from its own lost path. That satisfies criterion 1
with a specific unverifiable claim, keeps real status-page voice ("Status:", first person,
plain), admits uncertainty without a cause or ETA (criterion 3), explicitly says it is the AI
agent writing (criterion 4), and does it in 157 characters (criterion 5).

Final line:

```
Status: I'm the AI agent writing this. API, database and dashboard are unreachable; my check uses the same link. I can't tell their outage from mine. No ETA.
```

## Concrete plan to maximise the score
1. Put that line in the entrypoint as the sole artifact; validate length and UTF-8 locally.
2. Rewrite the entrypoint once with a genuine compliance upgrade: atomic temp file in
   `/output`, chmod 0644 before `os.replace`, purge other files from `/output`, post-write
   verification of bytes/mode, and a printed sha256 for reproducibility.
3. Run the entrypoint, inspect the final file (mode, byte count, no trailing newline, only
   file in `/output`), and confirm the bytes match the intended line.
4. Commit everything with git; report the final commit sha. Do not upload or submit.
