---
name: ufc-fighter-profile
description: "Use when the user asks who a UFC fighter is or how he or she fights, in fan or analyst wording: 'tell me about Pantoja', 'scouting report on Chimaev', 'what is Poirier's record', 'how many significant strikes does he land', 'does he wrestle a lot', 'who has he fought lately', 'fighter stats for Gaethje'. Use this whenever a single fighter is named with a request for numbers or a rundown. Load it for short fragments and follow-ups too, even with no name given, instead of answering from memory or going straight to the raw tools. Reports bio, record by method, career rates per 15 minutes with fight time counted, recent fights and rating history. Not for a specific fight's preview (see ufc-fight-preview), a ratings baseline (see ufc-elo-baseline), a finishing breakdown by method and round (see ufc-finish-profile) or stat leaderboards (call get_leaders)."
metadata:
  version: 2.0.0
  author: SportsDataHQ
---

# UFC fighter profile

A fighter's profile is his record, how he wins and loses, and the rates that describe how he fights, against the opponents he met. This skill assembles that from FighterAPI.

## Before you start
- For anything across games, seasons or players, apply the sports-data-preflight checks first (ids from search, the season convention, one league, enough data).
- Tools come from the FighterAPI MCP server (`https://mcp.fighterapi.com/mcp`). Call them; never fill in a number from memory.
- Rates are per 15 minutes of fight time; accuracy and defense are fractions. Round-by-round stats exist for UFC cards (not Contender Series). The UFC is the default; pass `league` for pfl or bellator. Ids from `search_fighters(query)` (1 cr).
- Career rates (significant strikes landed and absorbed, accuracy, defense, takedowns, takedown accuracy and defense, submission attempts, control share) are UFC only and are computed from stat sheets; fights with no sheet are missing from them. Say how many UFC fights the rates cover.
- A fighter's ratings are our Elo from UFC results; fights in other organisations do not move them.

## Default path (about 11 credits)
1. **Resolve the fighter.** `search_fighters(query)` (1 cr).
2. **The profile.** `get_fighter(fighter_id)` (5 cr): age, height, reach, stance, gym, record by method, career rates per 15 minutes, current and peak rating and the last five fights.
3. **The history.** `get_fighter_fights(fighter_id, limit: 10)` (5 cr): opponents, results, methods, rounds, strikes and takedowns per fight, rating before and after.
4. **Weight class context (optional).** `get_ratings(weight_class)` (2 cr): where he sits among active fighters.

## Reading the profile
Rates built against weak opposition overstate a fighter; show the opponents' ratings from the fight history. Finishing profile: share of wins by KO or TKO, submission and decision, and how he has lost. Striking differential is landed minus absorbed per 15 minutes; grappling is takedowns per 15 against the opponent's defense. Reach and height are weak predictors on their own; mention them only as context. Under 4 UFC fights, every rate is unstable.

## Output template
```
<Fighter> | <weight class> | age <a>, reach <r>, stance <s> | record <W-L-D> (UFC fights <n>)
Wins by method: KO/TKO <a> | submission <b> | decision <c> | Losses: <by method>
Striking per 15: landed <v>, absorbed <v>, accuracy <%>, defense <%> | Grappling per 15: takedowns <v>, accuracy <%>, defense <%>, submission attempts <v>, control <%>
Recent fights: <last 5: opponent (rating), result, method>
Rating: current <r>, peak <r>
Read: 2-3 bullets with fight counts
Data: search_fighters, get_fighter, get_fighter_fights[, get_ratings] | UFC
```

## Rules
- Show the number of fights behind each rate.
- Never use the stat sheet of a fight that has not happened, or build a prediction from a fight's own stats.
- Do not label a style (wrestler, striker) without the rates that support it.
- Every number names its tool (the Data line, plus inline where it could be doubted) and every rate shows its sample size.
- If a tool returns too little, say "not enough data" and stop; do not estimate or borrow another sample.
- Odds and prices are information about the market only: no picks, leans, stakes, payouts or sportsbook links.
- Out of credits: if a call is refused for credits, pass on the API's message as it comes (it says when free credits refill and how to add more), and stop; don't retry or switch tools to get around it.

## Example prompts
- "Profile Islam Makhachev"
- "Is Topuria a finisher?"
- "Recent opposition for Chandler"
