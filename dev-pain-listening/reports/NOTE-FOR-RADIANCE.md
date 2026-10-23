# For the radiance team: rhetorical mass tracks text length (Oct 23 2026)

**Short version:** on 145 real developer posts, `rm_raw` from rootwords correlates with character count at Spearman
**0.951** (p ≈ 1e-74). That is the risk ADR 0003 accepted unmeasured ("`pf_scalar` ranks long documents first"), and it
crosses the roughly 0.95 line that RM 3.2's open question 9 and decision 28 set for when mass is a proxy for length.

## What was measured
- **Engine:** pulp-lambdas `scoring_functions.rootwords.rm.score.score()` at commit `a8fa7df`, offline (`client=None`),
  with the pinned `en_core_web_lg`. Offline, only the three proposition axes abstain; the mass engine is unchanged.
- **Texts:** 145 relevant public posts (Reddit, Hacker News, the Cursor and Vercel forums, DEV.to, Stack Overflow), from 82
  to 4,000 characters. Median `rm_raw` was 716 (IQR 322 to 1,403).
- **Result:** Spearman (`rm_raw`, character count) = 0.951, n = 145.
- **Data and code:** `pulpshah/datareports`, `dev-pain-listening/`. Files: `analysis/score_rm.py`,
  `data/coded/rm_batch1.jsonl`, and `reports/eda_numbers.json` (key `rm_vs_length_spearman`).

## Why it matters
- With unnormalized mass (ADR 0003, Decision 1), `pf_scalar` = `rm_raw` × `pa_scalar` inherits length almost linearly.
  Ranking by raw PF mostly ranks by length.
- pulp101 already uses the length-fair form, `PF_fair = pf_scalar / (rm_raw + k)` (ADR 0009), which counters this for
  the comment leaderboard. Any other place that ranks or compares raw `pf_scalar` across texts of different lengths
  would rank long texts first.

## Suggested next steps (the radiance team's call)
1. Treat this as the first measurement toward RM 3.2's test T6. It is one genre (developer posts) and short texts, so
   it is not the six-genre, 500-capture corpus T6 asks for.
2. Until `RM_norm` with a calibrated `k` ships, rank by the length-fair form everywhere, not only in pulp101.
3. Report the per-genre correlation as data accumulates, and check whether the nine-element `d` carries the signal
   once length is partialled out.
