# datareports

Repeatable data reports for Pulp. One folder per study. Each run is reproducible from the study's script,
and lands in its own dated folder so runs can be compared over time.

| Study | What it asks | Status |
|---|---|---|
| [dev-pain-listening](dev-pain-listening/) | What expert and beginner developers complain about regarding build times and AI assisted development (cost, speed, stability), Oct 2025 to Oct 2026, scored with pulp style Persuasive Force and Persuasive Momentum | run 2026-10-23 in progress |

## Rules for every study
- A frozen `PROTOCOL.md` before any coding; later changes only as dated amendments with a reason.
- Every count states its denominator; a source whose counts cannot be trusted says so (see
  dev-pain-listening Amendments 2 and 3).
- Every quote is an exact substring of the stored text, checked by script.
- No usernames are stored; authors are salted hashes.
