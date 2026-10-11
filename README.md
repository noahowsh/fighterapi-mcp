# FighterAPI MCP server

[![Smithery](https://img.shields.io/badge/Smithery-listed-ff5601?style=flat-square)](https://smithery.ai/servers/noahowsh/FighterAPI) [![MCP Registry](https://img.shields.io/badge/MCP%20Registry-listed-0b7285?style=flat-square)](https://registry.modelcontextprotocol.io/v0/servers?search=io.github.noahowsh/fighterapi)

**The fight data API.** Results, judges' scorecards and the full stat sheet for nearly every UFC fight since 2000, round by round, plus PFL (2012 on) and Bellator (2009 to 2024) results, fighters and ratings with the same key. Fighter profiles, career rates, our own ratings and sportsbook moneylines (UFC from June 2020, PFL from April 2023, Bellator from January 2022 to 2024). REST API and MCP server. 500 free credits, no card.

Website: https://fighterapi.com · Docs: https://fighterapi.com/docs · Get a key: https://fighterapi.com/signup

```
You:    "What is Islam Makhachev's significant strike accuracy by round across his UFC fights?"
Claude: [calls get_fighter_fights]

You:    "Show the opening and closing moneyline for every main event this year."
Claude: [calls get_odds]
```

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
- Moneylines and total rounds, no props: UFC opening and closing lines from June 2020 (a median of 5 to 7 books per fight; ESPN's own feed is usually one book since mid-2024), PFL from April 2023 and Bellator from January 2022 to 2024 with fewer books; pre-fight snapshots: ESPN's once a day from October 2026, The Odds API's every hour in the two days before a fight

Coverage by season, read live from the database: https://fighterapi.com/docs

## Pricing

500 free credits on signup, no card. Plans: Starter $19/mo (10,000 credits), Pro $49/mo (30,000), Scale $149/mo (125,000). Wallet top-ups from $5, never expire. https://fighterapi.com/pricing

## Attribution

Fight data from public ESPN data; sportsbook lines from ESPN and The Odds API; round-by-round statistics compiled by UFC Stats (FightMetric). Ratings are ours. Not affiliated with the UFC, PFL, Bellator or any promotion.

## License

MIT for the contents of this repository. Data terms as above.
