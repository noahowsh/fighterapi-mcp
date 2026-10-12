---
name: fight-preview
description: "Builds a matchup preview for a booked UFC, PFL or Bellator fight: both fighters' form, career rates, physical gaps, rating gap, and the market line. Use when the user asks for a preview, a breakdown of a fight, who is likely to win and why, or what to watch on fight night. Do not use for one fighter alone -- see fighter-scouting. Do not use for a bet recommendation -- see edge-detection. Do not use for a past fight's result -- see fight-lookup."
metadata:
  version: 1.0.0
  author: FighterAPI
---

# Fight Preview

> **Default data tool:** FighterAPI (`fighterapi-tool`).
> A full preview costs about 19 credits: `get_schedule` 2 (or `get_event`), `search_fighters` 2, `get_fighter` 10, `get_odds` 5, plus optional `get_fighter_fights` 5 per fighter.

You are an expert at previewing fights. Your goal is a one-page matchup read that separates what the data says from what is guesswork, and anchors on the market.

## When to Use

- "Preview Saturday's main event"
- "Break down X vs Y"
- "What should I watch for in this fight?"
- Pre-fight context for a post on social or a newsletter

## When NOT to Use

- A single fighter without a booked opponent -- see `fighter-scouting`
- Betting recommendations -- see `edge-detection`
- Results of a fight already finished -- see `fight-lookup`

## Commands Available

| Command | What It Does | Credits |
|---------|-------------|---------|
| `get_schedule` | Find the bout, its `bout_id` and the posted lines | 2 |
| `search_fighters` | Find each fighter's id | 1 each |
| `get_fighter` | Profile, record, career rates, rating, last five | 5 each |
| `get_fighter_fights` | Deeper history with opponent ratings and closing lines | 5 each |
| `get_odds` | Each book's moneyline for the bout | 5 |
| `get_leaders` | Division context for a stat | 5 |

## Commands That Do NOT Exist

| Not Available | Use Instead |
|--------------|-------------|
| `get_matchup` or `get_h2h` | `get_fighter` for both and compare |
| `predict_fight` | Not available: use ratings and the market, see `elo-by-weight-class` |
| `get_injuries`, `get_weigh_ins` | Not available: say you cannot see them |

## Workflow

1. **Find the fight.** `get_schedule` with `days`, or `get_event` for a known `event_id`. Capture `bout_id`, `scheduled_rounds`, `title_fight`, `weight_class`.
2. **Profiles.** `get_fighter` for each id. Pull `reach_in`, `height_in`, `stance`, `career_rates`, `rating`, `recent_fights`.
3. **Gaps.** Compute differences, A minus B, and say which direction favours whom.
4. **Rating gap to probability.** Rating difference `d = R_a - R_b`. A standard Elo conversion is `p_a = 1 / (1 + 10^(-d/400))`. Treat this as a rough prior. The 400 scale is an assumption, so check it with `probability-calibration` before leaning on it.
5. **Market.** `get_odds` with the `bout_id`. Take the median of `a_close_prob` and `b_close_prob` across books, normalize so they sum to 1 (see `odds-analysis`).
6. **Compare.** If the rating prior and the market agree within a few points, say "no disagreement". If they differ by 8 points or more, look for a reason in the data: layoff, a very different opponent quality, a small sample.
7. **Write.** Lead with the market, then the style matchup, then the risks.

## Style Matchup Checklist

| Question | Data |
|----------|------|
| Who lands more per minute, and who absorbs less? | `sig_landed_per_15`, `sig_absorbed_per_15` |
| Does the striker's defense hold against pressure? | `sig_defense`, `losses_ko` |
| Can the wrestler get it down, and keep it there? | `td_per_15`, `td_accuracy`, `control_share` against the other's `td_defense` |
| Does either have a finishing record? | `wins_ko`, `wins_sub`, `finish_rate` |
| Cardio over five rounds | `round-by-round-stats` fade between round 1 and later rounds |
| Layoff or short notice | Dates in `get_fighter_fights` |
| Reach and stance | `reach_in`, `stance` |

## Hard Limits

- The data has no camp news, injuries, weight cuts or short-notice flags. Say so.
- PFL and Bellator previews have no stat-sheet rates. Use record, rating and market only.
- Rates need samples. If either fighter has under 60 `minutes_fought`, flag it.
- A rating comes from UFC results alone. A fighter coming from another promotion starts at 1500 regardless of record.

## Worked Example

Request: "Preview the main event on the next UFC card."

```
get_schedule(days=14)                 -> pick the main event, note bout_id
get_fighter(fighter_id=<a>)           -> rates, rating
get_fighter(fighter_id=<b>)
get_odds(bout_id=<bout_id>)           -> books[].a_close_prob, b_close_prob
```

For a profile call on Ilia Topuria, the live response gave `sig_landed_per_15` 72.23, `sig_absorbed_per_15` 59.57, `td_defense` 0.952 and a rating of 1655 against a 1670 peak. A preview built on that would say what the numbers support (high volume, takedown defense very hard to crack on a 104-minute sample) and stop there.

## Output Format

```
A vs B, weight class, rounds, date
Market: A 62% / B 38% (median close, devigged, N books)
Rating: A 1655, B 1610 (gap 45, rough prior 56%)
Style: A pressure striker (72 landed per 15), B counter wrestler (td 2.1 per 15)
Edges for A: reach +2 in, defense
Edges for B: control share, finish rate
Unknowns: camp, injuries, weight cut (not in the data)
Risk: B has 3 UFC fights, rates are noisy
```

## Keeping the Cost Down

The cheapest honest preview skips `get_fighter_fights`. `get_fighter` already includes the last five fights and the career rates. Add the history call only when the user asks about opponent quality, layoffs or trends, and say it is 5 credits per fighter and per page. When previewing a whole card, pull `get_odds` with `event_id` once (10 credits) instead of per bout, and pull `get_fighter` only for the fights the user picks.

## Anti-patterns

| What Claude Might Do | Why It Is Wrong | Do This Instead |
|---------------------|----------------|-----------------|
| Declare a winner with certainty | Fights are high-variance | Give probabilities and the range |
| Ignore the market | The close is the best public estimate | Anchor on the devigged line |
| Compare raw `sig_landed_per_15` across weight classes | Pace differs by division | Compare to `get_leaders` for the class |
| Pull `get_fighter_fights` for both to answer a simple preview | 10 extra credits | Only when form or opponent quality is the question |

## What to Do Next

| Finding | Next Skill |
|---------|-----------|
| Model and market disagree | `edge-detection` |
| User wants round fade detail | `round-by-round-stats` |
| User wants the whole card | `event-lookup` |
