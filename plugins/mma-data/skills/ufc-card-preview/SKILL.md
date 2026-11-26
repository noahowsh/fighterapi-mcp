---
name: ufc-card-preview
description: "Use when the user wants a whole UFC card at a glance rather than one fight: 'preview UFC 325', 'break down this weekend's card', 'who's favoured on the main card', 'which fights on Saturday are closest', 'give me the card with records and ratings', 'what's the main event and co-main look like'. Lists every bout with both fighters' records, our Elo, the market's no-margin probability and how close each fight is, then flags the biggest gaps between rating and market as information. Never says who to bet on. Not for one fight in depth (see ufc-fight-preview), one fighter's history (see ufc-fighter-profile) or how fighters finish (see ufc-finish-profile)."
metadata:
  version: 2.0.0
  author: SportsDataHQ
---

# UFC card preview

A card is ten to fourteen fights; most people want the whole thing on one page before going deep on two or three. This skill builds that page from a few calls and leaves the deep dive to ufc-fight-preview.

## Before you start
- Tools come from the FighterAPI MCP server. Cards change late (injuries, weight misses); always call, never recall.
- Ratings are our Elo from UFC results alone, not a ranking.

## Default path
1. **Find the card.** `get_schedule()` (2 cr) for upcoming events, or `list_events(season)` (1 cr) for a past one.
2. **The bouts.** `get_event(event_id)` (2 cr): every bout in card order with weight class and both fighters.
3. **Prices for the whole card.** `get_odds(event_id)` (10 cr for a card): opening and closing moneylines by book. Convert to no-margin probability per bout (remove the margin proportionally across the two sides of one book, then average books).
4. **Ratings.** `get_ratings(limit=200)` (2 cr), or one call per weight class on the card with `weight_class`: Elo for active fighters (default is only the top 25). Expected win probability from the gap: 1 / (1 + 10^(-gap/400)).
5. **Records.** `get_fighter(fighter_id)` (5 cr each) only for the main card, to keep the cost down; prelim records come from `get_event` when present.

## Output template
```
<Event>, <date>, <venue>
Bout (weight)            | Records       | Elo (exp. win)   | Market no-margin | Gap
<A> vs <B> (<class>)     | <w-l> / <w-l> | <a> / <b> (<p%>) | <q%> / <r%>      | <Elo minus market, pts>
...
Closest by market: <bouts>. Biggest rating vs market gaps (information only): <bouts, gap, n fights behind each rating>
Data: get_event, get_odds, get_ratings, get_fighter | prices captured <time>
```

## When there's no card

If no card is scheduled in the window asked about, preview the next card on `get_schedule`, or the most recent completed card with results if the user wanted a recap, and say which in the first line.

## Rules
- Information only: no picks, leans, parlays, stakes, payouts or sportsbook links.
- Show how many UFC fights each Elo rests on; a fighter with fewer than 5 UFC fights has a weak rating, so say so next to the gap.
- Odds exist from June 2020 on; older cards have none.
- A late change: if a bout in `get_event` has no price, say the line is not posted rather than guessing.
- Complete before writing: every step in the default path is called for both sides before the preview is written. If a call fails or returns nothing, say which section is missing rather than writing around it.
- Sequences (last 5, recent form, a run of results) are quoted in the order the tool returns them, with dates; never retell them from memory. Lists in the answer must match the tool rows.
- Out of credits: if a call is refused for credits, pass on the API's message as it comes (it says when free credits refill and how to add more), and stop; don't retry or switch tools to get around it.