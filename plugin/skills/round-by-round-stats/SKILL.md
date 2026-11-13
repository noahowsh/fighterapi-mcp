---
name: round-by-round-stats
description: "Computes per-round striking and grappling rates for UFC fights: significant strikes landed and attempted by round, target and position splits, takedowns, control time, submission attempts, and fatigue fades between rounds. Use when the user asks how a fighter performs by round, who fades, strike differential per round, control time, round-by-round scoring, or pace. Do not use for career averages across fights -- see career-rates. Do not use for the result of a fight -- see fight-lookup."
metadata:
  version: 1.0.0
  author: FighterAPI
---

# Round-by-Round Stats

> **Default data tool:** FighterAPI (`fighterapi-tool`).
> Use `get_fight` (5 credits) and read `data.rounds`. UFC only.
> Find `bout_id` values with `get_fighter_fights` (5 credits) or `get_event` (2 credits).

You are an expert in fight analytics. Your goal is to turn the round-by-round lines into rates a person can compare, with the right denominators and honest sample sizes.

## When to Use

- Strikes landed and absorbed in each round of a fight
- Whether a fighter's output or accuracy drops in rounds 3 to 5
- Where strikes land (head, body, leg) and from where (distance, clinch, ground)
- Control time, takedown attempts and submission attempts by round
- Which fighter would win each round on volume (a stat proxy, not the judges)

## When NOT to Use

- Career averages -- see `career-rates`
- The final result and scorecards -- see `fight-lookup`
- PFL or Bellator -- no round lines exist there

## Commands Available

| Command | What It Does | Credits |
|---------|-------------|---------|
| `get_fight` | `rounds` array: one row per fighter per round | 5 |
| `get_fighter_fights` | Fight list with `bout_id`, `sig_landed`, `sig_absorbed`, `td_landed` totals | 5 per page |
| `get_event` | Fight list for a card with `bout_id` | 2 |

## Commands That Do NOT Exist

| Not Available | Use Instead |
|--------------|-------------|
| `get_round_stats` | `get_fight`, `rounds` |
| `get_strike_map` or `get_strike_location` | The head, body, leg splits in `rounds` and `fighters[].stats` |
| `get_fight_pace` | Compute from `rounds` as shown below |
| `get_control_time` | `control_seconds` in `rounds`, `time_in_control_seconds` in `stats` |

## Data Shape

Each row in `data.rounds`:

```
fighter_id, fighter_name, round, knock_downs,
sig_landed, sig_attempted, total_landed, total_attempted,
td_landed, td_attempted, sub_attempts, reversals, control_seconds,
head_landed, head_attempted, body_landed, body_attempted, leg_landed, leg_attempted,
distance_landed, distance_attempted, clinch_landed, clinch_attempted,
ground_landed, ground_attempted
```

Real shape from UFC 298, round 1: Volkanovski `sig_landed` 26 of `sig_attempted` 52, with leg strikes 11 of 11 and `control_seconds` 0. A two-round fight returns four rows. Group by `fighter_id`, then order by `round`.

## Core Metrics

All of these come straight from the rows.

| Metric | Formula |
|--------|---------|
| Accuracy | `sig_landed / sig_attempted` (guard zero) |
| Strike differential | `sig_landed(self) - sig_landed(opp)` in the same round |
| Volume share | `sig_landed(self) / (sig_landed(self) + sig_landed(opp))` |
| Target mix | `head_landed / sig_landed`, same for body and leg |
| Position mix | `distance_landed / sig_landed`, clinch, ground |
| Takedown rate | `td_landed / td_attempted` |
| Control share | `control_seconds / round_seconds` |
| Submission pressure | `sub_attempts` per round |

Round length is 300 seconds for a full round. The last round of a finish is partial. For a fight that ended in round 2 at 3:32, round 2 was 212 seconds. Use `end_round`, `end_clock` and `duration_seconds` from the bout header.

## Rates per Minute

A raw count is wrong in a partial round. Scale it:

```python
def per_15(count, seconds):
    return 0 if seconds == 0 else count * 900 / seconds
```

Use `per_15` to compare a finish in round 2 with a five-round decision. Never add rounds from different fights without the matching seconds.

## Fatigue Fade

For a fight that went at least 3 rounds:

```python
fade = (sig_landed_per_min_round_last - sig_landed_per_min_round_1) / sig_landed_per_min_round_1
```

A negative number means the fighter slowed. Do not call it cardio from one fight. The opponent's pressure, takedowns eating clock and the round the fight ended all move it.

To say something about a fighter, collect their last 5 to 8 distance fights (via `get_fighter_fights`, filter rows where `end_round` equals `scheduled_rounds`), then `get_fight` per bout (5 credits each). Report the median fade and the count of fights.

## Round Winner by Volume

A simple, transparent proxy for how judges score a round:

1. Knockdown edge wins the round (10-8 candidates if heavy).
2. Otherwise more `sig_landed` wins.
3. Break ties with control seconds, then takedowns.

Label it "stat proxy". Judges weigh damage, effective grappling and aggression, and `judges_scores` in `get_fight` has only totals per judge, not per round.

## Worked Example

Request: "Did Volkanovski fade against Topuria?"

```
get_fight(bout_id="401612970")
rows = data.rounds filtered to fighter_id 3949584   # 2 rounds, fight ended R2 at 3:32
```

Round 1: 26 landed of 52 attempted (50.0% accuracy). Compute round 2 from its row and divide by its 212 seconds, not 300. The honest answer for a two-round fight is "no fade can be measured here": a single early finish has no late rounds. Pull earlier five-round fights before claiming a pattern.

## Output Format

```
Round   Sig landed   Acc   Opp landed   Diff   Head/Body/Leg    Control   TD
1       26/52        50%   18           +8     8/7/11           0:00      0/0
2       21/55        38%   ... (212 s, per-15 rate 89)
Fade (per-min round 2 vs round 1): -20%   Sample: 1 fight
```

## Pitfalls

| What Claude Might Do | Why It Is Wrong | Do This Instead |
|---------------------|----------------|-----------------|
| Treat attempted strikes as the opponent's defence | Attempts include strikes blocked, missed or slipped | Report accuracy and defence separately |
| Compare partial and full rounds as counts | Different seconds | Use `per_15` with the actual seconds |
| Claim cardio problems from one fight | Opponent and clock effects | Aggregate over 5+ distance fights |
| Mix rounds in a fight with a stoppage | Last round is cut short | Use `end_clock` for the final round |
| Run on PFL fights | `rounds` is null | Say it does not exist |

## What to Do Next

| Finding | Next Skill |
|---------|-----------|
| Pattern across the career | `career-rates` |
| Use rates as model inputs | `walk-forward-validation` |
| Preview a booked fight | `fight-preview` |
