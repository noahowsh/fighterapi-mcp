---
name: ufc-fight-preview
description: "Use when the user wants to know how a UFC, PFL or Bellator fight or card shapes up, in fan or analyst wording: 'Pimblett vs Gaethje', 'who wins Saturday', 'main event breakdown', 'UFC 300 preview', 'striker or grappler, who has the edge', 'is the favorite live', 'fight night preview', 'how does Makhachev match up with Tsarukyan', 'who takes this one', 'who is the pick on fight night', 'UFC preview, no boxing'. Use this whenever two fighters are named together or a card or bout is the subject. Also use it for bare follow-ups with no name given, and load it instead of answering from memory or going straight to the raw tools. Produces a one-page report: records by method, striking and grappling rates for and against, our Elo, recent opposition and the moneylines. Not for one fighter's profile (see ufc-fighter-profile), finishing (see ufc-finish-profile), a ratings-only baseline (see ufc-elo-baseline), stat leaders (call get_leaders) or modeling."
metadata:
  version: 2.0.0
  author: SportsDataHQ
---

# UFC fight preview

A one-page preview of one fight from live FighterAPI calls. The UFC is the default; pass `league` for PFL or Bellator.

## Before you start
- For anything across games, seasons or players, apply the sports-data-preflight checks first (ids from search, the season convention, one league, enough data).
- Tools come from the FighterAPI MCP server (`https://mcp.fighterapi.com/mcp`). Call them; never recall a record.
- Rates are per 15 minutes of fight time; accuracy and defense are fractions. Round-by-round stats exist for UFC cards (not Contender Series).
- Our ratings are an Elo from the promotion's own results; they do not see fights outside it.

## Default path (about 24 credits)
1. **Find the fight.** `get_schedule(days)` (2 cr) or `get_event(event_id)` (2 cr): bout id, card position, current moneyline.
2. **Profiles.** `get_fighter(fighter_id)` (5 cr) for both: age, height, reach, stance, record by method, career rates (significant strikes landed and absorbed per 15, accuracy, defense, takedowns per 15, takedown accuracy and defense, submission attempts, control).
3. **Recent opposition.** `get_fighter_fights(fighter_id, limit: 5)` (5 cr) for both: who they beat and lost to, how, and when. Rates built against weak opposition overstate a fighter.
4. **Strength.** `get_ratings(weight_class)` (2 cr): both fighters' Elo.
5. **Prices.** `get_odds(bout_id)` (5 cr): opening, closing and current moneylines and implied probabilities.

## How to frame the matchup
- Striking differential = landed minus absorbed per 15; grappling = takedowns landed per 15 vs the opponent's takedown defense.
- Finishing profile: share of wins by KO/TKO, submission, decision; and how each has lost.
- Reach and height are weak predictors on their own; mention them as context only.
- Never use stats from the fight being previewed (they don't exist yet; for past fights that's leakage).

## Output template
```
<Fighter A> (<record>, Elo <r>) vs <Fighter B> (<record>, Elo <r>) | <weight class>, <rounds> | <event, date>
Moneyline: <A> / <B> | Market implies <A%> / <B%>
Striking: SLpM / SApM / accuracy / defense for both
Grappling: TD per 15, TD accuracy, TD defense, sub attempts for both
Finishing: wins by method and losses by method for both
Recent: last 3 opponents and results for both
What to watch: 2-3 bullets from the numbers
Data: get_schedule, get_fighter, get_fighter_fights, get_ratings, get_odds | UFC
```

## Rules
- Career rates need fight time: show UFC fights counted. Under 4 UFC fights, rates are unstable.
- Odds are information about the market: no pick, stake or bet.
- Out of credits: if a call is refused for credits, pass on the API's message as it comes (it says when free credits refill and how to add more), and stop; don't retry or switch tools to get around it.