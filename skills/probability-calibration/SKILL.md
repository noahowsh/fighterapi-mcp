---
name: probability-calibration
description: "Checks and fixes the calibration of fight win probabilities from a model or a rating: reliability tables, Brier score, log loss, calibration slope and intercept, Platt scaling and isotonic regression, and how to compare with the devigged closing line. Use when the user asks whether a model's probabilities are trustworthy, wants a reliability diagram, or wants to tune the Elo scale. Do not use to decide whether the market is efficient -- see favourite-calibration. Do not use to hunt for bets -- see edge-detection."
metadata:
  version: 1.0.0
  author: FighterAPI
---

# Probability Calibration

> **Default data tool:** FighterAPI (`fighterapi-tool`).
> Outcomes and pre-fight ratings: `get_fighter_fights` (5 credits per page, `rating_before` and `result`). Market benchmark: `get_odds` with `event_id` (10 credits per card).
> For your own predictions file, skip the tool.

You are an expert in probabilistic forecasting. Your goal is to answer one question: when the model says 70%, does the fighter win about 70% of the time, and is that better than the closing line says?

## When to Use

- "Is my fight model calibrated?"
- "Is the Elo scale of 400 right for MMA?"
- "Build a reliability table"
- "Compare my model to the closing line"
- Before using any probability in `edge-detection`

## When NOT to Use

- Judging whether the betting market is calibrated -- see `favourite-calibration`
- Splitting data safely -- see `walk-forward-validation`
- Staking and bankroll -- see `backtesting`

## Commands Available

| Command | What It Does | Credits |
|---------|-------------|---------|
| `get_fighter_fights` | `rating_before`, `result`, `median_closing_line` per fight for one fighter | 5 per page |
| `get_event` | Results and winners for a card | 2 |
| `get_odds` | Closing lines and `winner` for a card, the benchmark | 10 |
| `get_fight` | Pre-fight `elo.before` for both sides | 5 |

## Commands That Do NOT Exist

| Not Available | Use Instead |
|--------------|-------------|
| `get_predictions` | Not available: the API does not publish fight predictions. Bring your own model output |
| `get_model_probabilities` | Same |
| `get_calibration` | Compute with the code below |

## Inputs

Each row needs: the model probability for one named fighter, the outcome (1 if that fighter won, 0 if not), the fight date, and ideally the devigged closing probability for the same fighter. Orient every row by `fighter_id`, never by side `a` or `b`. Drop draws and no contests, and count them.

Predictions must be made with information from before the fight. If the model used ratings or rates, those must be `rating_before` or rates computed from earlier fights only (`walk-forward-validation`).

## Metrics

| Metric | Formula | Reading |
|--------|---------|---------|
| Brier score | mean((p - y)^2) | Lower is better. Coin flip is 0.25 |
| Log loss | -mean(y ln p + (1 - y) ln(1 - p)) | Punishes confident misses hard. Coin flip is 0.693 |
| Calibration slope | coefficient on logit(p) in a logistic fit of y | 1 is ideal. Below 1 means overconfident |
| Calibration intercept | with slope fixed at 1 | Positive means the model under-predicts the favourite |
| Expected calibration error | weighted mean of abs(bin gap) | Summary of the reliability table |

```python
import numpy as np
def brier(p, y): return float(np.mean((p - y) ** 2))
def logloss(p, y, eps=1e-6):
    p = np.clip(p, eps, 1 - eps)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))
```

## Reliability Table

1. Bin predictions. With a few hundred fights use 5 bins of equal count (quantile bins), not equal width. Equal width leaves empty bins at the extremes.
2. In each bin: n, mean predicted, observed rate, and a Wilson interval (see `favourite-calibration`).
3. Plot predicted on x, observed on y, with the diagonal. Bars for n below 30 should be drawn lightly or merged.

Fight data is small. Ten bins on 400 fights gives 40 per bin and an interval about plus or minus 15 points. Prefer fewer bins and the slope and intercept, which use all the data.

## Fixing Miscalibration

- **Platt scaling.** Fit `logit(p_cal) = a + b * logit(p)` by logistic regression on held-out predictions. Two parameters, stable on small samples.
- **Isotonic regression.** Flexible, but needs a few hundred rows per side and can overfit. Check on a later period.
- **Temperature.** For an Elo prior, tune the `scale` in `p = 1/(1+10^(-d/400))` by minimizing log loss on a calibration window.

Fit the correction on one period and evaluate it on the next. Fitting and scoring the same rows rewards overfitting.

## Compare with the Market

Score the devigged closing probability on exactly the same rows (`odds-analysis`). That is the benchmark. If the model's Brier or log loss is not lower than the market's on out-of-sample rows, the model has no information the market lacks, however good it looks in isolation.

Test the difference with a paired bootstrap over fights (resample fight indices, recompute the score gap, repeat 2000 times) and report the interval. With a few hundred fights the interval will usually include zero. Say so.

## Pitfalls

| What Claude Might Do | Why It Is Wrong | Do This Instead |
|---------------------|----------------|-----------------|
| Evaluate on training rows | Optimistic | Hold out later fights |
| Use current ratings for past fights | Leaks results | `rating_before` |
| Bin at fixed width | Empty and tiny bins | Quantile bins, or slope and intercept |
| Judge by accuracy alone | Hides overconfidence | Brier and log loss |
| Compare to 50% | Weak baseline | Compare to the devigged close |
| Pool PFL and UFC | Different books, markets | Separate runs |

## Worked Example

Request: "Is the Elo scale of 400 right?"

```
get_ratings(weight_class="Lightweight", limit=50)    # who is active (2 credits)
get_fighter_fights(fighter_id=..., limit=200)         # per fighter: rating_before, rating_after, result
```

Each history row gives `rating_before` for the fighter. The opponent's pre-fight rating is on the opponent's own row for the same `bout_id`, so collect rows for both fighters and join on `bout_id`. For each fight compute `d = R_self - R_opp`, then `p_win` at several scales (300, 400, 500), score each with log loss on fights after a chosen date, and pick the scale that minimizes it on an earlier window and confirm on the later one. Expect a flat optimum: report the interval of scales within one standard error, not a single best number.

## Output Format

```
Fights scored: N (draws/NC dropped: k), window: dates
              Brier   LogLoss   Slope   Intercept
Model          x.xxx   x.xxx     x.xx    x.xx
Closing line   x.xxx   x.xxx     x.xx    x.xx
Paired bootstrap, model minus market Brier: x.xxx (95% CI a to b)
Reliability (5 quantile bins): table
Verdict: calibrated within noise / overconfident / no information beyond market
```

The numbers above are placeholders for layout. Replace them with computed values.

## What to Do Next

| Finding | Next Skill |
|---------|-----------|
| Well calibrated and competitive with the close | `edge-detection` |
| Not better than the close | Improve features, retest with `walk-forward-validation` |
| Need price benchmarks over many seasons | `favourite-calibration` |
