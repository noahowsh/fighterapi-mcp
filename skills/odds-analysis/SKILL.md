---
name: odds-analysis
description: "Converts fight odds between American, decimal and fractional formats and removes bookmaker margin to get true implied probabilities for two-way MMA moneylines. Use when the user asks about devigging, vig, no-vig lines, implied probability, overround, the multiplicative, additive, power or Shin method, or how to compare a price with a probability. Do not use for viewing current odds -- see odds-explorer. Do not use for calibrating a model -- see probability-calibration. Do not use for finding edges -- see edge-detection."
metadata:
  version: 1.0.0
  author: FighterAPI
---

# Odds Analysis

> **Default data tool:** FighterAPI (`fighterapi-tool`).
> Use `get_odds` (5 credits per fight, 10 per card) for prices. The math in this skill is local and costs nothing.
> For your own odds file, skip the tool and work with the file.

You are an expert in odds mathematics. Your goal is to turn a two-way moneyline into a fair probability, say how much margin was removed, and be clear about which method was used.

## When to Use

- "What probability does -130 imply?"
- "Remove the vig from this line"
- "Convert +110 to decimal"
- "What is the book's margin on this fight?"
- Preparing market probabilities for `edge-detection` or `favourite-calibration`

## When NOT to Use

- Looking at what books are posting -- see `odds-explorer`
- Testing a model's probabilities -- see `probability-calibration`
- Method-of-victory or round markets -- not in the data; moneylines and total rounds only

## Commands Available

| Command | What It Does | Credits |
|---------|-------------|---------|
| `get_odds` | Open, close, current moneyline per book; `a_close_prob`, `b_close_prob` (raw, with vig) | 5 / 10 |
| `get_schedule` | Current `lines` on upcoming fights | 2 |

## Commands That Do NOT Exist

| Not Available | Use Instead |
|--------------|-------------|
| `get_no_vig_line` | Compute from `get_odds` using the formulas below |
| `get_true_probability` | Same |
| `get_decimal_odds` | Convert locally |

## Format Conversion

```python
def american_to_prob(o):
    return 100 / (o + 100) if o > 0 else -o / (-o + 100)

def american_to_decimal(o):
    return 1 + o / 100 if o > 0 else 1 + 100 / -o

def prob_to_american(p):
    return round(-100 * p / (1 - p)) if p >= 0.5 else round(100 * (1 - p) / p)
```

Decimal odds are `1 / raw_prob`. Fractional odds are decimal minus 1. Always carry full precision and round only when displaying.

## Removing the Vig (Two-way Market)

Raw implied probabilities `q_a` and `q_b` sum to more than 1. The overround is `q_a + q_b - 1`. For a two-way market the margin is the overround itself.

Real example (UFC 298, Bet365 closing line): `a_close` -130, `b_close` +110.

```
q_a = 130/230 = 0.5652    q_b = 100/210 = 0.4762    sum = 1.0414
```

| Method | p_a | p_b | Note |
|--------|-----|-----|------|
| Multiplicative (normalize) | 0.5427 | 0.4573 | Default: scales both proportionally |
| Additive | 0.5445 | 0.4555 | Subtracts half the overround from each |
| Power | 0.5454 | 0.4546 | Solve `q_a^k + q_b^k = 1`; here k is about 1.0625 |
| Shin | 0.5445 | 0.4555 | Assumes insider flow; z about 0.041 |

All four land within about 0.3 points here. The choice matters at long odds. On a -1000/+650 fight, the multiplicative method assigns the underdog a larger share of the vig than the power or Shin methods do, so it will make a long shot look more likely.

```python
import math
def devig_mult(qa, qb):
    s = qa + qb
    return qa / s, qb / s

def devig_power(qa, qb):
    lo, hi = 0.5, 3.0
    for _ in range(100):
        k = (lo + hi) / 2
        lo, hi = (k, hi) if qa**k + qb**k > 1 else (lo, k)
    return qa**k, qb**k

def devig_shin(qa, qb):
    s = qa + qb
    p = lambda z, q: (math.sqrt(z*z + 4*(1-z)*q*q/s) - z) / (2*(1-z))
    lo, hi = 0.0, 0.5
    for _ in range(100):
        z = (lo + hi) / 2
        lo, hi = (z, hi) if p(z, qa) + p(z, qb) > 1 else (lo, z)
    return p(z, qa), p(z, qb)
```

Recommendation: use multiplicative for even fights, and check power or Shin when the favourite is -300 or shorter. Say which one you used.

## Across Books

1. Devig each book separately. Never average raw prices and then devig.
2. Take the median of the devigged `p_a` across books. The median resists a stale quote.
3. If a book posts only one side, drop that book for that fight.
4. For the best price on each side, shop prices (`odds-explorer`), but keep the consensus probability from the median.

ESPN's feed is often one book per fight from mid-2024. With one book, say the consensus is that one book.

## Open to Close

For the same book, convert the open and the close to devigged probabilities and subtract. This movement is in probability points, comparable across favourites and underdogs. Real example, same Bet365 row: open `a_open` -170 and `b_open` +140 gave raw `q_a` 0.630 and `q_b` 0.417 (sum 1.046). By the close, `a_close` -130. The market moved toward the underdog by about 6 raw points on side `a`.

## Total Rounds

`get_odds` also returns `total_rounds` (for example 3.5) with `over_odds` and `under_odds` (for example -120 and -120). Devig the pair the same way. Both sides at -120 imply 54.5% raw each and 50% each after the vig. The total rounds line is an expected fight length proxy, not a method-of-victory price.

## Break-even and Edge Arithmetic

- Break-even probability for a price is its raw implied probability `q`. At -130 you need to win 56.5% of the time just to break even.
- To compare a belief `p` with a price: expected value per unit staked is `p * (decimal - 1) - (1 - p)`. See `edge-detection`.
- A model that is 3 points above the devigged market is not a 3 point edge at the price. The vig is still in the price.

## Pitfalls

| What Claude Might Do | Why It Is Wrong | Do This Instead |
|---------------------|----------------|-----------------|
| Treat `a_close_prob` as a true probability | Includes the vig | Normalize or use power or Shin |
| Average American odds across books | Odds are not linear | Convert to probability first |
| Say "+110 is 110%" | It is a payout on 100 staked | Convert to 47.6% raw |
| Devig a three-way market the same way | MMA here is two-way | Handle draws separately if the user raises them |
| Present a devigged number as exact | It depends on method | Name the method |

## Output Format

```
Line: A -130 / B +110 (Bet365 close)
Raw implied: 56.5% / 47.6%   Overround 4.1%
Devigged (multiplicative): 54.3% / 45.7%
Devigged (power): 54.5% / 45.5%
Break-even at the posted price: A 56.5%, B 47.6%
```

## What to Do Next

| Finding | Next Skill |
|---------|-----------|
| Have a fair probability, want to compare to a model | `edge-detection` |
| Want to check historical accuracy of closes | `favourite-calibration` |
| Want to see more books | `odds-explorer` |
