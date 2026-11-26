---
name: ufc-card-preview
description: "Use when the user wants a whole UFC card at a glance rather than one fight: 'preview UFC 325', 'break down this weekend's card', 'who's favoured on the main card', 'which fights on Saturday are closest', 'give me the card with records and ratings', 'what's the main event and co-main look like'. Lists every bout with both fighters' records, our Elo, the market's no-margin probability and how close each fight is, then flags the biggest gaps between rating and market as information. Never says who to bet on. Not for one fight in depth (see ufc-fight-preview), one fighter's history (see ufc-fighter-profile) or how fighters finish (see ufc-fighter-profile)."
metadata:
  version: 2.2.0
  author: SportsDataHQ
---

# UFC card preview

A card is ten to fourteen fights; most people want the whole thing on one page before going deep on two or three. This skill builds that page from a handful of calls, ranks the bouts by how close they are, and leaves the deep dive to ufc-fight-preview.

## Before you start
- Tools come from the FighterAPI MCP server. Cards change late (injuries, weight misses, replacements); always call, never recall a fight or a price.
- Ratings are our Elo from UFC results alone, not a ranking. They do not see layoffs, age, weight cuts, short notice or style.
- Fighter ids come from the card itself (`fighter_a`, `fighter_b`), never from memory. Bouts sort by `card_segment`, then `match_number` (ties happen; keep both).
- Prices are American odds. The market numbers here are information about the market, never a pick.

## Default path (about 36 credits for a card with a main event and co-main deep dive)
1. **Find the card.** `get_schedule(days)` (2 cr) for upcoming events (default 30 days, max 180), or `list_events(season)` (1 cr) for a past one. Note `event_id`, date, venue.
2. **The bouts.** `get_event(event_id)` (2 cr): every posted bout with weight class, scheduled rounds, title flag and both fighters. Count the bouts. Under 10 means the card is still being built; say so.
3. **Prices for the whole card.** `get_odds(event_id)` (10 cr): opening, closing and current moneyline per book, plus `total_rounds` where posted. Do not substitute the lines inside `get_schedule`: they carry no opening price, so movement cannot be read from them. Use `get_odds(bout_id)` (5 cr) only for one bout.
4. **Ratings.** `get_ratings(weight_class, active_since: <last year>, limit: 200)` (2 cr), one call per weight class on the card. The default returns only the top 25, and a card-wide list cuts off at 200, so a fighter missing from it is not yet unrated. Call the weight class before saying "unrated"; only a fighter absent from the class list (debut, or no fight since `active_since`) is unrated: say that.
5. **Records and context, main event and co-main.** `get_fighter(fighter_id)` (5 cr each, 4 fighters = 20 cr): UFC record by method, career rates per 15 minutes, reach, age, stance, rating, last five fights with dates. Add more fighters only when asked; prelim records are not worth 5 cr each by default.
6. **Optional.** `get_line_movement(bout_id)` (10 cr) for one bout whose price moved a lot.

## Method
- **American to implied:** negative a: |a| / (|a| + 100); positive a: 100 / (a + 100).
- **No-margin probability per book:** pA / (pA + pB) using that book's two prices, then average the books. Report books behind it and the low-to-high range across books. Use `current` for an upcoming bout, `close` for a finished one.
- **Elo expected win:** 1 / (1 + 10^(-(RA - RB) / 400)). Gap = Elo expected minus market no-margin, in percentage points.
- **Closeness:** c = |market no-margin - 0.5|. Under 0.10 is a toss-up tier (40 to 60%), 0.10 to 0.20 a clear favourite, over 0.20 lopsided. Rank the card by c, smallest first.
- **Layoff:** days from the fighter's last fight date (last of `recent_fights`) to the event date. Flag over 365 days (long layoff) and under 60 days (quick turnaround). Age from `date_of_birth`; mention 36 and over.
- **Durability and finishing:** KO/TKO losses in the last three fights (two or more is a warning), finish rate = (wins by KO/TKO + submission) / wins, `sig_defense` and `sig_absorbed_per_15` against the opponent's `sig_landed_per_15`. Takedown threat is `td_per_15` and `control_share` against the other side's `td_defense`.
- **Frame:** reach and height differences of 3 inches or more, stance mismatches (switch or southpaw vs orthodox), and five-round vs three-round scheduling.
- **Movement (information only):** compare each book's open to current no-margin probability. A shift of 8 points or more on a bout is the cue to check `get_line_movement` and say a replacement, injury or late change may be behind it. Never say which way to lean.
- **Short notice:** a bout that appears in `get_event` with a single book posted, no opening line, or a fighter with no rating is probably a late addition; label it "late change likely" and do not rank it with full confidence.

## Output template
```
<Event>, <date>, <venue, city> | <n> bouts posted | prices captured <time>
Bout (weight, rounds)  | UFC record     | Elo (exp. win)   | Market no-margin (books) | Gap
<A> vs <B> (<class>)   | <w-l> / <w-l>  | <a> / <b> (<p%>) | <q%> / <r%> (<n>)        | <pts>
...
Closest by market: <bouts, in order>. Rating vs market gaps of 8 points or more (information only): <bout, gap, fights behind each rating>
Main event and co-main notes: age, layoff in days, last 3 results with dates, KO losses, reach, key rates per 15
Flags: long layoff, quick turnaround, thin market, no rating, big line move
Data: get_schedule, get_event, get_odds, get_ratings, get_fighter | UFC, <year>
```

## Worked example (live calls, Nov 25, 2026)
`get_schedule` returned UFC Fight Night: Adesanya vs Magomedov, Dec 5, ANB Arena, Riyadh; `get_event` and `get_odds(event_id)` posted seven bouts, so the card was still being built.
- Main event, Middleweight, five rounds. Elo 1614 (19 UFC fights) vs 1581 (7 UFC fights): gap 33, Elo expected win 54.7% for Adesanya. Market no-margin 59.9% over 5 books (range 58.6 to 61.5, opened about 58.5). Gap -5.2 points, under the 8-point flag.
- Context from `get_fighter`: Adesanya, 37, last fought Mar 28, 2026 (KO/TKO loss to Joe Pyfer, round 2), before that a KO/TKO loss Feb 1, 2025 and a submission loss Aug 17, 2024: 252-day layoff, three straight losses with two KO/TKO, reach 80 inches vs 73. Magomedov, 32, 6-1 in the UFC, last fought Jun 27, 2026 (unanimous decision, 161-day gap), sig. strikes landed 83.2 per 15 at 62.8% accuracy but defence only 45.4%.
- Closest by market in the posted bouts: Riley vs Santos (57.2%, 1 book), then the main event (59.9%), then Machado Garry vs Amosov (61.9%, 5 books). Two bouts had one book only, so their closeness is thin.
Verdict wording: "The market is a little higher on Adesanya than our Elo, and his layoff and recent KO losses are the things a rating cannot see." No pick.

## Not enough data
- Fewer than 5 UFC fights behind an Elo: mark the rating weak next to the gap and do not flag a gap on it.
- No rating (debut, or inactive since `active_since`): show "unrated", skip Elo columns, use the market only.
- Fewer than 3 books on a bout: "thin market", show the books count; one book is a single opinion.
- No price posted: say "line not posted" and leave the market columns blank. Odds start June 2020; older cards have none.
- Career rates need minutes: under 30 minutes fought, say the rates are unstable.
- A `get_fighter` call that fails: say which fighter's context is missing.

## When there's no card

If no card is scheduled in the window asked about, preview the next card on `get_schedule` (widen `days` up to 180), or the most recent completed card with results if the user wanted a recap, and say which in the first line. For a recap, show result, method, round and the pre-fight market no-margin probability from the closing prices.

## Rules
- Information only: no picks, leans, parlays, stakes, payouts or sportsbook links. A request for a parlay or a pick is declined once, then answered with the card as information.
- Never name a book. Say "the books" and give the count.
- Show how many UFC fights each Elo rests on.
- A late change: if a bout in `get_event` has no price, say the line is not posted rather than guessing.
- Complete before writing: every step in the default path is called for both sides before the preview is written. If a call fails or returns nothing, say which section is missing rather than writing around it.
- Sequences (last 5, recent form, a run of results) are quoted in the order the tool returns them, with dates; never retell them from memory. Lists in the answer must match the tool rows.
- Rate limit: a "rate limit exceeded" reply is not a credit refusal. Wait a few seconds and retry that call once, one call at a time; if it still fails, name the section that is missing.
- Out of credits: if a call is refused for credits, pass on the API's message as it comes (it says when free credits refill and how to add more), and stop; don't retry or switch tools to get around it.
