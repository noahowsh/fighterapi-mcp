---
name: fight-lookup
description: "Finds one UFC, PFL or Bellator fight and reports the result, method, round, time, scorecards and stat sheet. Use when the user asks who won a fight, how it ended, what the scorecards were, how many strikes or takedowns landed, or wants a fight id. Do not use for a whole card -- see event-lookup. Do not use for a fighter's career -- see fighter-scouting. Do not use for betting lines -- see odds-explorer."
metadata:
  version: 1.0.0
  author: FighterAPI
---

# Fight Lookup

> **Default data tool:** FighterAPI (`fighterapi-tool`).
> Use `get_fight` (5 credits) for the full record of one fight.
> Find the `bout_id` first with `get_event` (2 credits) or `get_fighter_fights` (5 credits).

You are an expert at reading a fight record. Your goal is to answer "what happened in this fight" precisely, with the numbers the stat sheet supports and no more.

## When to Use

- Result, method, round and time of a specific fight
- Judges' scorecards and referee
- Strike, takedown, control-time and submission counts for each fighter
- Finding the `bout_id` for a fight, for use by other skills

## When NOT to Use

- All fights on a card -- see `event-lookup`
- A fighter's career, record or style -- see `fighter-scouting`
- Rates over rounds or minutes -- see `round-by-round-stats`
- Sportsbook prices -- see `odds-explorer`

## Commands Available

| Command | What It Does | Credits |
|---------|-------------|---------|
| `search_fighters` | Find a fighter id by name or nickname | 1 |
| `get_fighter_fights` | List a fighter's fights, which carry the `bout_id` | 5 |
| `get_event` | List the fights on a card, which carry the `bout_id` | 2 |
| `get_fight` | Result, both stat sheets, rounds, ratings, book lines | 5 |

## Commands That Do NOT Exist

| Not Available | Use Instead |
|--------------|-------------|
| `search_fights` | `get_fighter_fights` or `get_event` |
| `get_fight_by_name` | Search the fighter, then match the opponent in `get_fighter_fights` |
| `get_fight_stats` | `get_fight`, the `fighters[].stats` object |
| `get_round_stats` | `get_fight`, the `rounds` array |

## How to Find the Fight

1. Know the card: `list_events` with `season`, find the card, then `get_event` and pick the bout.
2. Know a fighter: `search_fighters`, then `get_fighter_fights` with a small `limit`, and match `fighter_a_name` or `fighter_b_name` to the opponent.
3. Know only the date: `list_events` for that `season`, match `event_date`.

Resolve ambiguity out loud. If two fighters share a name, show weight class and country and ask.

## What `get_fight` Returns

`data.bout` holds the header: `weight_class`, `title_fight`, `scheduled_rounds`, `fighter_a`, `fighter_b`, `winner` (a fighter id), `method` and `method_display`, `end_round`, `end_clock`, `duration_seconds`, `judges_scores`, `referee`.

`data.fighters` is a two-item list. Each item has `fighter_id`, `name`, `stats` and `elo` (`before`, `after`). `stats` includes:

- Strikes: `sig_strikes_landed`, `sig_strikes_attempted`, `total_strikes_landed`, `knock_downs`
- Target and position splits: `sig_distance_head_landed`, `sig_clinch_body_attempted`, `sig_ground_leg_landed` and the rest of the head, body and leg by distance, clinch and ground grid
- Grappling: `takedowns_landed`, `takedowns_attempted`, `takedown_accuracy`, `advances`, `reversals`, `submissions`, `time_in_control_seconds`

`data.rounds` has one row per fighter per round with `round`, `sig_landed`, `sig_attempted`, `td_landed`, `td_attempted`, `sub_attempts`, `control_seconds` and the head, body, leg, distance, clinch and ground splits. `data.odds` lists each book's open, close and current line (2024 on).

Stat sheets and rounds are UFC only. For PFL and Bellator, and for UFC fights the source has no sheet for, they come back null. Say "no stat sheet" instead of inventing zeros.

## Reading the Result

- `winner` is a `fighter_id`. Map it to a name through `fighter_a` and `fighter_b`. Do not assume side `a` won.
- `method_display` is the label to show. The raw `method` values look like `kotko` and `decision---unanimous`.
- `judges_scores` is a string like `29-28 | 29-28 | 30-27`, null when the fight did not go to the cards. Scores are listed per judge, not per round.
- `end_clock` is the time within `end_round`. A fight that ends at `3:32` of round 2 lasted `duration_seconds` 512.
- A decision means `end_round` equals `scheduled_rounds` and the clock is the full round length.

## Worked Example

Request: "How did Topuria beat Volkanovski?"

```
search_fighters(query="Topuria")                 -> fighter_id 4350812
get_fighter_fights(fighter_id="4350812", limit=10)  -> find the UFC 298 row, bout_id 401612970
get_fight(bout_id="401612970")
```

Real shape of the answer (trimmed): `winner` is `4350812` (Topuria), `method_display` KO/TKO, round 2 at 3:32, 512 seconds. Volkanovski's stat sheet shows 47 of 107 significant strikes landed, no takedown attempts, and `elo` 1674 before, 1658 after. Always read each number from the response before quoting it.

## Output Format

```
UFC 298, Feb 17 2024, Featherweight title (5 rounds)
Winner: Ilia Topuria by KO/TKO, round 2, 3:32
Sig strikes: Volkanovski 47/107, Topuria x/y
Takedowns: 0/0 and x/y
Control: 0:00 and x:xx
Ratings: Volkanovski 1674 -> 1658, Topuria a -> b
Note: stat sheet is UFC Stats data; ratings are our Elo.
```

## Edge Cases

- **Draw or no contest.** `winner` is not a fighter id. Report the `method_display` and do not assign a loser.
- **Scheduled fight.** Result fields are null. Send the user to `get_schedule` or `fight-preview`.
- **Short-notice replacement.** The `bout_id` is for the fight as it happened. An earlier booking with a different opponent is not in the data.
- **Fight with no stat sheet.** Some UFC fights have no sheet at the source. The `fighters[].stats` object is null. State the result and note the gap.
- **Title fight scheduled for five rounds ending in round 3.** Use `scheduled_rounds` to say it did not go the distance.
- **Two fighters, same name.** `fighter_id` is the key. Never match on name alone.

## Anti-patterns

| What Claude Might Do | Why It Is Wrong | Do This Instead |
|---------------------|----------------|-----------------|
| Quote strike totals for a PFL fight | Stat sheets are null there | Say none exist |
| Call `get_fight` to learn the winner of 12 fights | 60 credits | `get_event` once (2 credits) |
| Call a fight a "robbery" or "dominant" | Opinion beyond the data | Report scorecards and counts, let the user judge |
| Say a fight lasted `end_round` rounds | Partial rounds exist | Use `end_round` and `end_clock` together |

## What to Do Next

| Finding | Next Skill |
|---------|-----------|
| User wants the rest of the card | `event-lookup` |
| User wants the loser's or winner's history | `fighter-scouting` |
| User wants round-by-round pace | `round-by-round-stats` |
| User asks what the closing line was | `odds-explorer` |
