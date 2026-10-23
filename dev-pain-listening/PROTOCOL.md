# Protocol: developer pain listening study (v1.0, frozen Oct 23 2026)

This file is written before any item is coded. Changes after that are made only as a new version at the
bottom of this file (Amendments), with the date and the reason, and never to make a result come out a
certain way.

## 1. Purpose

Learn what expert and beginner developers complain about, in public, regarding:

- **Build times**, in both senses: machine time (compile, typecheck, test, CI, dev server, hot reload) and
  time to a working, merged part (human plus agent time).
- **AI development**: cost (tokens, seats, credits, rework), speed (real and felt) and stability (drift,
  regressions, broken states, ignored instructions, nondeterminism).

Across four layers: frontend (FE), data, interactivity and backend (BE). **Data** follows Shah's definition
(Oct 23): what the application helps people learn, do and understand, and the information it captures to do
that. FE work is usually seen as UI and art style, not as data capture, and it is separated from the data
model. Pain at that seam (UI separated from data, full stack plumbing, scattered tools) is coded as its own
theme, `ui_data_gap`.

The findings feed loosethreads hypothesis tests and KPIs. loosethreads is first for Pulp's own team, then an
MCP based offering for customers. The likely go-to-market ICP (Shah, Oct 23): **higher end vibe coders** and
**entrant FE developers**, people limited by LLMs, prompting and scattered tools that separate UI from data,
who can feel technical debt build quickly whether or not they can name it.

## 2. Research questions

- RQ1. What are the most frequent and most severe pains, by theme, layer and experience tier?
- RQ2. How do the ICP groups (higher end vibe coders, entrant FE developers) differ from experts?
- RQ3. Which claims are made most persuasively (Persuasive Force estimate) and which get the most uptake
  (engagement), and do the two agree?
- RQ4. Do claims change quarter over quarter, and can a change be tied in time to a named event (a model
  release, a pricing or limit change, a tool release, an outage)?
- RQ5. Which pains have a matching loosethreads mechanism, and which are gaps?

## 3. Window and quarters

All items are dated in UTC between **2025-10-23 00:00** and **2026-10-23 00:00** (today minus 12 months).
Four equal windows anchored on that cutoff, not calendar quarters, so every window is about 91 days:

| Window | From (inclusive) | To (exclusive) |
|---|---|---|
| W1 | 2025-10-23 | 2026-01-23 |
| W2 | 2026-01-23 | 2026-04-23 |
| W3 | 2026-04-23 | 2026-07-23 |
| W4 | 2026-07-23 | 2026-10-23 |

## 4. Sample size

- **Pre-registered minimum: n = 1,000 relevant coded items** (relevant is defined in section 7).
- **Target: 1,200 relevant items, at least 300 per window**, so the minimum holds after exclusions and
  every window can be compared with the others.
- Expected relevance rate is about 60%, so about 500 candidates are drawn per window (about 2,000 in all).
  If a window falls under 300 relevant items, more candidates are drawn for that window by the same rules
  and seed sequence, and the shortfall is reported.
- Precision at n = 300 per window: a proportion near 50% has a 95% interval of about plus or minus 5.7
  points; a quarter over quarter change of about 11 points is detectable at 80% power. Subgroup (tier)
  comparisons are weaker and are reported with their intervals, never as bare percentages.

## 5. Sources and quotas

Reachable from this environment on Oct 23 (tested): Reddit through the Arctic Shift archive API, Hacker News
(Algolia API), Stack Exchange API, Discourse forums (forum.cursor.com, community.vercel.com) and the DEV.to
API. Not reachable: Bluesky search, the GitHub API, Lobsters search, X and Discord. They are named as gaps
in every report.

Candidate quota per window (about 500):

| Source | Share | Notes |
|---|---|---|
| Reddit | 50% | Posts and comments. Three community clusters below, about one third each. |
| Hacker News | 20% | Stories and comments. |
| Discourse forums | 15% | Cursor forum and Vercel community, about two thirds and one third. |
| DEV.to | 10% | Articles. |
| Stack Overflow | 5% | Questions. Low volume; kept for the beginner signal. |

Reddit community clusters:

- **Developer, expert leaning:** r/ExperiencedDevs, r/programming, r/webdev, r/reactjs, r/nextjs,
  r/javascript, r/typescript, r/node, r/Frontend, r/dataengineering, r/devops.
- **Learner and entrant:** r/learnprogramming, r/webdev (shared), r/Frontend (shared), r/cscareerquestions,
  r/learnjavascript, r/reactjs (shared).
- **AI and vibe coding:** r/ClaudeAI, r/ClaudeCode, r/cursor, r/vibecoding, r/ChatGPTCoding, r/lovable,
  r/replit, r/v0_, r/boltnewbuilders.

The cluster is a sampling frame, not a tier label. Tier is coded from each item's own evidence (section 7).

## 6. Queries and drawing

Each candidate must match at least one query family. The exact query strings are in
`collect/queries.json`, written before collection and versioned with this file.

- **Q-BUILD:** build time, slow build, compile time, typecheck, tsc, CI time, dev server, hot reload, HMR,
  Turbopack, webpack, Vite, Rolldown, esbuild, Storybook slow, Playwright slow or flaky, Docker build,
  monorepo, Nx, Turborepo, cold start.
- **Q-AICOST:** token cost, expensive, usage limit, rate limit, credits, pricing, bill, quota.
- **Q-AISTAB:** hallucinate, broke my code, regression, ignores instructions, inconsistent, rewrote,
  context window, technical debt, AI slop, review burden.
- **Q-AISPEED:** slower with AI, faster with AI, productivity, waiting on the agent, vibe coding.
- **Q-UIDATA:** full stack, wire up the backend, data fetching, state management, schema, forms, database,
  Supabase, API integration, design system plus AI.

Drawing rules:

- For each source, window and query family, every match is pulled up to a cap of 300, then a random sample is
  drawn with a fixed seed (`seed = 20261023 + window index`). Half the draw is uniform random over matches;
  half is weighted by engagement percentile within source and window, so both typical and widely seen posts
  are represented. Each item records which half drew it.
- **Population counts:** for every source, window and query family, the total match count is recorded
  (HN Algolia `nbHits`, the Arctic Shift and Discourse result counts where the API gives them). Volume trends
  (RQ4) are read from these counts, not from the sample, which has fixed quotas.
- **Weekly counts** for the main query families on HN and Reddit are recorded for the event analysis.
- **Dedupe:** by source id; then near duplicates (cross-posts, quoted reposts) by 5-word shingle Jaccard of at
  least 0.8.
- **Author cap:** at most 3 items per author per window. Authors are stored only as a salted hash.
- Reddit comments carry their parent post title as context. Text over 4,000 characters is coded on its first
  4,000 characters and flagged.

## 7. Codebook (v1)

Every field is filled for every item. `unknown` and `none` are allowed where the evidence is absent; a coder
never guesses.

| Field | Values |
|---|---|
| `relevant` | true when the item states a pain, problem, cost or a counter (praise, a fix, a disagreement) on a section 1 theme |
| `stance` | complaint, mixed, praise_or_fix, neutral_question, irrelevant |
| `themes` (multi) | build_time, ai_cost, ai_speed, ai_stability, ui_data_gap, tool_fragmentation, other |
| `layers` (multi) | fe, data, interactivity, be, ci_infra, cross |
| `pain_types` (multi) | slow, flaky, costly, wrong_output, drift_inconsistency, lock_in, cant_debug, learning_curve, context_limits, review_burden, debt_buildup, scattered_tools, none |
| `tier` | expert, intermediate, entrant, vibe_coder, unknown |
| `tier_evidence` | the words or signal used (stated years, role, vocabulary, self description), or none |
| `tier_confidence` | low, medium, high |
| `icp` | high_end_vibe_coder, entrant_fe, neither, unknown |
| `tools` (multi) | tools and products named, as written |
| `severity` | annoyed, blocked, switched_or_quit, none |
| `claim` | the item's main claim in one plain sentence |
| `argument_type` | anecdote, measurement, benchmark_or_link, authority, generalization, analogy, prediction, venting, question |
| `evidence_level` | none, personal_experience, numbers_given, external_source |
| `quantities` | every stated number with its unit (minutes, dollars, tokens, percent), as structured pairs |
| `events` | named events the item refers to (a release, a pricing change, an outage), as written |
| `quote` | the most representative verbatim span, at most 300 characters; must be an exact substring of the stored text |
| `suspected_promo` | true when the item promotes the poster's own product |
| `suspected_ai_written` | true, false or unsure |
| `channels` | eight values, see section 8 |

Tier rules (from the item only, never from tone):

- **expert:** states 5 or more years, a senior or staff role, or shows production specifics (profiling,
  cache keys, build graph, flags, CI configuration) used correctly.
- **intermediate:** states 2 to 4 years or a working developer role without expert signals.
- **entrant:** states under 2 years, learning, a bootcamp, a first job or a junior role.
- **vibe_coder:** builds mainly by prompting AI and says they do not write or read most of the code, or calls
  themselves a non-developer (designer, founder, PM) who builds with AI. **high_end_vibe_coder** in `icp`
  means a vibe coder shipping real products, paying for several tools, or talking about architecture, debt or
  deployment.
- **entrant_fe** in `icp` means an entrant whose work is frontend.

## 8. Persuasive Force estimate (pulp style)

This follows radiance's definition (pulp-lambdas at commit `a8fa7df`): **PF = rhetorical mass times
Persuasive Acceleration**, `pf_scalar = rm_raw x pa_scalar`, and pulp101's length-fair ranking key
`PF_fair = pf_scalar / (rm_raw + k)` with `k` the median `rm_raw` (pulp101 ADR 0009).

- **Rhetorical mass (`rm_raw`): real, not estimated.** Computed by pulp-lambdas
  `scoring_functions.rootwords.rm.score.score()` offline (`client=None`), with the pinned spaCy model
  `en_core_web_lg`. Offline, the mass engine is unchanged; only the three optional proposition axes abstain,
  as the engine documents.
- **Persuasive Acceleration (`pa_est`): estimated.** The coder scores each of radiance's eight channels in
  [-1, +1] using the channel definitions in `rootcause/taxonomy.py` (ethos, pathos, logos, kairos, style,
  clarity, focus, awareness) and their six dimensions as guidance, against one Objective for every item:
  *"persuade readers in this community that the stated claim about building software is true and worth
  acting on."* `pa_est` is the weighted sum with the registry's `comment_thread` Type weights (ethos .14,
  pathos .10, logos .13, kairos .20, style .05, clarity .12, focus .18, awareness .08; they sum to 1).
- **Deviations from radiance, recorded:** a Claude coder judges 8 channel values, not the 48-parameter judge
  over Groq; the trajectory factor is treated as neutral (radiance's own capture-grain case). So `pa_est`,
  `pf_est` and `pf_fair_est` are labeled estimates everywhere, and are never presented as radiance scores.
- `k` is frozen as the median `rm_raw` of batch 1's relevant items and reported. Uptake (engagement percentile
  within source and window) is kept separate from PF, so RQ3 can compare them.

## 9. Trust controls

- **Quotes:** a script checks every `quote` is an exact substring of the stored text; any that is not is
  recoded.
- **Blind second coder:** a fresh agent with no project context codes a random 20% of each batch from the
  codebook alone. Agreement is reported per field: Cohen's kappa for single label fields, Jaccard for multi
  label fields, Spearman for channel values. If kappa on `relevant`, `stance` or `tier` is under 0.6, the
  codebook is clarified as a new version and the batch is recoded before the next batch.
- **Counterevidence:** praise and fixes are coded, not dropped, and reported beside each complaint.
- **Promo and AI written items** are flagged and excluded from complaint counts (reported separately).
- **Every finding** states its interval, what it probably means, how confident it is, and the evidence
  (counts, links, quotes), as in the HGNN brief.
- **Event attribution** is correlational: a change is tied to an event only when the weekly counts move
  within two weeks after a dated event and the items themselves name it. Anything else is reported as timing
  only.

## 10. Batches and check-ins

Batch 1 is about 250 candidates across all windows and sources. After it: agreement, early insights and
questions go to Shah before the rest is collected. Later batches follow at a pace that protects the
credit budget; speed is not a goal.

## 11. Storage

Raw items (text, permalink, date, engagement, salted author hash), the sample with draw metadata, coded rows,
analysis scripts and reports live in this private repo. No usernames are stored.

## Amendments

### Amendment 1 (Oct 23 2026, before any item was drawn or coded)

**What changed.** Reddit posts are no longer found by keyword title search. The collector pages through
**every post** in each community week by week and keeps the ones that match a query family's frozen regex
(`collect/queries.json`, `families.*.regex`, with `pain_regex` for BUILD and UIDATA and an AI term required for
the AI families outside the AI cluster). r/programming (mostly link posts) and r/cscareerquestions (career
talk, rarely about tools) are dropped. `queries.json` is v1.1.

**Why.** Arctic Shift's title and full text search timed out on most requests on Oct 23 (the same query
succeeded and then failed minutes later), while date listings were reliable. Full listings also give a true
denominator: total posts per community per week. So Reddit volume trends (RQ4) are read as **shares of all
posts**, which removes the effect of a community growing or shrinking. This is stronger than section 6's
capped match counts.

**Effect on the design.** None on quotas, windows, n or the codebook. Reddit comments still use keyword body
search in about 30 day chunks; a chunk that fails after retries is logged as a gap, not filled in. Because that
search runs at about 30 seconds a chunk, comments are narrowed to 8 communities (r/ClaudeAI, r/ClaudeCode,
r/cursor, r/vibecoding, r/lovable, r/webdev, r/nextjs, r/learnprogramming) and 6 keywords (build time,
expensive, usage limit, technical debt, broke my, backend); `queries.json` v1.2.

**Other sources, same rule.** Every source's candidates must match a family regex on title plus text; a
keyword hit alone (for example HN's search for "vite") is not enough. Cursor forum items are treated as the AI
cluster (the forum is about an AI tool); Vercel community, DEV.to, Stack Overflow and HN are treated as general.

### Amendment 2 (Oct 23 2026, before any item was coded)

**Hacker News volume.** Algolia's `nbHits` is approximate and inconsistent: for "turbopack" the weekly counts
summed to 41 in W1 while the whole quarter reported 31, W4 reported 8 hits but listed 4, and an empty query
reported 33.6 million comments in W4. So no HN `nbHits` value is used for any trend. HN weekly volume is the
count of hits actually listed (`search_by_date`, paged), in `counts_hn_weekly_listed.jsonl`. There is no
reliable HN denominator, so HN trends are raw counts and are labeled so.

**Persuasion measures (Shah, Oct 23).** Two measures are reported for every relevant item:

- **PF, Persuasive Force = acceleration x RM** (`pf_est = pa_est x rm_raw`): signed. Positive means the item
  pushes readers toward its claim, negative means its own text works against it.
- **PM, Persuasive Momentum = RM x persuasive speed** (`pm_est = speed_est x rm_raw`): directionless. Speed is
  the weighted root mean square of the eight channel values, `speed_est = sqrt(sum_c w_c * v_c^2)` with the
  same `comment_thread` weights, so it is in [0, 1] and counts persuasive motion whatever its sign.
- Length-fair forms of both divide by `(rm_raw + k)`, with `k` the median `rm_raw` (pulp101 ADR 0009).

**Reddit lanes.** The Reddit post crawl runs as parallel lanes by cluster (and the AI cluster in three lanes
of communities) to finish sooner. The method per week is unchanged.

**Reddit comments, narrowed again (queries v1.3).** The comment search would have covered the first communities
fully and the rest not at all, which is worse than narrower, even coverage. Comments now come from 5
communities (r/ClaudeAI, r/cursor, r/vibecoding, r/webdev, r/learnprogramming) and 4 pain keywords (expensive,
usage limit, technical debt, broke my), all covered across every window. Comments already collected under
other keywords or communities stay in the raw pool but are excluded from the sample so coverage stays even.

### Amendment 3 (Oct 23 2026, before any item was coded)

**Reddit text removal.** In the archive, many posts' text is "[removed]" or "[deleted]", and the share
changes over time: r/ExperiencedDevs went from about 22% removed (Nov 2025 sample) to 52 of 62 posts (Aug 2026
sample). Regex shares over all posts would then fall for reasons that have nothing to do with what people said.
So each weekly count also records posts with text, posts removed, family matches among posts with text, and
family matches on titles alone. Reddit trend shares use **matches among posts with text over posts with
text**; title-only shares over all posts are reported beside them as a robustness check; the removed share is
reported per community and window. Weeks crawled before this change are recounted (counts only). A community
where text survives for few posts in a window is flagged, and the sample from it is described as moderation
survivors.

**DEV.to, stopped after two tags.** The "ai" tag alone held about 284,000 articles in the window, rising from
8,661 in W1 to 118,873 in W4 (13 times). That is far beyond the 200 item DEV.to quota, so DEV.to was stopped
once "vibecoding" and "ai" were complete in every window. The one partial "webdev" page (W4 only) is excluded
from the sample. The W1 to W4 rise is reported as a finding about DEV.to volume, not about developer pain.

**Comment chunks that failed.** Until 16:40 UTC on Oct 23, a comment chunk whose request gave up after its
retries was still marked done, with a count of 0. Those 23 chunks are read back from the logs and retried, and a
failed chunk is now never marked done. Comments now run as one lane per community. Any chunk still failing at the
end is listed as a gap in the report.

### Amendment 4 (Oct 23 2026, before any item was drawn or coded): the first run is cut off

To save credits, Shah ended collection at 16:50 UTC and asked for a first sample run, with expansion later.

- **Collected:** every source is complete except Reddit comments, which stopped at 128 of 260 chunks. Reddit posts are
  complete: 21 communities, 53 weeks each, 453,082 posts scanned, with text availability counted for every week.
- **Comments in this run:** only keyword and community pairs complete in every window enter the sample: r/ClaudeAI
  (expensive, usage limit, technical debt, broke my) and r/cursor (expensive, usage limit, technical debt). So comments
  speak for the AI cluster only. The dev and learner comment quotas move to those clusters' posts first.
- **Coding in this run:** batch 1 only, the first of the 8 proportional batches (about 250 candidates), with the blind
  second coder on 20%. The pre-registered n of 1,000 relevant items is reached by coding later batches; until then every
  number is reported as batch 1 with its interval, and quarter comparisons are labeled underpowered.

### Amendment 5 (Oct 23 2026, 19:55 UTC): ICP-targeted collection

The first run found only 5 of 145 coded items from the ICP (higher end vibe coders and entrant FE developers). To reach
them, two community clusters are added, collected with the same week-by-week listing and frozen family regexes as
Amendment 1, with text-availability counts as Amendment 3:
- **icp_builder** (people shipping products, often with AI and low-code tools): r/SideProject, r/indiehackers,
  r/nocode, r/SaaS, r/buildinpublic, r/Supabase (where UI-to-data wiring shows up), r/windsurf.
- **icp_entrant** (people early in frontend work): r/css, r/learnreactjs, r/tailwindcss, r/webdevelopment,
  r/codingbootcamp, r/FreeCodeCamp.

AI families still require an AI term in these clusters, because they are not AI-dedicated communities. This is an
expansion, not a change to the first run. Its sample is drawn later as a separate ICP stratum with its own seed, and its
coding waits for Shah's credit call. `queries.json` is v1.4.
