---
name: elo-by-weight-class
description: "Reads and uses FighterAPI's Elo fighter ratings by weight class: leaderboards of active fighters, rating gaps as win probabilities, peak vs current, rating change per fight, and strength of schedule. Use when the user asks who is rated highest at a weight, how big a rating gap is, who is underrated or overrated, or how a fighter's rating moved. Do not use for official rankings -- those are not in the data. Do not use for market prices -- see odds-explorer. Do not use to check calibration -- see probability-calibration."
metadata:
  version: 1.0.0
  author: FighterAPI
---

# Elo by Weight Class

> **Default data tool:** FighterAPI (`fighterapi-tool`).
> Use `get_ratings` (2 credits) for a ranked list. Use `get_fighter_fights` (5 credits) for rating before and after every fight, which is the only leak-free history.

You are an expert in rating systems for combat sports. Your goal is to use the ratings honestly: as a transparent prior built from results, not as a rival to the betting market, and not as an official ranking.

## When to Use

- "Top 10 welterweights by rating"
- "How far ahead is A of B?" and what that implies
- "Who has risen fastest in the last year?"
- Strength of schedule: the ratings of a fighter's opponents
- Building a rating-based feature for a model

## When NOT to Use

- Official promotion rankings -- not in the data; say so
- Odds and prices -- see `odds-explorer`
- Testing whether the ratings are calibrated -- see `probability-calibration`
- PFL or Bellator comparisons across promotions -- ratings are built per promotion

## Commands Available

| Command | What It Does | Credits |
|---------|-------------|---------|
| `get_ratings` | Elo leaderboard, highest first, for fighters active since a year | 2 |
| `get_fighter` | `rating.current` and `rating.peak` for one fighter | 5 |
| `get_fighter_fights` | `rating_before` and `rating_after` for every fight | 5 per page |
| `get_fight` | `fighters[].elo.before` and `after` for both sides of one fight | 5 |

## Commands That Do NOT Exist

| Not Available | Use Instead |
|--------------|-------------|
| `get_rankings` | `get_ratings` (our Elo) |
| `get_ratings_history` or `get_ratings_as_of` | `get_fighter_fights`, which has `rating_before` per fight |
| `get_pound_for_pound` | Sort `get_ratings` without a `weight_class` and say it mixes divisions |
| `get_win_probability` | Compute from the rating gap (formula below) |

## How the Ratings Are Built

The response states the method. Read `data.method` in the live reply: Elo from UFC results alone, start 1500, K 40 for a fighter's first five bouts then 24, finishes weighted 1.15, draws 0.5, no contests unrated. Quote the method from the response rather than from memory, because it can change.

What that implies:

- A fighter's first fights move the rating more (K 40). Early ratings are noisy.
- Finishes move the rating more than decisions.
- There is no opponent-weight-class adjustment. A rating belongs to a fighter, not to a division. A fighter who moves weight keeps the rating.
- Ratings carry no layoff decay, injuries or age.

## Parameters

`get_ratings`: `weight_class` (for example Welterweight or Women's Strawweight), `active_since` (a year, default is last year), `limit` (default 25, up to 200), `league`. Rows: `rank`, `fighter_id`, `name`, `weight_class`, `rating`, `last_fight`, `fights`, `ufc_fights`.

Real call (Lightweight, top 3 active since 2025): first place Max Holloway at 1684 with 33 fights. The `weight_class` on a row is the fighter's current class.

## Rating Gap to Probability

For fighters with ratings `R_a` and `R_b`:

```python
def p_win(r_a, r_b, scale=400):
    return 1 / (1 + 10 ** (-(r_a - r_b) / scale))
```

The standard Elo form uses a 400 scale. That is an assumption about how this rating behaves. Fit it: collect `rating_before` for each side of many past fights (from `get_fighter_fights`), compute `p_win`, compare with outcomes, and adjust `scale` until calibration is good (`probability-calibration`). If the market is better calibrated, the market wins. Use the rating as a prior to be shrunk toward the market.

## Strength of Schedule

1. `get_fighter_fights` for the fighter.
2. For each row, the opponent is whichever of `fighter_a` or `fighter_b` is not the fighter. Pull their rating at the time through `get_fight` (`fighters[].elo.before`, 5 credits) when you need exactness, or approximate with the opponent's current rating from `get_ratings` and label it approximate.
3. Mean opponent rating, weighted by recency.

Opponent ratings are more informative than record. A 9-1 fighter whose opponents averaged 1480 should be read differently from a 9-3 fighter whose opponents averaged 1600.

## Rating Change as a Surprise Score

For each fight, `rating_after - rating_before`. A big drop for a favourite is the model's surprise. Large positive moves for a fighter in a short span signal a surge, but with K 40 early on, check the fight count.

## Leak-free Rules

- Never use `get_ratings` or `rating.current` as a feature for a fight in the past. They include that fight and everything after. Use `rating_before` from the fight row.
- For a live fight, current ratings are correct inputs.
- When backtesting, join on the fight, not the fighter.

## Worked Example

Request: "Is a 45-point rating gap meaningful at lightweight?"

```
get_ratings(weight_class="Lightweight", active_since=2025, limit=3)
```

With the standard scale, a gap of 45 is `p_win` of about 0.56. That is a small edge, a little over a coin flip. Show the user how many active lightweights sit within 45 points of each other, then show a calibration check if they want to trust it.

## Output Format

```
Welterweight, active since 2025, top 5 by Elo
1  Name  1690  (fights 18, last fight 2026-03-08)
...
Gap 1 vs 2: 24 points -> 53.4% (scale 400, unfitted)
Method: Elo from UFC results alone (read from data.method)
```

## Anti-patterns

| What Claude Might Do | Why It Is Wrong | Do This Instead |
|---------------------|----------------|-----------------|
| Call it "the rankings" | It is our rating, not the UFC's | Say "our Elo rating" |
| Use current rating for a past fight | Leaks the future | `rating_before` |
| Compare ratings across promotions | Built from different results | Compare within a promotion |
| Treat a rating gap as a betting edge | Market already prices it | Compare to the devigged close |
| Trust a fighter with 3 fights | K 40 swings | Flag early ratings as noisy |

## What to Do Next

| Finding | Next Skill |
|---------|-----------|
| Want to check the 400 scale | `probability-calibration` |
| Build a model | `walk-forward-validation` |
| Compare to market | `edge-detection` |
