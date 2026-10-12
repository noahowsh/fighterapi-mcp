---
name: odds-explorer
description: "Compares sportsbook moneylines for a UFC, PFL or Bellator fight or card: open, close and current prices, best price per side, vig, total rounds, and line movement. Use when the user asks for the odds, the line, who is favoured, which book has the best price, how the line moved, or what a fight closed at. Do not use for removing the vig or converting formats -- see odds-analysis. Do not use to compare a model against the market -- see edge-detection."
metadata:
  version: 1.0.0
  author: FighterAPI
---

# Odds Explorer

> **Default data tool:** FighterAPI (`fighterapi-tool`).
> Use `get_odds` with `bout_id` (5 credits) for one fight or with `event_id` (10 credits) for a whole card.
> Use `get_line_movement` (10 credits) for snapshots before the bell, recent fights only.
> Use `get_schedule` (2 credits) for the current line on every upcoming fight.

You are an expert in fight betting markets. Your goal is to show the user what is on offer, what it costs them in vig, and what the line did.

## When to Use

- Current prices on an upcoming fight
- Best price for each fighter across books
- Opening vs closing line on a past fight
- Total rounds line and over/under prices
- Reading line movement as a market signal

## When NOT to Use

- Converting odds or devigging -- see `odds-analysis`
- Model probability vs price -- see `edge-detection`
- Testing whether favourites win as often as priced -- see `favourite-calibration`
- Method of victory, round betting, props -- not in the data

## Commands Available

| Command | What It Does | Credits |
|---------|-------------|---------|
| `get_odds` | Every book's open, close and current moneyline for both fighters, implied probabilities, total rounds | 5 per fight, 10 per card |
| `get_line_movement` | Timed snapshots of each book's line | 10 |
| `get_schedule` | Upcoming fights with `lines` from any book that posted | 2 |
| `get_fight` | Includes `odds` per book (2024 on) alongside the stat sheets | 5 |

## Commands That Do NOT Exist

| Not Available | Use Instead |
|--------------|-------------|
| `get_live_odds` | `get_odds` returns `a_current` and `b_current` |
| `get_method_odds`, `get_round_odds`, `get_props` | Not available: moneylines and total rounds only |
| `compare_books` | Read the `books` array from `get_odds` and compare |
| `get_best_line` | Compute the best price from `books` |

## Data Shape

`get_odds` returns `data.bouts`, a list. Each bout has the fight header and `books`. Each book row:

```
provider, a_open, a_close, a_current, b_open, b_close, b_current,
a_close_prob, b_close_prob, total_rounds, over_odds, under_odds, captured_at
```

`a` and `b` are `fighter_a` and `fighter_b` from the bout header. Prices are American odds. `a_close_prob` and `b_close_prob` are the raw implied probabilities of the closing price, before devigging, so they add to more than 1.

Real example (UFC 298, Bet365): `a_close` -130 and `b_close` 110 gave `a_close_prob` 0.565 and `b_close_prob` 0.476, which sum to 1.042. That 4.2 point overround is the vig. See `odds-analysis` to remove it.

## Coverage Limits

- UFC opening and closing lines start with the June 2020 cards. PFL starts April 2023. Bellator covers January 2022 to 2024 with fewer books.
- A median of 5 to 7 books per fight. From mid-2024 ESPN's feed is often a single book, so thin cards have thin comparisons.
- Pre-fight snapshots (`get_line_movement`) exist only for recent fights: ESPN once a day from October 2026, The Odds API hourly in the two days before. For older fights, open vs close from `get_odds` is the movement you have.

## Finding the Best Price

```python
books = bout["books"]
best_a = max(books, key=lambda b: b["a_close"] if b["a_close"] is not None else -9999)
best_b = max(books, key=lambda b: b["b_close"] if b["b_close"] is not None else -9999)
```

For American odds a higher number is always the better price for the bettor (+150 beats +140, -110 beats -120). Skip rows where the price is null. Report the provider, and note that a best price on both sides from different books is a "shop" and can have a combined overround below the market's.

## Reading Movement

For a past fight, move = close minus open on the same side. Convert to implied probability first (`odds-analysis`) so +/- crossings do not mislead: -170 to -130 is a 6.4 point drop in implied probability for that fighter even though both numbers are negative.

- Consensus matters more than one book. Look at the median move across providers.
- A move that most books share is information. A move at one book is a book-specific price.
- Fight week news (weight miss, injury, late replacement) explains most large moves. The data has no news. Say the cause is unknown.
- `get_line_movement` returns `data.movement`, an object keyed by provider, each a list of `{captured_at, a_price, b_price, total_rounds}`, plus `snapshots`. Use `provider` to limit it to one book.

## Worked Example

Request: "Where is the line on the next Contender Series main event?"

```
get_schedule(days=7)  -> bout 401891665, lines:
  BetOnline  a -130, b 110, total_rounds 2.5
  Pinnacle   a -130, b 111
get_line_movement(bout_id="401891665")
  movement.BetOnline: three hourly snapshots, a_price -130 each time
```

Answer: the two books agree on side a at -130, the line had not moved across the captured snapshots, and the `total_rounds` is posted by one book only. The user should not read that as a total consensus.

## Output Format

```
Fight: A vs B (date, weight class)
Book        A open  A close   B open  B close   Total
Bet365      -170    -130      +140    +110      3.5
...
Best close: A -125 (Book), B +115 (Book)
Close, devigged median: A 54.2%, B 45.8%   (see odds-analysis)
Move, open to close: A implied 63.0% -> 56.5%
Note: lines are moneylines only; no props in this data.
```

## Anti-patterns

| What Claude Might Do | Why It Is Wrong | Do This Instead |
|---------------------|----------------|-----------------|
| Call `get_odds` per bout across a card | 5 each vs 10 for the card | `event_id` |
| Say "sharp money" from one book's move | One book is not a market | Use the median move |
| Compare `a_close_prob` to a model without devigging | Includes vig | `odds-analysis` first |
| Read `get_line_movement` for a 2021 fight | No snapshots that old | Use open and close |
| Present nulls as zero | A null price means no quote | Skip it and say so |

## What to Do Next

| Finding | Next Skill |
|---------|-----------|
| User wants true probability | `odds-analysis` |
| User has a model or rating | `edge-detection` |
| User wants history of favourites | `favourite-calibration` |
