---
name: backtesting
description: "Simulates a fight-betting rule on past UFC, PFL or Bellator cards using each book's opening and closing moneylines: flat and fractional-Kelly staking, ROI, hit rate, drawdown, bootstrap intervals, closing-line value, and naive baselines. Use when the user asks how a betting rule or model would have performed, wants a profit test, or asks about underdog or favourite strategies. Do not use for model accuracy or calibration -- see walk-forward-validation and probability-calibration. Do not use for a live bet -- see edge-detection."
metadata:
  version: 1.0.0
  author: FighterAPI
---

# Backtesting

> **Default data tool:** FighterAPI (`fighterapi-tool`).
> Use `get_odds` with `event_id` (10 credits per card) for opening and closing lines and the `winner` in one call. Use `list_events` (1 credit) for card ids.
> A year of UFC cards is about 520 credits. Warn the user and state the total before pulling.

You are an expert in betting simulation. Your goal is to estimate what a rule would have returned using only prices that were available, and to be honest that fight data is small and noisy.

## When to Use

- "How would betting every underdog over +200 have done?"
- "Backtest my model's picks against the opening line"
- "Does betting the favourite at the open beat the close?"
- Estimating ROI, drawdown and closing-line value for a rule

## When NOT to Use

- Model discrimination or calibration -- see `walk-forward-validation`, `probability-calibration`
- Whether the market is efficient on average -- see `favourite-calibration`
- Deciding a bet today -- see `edge-detection`

## Commands Available

| Command | What It Does | Credits |
|---------|-------------|---------|
| `list_events` | Card ids by `season` and `status=final` | 1 |
| `get_odds` | For a card: every bout, `winner`, per-book `a_open`, `a_close`, `b_open`, `b_close` | 10 |
| `get_fighter_fights` | One fighter's fights with `median_closing_line` and `result` | 5 per page |

## Commands That Do NOT Exist

| Not Available | Use Instead |
|--------------|-------------|
| `run_backtest` | Simulate locally with the steps below |
| `get_historical_odds` | `get_odds` with a past `event_id` |
| `get_prop_history` | Not available: no props, no method or round markets |
| `get_closing_line_value` | Compute from `get_odds` |

## Step 0: Refuse In-Sample Tests

A rule found by looking at the same fights you test on is not a test. Fit or choose the rule on earlier seasons, then run it once on later ones (`walk-forward-validation`). Report how many rules or thresholds you tried.

## Step 1: Build the Dataset

1. `list_events(season=Y, status="final", limit=100)` per year. Confirm `next_offset` is null.
2. `get_odds(event_id=...)` per card. Save every response to disk.
3. Flatten to one row per bout per book: bout id, date, fighter ids, `winner`, book name, `a_open`, `a_close`, `b_open`, `b_close`.
4. Keep only bouts with a `winner` and non-null prices on both sides. Count and report drops (draws, no contests, missing lines).
5. Sort by `event_date`.

Coverage: UFC lines begin with the June 2020 cards, PFL in April 2023, Bellator January 2022 to 2024 with fewer books. Do not backtest outside those windows.

## Step 2: Choose Which Price You Could Have Taken

This is where backtests cheat.

| Price | Meaning | Honest? |
|-------|---------|---------|
| `a_open` | Posted early. Real, but limits can be small and the book may move | Yes, with caution |
| `a_close` | Final price before the bell | Only if you could bet at the close |
| `a_current` | Snapshot at capture time | Only for live strategies |
| Best price across books | Optimistic: needs accounts at every book | Report both best and median |

State the rule: "bet at the opening price of the median book". Betting an open that a model computed after seeing the close is leakage.

## Step 3: Simulate

```python
def profit(stake, american, won):
    if not won:
        return -stake
    return stake * (american / 100 if american > 0 else 100 / -american)

def run(rows, rule, stake=1.0):
    bankroll, curve = 0.0, []
    for r in sorted(rows, key=lambda r: r["event_date"]):
        bet = rule(r)                      # returns None or (fighter_id, american_price)
        if bet:
            fid, price = bet
            bankroll += profit(stake, price, r["winner"] == fid)
        curve.append(bankroll)
    return curve
```

Rules express a side by fighter id, not by `a` or `b`. For example "underdog at the open" picks whichever side has the higher open price.

Fractional Kelly: `stake = bankroll * kelly_fraction * (p*b - (1-p)) / b`. Use a quarter Kelly or less and cap per bet, and still treat drawdown as the main result.

## Step 4: Metrics

| Metric | Formula |
|--------|---------|
| Bets, wins, hit rate | counts |
| ROI | total profit / total staked |
| Average price | mean decimal odds |
| Max drawdown | largest peak-to-trough fall in the cumulative profit curve |
| Longest losing streak | count |
| CLV | devigged close probability of the side minus devigged probability at the price taken |

## Step 5: Uncertainty

Bootstrap the bets (resample with replacement, 5000 draws) and report the 95% interval of ROI.

```python
import random
def boot_roi(pnls, stakes, n=5000):
    out = []
    for _ in range(n):
        idx = [random.randrange(len(pnls)) for _ in pnls]
        out.append(sum(pnls[i] for i in idx) / sum(stakes[i] for i in idx))
    out.sort()
    return out[int(0.025 * n)], out[int(0.975 * n)]
```

Rule of thumb: with flat stakes at typical MMA prices, the standard deviation of one bet is near one unit, so 200 bets have a standard error of ROI of about 7 points. A 5% ROI on 200 bets is well inside noise. Say so.

## Step 6: Baselines

Run the same machinery on these and show them beside your rule:

| Baseline | Rule |
|----------|------|
| All favourites at the open | Expected ROI close to minus the vig |
| All underdogs at the open | Same |
| Favourites at the close | Check the vig drag |
| Random side | Variance floor |

If your rule does not beat the "bet everything" baseline by more than the bootstrap interval, there is no result.

## Step 7: Edge Compression and Stability

Split the bets by year. A real edge shows up in each year with a similar sign. An edge concentrated in one year, one weight class or one book is a story, not a result. Check ROI by book: a price only one book offered is not a market.

## Pitfalls

| What Claude Might Do | Why It Is Wrong | Do This Instead |
|---------------------|----------------|-----------------|
| Use `a_close` to compute the pick and the price | You pick with information not yet known | Pick from open info, price from the open |
| Report best-of-all-books price as achievable | Needs many accounts and limits | Report median-book too |
| Backtest before June 2020 | No lines | State the limit |
| Treat a high hit rate as success | Underdog hit rates are low by design | Look at ROI and CLV |
| Ignore stake limits and line moves | Real fills differ | Say the test is idealized |
| Stop at first good threshold | Data mining | Report all tried |

## Output Format

```
Rule: underdog at +200 or longer, median book open, UFC 2020-06 to 2025
Bets: N   Wins: W (x%)   Avg price: +xxx
Flat ROI: x.x%   95% bootstrap CI: a to b
Max drawdown: x units   Longest losing run: k
CLV vs devigged close: x.x points (n=N)
Baselines: all dogs x.x%, all favs x.x%
Verdict: inside noise / persistent across years / ...
This is a historical estimate, not a forecast or a recommendation to wager.
```

The numbers above are placeholders for layout. Replace them with computed values.

## What to Do Next

| Finding | Next Skill |
|---------|-----------|
| Rule survives out of sample | `edge-detection` for current cards |
| Wants better probabilities | `probability-calibration` |
| Wants the market benchmark | `favourite-calibration` |
