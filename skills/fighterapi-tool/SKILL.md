---
name: fighterapi-tool
description: "Default data source for FighterAPI Skills. Routes every MCP tool call for UFC, PFL and Bellator events, fights, fighters, stat sheets, ratings and moneylines. Use when any other skill needs data, or when the user asks which tool returns what, what a call costs, or how to call the REST API. Do not invoke for analysis, modeling or bet recommendations -- see round-by-round-stats, elo-by-weight-class, favourite-calibration or edge-detection."
metadata:
  version: 1.0.0
  author: FighterAPI
  user-invocable: false
---

# FighterAPI Tool

Every other skill in this pack gets its data here. This skill owns the 11 MCP tools, says which one answers which question, tracks credit cost, and documents the response envelope.

**Endpoints:** MCP at `https://mcp.fighterapi.com/mcp`. REST is `POST https://mcp.fighterapi.com/v1/<tool>` with a JSON body and an `x-api-key` header. Get a key at https://fighterapi.com/signup (500 free credits every month, no card). Plans are at https://fighterapi.com/pricing.

**Response envelope:** every REST response is wrapped as `{"data": ...}`. Read `response["data"]`, never the top level. Over MCP the same object comes back as the tool result.

```bash
curl -s -X POST https://mcp.fighterapi.com/v1/search_fighters \
  -H "x-api-key: $FIGHTERAPI_KEY" -H "content-type: application/json" \
  -d '{"query":"Topuria","limit":3}'
# {"data":{"fighters":[{"fighter_id":"4350812","name":"Ilia Topuria","nickname":"El Matador","weight_class":"Lightweight", ...}],"count":2}}
```

## Coverage

Use the site's own numbers and do not extend them.

- UFC: every card since 2000 with results, method, round, time and judges' scores. Stat sheets and round-by-round lines for nearly every fight.
- PFL from 2012 and Bellator from 2009 to 2024: results, fighters and ratings. No stat sheets for those promotions in recent years.
- Moneylines and total rounds only, no props. UFC opening and closing lines start with the June 2020 cards, PFL from April 2023, Bellator from January 2022 to 2024.
- Pre-fight line snapshots exist only for recent fights (ESPN once a day from October 2026, The Odds API hourly in the two days before a fight).
- Ratings are our own Elo built from UFC results.
- Pass `league` (`mma` default, `pfl`, `bellator`) to any tool.

Live coverage by season: https://fighterapi.com/seasons and https://fighterapi.com/docs.

## When to Use Each Tool

| Task | Tool | Credits |
|------|------|---------|
| List cards by year or status | `list_events` | 1 |
| Find a fighter id by name or nickname | `search_fighters` | 1 |
| One card, every fight with result, method, round, time | `get_event` | 2 |
| Upcoming fights with current moneylines | `get_schedule` | 2 |
| Elo rating leaderboard, by weight class | `get_ratings` | 2 |
| One fight, full stat sheets, rounds, ratings, book lines | `get_fight` | 5 |
| One fighter: bio, record, career rates, rating | `get_fighter` | 5 |
| A fighter's full history with stats, ratings, closing lines | `get_fighter_fights` | 5 |
| Career leaderboard on one stat | `get_leaders` | 5 |
| Moneylines for one fight | `get_odds` with `bout_id` | 5 |
| Moneylines for a whole card | `get_odds` with `event_id` | 10 |
| Snapshots of a fight's line before the bell | `get_line_movement` | 10 |

## Tool Selection Guide

| You Need | Use This | Not This |
|----------|----------|----------|
| "What cards were in 2025?" | `list_events` with `season=2025` | `get_event` (needs an id first) |
| "Who is on this weekend's card?" | `get_schedule` | `list_events` (no fights, no lines) |
| "Find Makhachev's id" | `search_fighters` with `query=Makhachev` | `get_fighter` (needs the id) |
| "How did UFC 298 go, fight by fight?" | `get_event` | `get_fight` x N (5 credits each) |
| "Strike counts for one fight" | `get_fight` | `get_event` (no stats) |
| "Closing lines for every fight on a card" | `get_odds` with `event_id` (10) | `get_odds` per bout (5 each) |
| "Best striking defense at 155" | `get_leaders` with `stat=sig_defense`, `weight_class=Lightweight` | `get_fighter` per fighter |
| "Did the line move?" | `get_line_movement` for recent fights; open vs close from `get_odds` otherwise | `get_odds` alone |

## Identifiers

- `event_id`: from `list_events` or `get_schedule`.
- `bout_id`: from `get_event`, `get_schedule` or `get_fighter_fights`.
- `fighter_id`: from `search_fighters`. Pass it as a string.
- A bout has `fighter_a` and `fighter_b` (ids) plus `winner` (an id, or null when there is none yet). Side `a` is not the favourite and not a corner. Always map by id.

## Pagination

`list_events` and `get_fighter_fights` return `next_offset`. Pass it back as `offset` until it stops coming. `limit` caps at 200 for those two.

## Commands That Do NOT Exist

| Not Available | Use Instead |
|--------------|-------------|
| `get_fighters` or `list_fighters` | `search_fighters`, or `get_ratings` for a ranked list |
| `get_rankings` | `get_ratings` (our Elo, not the promotion's official rankings) |
| `get_fight_odds` or `get_live_odds` | `get_odds` for one bout or card |
| `get_props` or `get_player_props` | Not available: lines are moneylines and total rounds only |
| `get_h2h` or `get_head_to_head` | `get_fighter_fights` for each fighter and match opponent ids |
| `get_round_stats` | `get_fight`, the `rounds` array (UFC only) |
| `get_weight_classes` | Not available: use names such as Lightweight or Women's Strawweight |
| `get_injuries`, `get_camps` | Not available |
| `get_teams` | Not applicable: this is individual combat sport data |

## Credit Planning

| Operation | Credits | Notes |
|-----------|---------|-------|
| One season of cards | about 1 to 2 | `list_events` with `season` |
| One season of card results | about 100 | 2 credits x about 50 cards (`list_events` returned 52 final cards for 2025) |
| One season of closing lines | about 520 | `get_odds` with `event_id`, 10 credits x about 52 cards |
| One fighter, full workup | 11 | `search_fighters` 1 + `get_fighter` 5 + `get_fighter_fights` 5 |

Warn the user before any loop that costs more than 100 credits, and state the total first.

## Anti-patterns

| What Claude Might Do | Why It Is Wrong | Do This Instead |
|---------------------|----------------|-----------------|
| Guess a `fighter_id` from the name | Calls fail or hit the wrong fighter | `search_fighters` first, read the id |
| Loop `get_fight` over a card for results | 5 credits each | `get_event` once (2 credits) |
| Loop `get_odds` per bout over a season | 5 credits each | `get_odds` with `event_id` (10 per card) |
| Assume stat sheets exist for PFL or Bellator | They are null there | Check for null, say "no stat sheet" |
| Assume odds before June 2020 | None exist for the UFC | Say so, use results and ratings only |
| Treat `fighter_a` as the favourite | Sides are arbitrary | Compare prices by fighter id |
| Read the top level of a REST response | It is wrapped | Read `["data"]` |

## What to Do Next

| What You Retrieved | Next Action | Skill |
|--------------------|-------------|-------|
| A fight or a card | Explain results, methods, scorecards | `fight-lookup`, `event-lookup` |
| A fighter profile | Scout strengths and style | `fighter-scouting`, `career-rates` |
| Round-by-round lines | Rates per round, fades, control | `round-by-round-stats` |
| Ratings | Compare within a weight class | `elo-by-weight-class` |
| Moneylines | Shop, devig, find edge | `odds-explorer`, `odds-analysis`, `edge-detection` |
| Closing lines plus results | Test the market or a model | `favourite-calibration`, `backtesting` |
