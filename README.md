# FighterAPI MCP server

[![MCP Registry](https://img.shields.io/badge/MCP%20Registry-listed-0b7285?style=flat-square)](https://registry.modelcontextprotocol.io/v0/servers?search=io.github.noahowsh/fighterapi)

**The fight data API.** Results, judges' scorecards and the full stat sheet for nearly every UFC fight since 2000, round by round, plus PFL (2012 on) and Bellator (2009 to 2024) results, fighters and ratings with the same key. Fighter profiles, career rates, our own ratings and sportsbook moneylines (UFC from June 2020, PFL from April 2023, Bellator from January 2022 to 2024). REST API and MCP server. 500 free credits every month, no card.

Website: https://fighterapi.com?utm_source=github&utm_medium=readme&utm_campaign=fighterapi-mcp · Docs: https://fighterapi.com/docs?utm_source=github&utm_medium=readme&utm_campaign=fighterapi-mcp · Get a key: https://fighterapi.com/signup?utm_source=github&utm_medium=readme&utm_campaign=fighterapi-mcp

```
You:    "What is Islam Makhachev's significant strike accuracy by round across his UFC fights?"
Claude: [calls get_fighter_fights]

You:    "Show the opening and closing moneyline for every main event this year."
Claude: [calls get_odds]
```


## Run it locally (stdio)

Most clients connect to `https://mcp.fighterapi.com/mcp` directly. For a client that launches a local process instead:

```bash
git clone https://github.com/sports-data-hq/fighterapi-mcp.git && cd fighterapi-mcp && npm install
FIGHTERAPI_API_KEY=your_key node index.js
```

```json
{ "mcpServers": { "fighterapi": { "command": "node", "args": ["/path/to/fighterapi-mcp/index.js"], "env": { "FIGHTERAPI_API_KEY": "your_key" } } } }
```

It forwards to the hosted server with your key, so every tool and credit cost is the same.

## Try it now, no key

- **A free season of UFC data:** the last completed season as CSV (games, standings, player season totals and our ratings). [Download the zip](https://github.com/sports-data-hq/fighterapi-mcp/releases/download/season-pack/fighterapi-season-pack.zip) or browse [what's in it](data/README.md).
- **Open it in Colab:** [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sports-data-hq/fighterapi-mcp/blob/main/notebooks/fighterapi-season-pack.ipynb) loads the pack and answers three questions in a minute.
- **Ask Claude without a key:** install the skills below; `season-pack-offline` answers from the pack until you connect.

**With a free key it does far more:** every earlier season, today's games, play-by-play, lineups, odds and player props with their history and movement, and every skill below running on live data. [Get a free key](https://fighterapi.com/signup?utm_source=github&utm_medium=readme&utm_campaign=fighterapi-try-now): 500 credits a month, no card.

## Skills

4 Claude skills for UFC ship in this repo, plus 13 analytics skills for models, backtests, calibration and comparing a model with the market. Every number in an answer comes from a live FighterAPI tool call, and odds are information only: no stakes, no picks.

Claude Code:

```
/plugin marketplace add sports-data-hq/fighterapi-mcp
/plugin install mma-data@fighterapi
/plugin install sports-analytics-core@fighterapi
```

Codex: `codex plugin marketplace add sports-data-hq/fighterapi-mcp`. Any agent that reads skills: `npx skills add sports-data-hq/fighterapi-mcp`.

| Skill | What it does |
|---|---|
| `ufc-card-preview` | A whole card on one page: records, our Elo and the market's probability for every bout |
| `ufc-elo-baseline` | The Elo gap between two fighters as an expected win probability, beside the market as information |
| `ufc-fight-preview` | One-page fight preview: records by method, striking and grappling rates, Elo, opposition and the line |
| `ufc-fighter-profile` | A fighter's record by method, finish rates by method and round, career rates per 15 minutes, recent fights and ratings |

The analytics skills: `backtesting`, `data-pipeline`, `elo-engineering`, `feature-engineering`, `market-vs-model`, `model-building`, `odds-market-analysis`, `prediction-tracker`, `probability-calibration`, `season-pack-offline`, `sports-data-preflight`, `visualization`, `walk-forward-validation`.

Real answers on live data, with the credits each used: [example answers](https://github.com/sports-data-hq/sportsdatahq-skills/tree/main/docs/examples/mma).

All nine sports' skills live in [sports-data-hq/sportsdatahq-skills](https://github.com/sports-data-hq/sportsdatahq-skills). The copies here are synced from there, so please open issues and pull requests there.

## Useful pages

- Docs and every tool: https://fighterapi.com/docs?utm_source=github&utm_medium=readme&utm_campaign=fighterapi-mcp
- Guides: https://fighterapi.com/guides?utm_source=github&utm_medium=readme&utm_campaign=fighterapi-mcp
- UFC odds: https://fighterapi.com/odds?utm_source=github&utm_medium=readme&utm_campaign=fighterapi-mcp
- Data coverage: https://fighterapi.com/data?utm_source=github&utm_medium=readme&utm_campaign=fighterapi-mcp
- Pricing: https://fighterapi.com/pricing?utm_source=github&utm_medium=readme&utm_campaign=fighterapi-mcp

## Python

The official Python client is on PyPI: [fighterapi](https://pypi.org/project/fighterapi/).

```bash
pip install fighterapi
export FIGHTERAPI_API_KEY=sk_live_...
```

```python
from fighterapi import Client

client = Client()

events = client.list_events(status="final", limit=3)["events"]
for e in events:
    print(e["event_id"], e["event_date"], e["name"])
```

Typed errors for a bad key, no credits left, not found and rate limits, automatic retries, and `to_dataframe` for pandas.

## Quick start

This is a hosted (remote) MCP server over Streamable HTTP. There is nothing to install.

**Claude Code**

```bash
claude mcp add --transport http fighterapi "https://mcp.fighterapi.com/mcp?key=YOUR_API_KEY"
```

**Claude Desktop, Cursor and other clients**

```json
{
  "mcpServers": {
    "fighterapi": {
      "url": "https://mcp.fighterapi.com/mcp?key=YOUR_API_KEY"
    }
  }
}
```

The key can also be sent as an `x-api-key` header or `Authorization: Bearer`. Connecting and listing tools works without a key; calling a tool needs one.

**REST**

```bash
curl -X POST https://mcp.fighterapi.com/v1/list_events -H "x-api-key: YOUR_API_KEY"
```

Every tool is `POST /v1/{tool}` with a JSON body.

## Examples

Runnable Python (standard library only) and Node 18+ (no dependencies) examples live in [`examples/`](examples/):

- [`examples/python/quickstart.py`](examples/python/quickstart.py) and [`examples/node/quickstart.mjs`](examples/node/quickstart.mjs): schedule plus a headline call.
- [`examples/python/mma_fighter_record_and_odds.py`](examples/python/mma_fighter_record_and_odds.py): A fighter profile (UFC record by method, Elo, career strike and takedown rates), their recent fights with the median closing line, and every sportsbook's open and close moneyline for their latest fight.

```bash
export FIGHTERAPI_API_KEY=your_key
python3 examples/python/quickstart.py
node examples/node/quickstart.mjs
```

See [`examples/README.md`](examples/README.md) for details. Get a free key (500 credits a month, no card) at https://fighterapi.com/signup?utm_source=github&utm_medium=readme&utm_campaign=fighterapi-mcp.

## Use it in

- **Claude, ChatGPT, Cursor, VS Code, Gemini CLI, Grok, Perplexity, Le Chat:** add `https://mcp.fighterapi.com/mcp` as a remote MCP server. Step-by-step for each: https://fighterapi.com/mcp?utm_source=github&utm_medium=readme&utm_campaign=fighterapi-mcp
- **Gemini CLI:** `gemini extensions install https://github.com/sports-data-hq/fighterapi-mcp`
- **Cursor:** the [SportsDataHQ plugins for Cursor](https://github.com/sports-data-hq/sportsdatahq-cursor-plugins)
- **Google Sheets:** `=SDHQ("fighterapi","list_events")` fills a live table: https://sportsdatahq.com/sheets?utm_source=github&utm_medium=readme&utm_campaign=fighterapi-mcp
- **REST:** `POST https://mcp.fighterapi.com/v1/<tool>` with an `x-api-key` header: https://fighterapi.com/docs?utm_source=github&utm_medium=readme&utm_campaign=fighterapi-mcp

## Tools (11)

| Tool | What it returns |
|------|-----------------|
| `list_events` | Cards by year and status, with the main event |
| `search_fighters` | Find fighters by name or nickname |
| `get_event` | A card's fights with results, method, round, time and judges' scores |
| `get_schedule` | Upcoming fights with current moneylines where a book has posted one |
| `get_ratings` | Our fighter ratings (Elo from every UFC result since 2000) |
| `get_fight` | One fight: result, full stat sheets, round-by-round lines, ratings and odds |
| `get_fighter` | Profile, UFC record by method, career rates, rating and recent fights |
| `get_fighter_fights` | A fighter's full UFC history with stats, ratings and closing lines |
| `get_leaders` | Career leaderboards from every fight's stat sheet |
| `get_odds` | Opening, closing and current moneylines by sportsbook for a fight (5) or a card (10) |
| `get_line_movement` | Snapshots of each posted line before a fight |

Leagues: mma (default, UFC), pfl, bellator (pass `league` to any tool).

## Data

- Every UFC card since 2000 with results, method, round, time and judges' scorecards; the full stat sheet, round by round, for nearly every card
- PFL (2012 on) and Bellator (2009 to 2024) results, fighters and ratings; no stat sheets exist for those promotions in recent years
- Fighter profiles with reach, stance and gym, career rates by method, and our Elo ratings from every UFC result since 2000
- Moneylines and total rounds, no props: UFC opening and closing lines from June 2020 (a median of 5 to 7 books per fight; usually one book since mid-2024), PFL from April 2023 and Bellator from January 2022 to 2024 with fewer books; pre-fight snapshots: once a day from October 2026, and every hour in the two days before a fight

Coverage by season, read live from the database: https://fighterapi.com/docs?utm_source=github&utm_medium=readme&utm_campaign=fighterapi-mcp

## Pricing

500 free credits every month, no card. Plans: Starter $19/mo (10,000 credits), Pro $49/mo (30,000), Scale $149/mo (125,000), Business $299/mo (300,000). Wallet top-ups from $5, never expire. https://fighterapi.com/pricing?utm_source=github&utm_medium=readme&utm_campaign=fighterapi-mcp

## Attribution

Ratings are ours. Not affiliated with the UFC, PFL, Bellator or any promotion.

## License

MIT for the contents of this repository. Data terms as above.

## Use with Codex

The SportsDataHQ skills marketplace also works in Codex (it reads `.agents/plugins/marketplace.json`):

```bash
codex plugin marketplace add sports-data-hq/sportsdatahq-skills
```

Install `mma-data`, which bundles the MMA skills and the FighterAPI MCP server.

## Use with Gemini CLI

```bash
export FIGHTERAPI_API_KEY=your_key
gemini extensions install https://github.com/sports-data-hq/fighterapi-mcp
```

The extension adds the FighterAPI MCP server (https://mcp.fighterapi.com/mcp) and sends the key in the `x-api-key` header. Get a free key (500 credits a month) at https://fighterapi.com/signup?utm_source=github&utm_medium=readme&utm_campaign=fighterapi-mcp.
