---
name: ufc-finish-profile
description: "Use when the user wants to know how a UFC fighter wins and loses: 'does he finish fights', 'KO or submission', 'how often does she go to decision', 'is he chinny', 'finish rate for Makhachev', 'who finishes the most at lightweight'. Breaks a fighter's UFC wins and losses by method and round, with finish rate, rounds, and how that compares with the weight class. Not for a fight preview (see ufc-fight-preview), the Elo baseline (see ufc-elo-baseline) or a general fighter profile (see ufc-fighter-profile)."
metadata:
  version: 2.0.0
  author: SportsDataHQ
---

# UFC finish profile

How a fighter's fights end is more telling than the record. This skill breaks wins and losses by method and round from FighterAPI, with the count behind every share.

## Before you start
- For anything across games, seasons or players, apply the sports-data-preflight checks first (ids from search, the season convention, one league, enough data).
- Tools come from the FighterAPI MCP server (`https://mcp.fighterapi.com/mcp`). Call them; never fill in a number from memory.
- Seasons are calendar years. Fighters from `search_fighters(name)` (1 cr). UFC detail (stat sheets, rounds) is UFC only; for PFL and Bellator pass `league` and say the detail is thinner.
- `get_fighter(fighter_id)` (5 cr) returns the record by method and the career rates per 15 minutes. `get_fighter_fights(fighter_id)` (5 cr) returns every fight with the opponent, result, method, round and time. Method and round come from those rows; classify them as returned.
- `get_leaders(stat: "finish_rate", weight_class, since, min_fights)` (5 cr): wins by KO/TKO or submission as a share of wins. Finishes suffered (losses by KO/TKO or submission as a share of losses) are not a returned stat; compute them from `get_fighter_fights` and say so.
- Chin and durability are not measured. Knockdowns absorbed are not returned; do not call anyone chinny. Report losses by KO/TKO, which is what the rows show.

## Default path (about 15 to 30 credits)
1. **Resolve the fighter.** `search_fighters(name)` (1 cr).
2. **Record by method.** `get_fighter(fighter_id)` (5 cr): wins and losses by KO/TKO, submission and decision.
3. **Every fight.** `get_fighter_fights(fighter_id)` (5 cr): compute finish rate for wins, finish rate against in losses, round of finish and fights going to the judges. Say these are computed.
4. **Class context.** `get_leaders(stat: "finish_rate", weight_class, since)` (5 cr) to place his finish rate; fighters under the minimum fights are excluded.
5. **One fight (optional).** `get_fight(bout_id)` (5 cr) for the round-by-round lines of a finish.

## Reading it
A finish rate over fewer than 8 wins is thin: say it. Strength of opposition matters: a finish rate built on early-career opponents is not the same as one against top-10 names; check opponents and the rating before the fight in `get_fighter_fights`. Do not predict how a coming fight ends.

## Output template
```
<Fighter> | <weight class> | UFC fights <n> (wins <w>, losses <l>)
Wins by method: KO/TKO <a> | submission <b> | decision <c> | finish rate <%> (of <w> wins)
Losses by method: KO/TKO <a> | submission <b> | decision <c> | finished in <%> of <l> losses (computed)
Rounds: wins finished in round 1 <x>, round 2 <y>, later <z>
Class context: finish rate rank <n> of <m> at <weight class> since <year> (min <k> fights)
Read: 2-3 bullets with counts, thin samples flagged
Data: search_fighters, get_fighter, get_fighter_fights, get_leaders | UFC, <weight class>
```

## Rules
- Say computed figures were computed from fight rows.
- Do not describe chin or durability; only losses by method.
- Show wins and losses counted beside every percentage.
- Every number names its tool (the Data line, plus inline where it could be doubted) and every rate shows its sample size.
- If a tool returns too little, say "not enough data" and stop; do not estimate or borrow another sample.
- Odds and prices are information about the market only: no picks, leans, stakes, payouts or sportsbook links.

## Example prompts
- "Does Makhachev finish fights or win by decision?"
- "Who has the best finish rate at lightweight since 2020?"
- "How often does Jon Jones get finished?"
