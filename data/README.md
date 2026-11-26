# FighterAPI season pack

The last completed season of UFC as CSV, free to use under the [FighterAPI Sample Data Licence](../DATA-LICENSE.md). Use it in anything you build, credit FighterAPI, and don't republish the files themselves.

**Download:** the latest `fighterapi-season-pack.zip` from this repository's [season-pack release](https://github.com/sports-data-hq/fighterapi-mcp/releases/tag/season-pack). `preview/` holds the first 100 rows of a few files.

Seasons: 2025. Season naming: the calendar year. Competitions, by their API id: ufc. No odds, props or play-by-play: those, every earlier season and live data are on the API, free to start at https://fighterapi.com/signup?utm_source=github&utm_medium=pack&utm_campaign=fighterapi-pack.

## Files

| File | Rows |
|---|---|
| `fighterapi-ufc-2025-events.csv` | 52 |
| `fighterapi-ufc-2025-fighters.csv` | 713 |
| `fighterapi-ufc-2025-fights.csv` | 571 |
| `fighterapi-ufc-2025-ratings.csv` | 713 |

## Columns

- **events**: `league`, `season`, `name`, `date`, `venue`, `city`, `country`, `contender_series`, `fights`
- **fighters**: `league`, `season`, `fighter`, `weight_class`, `country`, `fights`, `wins`, `losses`, `draws_no_contests`, `wins_ko_tko`, `wins_submission`, `wins_decision`, `fight_seconds`, `fight_minutes`, `sig_strikes_landed`, `sig_strikes_attempted`, `total_strikes_landed`, `knockdowns`, `takedowns_landed`, `takedowns_attempted`, `submission_attempts`, `control_seconds`, `elo_end_of_season`
- **fights**: `league`, `season`, `event`, `date`, `card_segment`, `match_number`, `weight_class`, `title_fight`, `fighter_a`, `fighter_b`, `winner`, `method`, `end_round`, `end_clock`, `duration_seconds`, `scheduled_rounds`
- **ratings**: `league`, `season`, `rank`, `fighter`, `weight_class`, `elo`, `last_fight`

Credit line for anything you publish: **Data: FighterAPI (fighterapi.com)**
