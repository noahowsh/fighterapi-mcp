---
name: walk-forward-validation
description: "Validates fight-prediction models without leakage using time-ordered folds: expanding or rolling windows, purge gaps, rating and rate features built only from earlier fights, baselines, and significance checks. Use when the user asks how to test a model fairly, whether results are leaking, how to split fight data, or how to build features without using the future. Do not use for betting simulation -- see backtesting. Do not use for calibration plots -- see probability-calibration."
metadata:
  version: 1.0.0
  author: FighterAPI
---

# Walk-Forward Validation

> **Default data tool:** FighterAPI (`fighterapi-tool`).
> Training rows come from `get_event` (2 credits per card, results), `get_fighter_fights` (5 credits per page, `rating_before` and stats) and `get_odds` with `event_id` (10 credits per card, closing lines).
> For your own CSV, skip the tool.

You are an expert in time-series validation. Your goal is to estimate how a model would have done if it had been run live, fight by fight, and to refuse any test that lets the future into the past.

## When to Use

- Splitting fight data for a model test
- Checking an existing result for leakage
- Choosing windows (train on 2010 to 2019, test 2020)
- Deciding whether a feature is safe to use

## When NOT to Use

- Betting returns, staking, drawdown -- see `backtesting`
- Calibration of probabilities -- see `probability-calibration`
- Describing fighters -- see `fighter-scouting`

## Commands Available

| Command | What It Does | Credits |
|---------|-------------|---------|
| `list_events` | Card ids and dates by `season` | 1 |
| `get_event` | Results of a card | 2 |
| `get_fighter_fights` | History with `rating_before`, stats, `median_closing_line` | 5 per page |
| `get_odds` | Closing lines for a card | 10 |

## Commands That Do NOT Exist

| Not Available | Use Instead |
|--------------|-------------|
| `get_training_set` or `export_dataset` | Assemble rows from the calls above |
| `get_features` | Compute them locally from earlier fights |
| `get_ratings` as-of a date | `rating_before` on each fight row |

## Why Random K-fold Fails Here

1. **Time order.** A fighter's later fights are informed by their earlier ones. Shuffling lets the model train on a fighter's 2024 fights and test on 2021.
2. **The same fighters in train and test.** Fights share fighters. A random split memorizes fighters instead of learning skill.
3. **Rating contamination.** Any rating that includes a fight's result cannot be a feature for that fight.
4. **Rule and era change.** Weight classes and the sport's style shift. The test must look like the future.

## Fold Structure

Expanding window: train from the start up to a cutoff date, test on the next block, then move the cutoff forward and repeat.

```
Fold 1: train 2005-2016   test 2017
Fold 2: train 2005-2017   test 2018
Fold 3: train 2005-2018   test 2019
Fold 4: train 2005-2019   test 2020
...
```

For odds-based work the first test fold cannot start before June 2020 (UFC lines start with those cards), so closing-line comparisons run on 2020 onward. A rating model can be trained on earlier years and tested on the line era.

Use blocks of one year, or six months if volume is thin. A UFC year has dozens of cards (52 final cards came back for 2025, check `bouts` per card in `list_events` for the fight count), so one-year blocks give usable test sets. Reporting one summary number from one fold is not enough: show every fold.

## Temporal Discipline Inside a Fold

- Every feature for a fight is computed from fights strictly before its `event_date`. Fights on the same card are simultaneous: do not let one fight feed another on the same date.
- Use `rating_before` from the fight row, not `get_ratings` or `rating.current`.
- Career rates (`career_rates` from `get_fighter`) are lifetime values as of today and leak the future for any past fight. Rebuild rates from the fighter's earlier rows or round lines.
- Opponent features obey the same rule.
- Encode a fighter's debut as missing, not zero.
- Fit scalers, imputers and calibrators on the training block only.
- Purge: if a feature spans a window, drop training fights whose window overlaps the test block.

```python
def features_as_of(history, as_of_date):
    prior = [f for f in history if f["event_date"] < as_of_date]
    n = len(prior)
    if n == 0:
        return None
    return {"fights": n, "wins": sum(f["result"] == "win" for f in prior)}
```

`history` is the `fights` array from `get_fighter_fights`. `event_date` strings compare correctly because they are ISO dates.

## Baselines

A model result means nothing without these on the same fold:

| Baseline | Source |
|----------|--------|
| Coin flip (Brier 0.25) | Constant |
| Higher rating wins | `rating_before` |
| Devigged closing line | `get_odds`, see `odds-analysis` |
| Always pick the favourite | Closing line |

If the model does not beat the closing line on log loss out of sample, it has no usable edge. Report that plainly.

## Significance

- Accuracy against a baseline: a binomial or paired McNemar test on the same fights.
- Log loss or Brier difference: paired bootstrap over fights, 2000 resamples, report the 95% interval.
- Many models or features tried means many tests. Reserve the final fold, use it once, and discount anything found by search.

Example scale: 300 test fights, a model correct 62% vs a baseline 58%, gives a gap whose paired interval will usually include zero. Fight data is small and noisy.

## Report Per Fold

```
Fold  Train          Test   N    Model Brier   Close Brier   Model LL   Close LL
1     2005-2016      2017   ..   ..            n/a           ..         n/a
4     2005-2019      2020   ..   ..            ..            ..         ..
Mean over folds, and paired bootstrap interval on the difference
```

Pre-2020 folds have no closing lines. Mark them n/a rather than filling with something else.

## Pitfalls

| What Claude Might Do | Why It Is Wrong | Do This Instead |
|---------------------|----------------|-----------------|
| Use `career_rates` as a feature for old fights | Includes later fights | Rebuild from earlier rows |
| Tune hyperparameters on the test fold | Optimistic | Nested time-ordered tuning |
| Report one fold | Cherry-picked window | All folds |
| Count same-card fights as ordered | They happened together | Group by `event_id` |
| Include draws as losses | Wrong label | Drop and count |
| Skip a baseline | Results unanchored | Always run the close |

## Credit Planning

| Task | Credits |
|------|---------|
| Results for one year of cards | about 100 |
| Closing lines for one year of cards | about 520 |
| Histories for 100 fighters, one page each | 500 |

Budget first, then pull. Cache every response locally; do not re-fetch.

## What to Do Next

| Finding | Next Skill |
|---------|-----------|
| Model beats the close out of sample | `probability-calibration`, then `edge-detection` |
| Model does not | Revisit features; `round-by-round-stats` and `career-rates` for ideas |
| Want money results | `backtesting` |
