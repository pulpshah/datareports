# TAM, SAM and SOM for loosethreads as an MCP offering (Oct 23 2026)

**A sizing under stated assumptions, not a forecast.**
- Every input is a range labeled **measured** (this study), **external** (a cited source) or **assumed** (a judgment for
  Shah to confirm or replace).
- 200,000 simulated draws turn the ranges into the 80% ranges below.
- Change an assumption in `analysis/tam.py` and rerun to see the effect.

## Result (median, with the 80% range)
| | People | Dollars a year |
|---|---|---|
| **TAM:** everyone building software with AI weekly | 32.5M (29.4M to 35.6M) | **$11.3B** ($8.0B to $16.0B) |
| **SAM:** the ICP in reachable markets | 2.2M (1.75M to 2.73M) | **$767M** ($515M to $1.13B) |
| of which entrant FE developers who pay for or choose AI tools | 1.86M | |
| of which higher-end vibe coders | 0.34M | |
| **SOM:** paying within 3 years | 35,600 seats (20,900 to 55,000) | **$12.3M ARR** ($6.7M to $21.3M) |

All at an assumed $15 to $50 a seat a month (mode $25).

**Two cross-checks:**
- **Against spend that exists today:** TAM is 1.4 times current AI coding tool spend (80%: 0.9 to 2.0 times), using
  $6B to $11B a year. Read TAM as an upper bound: every weekly AI builder paying for one add-on.
- **The pain pool (heavily assumed, a reference only):** about $51B a year (80%: $24B to $103B) of builder time lost to
  the problems contracts and gates address. It rests on a measured median of 3 hours per stated incident, times assumed
  frequency, hourly value and addressable share. It shows the problem is large relative to the price. It is not
  revenue.

## What moves the answer
Rank correlation of each input with SOM:

| Input | Correlation | Kind |
|---|---|---|
| 3-year penetration | 0.72 | assumed |
| Price a seat | 0.55 | assumed |
| Paying or choosing share | 0.25 | assumed |
| Entrant share | 0.17 | assumed |
| Reachable share | 0.15 | assumed |
| Web share | 0.12 | assumed |

**So SOM is mostly a go-to-market question:** price and penetration. Better market data barely moves it. The research
can narrow price; penetration needs a real launch signal.

## What the research says about price and willingness (measured)
- **Price anchors:** AI coding spend clusters at $20, $100 and $200 a month (986, 418 and 674 mentions). A $20 to $25
  entry seat sits at the most familiar anchor.
- **Cost is the top pain and rising:** cost talk went from 29.2% to 36.2% of posts in AI communities, and the median
  stated bill rose from $75 in W1 to $166 in W3. A product that makes cost per part predictable answers the most-voiced
  complaint. Selling "cheaper" would answer a lesser one.
- **Time lost:** median 3 hours per stated incident (n = 5,435).
- **Who pays more:** higher-end vibe coders already state $25 to $200 a month across tools; learners rarely talk money
  (2% to 3% of posts). The 0.34M higher-end vibe coders are a smaller slice of SAM but likely tolerate a higher price
  than the 1.86M entrant FE developers. That points to two tiers.
- **Reach for go-to-market:** in one year, 66,010 distinct people posted about these pains in the AI communities studied
  alone (r/ClaudeAI 26,644, r/vibecoding 22,286, r/ClaudeCode 18,940). That is a channel size, not a market size.

## Inputs
| Input | Low | Mode | High | Kind | Source |
|---|---|---|---|---|---|
| Developers worldwide | 40.2M | 47.2M | 48.4M | external | IDC 2025 projection; SlashData 2025; a Q3 2025 secondary figure |
| Share using AI weekly | 51% | 62% | 65% | external | Stack Overflow 2025: 51% of professionals daily; 47.1% daily plus 17.7% weekly overall |
| Active non-developer AI builders | 2M | 5M | 10M | assumed | Lovable ~8M users, Bolt 5M+, Replit 40M (mostly free, overlapping) |
| Price a seat a month | $15 | $25 | $50 | assumed | anchored by the measured $20 tier |
| Entrant share (under about 5 years) | 25% | 32% | 40% | assumed | Stack Overflow 2025 shows early career as a large group |
| Web front end or full stack share | 40% | 48% | 55% | assumed | |
| Pays for or chooses AI tools | 30% | 45% | 60% | assumed | |
| Paying vibe-platform builders | 0.8M | 1.2M | 1.8M | external | Lovable ~$400M ARR at $30 to $50 a month; Replit 175K paying (Sacra); Bolt ~0.1M |
| Higher-end share of those | 30% | 45% | 60% | assumed | |
| Reachable share (English and web first) | 50% | 60% | 70% | assumed | |
| 3-year penetration of SAM | 0.5% | 1.5% | 3% | assumed | typical early devtools range |
| AI coding tool spend, 2026 | $6B | $8B | $11B | external | Cursor >$2B annualized; Claude Code $2.5B (Anthropic's claim); Lovable ~$0.4B; Copilot assumed $1.5B to $4B |
| Hours lost per incident | 1 | 3 | 8 | measured | this study, median 3 (n = 5,435), capped |
| Incidents a month; hourly value; addressable share | 1 to 4; $25 to $75; 20% to 50% | | | assumed | pain pool reference only |

## Limits
- Most inputs are external or assumed. Only the price anchors and the hours lost come from this study.
- **External figures are uneven.** Cursor's revenue comes via Bloomberg; Claude Code's run rate is Anthropic's own claim;
  vibe-platform user counts mix free and paid. None is audited.
- **The ICP is defined by judgment** (experience, web share, paying share). The ICP-targeted collection now running
  (Amendment 5) will show how these people talk and what they pay, which can replace several assumptions with
  measurements.
- **Nothing here says what loosethreads should charge.** That is Shah's call. The price and penetration rows are where his
  numbers go.

## Sources
- [ShiftMag: there are 47 million developers in the world (SlashData)](https://shiftmag.dev/there-are-47-million-developers-in-the-world-5200)
- [Quash: software development statistics 2026](https://quashbugs.com/blog/software-development-statistics)
- [Stack Overflow Developer Survey 2025, AI](https://survey.stackoverflow.co/2025/ai)
- [Stack Overflow press: 2025 survey, trust in AI at a low](https://stackoverflow.co/company/press/archive/stack-overflow-2025-developer-survey/)
- [TechCrunch: Cursor has reportedly surpassed $2B in annualized revenue](https://www.techcrunch.com/2026/03/02/cursor-has-reportedly-surpassed-2b-in-annualized-revenue/)
- [Dealroom: Cursor doubles revenue to $2B](https://app.dealroom.co/news/note/cursor-doubles-revenue-to-2b-amid-slowdown-speculation)
- [Sacra: Replit at $106M ARR](https://sacra.com/research/replit-at-106m-arr)
- [Tech Insider: Lovable eyes a $12B valuation](https://tech-insider.org/ie/lovable-vibe-coding-12-billion-2026/)
- [SaaStr: the vibe coding TAM](https://www.saastr.com/the-vibe-coding-tam-how-big-can-this-market-really-get)
- [GitHub Octoverse 2025](https://github.blog/news-insights/octoverse/octoverse-a-new-developer-joins-github-every-second-as-ai-leads-typescript-to-1/)
