# Developer pain listening: first run (batch 1), Oct 23 2026

**Added Oct 23, later:**
- `reports/MONEY.md`: the money stated across all 277,504 items.
- `reports/EVENTS.md`: the event timeline behind the Hacker News spikes.
- `reports/NOTE-FOR-RADIANCE.md`: the rm_raw versus length finding, for the radiance team.

**Scope.** Oct 23 2025 to Oct 23 2026, four equal quarters (W1 to W4). Two layers of evidence:

1. **Population trends** from every Reddit post in 21 communities, about 453,000 scanned, 222,114 with surviving
   text, plus listed Hacker News counts. Keyword level, very large n. `reports/trends.json`.
2. **Coded sample**, batch 1 of 8: 273 candidates drawn by fixed rules, 145 relevant, each coded for claim, theme,
   layer, pain, experience, argument and eight persuasion channels. Persuasion is scored pulp style: rhetorical mass
   (`rm_raw`) from radiance's rootwords engine, acceleration estimated from the channels. `reports/eda_numbers.json`,
   `reports/tables/`.

The pre-registered n of 1,000 relevant items needs batches 2 to 8 (Amendment 4). Until then, coded results are
descriptive, with 95% intervals; quarter and tier comparisons in the coded sample are underpowered and say so.

## 1. Headline findings

1. **Cost has become the main thing AI coders talk about.** In AI communities, posts with cost language rose from 29.2% to
   36.2% of posts with text (linear trend z = 16.3, p < 1e-59); r/cursor 31.8% to 45.9%, r/ClaudeCode 31.5% to 39.1%. In the
   coded sample, cost is the top theme (35.9%, CI 29 to 44) and "costly" the top pain (34.5%).
2. **The cost complaint is about unpredictability, not price.** The single biggest cost claim (C01, 10.3% of relevant
   items) is that limits and credits drain fast or change without notice: "jumped from 80% to 95% after two light prompts",
   "Ultra limits hit at $1,700 one month and $800 the next", "Opus 4.7 used up a Max x5 limit in about 20 minutes".
   Next come paying for failed work (C02: loops, lost work, "free" fixes that charged) and billing plumbing that blocks
   people (C03).
3. **"Is AI faster?" is fading as a topic** (AI communities 22.0% to 14.9%, z = -23.1; r/vibecoding 41% to 28%). Where it is
   still discussed, the claim is "faster, but less than claimed, and hollow" (C09).
4. **AI breakage complaints are moving from AI communities into mainstream developer communities.** They are down in AI
   communities (r/ClaudeAI 31.5% to 25.8%) and up across dev communities from 6.4% to 9.5% (z = 10.5): r/Frontend 3.6% to
   13.9%, r/reactjs 5.2% to 10.1%, r/nextjs 3.6% to 8.0%. Title-only shares, which removal cannot touch, rise too.
5. **The AI tools themselves are a stability problem.** The most frequent coded claim (C11, 11.7%) is that editor and agent
   updates break things: crashes, broken undo, lost chats, wrong default model, slow responses. It is separate from bad
   output (C06 drift and ignored rules; C07 destructive or out-of-scope work).
6. **Builds break in the platform, not the code.** In the coded sample, build pain is mostly failures with opaque errors on
   hosted platforms (C12, 7.6%, every one a complaint; one began when the platform's build CLI stopped bundling a declared dependency).
   Slowness proper (C13) is rarer and comes from experts: "pip compiles from source for about 9 minutes on every CI run".
   Population level, build talk rose among developers from 15.0% to 19.8% (z = 10.4); r/reactjs 15% to 27%.
7. **Wiring UI to data is where newer builders stall** (C14): analytics pipelines, Jobber to QuickBooks, Stripe state
   drifting from the database, multi step forms, auth across a Go backend and Next.js. All 9 are questions, none
   complaints. That makes the gap hard to see, because people experience it as their own ignorance and not as a tool's fault.
8. **Experts fix; entrants worry.** Of the 30 items with a stated experience level, experts cluster in context discipline
   (C05: 3 of 7) and build tooling (C13: 3 of 8), and entrants in skill erosion (C10: 4 of 5) and UI to data (C14). The
   learning-curve pain differs by tier (Cramer's V 0.66, q = 0.049). The ICP itself (higher end vibe coders, entrant FE
   developers) is nearly invisible here: 1 vibe coder and 4 entrant FE items. Reaching it needs targeted collection.
9. **Evidence wins persuasion, but not upvotes.** Length-fair Persuasive Momentum is highest for posts that give numbers
   (median 0.269) and lowest for venting (0.064); both differences hold after false-discovery control (q = 0.002 by
   argument type, q = 0.035 by evidence level). Neither PF nor PM predicts uptake (Spearman 0.06; within Reddit -0.09).
10. **Moderators remove a rising share of public developer talk.** Removed text rose on r/ExperiencedDevs from 15% to 81%,
    r/dataengineering 30% to 77%, r/node 24% to 62%, r/vibecoding 17% to 47% in W4. The readable conversation is shrinking
    and is increasingly what moderators let stand.

## 2. Population trends (Reddit, every post)

Share of posts with surviving text whose title or body matches each family's frozen regex. n per quarter in AI
communities: 27,309 / 45,728 / 45,244 / 33,798; dev: 16,875 / 14,866 / 10,033 / 6,234; learner: 7,011 / 6,170 / 5,040 / 3,806.

| Cluster | Family | W1 | W2 | W3 | W4 | trend z |
|---|---|---|---|---|---|---|
| AI | cost | 29.2% | 34.8% | 34.9% | 36.2% | +16.3 |
| AI | stability | 24.0% | 27.5% | 23.8% | 24.2% | -4.9 |
| AI | speed | 22.0% | 20.1% | 18.8% | 14.9% | -23.1 |
| AI | UI and data | 9.6% | 10.5% | 9.1% | 7.8% | -10.4 |
| AI | build | 15.7% | 19.0% | 17.2% | 17.3% | +1.2 |
| dev | build | 15.0% | 17.6% | 19.3% | 19.8% | +10.4 |
| dev | AI cost | 5.8% | 8.5% | 9.6% | 9.4% | +11.6 |
| dev | AI stability | 6.4% | 9.5% | 10.4% | 9.5% | +10.5 |
| dev | AI speed | 4.8% | 6.5% | 6.5% | 5.7% | +4.4 |
| dev | UI and data | 13.0% | 14.2% | 15.5% | 14.8% | +5.2 |
| learner | build | 10.3% | 10.1% | 10.3% | 10.9% | +0.9 |
| learner | AI cost | 2.2% | 2.6% | 2.7% | 2.5% | +1.2 |
| learner | AI stability | 3.1% | 3.4% | 4.1% | 3.3% | +1.5 |
| learner | UI and data | 8.2% | 8.7% | 8.8% | 7.3% | -1.1 |

**Hacker News, listed hits per quarter:** "AI slop" 4,854 / 6,118 / 7,040 / 7,900 (+63%); "technical debt" 1,723 /
1,603 / 1,118 / 1,082; "usage limits" 672 / 1,027 / 950 / 850; "turbopack" 44 / 36 / 12 / 10. "claude code" and "vite"
hit Algolia's 1,000 per query cap and are excluded. Weekly spikes worth tying to events (not yet checked): "cursor
pricing" weeks of Jan 8, Mar 12, Jun 11 and Jul 30; "usage limits" week of Apr 16; "rate limit" week of Feb 19.

## 3. Coded sample: who and what (n = 145 relevant of 273; relevance 53%, CI 47 to 59)

| | Values (share of relevant, 95% CI) |
|---|---|
| Stance | complaint 50% (42 to 58), praise or fix 24%, mixed 18%, neutral question 8% |
| Severity | none 49%, annoyed 39%, blocked 11% (7 to 17), switched or quit 1.4% |
| Experience | unknown 79%, expert 9.7%, entrant 5.5%, intermediate 4.8%, vibe coder 0.7% |
| Themes | AI cost 36%, other 34%, AI stability 27%, AI speed 15%, build 5.5%, UI and data 4.8%, tool sprawl 4.8% |
| Layers | whole app 70%, CI and infra 18%, frontend 14%, backend 14%, data 6.9%, interactivity 2.8% |
| Pains | costly 34%, wrong output 15%, context limits 10%, can't debug 10%, slow 9.7%, drift 9.0%, review burden 6.2%, debt 5.5% |
| Argument | anecdote 56%, generalization 11%, question 10%, venting 9%, authority 6%, measurement 4.8%, benchmark or link 0.7% |
| Evidence | personal experience 64%, none 17%, numbers 15%, outside source 3.5% |
| Flags | self-promotion 11% (16 items, excluded from complaint counts); AI written: 2 yes, 21 unsure |

By source, relevant items: Reddit 61, forums 43, Hacker News 17, DEV.to 16, Stack Overflow 8. Relevance differs by source
(Cramer's V 0.44, q < 0.001).

## 4. The core claims (lead's grouping of 145 coded claims; every item in exactly one)

| Id | Claim | n | share | complaint | experts | median PF fair | median PM fair | median uptake |
|---|---|---|---|---|---|---|---|---|
| C11 | AI tools are unstable: updates break the editor or agent, fixes lag | 17 | 11.7% | 65% | 1 | 0.09 | 0.12 | 0.47 |
| C01 | AI costs are unpredictable: limits and credits drain fast or change | 15 | 10.3% | 80% | 0 | 0.08 | 0.10 | 0.75 |
| C04 | Premium models cost more without being better; route across models | 13 | 9.0% | 31% | 1 | 0.11 | 0.14 | 0.66 |
| C12 | Builds break in the platform, not the code; opaque errors | 11 | 7.6% | 100% | 2 | 0.23 | 0.27 | 0.67 |
| C07 | Agents do destructive or out-of-scope work unless boxed in | 10 | 6.9% | 30% | 0 | 0.25 | 0.28 | 0.80 |
| C09 | AI speeds work up, but less than claimed, and can feel hollow | 10 | 6.9% | 10% | 2 | 0.19 | 0.21 | 0.67 |
| C14 | Wiring UI to data and services is where newer builders stall | 9 | 6.2% | 0% | 0 | 0.14 | 0.19 | 0.66 |
| C06 | Agents ignore rules and drift; long sessions pollute context | 8 | 5.5% | 75% | 0 | 0.13 | 0.15 | 0.58 |
| C13 | Build tooling is slow and upgrades are feared | 8 | 5.5% | 63% | 3 | 0.25 | 0.27 | 0.48 |
| C15 | Too many tools, rules files and MCP servers to glue and vet | 8 | 5.5% | 25% | 1 | 0.22 | 0.25 | 0.54 |
| C05 | Context discipline cuts cost (scoped rules, skills, less context) | 7 | 4.8% | 14% | 3 | 0.18 | 0.21 | 0.50 |
| C03 | Billing and account plumbing blocks people | 6 | 4.1% | 83% | 0 | 0.17 | 0.21 | 0.75 |
| C08 | AI writes code faster than anyone understands it; debt and risk pile up | 6 | 4.1% | 50% | 0 | 0.16 | 0.19 | 0.42 |
| C02 | People pay for AI work that failed | 5 | 3.5% | 100% | 0 | 0.19 | 0.22 | 0.72 |
| C10 | Leaning on AI erodes the skills new developers need | 5 | 3.5% | 60% | 0 | 0.17 | 0.21 | 0.89 |
| C16 | One-off observations | 7 | 4.8% | | | | | |

Read across: the most common complaints (C11, C01) are the least persuasive per word (PM fair 0.10 to 0.12): short,
annoyed, anecdotal. The most persuasive are the fix-it claims (C07, C12, C13: 0.27 to 0.28), which carry specifics. C10
(skill erosion) has the highest uptake (0.89) on few items.

**Claims grouped by the three questions behind the study:**
- **Cost:** C01, C02, C03, C04, C05 together are 31.7% of relevant items.
- **Stability:** C06, C07, C08, C11 are 28.3%.
- **Speed:** C09 is 6.9%, so speed is a minor theme now.
- **Build:** C12, C13 are 13.1%.
- **UI to data, and sprawl:** C14, C15 are 11.7%.

## 5. Persuasion (pulp style)

| Measure | median (95% CI) | IQR |
|---|---|---|
| rm_raw (rhetorical mass, real) | 716 (594 to 906) | 322 to 1,403 |
| acceleration estimate | 0.33 (0.30 to 0.34) | 0.26 to 0.37 |
| speed estimate | 0.38 (0.36 to 0.40) | 0.32 to 0.43 |
| PF fair = acceleration x rm / (rm + k) | 0.157 (0.129 to 0.181) | 0.082 to 0.219 |
| PM fair = speed x rm / (rm + k) | 0.189 (0.155 to 0.206) | 0.108 to 0.257 |

k = 716.35, the median rm_raw of batch 1's relevant items (frozen).

- **Mass is a length proxy here.** rm_raw correlates 0.95 with character count. That is the risk radiance's ADR 0003
  accepted without measuring it, and it crosses the 0.95 line in RM 3.2's open question 9 and decision 28. Raw PF and PM
  mostly rank long posts first. Rank by PF fair and PM fair, and hand this measurement to the radiance team.
- **Channel means (−1 to +1):** focus 0.56, clarity 0.51, kairos 0.33, logos 0.22, awareness 0.21, ethos 0.16, pathos 0.14,
  style 0.08. Developer posts persuade by being on point and clear, rarely by credibility or feeling.
- **By argument type (PM fair):** authority 0.25, anecdote 0.20, generalization 0.16, question 0.15, venting 0.06.
- **By evidence (PM fair):** numbers 0.27, personal experience 0.19, none 0.12.
- **By tier (PF fair):** expert 0.29 (n 14), entrant 0.17 (n 8). Underpowered.
- **Uptake:** Spearman with engagement percentile is 0.06 for PF fair and 0.06 for PM fair (Reddit alone −0.09 and
  −0.11). Persuasiveness does not predict upvotes in this sample. Caveat: archive scores are captured soon after posting
  and understate final scores.

## 6. Tools named (relevant items)

| Tool | items | net complaint | main theme |
|---|---|---|---|
| Cursor | 36 | +0.31 | stability and product bugs |
| Claude | 15 | -0.07 | cost |
| Claude Code | 13 | -0.08 | cost |
| TypeScript | 7 | +0.29 | AI stability |
| Vercel | 7 | +1.00 | build and deploy failures |
| MCP | 7 | -0.57 | tooling (mostly people building it) |
| Codex | 6 | -0.50 | cost |
| v0 | 5 | +0.60 | cost |

Net complaint = (complaints − praise or fix) / items.

## 7. Numbers people report (coded quantities)

- Monthly AI spend stated: median $100 (IQR $20 to $200, n = 9, max $700).
- Usage percentages: median 80% of a limit (n = 10).
- Build and wait times are too few to summarize (n = 4).

The next batches will add to these.

## 8. Agreement and checks

- **Blind second coder, 55 items:** relevant kappa 0.93, stance 0.84, tier 0.94, evidence 0.94, severity 0.76; themes
  Jaccard 0.90, layers 0.90, pains 0.67; channels Spearman 0.63 (kairos) to 0.92 (pathos); acceleration estimate 0.82.
  All above the 0.6 bar. Argument type (0.56) and pains (0.67) are the weakest and are read with care.
- **Quotes:** every quote is an exact substring of its source; the validator found 0 problems in 273 rows.
- **False discovery:** 72 tests, Benjamini-Hochberg. Seven pass q < 0.05: mass versus length; relevance by source; PF fair
  and PM fair by argument type and by evidence level; the learning-curve share by tier. No coded quarter comparison passes
  at this n.
- **Codebook gap for v1.1:** coders split on whether a failing build (not a slow one) is build pain. Proposed: yes, as
  build_time with pain `flaky` or `cant_debug`.

## 9. Limits

- 79% of coded items state no experience level, so tier results rest on 30 items.
- Comments cover the AI cluster only in this run (Amendment 4).
- Bluesky, GitHub issues, X, Discord and Lobsters were unreachable.
- Reddit text removal is rising, so the readable sample is partly what moderators kept.
- The acceleration estimate is Claude-judged on 8 channels, not radiance's 48-parameter judge.

## 10. What this suggests for loosethreads (to turn into hypotheses and KPIs)

| Public pain | Hypothesis to test | KPI loosethreads can measure |
|---|---|---|
| Costs drain unpredictably (C01, C02) | Contracts as compact context cut tokens per part and make cost predictable | tokens and dollars per part; variance of cost per part; share of spend on failed attempts |
| Agents drift and ignore rules (C06, C07) | Contracts plus gates keep agent output on spec without rereading rules | first-run pass rate; fix rounds to green; drift found after merge |
| Tools break on update (C11) | Pinned, checked toolchains keep lanes green across updates | red runs caused by tooling, not code; time to recover |
| Builds fail in the platform (C12) | A local render matrix catches deploy failures before the platform does | matrix catches per platform failure; share of check time in the matrix (today about 46 of 50 seconds) |
| UI to data is where builders stall (C14) | Parts that carry their data contract remove the wiring step | time to first working data-backed screen for a new builder |
| Code nobody understands (C08) | Contracts make AI output reviewable | review minutes per part |
| ICP barely visible in public talk | (collection, not a product test) | targeted sample of vibe coder and entrant FE communities in the next run |
