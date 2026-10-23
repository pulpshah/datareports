# Money in public developer talk (Oct 23 2026)

Every dollar amount, credit figure, token count and time-lost statement in all 277,504 pooled items, found by fixed
patterns with no model (`analysis/money.py`). These are amounts people **state**, not verified spend. They are the
evidence base for pricing and the input to TAM, SAM and SOM, which come next.

## Headline
1. **Three price points dominate AI coding spend: $20, $100 and $200 a month.** Of the "per month" amounts, $20 appears
   986 times, $200 674 times and $100 418 times. Those are the Pro, Max and Ultra tiers of the main tools. The median
   by plan word: pro $20, plus $20, max $150 (IQR $100 to $200), ultra $200, team $100.
2. **When people state a bill or an overage, the median is $100** (IQR $20 to $500, n = 2,306 items). The bill median
   rose from $75 in W1 to $100 in W2 and **$166 in W3**, then fell back to $100 in W4. That matches the cost-talk peak in
   r/ClaudeCode in W3, and the limit increases reported in May.
3. **AI communities talk money about twice as often as developers, and four times as often as learners.**

   | Community cluster | W1 | W2 | W3 | W4 |
   |---|---|---|---|---|
   | AI | 11.4% | 12.0% | 10.9% | 12.1% |
   | general (HN, DEV.to, Vercel forum, Stack Overflow) | 7.1% | 8.1% | 8.8% | 6.3% |
   | dev | 5.5% | 6.1% | 5.1% | 4.7% |
   | learner | 3.3% | 2.8% | 2.1% | 2.4% |

   Share of each cluster's pooled items that state a dollar amount.
4. **Time lost, when stated, has a median of 3 hours** (IQR 20 minutes to 48 hours, n = 5,435 items). Learners report the
   most (median 4 hours).
5. **Credits:** median 100 when a figure is stated (n = 1,075). **Tokens:** median 106,000 (n = 4,353), with a very long
   tail.

## Per-month amounts per item (one value per item, so a long post with many prices does not dominate)
| Cluster | n | median | IQR | p90 |
|---|---|---|---|---|
| AI | 3,290 | $50 | $20 to $200 | $500 |
| general | 2,697 | $50 | $10 to $800 | $5,000 |
| dev | 268 | $40 | $15 to $204 | $1,500 |
| learner | 25 | $25 | $10 to $100 | $736 |

## How much to trust it
- **Precision check:** 30 random "per month" mentions, read by hand.
  - About 60% are real AI coding tool spend (Cursor, Claude, Codex, ChatGPT plans; AI site hosting).
  - About 25% are other software prices people quote (screenshot APIs, storyboard tools, cloud droplets).
  - About 10% are income the pattern missed ("making $70k/month", "earns $5k/month").

  The income pattern is widened for the next run.
- **What holds:** the medians and the $20, $100 and $200 anchors are robust. Means and the 90th percentile are not; the
  tail mixes income and business figures.
- **Unclassified:** 14,674 items state an amount with no clear unit or purpose ("one-off or unclear"). They are kept but
  not used above.
- **Scale and selection:** this is what people choose to say in public. Heavy spenders and angry users are
  overrepresented.

## Files
- `reports/money.json`: every number above.
- `reports/tables/money_mentions.csv`: all 65,016 mentions with their context (200 characters), source, community and
  quarter.
- `reports/tables/money_usd_share_by_cluster_window.csv`

## Next (waiting on Shah's go)
TAM, SAM and SOM. Inputs:
- these amounts;
- the 125,972 unique authors by cluster;
- outside data on developer population, AI tool adoption and plan prices.

Measured, external and assumed inputs stay in separate columns.
