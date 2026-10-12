---
name: event-lookup
description: "Lists UFC, PFL and Bellator cards and breaks down one card fight by fight. Use when the user asks what cards happened in a year, what is on this weekend, how a card went, what the results and finish methods were, which fights went the distance, or wants the main event. Do not use for deep stats on one fight -- see fight-lookup. Do not use for prices -- see odds-explorer. Do not use for a fighter's history -- see fighter-scouting."
metadata:
  version: 1.0.0
  author: FighterAPI
---

# Event Lookup

> **Default data tool:** FighterAPI (`fighterapi-tool`).
> Use `list_events` (1 credit) to find cards, `get_event` (2 credits) for one card's fights, and `get_schedule` (2 credits) for what is coming.

You are an expert at summarizing fight cards. Your goal is a clean card view: who fought, who won, how, and when, with finish rates computed from the rows rather than recalled.

## When to Use

- "What UFC cards were there in 2024?"
- "What is on in the next two weeks?"
- "How did last night's card go?"
- Counting finishes, decisions, upsets or title fights on a card or across a year
- Getting `event_id` and `bout_id` values for other skills

## When NOT to Use

- Strike-level detail for one fight -- see `fight-lookup`
- Lines and prices -- see `odds-explorer`
- A fighter's whole record -- see `fighter-scouting`

## Commands Available

| Command | What It Does | Credits |
|---------|-------------|---------|
| `list_events` | Cards newest first, with venue, status, fight count, main event | 1 |
| `get_event` | Every fight on a card in order with result, method, round, time, scorecards, referee | 2 |
| `get_schedule` | Upcoming fights for the next N days with current moneylines | 2 |

## Commands That Do NOT Exist

| Not Available | Use Instead |
|--------------|-------------|
| `get_card` or `get_fight_card` | `get_event` |
| `search_events` | `list_events` with `season` and read `name` |
| `get_results` | `get_event` |
| `get_upcoming` | `list_events` with `status=scheduled`, or `get_schedule` |

## Parameters That Matter

- `list_events`: `season` (a year), `status` (`scheduled` or `final`), `limit` (up to 200), `offset`, `league` (`mma`, `pfl`, `bellator`). Results are newest first.
- `get_event`: `event_id` only (plus `league`).
- `get_schedule`: `days` (default 30, maximum 180), plus `league`.

`list_events` returns `event_id`, `name`, `event_date`, `venue`, `city`, `country`, `status`, `bouts` (the fight count) and `main_event`. A `scheduled` card has no results yet.

## Reading a Card

`get_event` returns `data.event` and `data.bouts`. Each bout has `card_segment` and `match_number`, `weight_class`, `title_fight`, `scheduled_rounds`, both fighters' ids and names, `winner` (an id), `method`, `method_display`, `end_round`, `end_clock`, `duration_seconds` and `judges_scores`.

Order matters. `match_number` and `card_segment` give the running order, with the main event first in the list. Present it as the card is read: main event, co-main, then the rest, unless the user asks for chronological order.

## Computing Card Summaries

Derive everything from the rows. Do not estimate.

```python
bouts = resp["data"]["bouts"]
done = [b for b in bouts if b["winner"]]
finishes = [b for b in done if not b["method"].startswith("decision")]
finish_rate = len(finishes) / len(done)
went_distance = [b for b in done if b["end_round"] == b["scheduled_rounds"]]
```

- Finish rate: share of decided fights whose `method` does not start with `decision`.
- Method split: group by `method_display`.
- Upset flag: needs prices. Pull `get_odds` with `event_id` (10 credits) and compare the winner's closing line to the other side. That is a `favourite-calibration` job at scale.
- Draws and no contests have no winner. Count them separately. Do not drop them silently.

## Year-in-review Pattern

1. `list_events` with `season=2025`, `status=final`, `limit=100`. Read `count` and `next_offset` to confirm you have them all.
2. Pick the cards of interest, then `get_event` per card (2 credits each).
3. Aggregate finish rate, title fights, and fights by weight class.

A full year costs about one credit for the list plus 2 per card. State the total before running it.

## Worked Example

Request: "What is coming up?"

```
get_schedule(days=14)
```

The response is `data.days`, `data.bouts` and `data.count`. Each upcoming bout carries the same header fields as a result row, with `winner`, `method` and `end_round` null, plus `lines`: a list of `{provider, a, b, total_rounds}` for each book that has posted. `lines` is null when no book has posted yet. In a live call, a Contender Series bout showed two books posting `a` -130, `b` 110 and 111. Group by `event_name` and `event_date`, show the main event first, and flag bouts with no line yet instead of leaving a blank.

## Output Format

```
UFC 298, Feb 17 2024, Honda Center, Anaheim (12 fights)
Main event: Topuria def. Volkanovski, KO/TKO, R2 3:32 (featherweight title)
Co-main: Whittaker def. Costa, UD (29-28, 29-28, 30-27)
...
Finishes: 7 of 12 decided fights. Decisions: 5.
```

## Anti-patterns

| What Claude Might Do | Why It Is Wrong | Do This Instead |
|---------------------|----------------|-----------------|
| Call `get_fight` for each bout to get results | 5 credits each, `get_event` has results for 2 | `get_event` |
| Trust the card name for the main event | Names change after the card is set | Read `main_event` from `list_events` |
| Report a card as complete while `status` is `scheduled` | No results exist | Show it as upcoming with any `lines` |
| Compute finish rate over all bouts | Draws and no contests have no winner | Divide by decided fights, and say so |

## What to Do Next

| Finding | Next Skill |
|---------|-----------|
| One fight stands out | `fight-lookup` |
| Upcoming card the user cares about | `fight-preview` |
| Want prices for the card | `odds-explorer` |
| Want to test how often favourites won | `favourite-calibration` |
