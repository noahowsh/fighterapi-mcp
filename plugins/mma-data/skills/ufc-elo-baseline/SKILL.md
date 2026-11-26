---
name: ufc-elo-baseline
description: "Use when the user wants the rating-based view of UFC fighters, in fan or analyst wording: 'what do the ratings say about Pereira vs Hill', 'who is rated higher', 'Elo gap', 'is he rated top at 155', 'did the numbers see that upset', 'rating baseline for the co-main', 'how far apart are they on paper'. Use this whenever ratings or Elo are mentioned for fighters. Load it for short fragments and follow-ups too, even with no name given, instead of answering from memory or going straight to the raw tools. Converts the pre-fight rating gap into an expected win probability, compares it with the market as information and shows rating history. Refuses to use in-fight stats from the fight being predicted (leakage). Not for a full fight preview (see ufc-fight-preview), a fighter profile (see ufc-fighter-profile), finishing (see ufc-finish-profile) or model building (see model-building)."
metadata:
  version: 2.0.0
  author: SportsDataHQ
---

# UFC Elo baseline

A rating is a compact summary of a fighter's results against the opponents he faced. This skill turns two ratings into a baseline expectation and says how much to trust it. It uses only what was known before the bell.

## Before you start
- For anything across games, seasons or players, apply the sports-data-preflight checks first (ids from search, the season convention, one league, enough data).
- Tools come from the FighterAPI MCP server (`https://mcp.fighterapi.com/mcp`). Call them; never fill in a number from memory.
- Rates are per 15 minutes of fight time; accuracy and defense are fractions. Round-by-round stats exist for UFC cards (not Contender Series). The UFC is the default; pass `league` for pfl or bellator. Ids from `search_fighters(query)` (1 cr).
- Our ratings are an Elo built from the promotion's own results (the UFC since 2000). They do not see fights outside the promotion, so a fighter back from another organisation is under-rated or unrated.
- The expected score for fighter A is 1 / (1 + 10^(-(R_A - R_B) / 400)). Our ratings use the standard 400-point Elo scale, so this conversion is exact for them.
- **Leakage rule.** For a fight that has not happened, there are no stat sheets to use. For a fight that has happened, never use that fight's own strikes, takedowns, rounds or result to build the baseline: use the ratings before the fight (`get_fight` gives them) and earlier fights only. If the user asks you to predict a past fight using its own stat sheet, refuse that part and say why.

## Default path (about 30 credits)
1. **Resolve the fighters.** `search_fighters(query)` (1 cr each).
2. **Ratings.** `get_ratings(weight_class)` (2 cr), or `get_fighter(fighter_id)` (5 cr) for current and peak rating, record and last five fights.
3. **Rating history.** `get_fighter_fights(fighter_id, limit: 10)` (5 cr): rating before and after each fight, opponents and results, so a recent big move or a long layoff is visible.
4. **Baseline.** Apply the expected-score formula to the pre-fight ratings; give the gap and the probability.
5. **Market (optional).** `get_odds(bout_id)` (5 cr): opening and closing moneylines as the market's view. Show our baseline and the market side by side, never merged.
6. **A past fight (optional).** `get_fight(bout_id)` (5 cr) for the ratings before it and the closing price; only ratings and the result for scoring the baseline afterwards.

## Trust and limits
A rating gap of 100 is about a 64% expected score. Ratings are less certain for fighters with few UFC fights (under 4), after a long layoff (over 18 months) or after a weight-class change; say which applies. A baseline ignores styles, injuries, camp and weight cuts. It is a starting point, and the fight preview skill holds the rest of the picture.

## Output template
```
<Fighter A> (rating <r>, UFC fights <n>) vs <Fighter B> (rating <r>, <n>) | <weight class> | <event, date>
Rating gap <g> -> baseline expected win probability <A x%> / <B y%>
Rating history: <A: last 3 changes> | <B: ...>
Flags: <few fights / layoff / weight-class change / outside-promotion record>
Market (if asked): <A implied %> / <B %> (information only)
Data: search_fighters, get_ratings, get_fighter, get_fighter_fights[, get_odds] | UFC
```

## Rules
- Use only information from before the fight; stat sheets from the fight being predicted are off limits.
- Say "our rating" and "the market" and never blend them.
- A baseline is not a prediction of method or round.
- Every number names its tool (the Data line, plus inline where it could be doubted) and every rate shows its sample size.
- If a tool returns too little, say "not enough data" and stop; do not estimate or borrow another sample.
- Odds and prices are information about the market only: no picks, leans, stakes, payouts or sportsbook links.
- Sequences (last 5, recent form, a run of results) are quoted in the order the tool returns them, with dates; never retell them from memory. Lists in the answer must match the tool rows.
- Out of credits: if a call is refused for credits, pass on the API's message as it comes (it says when free credits refill and how to add more), and stop; don't retry or switch tools to get around it.

## Example prompts
- "What does Elo say about Jones vs Aspinall?"
- "Who is the highest-rated lightweight right now?"
- "Did the ratings see that upset coming?"
