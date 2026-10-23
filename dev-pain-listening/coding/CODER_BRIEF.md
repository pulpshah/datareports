# Coder brief (codebook v1)

You are coding public posts and comments by software developers, collected from Reddit, Hacker News, the
Cursor and Vercel forums, DEV.to and Stack Overflow, dated Oct 2025 to Oct 2026. Each item is one JSON line in
your input file. You code every item independently, from its own words. You never browse, never look an
author up, and never guess: where the item gives no evidence, use `unknown`, `none` or an empty list.

The study is about what developers say regarding **build times** (compile, typecheck, test, CI, dev server,
hot reload, and the time it takes to get a working feature built) and **AI assisted development** (its cost,
its speed, and its stability), across frontend, data, interactivity and backend work.

## Input fields you use

`id`, `src`, `kind` (post, comment, story, article, question), `community`, `date`, `parent_title` (for a
comment: the title of the post it replies to; context only), `title`, `own_text` (the words you code),
`author_flair` (a self chosen label; it can be evidence of experience).

## Output

Write one JSON object per input item, one per line, to the output file named in your task, in the input
order. Every key below must be present.

```json
{"id": "...",
 "relevant": true,
 "stance": "complaint",
 "themes": ["ai_cost"],
 "layers": ["fe"],
 "pain_types": ["costly"],
 "tier": "vibe_coder",
 "tier_evidence": "I'm a designer, I don't read the code",
 "tier_confidence": "high",
 "icp": "high_end_vibe_coder",
 "tools": ["Cursor", "Claude"],
 "severity": "blocked",
 "claim": "One plain sentence stating what the item claims.",
 "argument_type": "anecdote",
 "evidence_level": "personal_experience",
 "quantities": [{"value": 200, "unit": "USD per month", "about": "Cursor bill"}],
 "events": ["Cursor pricing change"],
 "quote": "exact words copied from own_text",
 "suspected_promo": false,
 "suspected_ai_written": "false",
 "channels": {"ethos": 0.2, "pathos": 0.4, "logos": 0.1, "kairos": 0.5, "style": 0.0, "clarity": 0.3, "focus": 0.4, "awareness": -0.1},
 "notes": ""}
```

## Fields

**relevant**: true when the item states a pain, problem or cost, or a counter to one (praise, a fix, a
disagreement, a measured result), about build times or AI assisted development, or about the difficulty of
connecting user interface to data and backend. False for news reposts with no stance, job posts, unrelated
topics, and keyword accidents ("build" a team, "vite" in a username). An irrelevant item still gets every key;
use `irrelevant`, empty lists, `none` and zeros.

**stance**: `complaint` (mainly a pain), `mixed` (pain and praise or fix together), `praise_or_fix` (mainly
says something works, or gives a fix), `neutral_question` (asks without stating a pain), `irrelevant`.

**themes** (one or more):
- `build_time`: machine time to compile, typecheck, test, bundle, deploy, run CI, start a dev server or reload.
- `ai_cost`: money, tokens, credits, plans, usage limits, rate limits.
- `ai_speed`: whether AI makes the work faster or slower, waiting on the agent, time lost to rework.
- `ai_stability`: AI output that is wrong, drifts, regresses, breaks working code, ignores instructions,
  forgets context, is inconsistent across runs, or a model that got worse.
- `ui_data_gap`: the user interface is separated from the data, backend or state, and wiring them together
  is hard (full stack plumbing, schemas, data fetching, forms that capture data, keeping UI and data in sync).
- `tool_fragmentation`: too many separate tools, switching between them, glue work.
- `other`: relevant, but none of the above.

**layers** (one or more): `fe` (UI, components, styling, design systems), `data` (what the app captures,
stores, models and shows: schemas, databases, data fetching, analytics, charts), `interactivity` (state,
events, animation, gestures, realtime, forms behavior), `be` (servers, APIs, auth, jobs), `ci_infra` (build
tools, CI, deploys, hosting, containers), `cross` (the whole app, or not specific).

**pain_types** (one or more, or `none` for praise): `slow`, `flaky` (passes and fails without a change),
`costly`, `wrong_output`, `drift_inconsistency`, `lock_in`, `cant_debug` (cannot find why something broke),
`learning_curve`, `context_limits`, `review_burden` (too much to review or check), `debt_buildup` (mess,
shortcuts or unreadable code piling up), `scattered_tools`, `none`.

**tier**, from evidence in the item only, never from tone or grammar:
- `expert`: states 5 or more years, a senior, staff, principal or lead role, or shows production specifics
  used correctly (profiling, build graphs, cache keys, flags, CI configuration, architecture tradeoffs).
- `intermediate`: states 2 to 4 years, or a working developer role, without expert signals.
- `entrant`: states under 2 years, learning, a course or bootcamp, a first job, a junior role, a student.
- `vibe_coder`: builds mainly by prompting AI and says they do not write or read most of the code, or calls
  themselves a non developer (designer, founder, product manager, marketer) who builds with AI.
- `unknown`: no evidence. This is common and correct.

**tier_evidence**: the words or signal you used, copied or closely paraphrased, or `none`.
**tier_confidence**: `low`, `medium`, `high`. Use `low` for vocabulary alone, `high` for an explicit statement.

**icp**: `high_end_vibe_coder` (a vibe_coder who ships real products, pays for several tools, or talks about
architecture, technical debt, scaling or deployment), `entrant_fe` (an entrant whose work is frontend),
`neither`, `unknown` (tier unknown).

**tools**: products, frameworks and models named, as written (Cursor, Claude Code, Next.js, Turbopack, Vite,
Supabase, v0, Lovable, GPT-5, and so on).

**severity**: `annoyed`, `blocked` (cannot proceed, lost a day, project stuck), `switched_or_quit` (changed
tool, canceled, gave up), `none`.

**claim**: the item's main claim in one plain sentence in your words, specific enough to compare with other
items ("Next.js production builds on CI take 9 minutes and the cause cannot be found"), not a topic label.

**argument_type**: the main way the item supports its claim: `anecdote` (what happened to me), `measurement`
(my own numbers), `benchmark_or_link` (points to an outside source), `authority` (trust me, or a named expert
says), `generalization` (everyone, always, all), `analogy`, `prediction`, `venting` (feeling with no support),
`question`.

**evidence_level**: `none`, `personal_experience`, `numbers_given`, `external_source`. Pick the strongest
present.

**quantities**: every number with a unit that the item states (minutes, seconds, dollars, tokens, percent,
files, lines), as `{value, unit, about}`. Empty list if none.

**events**: named events the item refers to (a model or tool release, a pricing or limit change, an outage, a
policy change), as written. Empty list if none.

**quote**: the most representative span, at most 300 characters, **copied character for character from
own_text** (a script checks this). Do not fix typos, do not join separate sentences with "...".

**suspected_promo**: true when the item promotes the poster's own product, course or service.
**suspected_ai_written**: `true`, `false` or `unsure`.

**notes**: anything a second reader should know (sarcasm, a reply that only makes sense with its parent, a
truncated item). Usually empty.

## channels: how persuasive the item is, on eight channels

Score each channel from -1.0 to +1.0 in steps of 0.1, against this one objective for every item:
**"persuade readers in this community that the item's claim about building software is true and worth
acting on."** Score what the text does, not whether you agree with it. 0.0 means the channel is absent or
neutral. Positive means the channel helps the text persuade; negative means it works against it. Most items
are modest: reserve values beyond plus or minus 0.7 for clear cases. Irrelevant items get 0.0 on every channel.

- **ethos**: the speaker's standing to be believed, the character, competence and legitimacy the text
  projects. Dimensions: trust, influence, capability, reliability, assurance, acceptance. (+ shows real
  experience and good faith; - projects incompetence, bad faith or an agenda.)
- **pathos**: the feelings the text evokes in readers and what they dispose readers to do. Dimensions:
  sentiment, vulnerability, expectation, alertness, togetherness, pity. (+ feelings that move readers toward
  the claim, like shared frustration or relief; - feelings that push readers away, like contempt for them.)
- **logos**: the argument as an argument: premises, inferences, and whether they hold together. Dimensions:
  premise, conclusion, fallaciousness, validity, bias, soundness. (+ reasons that support the conclusion;
  - fallacies, contradictions, a conclusion the premises do not support.)
- **kairos**: fit between the text and its moment: timing, phase, pacing and horizon for this community now.
  Dimensions: window fit, phase fit, turn ecology, tempo stability, readiness match, horizon alignment.
  (+ lands on a live issue at the right moment; - stale, premature, or out of step with the thread.)
- **style**: the surface craft: register, figure, cadence, imagery, judged by whether it serves the message.
  Dimensions: tone, humor, repetition, visualization, rhythm, contrast. (+ craft that helps; - craft that
  hurts, like hostile sarcasm or a wall of text.)
- **clarity**: how much work it costs a reader to understand it correctly. Dimensions: comprehensibility,
  precision, coherence, cohesion, conciseness, structure. (+ easy to follow and exact; - confusing, vague.)
- **focus**: whether the text keeps its attention on the live question and the objective. Dimensions: topic
  adherence, goal alignment, prioritization, semantic depth, responsiveness, diversion. (+ stays on point and
  goes deep; - wanders, diverts.)
- **awareness**: the thinking the text displays about its own thinking: how it handles its own biases, and
  whether it stays revisable. Dimensions: system 1, system 2, logic, bias, virtues, presence. (+ admits limits,
  weighs alternatives; - dogmatic, unaware of its own bias.)

## Rules

- Code every item; never skip one. Keep the input order.
- Never invent a fact that is not in the item.
- Output only the JSON lines to the file, nothing else in the file.
