---
name: dispatch
description: "Routes a FighterAPI request to the two or three skills that should load together. Use first when a UFC, PFL or Bellator request arrives and it is unclear which skill applies, for example 'break down this card', 'is the favourite overpriced', 'who has the best cardio', or 'backtest a model'. Do not use once the skill is obvious. Do not use for the data itself -- see fighterapi-tool."
metadata:
  version: 1.0.0
  author: FighterAPI
---

# Dispatch

> **Default data tool:** FighterAPI (`fighterapi-tool`). Dispatch makes no tool calls itself.

Load the smallest set of skills that answers the request. Loading all sixteen wastes context and credits. Pick one primary skill, add at most two supporting skills.

## Routing Table

| User Says | Primary | Add |
|-----------|---------|-----|
| "Who won, how, what round" | `fight-lookup` | |
| "What happened at UFC 300" or "show me last Saturday's card" | `event-lookup` | `fight-lookup` |
| "Tell me about this fighter" | `fighter-scouting` | `career-rates` |
| "Best strikers, best grapplers, who has the best chin" | `career-rates` | `fighter-scouting` |
| "How does he fade in round 3", "strikes per round", "control time" | `round-by-round-stats` | `fight-lookup` |
| "Top Elo at welterweight", "who is underrated by rating" | `elo-by-weight-class` | `probability-calibration` |
| "Preview this fight" or "who wins" | `fight-preview` | `fighter-scouting`, `odds-explorer` |
| "Best price", "which book", "did the line move" | `odds-explorer` | |
| "Convert odds", "remove the vig", "true probability" | `odds-analysis` | |
| "Are favourites overpriced", "do -300 favourites win 75%" | `favourite-calibration` | `odds-analysis` |
| "Is my model good", "is this model calibrated" | `probability-calibration` | `walk-forward-validation` |
| "Test my model without cheating" | `walk-forward-validation` | `probability-calibration` |
| "Is there value on this fight" | `edge-detection` | `odds-analysis`, `elo-by-weight-class` |
| "Backtest this strategy" | `backtesting` | `walk-forward-validation`, `edge-detection` |
| "What can I call, what does it cost" | `fighterapi-tool` | |

## Multi-skill Workflows

| Workflow | Skill Order |
|----------|-------------|
| Fight-night card breakdown | `event-lookup` then `fight-preview` for each fight the user picks |
| Is there a bet here | `odds-explorer` then `odds-analysis` then `edge-detection` |
| Build and validate a rating model | `elo-by-weight-class` then `walk-forward-validation` then `probability-calibration` |
| Test the market | `favourite-calibration` then `backtesting` |
| Scout a division | `elo-by-weight-class` then `career-rates` then `fighter-scouting` |

## Disambiguation

- "Odds" can mean looking at prices (`odds-explorer`) or converting and devigging them (`odds-analysis`). If the user has a number in hand and wants a probability, `odds-analysis`. If they want to see what books are posting, `odds-explorer`.
- "Rating" in this pack is our Elo from `get_ratings`. It is not an official promotion ranking. Say so when a user asks for "the rankings".
- "Stats" for a single fight means `fight-lookup`. Stats as rates over a career means `career-rates`. Stats by round means `round-by-round-stats`.
- A request about PFL or Bellator uses the same skills with `league=pfl` or `league=bellator`. Stat sheets are null there, so route round and rate requests to a UFC alternative or say they do not exist.

## Scope Guards

- There are no player props, method-of-victory or round-group markets in the data. Lines are moneylines and total rounds. Decline prop-modeling requests and say what is available.
- There are no teams. Do not route to a team-analysis workflow.
- Betting requests: load `edge-detection` so the answer carries the variance and closing-line caveats.

## Example Routings

| Request | Skills Loaded | Why |
|---------|---------------|-----|
| "Break down UFC this Saturday" | `event-lookup`, then `fight-preview` for the main event | The card first, then depth where the user points |
| "Is Makhachev really -400?" | `odds-explorer`, `odds-analysis` | Show the price across books, then the devigged probability |
| "Who are the best wrestlers at 170?" | `career-rates` | One `get_leaders` call per stat with `weight_class` set |
| "Does he gas out late?" | `round-by-round-stats` | Needs `get_fight` on several distance fights |
| "Would underdogs at +250 have made money since 2021?" | `backtesting`, `favourite-calibration` | A price test, with the market benchmark |
| "Rate this fighter 1 to 10" | `fighter-scouting` | Reports numbers, declines to invent a score |
| "Is my XGBoost model any good?" | `walk-forward-validation`, `probability-calibration` | Split, then calibration, then the market comparison |
| "Prop bets on round or method" | none | Not in the data; say so and offer moneyline and total rounds |

## Credit-aware Routing

Pick the cheapest path that answers the question, and tell the user the cost when it exceeds about 20 credits.

| Question Shape | Cheapest Path | Credits |
|----------------|---------------|---------|
| Results for a card | `get_event` | 2 |
| Prices for a card | `get_odds` with `event_id` | 10 |
| One fighter, quick read | `search_fighters` + `get_fighter` | 6 |
| One fighter, full history | `get_fighter_fights` | 5 per page |
| A division's best at a stat | `get_leaders` | 5 |
| Division rating order | `get_ratings` | 2 |
| One year of closing lines | `list_events` + `get_odds` per card | about 520 |

The free tier is 500 credits every month with no card, so a year of closing lines does not fit in a month. Plan the pull or sample cards. Plans are at https://fighterapi.com/pricing.

## When a Request Spans Promotions

UFC has stat sheets, round lines, career rates and the longest odds history. PFL and Bellator have results, fighters and ratings, with lines only for part of their history. If the user asks for round-level or rate analysis on a PFL or Bellator fighter, say it is not available and offer the results, record and rating instead.

## Pre-flight Questions

Ask only what is missing, in one message:

1. Which promotion (UFC by default)?
2. Which fighter or card, and what date range?
3. For modeling: what is the target (win, method, finish) and how many credits may be spent?

## Anti-patterns

| What Claude Might Do | Why It Is Wrong | Do This Instead |
|---------------------|----------------|-----------------|
| Load every skill "to be safe" | Burns context, dilutes the answer | One primary, up to two supporting |
| Route "who wins" straight to `edge-detection` | An edge needs a price and a probability first | `fight-preview`, then `edge-detection` if the user wants a bet |
| Route calibration questions to `backtesting` | Calibration is about probabilities, not bankroll | `probability-calibration` |
| Skip `fighterapi-tool` for credit questions | It owns the costs | Load it when cost is the question |

## The Sixteen Skills

| Group | Skills |
|-------|--------|
| Data exploration | `fight-lookup`, `event-lookup`, `fighter-scouting`, `odds-explorer` |
| MMA analytics | `round-by-round-stats`, `career-rates`, `elo-by-weight-class`, `favourite-calibration` |
| Methodology | `odds-analysis`, `probability-calibration`, `walk-forward-validation` |
| Betting | `edge-detection`, `backtesting` |
| Workflow | `fight-preview` |
| Infrastructure | `fighterapi-tool`, `dispatch` |

The full catalog with one-line descriptions is in `skills/README.md`.

## What to Do Next

After routing, hand control to the primary skill and let it call `fighterapi-tool` for data.
