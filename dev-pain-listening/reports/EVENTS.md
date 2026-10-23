# What moved the spikes: event timeline (Oct 23 2026)

The weekly Hacker News spikes from `reports/trends.json`, each checked two ways: the top stories in that week for that
keyword (pulled from the Hacker News archive, at no cost) and a web search for a dated outside event.

**The rule** (PROTOCOL section 9) ties a spike to an event only when the counts move within two weeks of a dated event
and the posts themselves name it. Otherwise the result is "timing only" or "unexplained". This is correlation, not
proof of cause.

| Spike (week of) | Count | What the week's stories say | Outside event | Verdict |
|---|---|---|---|---|
| "vibe coding", Jan 22 | 428 | "After two years of vibecoding, I'm back to writing by hand" (865 points, 634 comments, Jan 26); "Gas Town's agent patterns ... vibecoding at scale" (403 points); "Vibe coding kills open source" (arXiv 2601.15494, 330 points) | The posts are the event: a backlash moment | **Attributed** (the week's top stories). It comes just before AI-speed talk begins its steady fall (AI communities 22.0% in W1 to 14.9% in W4). |
| "cursor pricing", Jan 8 | 8 | "Cancelled 2x Cursor Ultra plans, here's why"; "Ask HN: Cursor (LLM) Costs" | None found | **Timing only:** user reports, no dated change. It matches coded claim C01 ("Ultra limits hit at $1,700 one month and $800 the next"). |
| "cursor pricing", Mar 12 | 10 | "Cursor models are now MAX mode only" (Mar 17) | From Mar 16, Team and Enterprise accounts on legacy request pricing must turn on Max Mode to use frontier models (GPT 5.3 Codex, GPT 5.4, Opus 4.5 and 4.6, Sonnet 4.5 and 4.6). Cursor's reason: frontier models use far more tokens. Source: Cursor's own forum megathread. Also Mar 13: Anthropic made the 1M context window generally available at standard pricing, while Cursor's page still showed about 2x above 200k input tokens. | **Attributed:** a dated change, named by the week's posts. |
| "usage limits", Apr 16 | 156 | "Ask HN: Did Claude lower its usage limits?" (Apr 20); "TIL: You can read Claude Code quota locally"; "Hydra: never stop coding when your AI CLI hits a rate limit" | A Mar 31 Substack post reports Anthropic quietly tightening 5-hour sessions during U.S. weekday hours. This is a single unofficial source; no official notice was found. | **Probable:** people perceived a cut, but the event itself is unconfirmed. |
| "rate limit", Feb 19 | 167 | Tools to resume coding sessions across Claude, Gemini and Codex when limited ("npx continues") | None found | **Timing only:** a wave of workarounds, not one event. |
| "turbopack", Jan 15 to 22 and Apr 2 to 9 | 6 to 11 | No stories; comments only | Only third-party notes on a January Turbopack engineering post and steady 16.2 patch releases | **Unexplained:** tiny counts. |
| "technical debt", Feb 26 | 190 | "Garbage In, Garbage Out: the degradation of human requirements in the LLM era" (9 points) | None | **Unexplained**, and small. |
| "cursor pricing", Jun 11 and Jul 30 | 12 and 10 | No relevant story | None dated. A Cursor forum thread complains that Cursor still required Max Mode after a large OpenAI price cut, but its date is not confirmed. | **Unexplained.** |
| "build times", Mar 5 | 594 | No relevant story | None | **Noise:** the keyword matches broadly. |

## The Claude limits sequence later in the year (for the Q3 and Q4 reading)
These dates come mostly from third-party sources, so they should be checked against Anthropic's help center:
- May 6: 5-hour limits doubled for paid plans, and the peak-hour throttle was removed (Verdent).
- May 13: weekly limits up 50% on Pro, Max, Team and seat-based Enterprise, set to expire Jul 13 (Verdent).
- Aug 29: the temporary increase was extended to Sep 14, followed by a permanent 25% increase, which BleepingComputer
  frames as a 17% cut from the temporary level.

How it reads against the counts: "usage limits" on Hacker News peaked in W2 (1,027) and eased in W3 (950) and W4 (850),
consistent with the May increases. Cost talk in AI communities still rose every quarter (29.2% to 36.2%), so limits
easing did not end the cost conversation. In r/ClaudeCode, cost talk peaked in W3 (41.3%) and eased in W4 (39.1%).

## Sources
- [Cursor forum: Frontier models moving to Max Mode for legacy Team and Enterprise plans](https://forum.cursor.com/t/megathread-frontier-models-moving-to-max-mode-for-legacy-team-enterprise-plans/155053)
- [Cursor forum: 1M context GA at standard pricing for Opus 4.6 and Sonnet 4.6](https://forum.cursor.com/t/anthropic-just-announced-1m-context-ga-at-standard-pricing-for-opus-4-6-sonnet-4-6-when-will-cursor-reflect-this/154701)
- [Cursor forum: OpenAI price cut, Cursor still requires Max Mode](https://forum.cursor.com/t/openai-drops-gpt5-6-luna-prices-80-yet-cursor-still-requires-max-mode/167144)
- [Substack: Claude usage limits (Mar 31)](https://nicholasrhodes.substack.com/p/claude-usage-limits-fix)
- [Verdent: Claude Code limits doubled, May 2026](https://www.verdent.ai/es/guides/claude-code-limits-doubled-may-2026)
- [BleepingComputer: Anthropic cutting Claude Code's current weekly limits by 17 percent](https://www.bleepingcomputer.com/news/artificial-intelligence/anthropic-is-cutting-claude-codes-current-weekly-limits-by-17-percent/)
- [DataCamp: Claude Code usage limits](https://www.datacamp.com/tutorial/claude-code-usage-limits)
- [releases.sh: Next.js release highlights](https://releases.sh/vercel/next-js/highlights)
- Hacker News stories as cited, from the Algolia archive (`hn.algolia.com`).
