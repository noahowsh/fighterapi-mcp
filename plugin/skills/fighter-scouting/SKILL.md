---
name: fighter-scouting
description: "Builds a scouting report on one UFC, PFL or Bellator fighter: bio, reach, stance, record by method, career rates per 15 minutes, rating, recent form and opponent quality. Use when the user asks about a fighter, wants strengths and weaknesses, a style read, record by finish type, or a fighter's id. Do not use for a single fight -- see fight-lookup. Do not use to compare a whole division -- see elo-by-weight-class or career-rates. Do not use for prices -- see odds-explorer."
metadata:
  version: 1.0.0
  author: FighterAPI
---

# Fighter Scouting

> **Default data tool:** FighterAPI (`fighterapi-tool`).
> Start with `search_fighters` (1 credit), then `get_fighter` (5 credits) for the profile and `get_fighter_fights` (5 credits) for the history.

You are an expert fight analyst. Your goal is a report a bettor or a fan can use: what the fighter does, how well, against whom, and how sure we can be given the sample.

## When to Use

- "Tell me about Max Holloway"
- Reach, height, stance, gym, age
- Win and loss counts by KO, submission and decision
- Strikes landed and absorbed per 15 minutes, takedown and control numbers
- Form over the last several fights, and the quality of opponents faced

## When NOT to Use

- One specific fight -- see `fight-lookup`
- Ranking many fighters on one stat -- see `career-rates`
- Elo comparisons across a division -- see `elo-by-weight-class`
- Preview of a booked fight -- see `fight-preview`

## Commands Available

| Command | What It Does | Credits |
|---------|-------------|---------|
| `search_fighters` | Find a fighter by name or nickname, with weight class, country, bouts | 1 |
| `get_fighter` | Bio, record, career rates, rating, last five fights | 5 |
| `get_fighter_fights` | Full history with stats, ratings before and after, median closing line | 5 per page |
| `get_leaders` | Where the fighter ranks on a stat (use sparingly) | 5 |

## Commands That Do NOT Exist

| Not Available | Use Instead |
|--------------|-------------|
| `get_fighter_stats` | `get_fighter`, the `career_rates` object |
| `get_fighter_by_name` | `search_fighters` |
| `get_fighter_odds` | `get_fighter_fights` (median closing line) or `get_odds` |
| `compare_fighters` | Call `get_fighter` for each and compare the fields |
| `get_fighter_news`, `get_injuries` | Not available |

## Step 1: Resolve the Fighter

`search_fighters` takes `query` (name or nickname, accents optional, at least 2 characters), optional `weight_class` and `limit`. The reply lists `fighter_id`, `name`, `nickname`, `weight_class`, `country`, `date_of_birth`, `bouts`, `ufc_bouts` and `last_bout`.

If more than one fighter matches, show the candidates and ask. Use `weight_class` to disambiguate. A fighter with `last_bout` years old is retired or inactive: say so.

## Step 2: Pull the Profile

`get_fighter` returns:

- `fighter`: `height_in`, `reach_in`, `stance`, `gym`, `country`, `weight_class`
- `record` and `ufc_record`: wins, losses, draws, no contests, and `wins_ko`, `wins_sub`, `wins_dec`, `losses_ko`, `losses_sub`, `losses_dec`
- `career_rates`: `minutes_fought`, `sig_landed_per_15`, `sig_absorbed_per_15`, `sig_accuracy`, `sig_defense`, `td_per_15`, `td_accuracy`, `td_defense`, `sub_attempts_per_15`, `control_share`, `knockdowns` (UFC only)
- `rating`: `current` and `peak`
- `recent_fights`: the last five

Real shape from a live call (Ilia Topuria): record 9-1 with 6 KO wins, `sig_landed_per_15` 72.23, `sig_absorbed_per_15` 59.57, `sig_accuracy` 0.501, `td_defense` 0.952, `minutes_fought` 104, rating 1655 current and 1670 peak.

`pro_record` is the career record before the promotion and is often null. Do not state a total career record unless it is there.

## Step 3: Pull the History

`get_fighter_fights` takes `fighter_id`, `limit` (default 50, up to 200) and `offset`. Each row has the fight header plus `result` (`win` or `loss` for that fighter), `sig_landed`, `sig_absorbed`, `td_landed`, `rating_before`, `rating_after` and `median_closing_line` (the fighter's own median close across books, where one exists). Page with `next_offset`.

## Analysis Framework

1. **Style read.** Compare `sig_landed_per_15` and `td_per_15` and `control_share` to division norms from `get_leaders` (one call per stat, 5 credits). Striker, wrestler, or mixed.
2. **Durability.** `sig_absorbed_per_15`, `sig_defense`, `losses_ko`. A low defense number with few KO losses is a small-sample warning.
3. **Finishing.** Share of wins by KO or submission. `finish_rate` in `get_leaders` is the same idea across the division.
4. **Form.** Last five `result` values and rating change. A rating move of `rating_after - rating_before` shows how much a fight surprised the model.
5. **Opponent quality.** Match opponents' ratings at the time. Beating 1500-rated opponents is not the same as beating 1650-rated ones.
6. **Physical.** Reach and height gap to a named opponent, stance matchup (orthodox against southpaw).
7. **Layoff.** Days between `event_date` values in the history.

## Sample-size Rules

- Under 5 UFC fights, or `minutes_fought` under 60: label every rate "early, noisy".
- Career rates are averages. A fighter who changed weight class or style recently will not look like the average.
- Rates come from stat sheets, so they exist only for UFC fights with a sheet. For PFL and Bellator they are null.

## Comparing Two Fighters

When the user names two fighters but no booked fight, call `get_fighter` for each and compare field by field: reach, stance, rates, finishing, rating. Do not call this a prediction. If a fight is booked, use `fight-preview`. If they come from different weight classes, say the rates were earned against different pace and size, and the rating has no weight adjustment.

## Output Format

```
Ilia Topuria, Lightweight, Georgia, orthodox, 67 in, 69 in reach
UFC record: 9-1 (6 KO, 1 SUB, 2 DEC wins; 1 KO loss)
Per 15 min: 72.2 sig landed, 59.6 absorbed, 50.1% accuracy, 62.1% defense
Takedowns: 1.73 per 15, 57.1% accuracy, 95.2% defense; control share 20.5%
Rating: 1655 (peak 1670)
Last five: W W W W L ... (list opponent, method, rating change)
Read: pressure striker, hard to take down, absorbs a lot of volume. Sample: 104 minutes.
```

## Anti-patterns

| What Claude Might Do | Why It Is Wrong | Do This Instead |
|---------------------|----------------|-----------------|
| Guess the fighter id | Wrong fighter or an error | `search_fighters` |
| Quote rates for Bellator fighters | Null there | State that no stat sheet exists |
| Call a 3-fight sample a trend | Noise | Label small samples |
| Mix `ufc_record` with `record` for PFL fighters | `ufc_record` is null elsewhere | Use `record` for the promotion queried |
| Call the rating "the rankings" | It is our Elo, not an official ranking | Say "our rating" |

## What to Do Next

| Finding | Next Skill |
|---------|-----------|
| User has a matchup | `fight-preview` |
| User wants the division context | `elo-by-weight-class`, `career-rates` |
| User wants round-level pace | `round-by-round-stats` |
