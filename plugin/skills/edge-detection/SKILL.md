---
name: edge-detection
description: "Compares a model or rating probability with the devigged closing or current moneyline on a UFC, PFL or Bellator fight to estimate expected value, fair price, and stake sizing, with variance and closing-line-value caveats. Use when the user asks if there is value on a fight, whether a price is too long or too short, or what a fair line is for their probability. Do not use for removing the vig -- see odds-analysis. Do not use to build or validate the model -- see walk-forward-validation. Do not use for props: none exist in the data."
metadata:
  version: 1.0.0
  author: FighterAPI
---

# Edge Detection

> **Default data tool:** FighterAPI (`fighterapi-tool`).
> Use `get_odds` with `bout_id` (5 credits) for prices, `get_schedule` (2 credits) for upcoming fights with `lines`, and `get_fighter` (5 credits) for rating and form inputs.

You are an expert in bet evaluation. Your goal is to say whether a belief about a fight differs from a price by more than the noise and the vig, and to be loud about how uncertain that is. These are estimates, not promises.

## When to Use

- "Is there value on this fight?"
- "What is a fair price at 58%?"
- "Which side does my model like on Saturday's card?"
- Ranking a card's fights by the gap between a model and the market

## When NOT to Use

- Converting odds or devigging -- see `odds-analysis`
- Fitting or testing the model -- see `walk-forward-validation` and `probability-calibration`
- Historical profit tests -- see `backtesting`
- Method of victory and round props -- not in the data

## Commands Available

| Command | What It Does | Credits |
|---------|-------------|---------|
| `get_odds` | Per-book open, close and current moneyline for a fight or card | 5 / 10 |
| `get_schedule` | Upcoming fights with the current `lines` | 2 |
| `get_line_movement` | Recent snapshots, to see where the price is heading | 10 |
| `get_fighter` | Rating, rates and form for a model input | 5 |

## Commands That Do NOT Exist

| Not Available | Use Instead |
|--------------|-------------|
| `get_edges` or `get_value_bets` | Compute with the steps below |
| `get_predictions` | Not available: bring your own probability or use a rating prior |
| `get_props`, `get_method_odds` | Not available |

## Prerequisites

1. A probability for one named fighter, from a model that passed `walk-forward-validation` and was calibrated in `probability-calibration`. A raw Elo gap is a weak prior, not a model.
2. The market probability, devigged (`odds-analysis`), using the median across books.
3. The best available price for the side in question (`odds-explorer`).

If the model has not beaten the devigged close out of sample, do not look for edges with it. The market is likely better.

## Calculation

Let `p` be your probability for fighter X and `o` the decimal odds you can actually get.

```python
def ev_per_unit(p, decimal_odds):
    return p * (decimal_odds - 1) - (1 - p)

def edge_points(p_model, p_market_devig):
    return p_model - p_market_devig

def fair_american(p):
    return round(-100 * p / (1 - p)) if p >= 0.5 else round(100 * (1 - p) / p)
```

- **Edge in points** compares probabilities (model minus devigged market). It ignores the vig you still pay.
- **Expected value** compares your probability with the price you can take. It is the real test. Positive EV needs `p` above the raw break-even `1/decimal`.
- **Fair price** is `fair_american(p)`. Compare it with the best posted price. Taking a price shorter than fair costs EV.

Real price reference (UFC 298, Bet365 close): -130 on side `a`, +110 on side `b`. Break-even at -130 is 56.5%, at +110 it is 47.6%. If your belief for side `b` is 49%, EV per unit at +110 is `0.49*1.10 - 0.51 = 0.029`, about +2.9%, and that is before you ask whether your 49% is good to within a few points. It almost never is.

## Uncertainty First

Fight probabilities are imprecise.

- Ratings built from a handful of fights carry error of several points either way.
- A 3 point model edge on an 8 point model error is not an edge.
- Report a range. Run the calculation at `p - 0.04` and `p + 0.04`. If EV changes sign across the range, call it "no edge at the model's resolution".
- Require a minimum: for example EV above 3 to 5% at the pessimistic end before calling anything a candidate.

## Closing-Line Value

The best public evidence an edge is real is that the line moves your way.

1. Record the price you took and the closing price from `get_odds` after the fight.
2. Compute devigged probability of your side at the take, and at the close.
3. CLV in points = close probability minus take probability. Persistently positive CLV across many fights is stronger evidence than short-run profit.

A profit on 30 fights with negative CLV is likely luck. Positive CLV on 100+ fights is the signal to trust.

## Variance

- A 55% fighter loses 45 times in 100. Over 20 bets, a real 4% edge has a wide range of outcomes including a loss.
- Fights are single-event, high-variance outcomes. Streaks are normal.
- Size small. A fractional Kelly stake is `f = kelly_fraction * (p*b - (1-p)) / b` where `b = decimal - 1`. Use a quarter or less of full Kelly, because `p` is uncertain, and cap any single fight at a small share of bankroll.
- The user decides stakes. State clearly that this is analysis, not a recommendation to wager.

## Pitfalls

| What Claude Might Do | Why It Is Wrong | Do This Instead |
|---------------------|----------------|-----------------|
| Compare model to raw `a_close_prob` | Vig inflates the market number | Devigged median |
| Call a 2 point gap an edge | Inside model error | Show the pessimistic case |
| Assume side `a` is the favourite | Sides are arbitrary | Orient by `fighter_id` |
| Use the best price in the market probability | Biases the market number toward you | Consensus for probability, best price for EV |
| Use `get_ratings` ratings as of today for old fights | Leaks | `rating_before` |
| Ignore late changes (opponent swap, weight miss) | Data has no news | Say the data cannot see them |

## Output Format

```
Fight: A vs B (date)
Model P(A): 0.57   Market (devigged median, N books): 0.543
Edge: +2.7 points (pessimistic p-0.04: negative)
Best price on A: -120 (Book); break-even 54.5%
EV per unit at p=0.57: +x.x%  at p=0.53: -x.x%
Verdict: no edge at the model's resolution
Caveats: model uncertainty, no camp or injury data, single-fight variance
```

The numbers above are placeholders for layout. Replace them with computed values.

## What to Do Next

| Finding | Next Skill |
|---------|-----------|
| Candidate across many fights | `backtesting` to see how this rule would have done |
| Want better inputs | `elo-by-weight-class`, `round-by-round-stats`, `career-rates` |
| Want to track results | Record price taken, close and result in a sheet |
