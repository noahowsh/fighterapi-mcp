# FighterAPI Skills catalog

Sixteen skills that turn Claude into an MMA analyst wired to the FighterAPI MCP tools (UFC since 2000, plus PFL and Bellator). Every skill states which tool it calls and what it costs in credits. Free tier: 500 credits every month, no card. Plans: https://fighterapi.com/pricing

Start with `dispatch` if you are unsure which skill fits. `fighterapi-tool` lists every tool and its credit cost.

| Skill | Category | What it does |
|-------|----------|--------------|
| [`fight-lookup`](fight-lookup/SKILL.md) | Data Exploration | Result, method, scorecards and stat sheet for one fight |
| [`event-lookup`](event-lookup/SKILL.md) | Data Exploration | Cards by year, fight-by-fight results, finish rates, upcoming fights |
| [`fighter-scouting`](fighter-scouting/SKILL.md) | Data Exploration | Scouting report: record by method, career rates, rating, recent form |
| [`odds-explorer`](odds-explorer/SKILL.md) | Data Exploration | Compare open, close and current moneylines and total rounds across books |
| [`round-by-round-stats`](round-by-round-stats/SKILL.md) | MMA Analytics | Per-round striking and grappling rates, target splits, fatigue fade |
| [`career-rates`](career-rates/SKILL.md) | MMA Analytics | Rank fighters on strikes, takedowns, control and finish rate per 15 minutes |
| [`elo-by-weight-class`](elo-by-weight-class/SKILL.md) | MMA Analytics | Elo leaderboards by division, rating gaps as win probabilities |
| [`favourite-calibration`](favourite-calibration/SKILL.md) | MMA Analytics | Closing odds vs results: do favourites win as often as priced |
| [`odds-analysis`](odds-analysis/SKILL.md) | Methodology | Odds conversion and vig removal: multiplicative, power and Shin |
| [`probability-calibration`](probability-calibration/SKILL.md) | Methodology | Reliability tables, Brier, log loss, Platt scaling, model vs closing line |
| [`walk-forward-validation`](walk-forward-validation/SKILL.md) | Methodology | Leak-free time-ordered testing for fight models |
| [`edge-detection`](edge-detection/SKILL.md) | Betting | Model vs devigged market, expected value, CLV, variance and staking caveats |
| [`backtesting`](backtesting/SKILL.md) | Betting | Simulate betting rules on past cards with opening and closing lines |
| [`fight-preview`](fight-preview/SKILL.md) | Workflow | Matchup preview: form, rates, physical gaps, rating gap and the market |
| [`fighterapi-tool`](fighterapi-tool/SKILL.md) | Infrastructure | Tool router: all 11 tools, credits, response envelope, REST and MCP |
| [`dispatch`](dispatch/SKILL.md) | Infrastructure | Routes a request to the two or three skills that should load together |

## Notes

- Lines are moneylines and total rounds. There are no player props, method-of-victory or round markets, so there is no prop-modeling skill.
- Stat sheets, round-by-round lines and career rates are UFC only. PFL and Bellator have results, fighters and ratings.
- UFC opening and closing lines start with the June 2020 cards. See https://fighterapi.com/docs for coverage by season.
- Betting skills give estimates and warn about variance, sample size and closing-line value. They are analysis, not advice to wager.
