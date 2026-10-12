---
name: favourite-calibration
description: "Tests whether UFC, PFL and Bellator favourites win as often as their closing moneylines imply: devigged closing probability buckets vs actual win rate, favourite-longshot bias, Brier score and log loss of the market, by weight class and era. Use when the user asks if favourites are overpriced or underpriced, whether heavy favourites are a trap, or how accurate closing lines are. Do not use to price a single fight -- see odds-analysis. Do not use to test a custom model -- see probability-calibration."
metadata:
  version: 1.0.0
  author: FighterAPI
---

# Favourite Calibration

> **Default data tool:** FighterAPI (`fighterapi-tool`).
> Use `list_events` (1 credit) for card ids and `get_odds` with `event_id` (10 credits per card) for closing lines plus results in one call.
> A full year of UFC cards costs about 520 credits. Free tier is 500 credits every month, so start with one season or a sample.

You are an expert in market efficiency. Your goal is to measure how well the closing line predicts fights, and where it errs, without overstating what a few hundred fights can show.

## When to Use

- "Do -300 favourites win 75% of the time?"
- "Are heavy favourites in MMA a good bet?"
- "Is the closing line well calibrated?"
- "Do underdogs in the main event win more than priced?"
- Establishing the market benchmark for a model (`probability-calibration`, `backtesting`)

## When NOT to Use

- Converting a single price -- see `odds-analysis`
- Calibrating your own model -- see `probability-calibration`
- Recommending a bet on a booked fight -- see `edge-detection`
- Events before June 2020 for the UFC -- no lines exist

## Commands Available

| Command | What It Does | Credits |
|---------|-------------|---------|
| `list_events` | Card ids by year, `status=final` | 1 |
| `get_odds` | `event_id`: every bout on the card with `winner` and per-book opening and closing lines | 10 |
| `get_fighter_fights` | `median_closing_line` per fight for one fighter | 5 |

## Commands That Do NOT Exist

| Not Available | Use Instead |
|--------------|-------------|
| `get_historical_odds` | `get_odds` with `event_id` of a past card |
| `get_closing_lines` | Read `a_close` and `b_close` from `get_odds` |
| `get_favorite_record` | Compute from `get_odds` rows as below |

## Data Plan

1. `list_events(season=Y, status="final", limit=100)`. Check `next_offset` is null so you have every card. 2025 returned 52 final cards, which includes smaller shows.
2. `get_odds(event_id=...)` per card. Each bout carries `winner` (a fighter id) and `books`.
3. Keep fights with a winner and at least one book with both closing prices. Report how many you drop.
4. Pool seasons only after checking each season's book counts. A median of 5 to 7 books per fight is typical, but ESPN's feed alone is common from mid-2024.

## Method

**Step 1: closing probability per book.** Convert both closing prices to implied probabilities and remove the vig by normalizing (details in `odds-analysis`):

```python
def american_to_prob(o):
    return 100 / (o + 100) if o > 0 else -o / (-o + 100)

def devig_close(book):
    a, b = book.get("a_close"), book.get("b_close")
    if a is None or b is None:
        return None
    pa, pb = american_to_prob(a), american_to_prob(b)
    return pa / (pa + pb)        # probability that fighter_a wins
```

**Step 2: consensus.** Median across books per fight, ignoring nulls. The median resists a stale outlier price.

**Step 3: favourite orientation.** Side `a` is not the favourite. Compute `p_fav = max(p_a, 1 - p_a)` and track which id is the favourite. Win flag: `winner == favourite_id`. Exclude draws and no contests (no winner) and say how many.

**Step 4: bucket.** Group by `p_fav` in bands: 50-55, 55-60, 60-65, 65-70, 70-75, 75-80, 80-90, 90+. For each band: n, mean `p_fav`, observed win rate, gap (observed minus mean), and a 95% interval.

```python
import math
def wilson(w, n, z=1.96):
    if n == 0: return (0.0, 1.0)
    p = w / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (c - h, c + h)
```

**Step 5: scores.** Brier = mean((p_fav - win)^2). Log loss = -mean(win*ln(p) + (1-win)*ln(1-p)). Compare with a constant-probability baseline at the base rate.

**Step 6: slices.** By weight class, by title fight vs not, by `scheduled_rounds`, by year. Only report slices with at least 30 fights, and say that you tested several slices.

## Worked Example

I ran the loop above on the first two final 2025 cards (a deliberately tiny sample, 20 credits plus 1 for the list). It kept 24 decided fights with closing lines from 6 books each, a mean devigged favourite probability of 0.666, and the favourite won 18 (75%). That says nothing about calibration: 24 fights has a 95% interval for the win rate of roughly 55% to 88%. It shows the pipeline works. A real answer needs hundreds of fights.

Sample sizes that make a claim: a bucket needs 30 or more fights to quote, 100 or more to read a bias of 3 or 4 points. A 5 point gap on 40 fights is inside the noise.

## Interpreting Results

| Observation | Possible Reading | Check |
|-------------|------------------|-------|
| Observed above mean in heavy favourite bands | Heavy favourites underpriced by the market | More seasons, other books |
| Observed below mean in underdog bands | Longshots overpriced | Same |
| Gap only in one weight class | Probably noise | Sample size, multiple-testing |
| Gap only in recent years | Line behaviour changed, or fewer books | Book count per year |

Do not claim a bias exists from one dataset slice. State the interval and what would change your mind. A systematic gap larger than the vig, persistent across years and books, would be worth a deeper look in `backtesting`, with transaction costs.

## Pitfalls

- **Vig in the numbers.** Using raw `a_close_prob` instead of a devigged value overstates every probability by about half the overround.
- **Closing line is not a bettor's price.** You cannot usually bet at the close. See `backtesting` on price availability.
- **Selection.** Fights that never get a line (late replacements, small shows) are missing. Your sample is the fights books priced.
- **Heterogeneity.** Contender Series and prelims are priced differently from main events. Report `card_segment` splits.
- **Draws and no contests** have no `winner`. Dropping them is fine if stated.
- **Books are not independent.** Six books do not give six independent estimates.

## Output Format

```
UFC, devigged median closing lines, seasons X to Y, N fights
Band      n    mean p   observed   95% CI
50-55%    31   0.526    0.484      0.32-0.65
...
Brier 0.205 (base-rate baseline 0.249), log loss 0.600
Verdict: no band outside its interval; sample too small to claim bias
```

The numbers in this template are placeholders for layout. Replace them with computed values.

## What to Do Next

| Finding | Next Skill |
|---------|-----------|
| Market is well calibrated | Use it as the benchmark in `probability-calibration` |
| A band looks off | Retest on more seasons in `walk-forward-validation` order |
| User wants to bet the gap | `backtesting`, then `edge-detection` |
