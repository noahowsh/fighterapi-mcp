---
name: career-rates
description: "Ranks and profiles UFC fighters on career rates from the stat sheets: significant strikes landed and absorbed per 15 minutes, accuracy, defense, takedowns, control share, submission attempts, knockdowns and finish rate. Use when the user asks who the best striker, wrestler or finisher is, who has the best chin or defense, or how a fighter compares to a division. Do not use for a single fight's rounds -- see round-by-round-stats. Do not use for a full scouting report -- see fighter-scouting."
metadata:
  version: 1.0.0
  author: FighterAPI
---

# Career Rates

> **Default data tool:** FighterAPI (`fighterapi-tool`).
> Use `get_leaders` (5 credits) for a ranked list on one stat. Use `get_fighter` (5 credits) for one fighter's full `career_rates`.

You are an expert in combat sports statistics. Your goal is to rank and compare fighters on rates that are fair across fight lengths, with minimum-fight filters that keep one lucky night from topping a list.

## When to Use

- "Who lands the most significant strikes per minute at 155?"
- "Best takedown defense in the UFC"
- "Who finishes the most"
- "How does this fighter's output compare to the division?"

## When NOT to Use

- Per-round detail inside one fight -- see `round-by-round-stats`
- A full profile with record and form -- see `fighter-scouting`
- Predicting a fight -- see `fight-preview`

## Commands Available

| Command | What It Does | Credits |
|---------|-------------|---------|
| `get_leaders` | Leaderboard on one `stat`, filtered by `weight_class`, `since`, `min_fights` | 5 |
| `get_fighter` | One fighter's `career_rates` and rating | 5 |
| `search_fighters` | Find a fighter id | 1 |

## Commands That Do NOT Exist

| Not Available | Use Instead |
|--------------|-------------|
| `get_stats_leaders` or `get_top_fighters` | `get_leaders` |
| `get_pound_for_pound` | `get_ratings` (our Elo, not an official list) |
| `get_career_stats` | `get_fighter`, `career_rates` |
| `get_leaders` with several stats at once | One call per stat |

## The Eleven Leaderboard Stats

`get_leaders` takes `stat` as one of:

| `stat` | Meaning |
|--------|---------|
| `sig_landed_per_15` | Significant strikes landed per 15 minutes |
| `sig_absorbed_per_15` | Significant strikes absorbed per 15 minutes |
| `sig_accuracy` | Share of significant strikes that land |
| `sig_defense` | Share of opponent significant strikes that miss |
| `td_per_15` | Takedowns landed per 15 minutes |
| `td_accuracy` | Takedowns landed over attempted |
| `td_defense` | Opponent takedowns stopped |
| `knockdowns` | Total knockdowns |
| `sub_attempts_per_15` | Submission attempts per 15 minutes |
| `control_share` | Share of fight time in control |
| `finish_rate` | Wins by KO/TKO or submission as a share of wins |

Other parameters: `weight_class` (for example Lightweight), `since` (a year, counts only fights from then on), `min_fights` (default 5, up to 50) and `limit` (default 20, up to 100). Each row has `rank`, `fighter_id`, `name`, `weight_class`, `fights` and `value`.

Real call (Lightweight, `sig_accuracy`, `min_fights` 8): first place Benoit Saint Denis at 0.613 over 12 fights. Quote results as returned and say the filter you used.

## Choosing a Minimum

| Stat | Reasonable `min_fights` | Why |
|------|------------------------|-----|
| Per-15 and accuracy stats | 8 or more | Rates stabilize slowly; 3 fights is noise |
| `finish_rate` | 8 or more | Few fights makes 100% or 0% common |
| `knockdowns` | Use with `since` and compare per fight | A raw count favours long careers |
| `td_defense` | 8 or more, and check attempts faced | 100% defense on 2 attempts means nothing |

`get_leaders` does not return attempts faced. If a defense stat looks perfect, pull `get_fighter` for that fighter and check `minutes_fought` and `td_per_15` context before trusting it.

## Style Profiles

Build a style label from percentiles within the weight class, not from raw values.

1. Pull `get_leaders` for `sig_landed_per_15`, `td_per_15` and `control_share` with a large `limit` (100).
2. Place the fighter's `career_rates` among the returned values.
3. Label: high strikes and low takedowns is a striker; high takedowns and control is a grappler; high on both is a pressure all-rounder.

This costs 15 credits for three leaderboards. State it first. Leaderboards are capped at 100 per call, so a fighter outside the top 100 on a stat will not be located by position. Use the `value` of the 100th row as a threshold and say "outside the top 100".

## Combining Rates

- **Net striking** = `sig_landed_per_15` minus `sig_absorbed_per_15`. Both are per 15 minutes, same scale, so the difference is valid.
- **Never subtract an accuracy from a per-15 rate.** Different scales.
- **Durability proxy** = `sig_defense` together with `sig_absorbed_per_15`. A fighter can absorb few strikes by never fighting at range. Pair them with KO losses from `get_fighter`.
- **Finishing profile** = `finish_rate` together with `knockdowns` and `sub_attempts_per_15`.

## Pitfalls

- Rates are career averages. A fighter's best years and worst years blend. Use `since` for a recent window and compare.
- Weight-class moves: with `weight_class` set, only fights in that class count. A fighter's fights at other weights are excluded. Say so.
- UFC only. PFL and Bellator fighters have no `career_rates`.
- Opponent quality is not in the rate. A high `sig_landed_per_15` against weak opposition is not equal to the same number against contenders. Pair with `elo-by-weight-class`.
- Early finishes produce small minute totals. `minutes_fought` is in `get_fighter`.

## Worked Example

Request: "Where does Topuria rank at lightweight on striking accuracy?"

```
get_leaders(stat="sig_accuracy", weight_class="Lightweight", min_fights=8, limit=100)
get_fighter(fighter_id="4350812")
```

`get_fighter` gave `sig_accuracy` 0.501 over 104 minutes. Find the position in the leaderboard by `fighter_id`, report it with the filter, and note the fighter might be excluded if fewer than 8 fights qualify (he had 10 UFC bouts at the time of the call, so he would qualify at 8).

## Output Format

```
Lightweight, sig_accuracy, min 8 fights, since 2020
1  Benoit Saint Denis  0.613  (12 fights)
2  ...
Fighter: Topuria 0.501, rank N of M (placed by fighter_id)
Caveat: sample, opponent quality not controlled
```

## What to Do Next

| Finding | Next Skill |
|---------|-----------|
| Fighter stands out | `fighter-scouting` |
| Want rates as model features | `walk-forward-validation` |
| Want division Elo context | `elo-by-weight-class` |
