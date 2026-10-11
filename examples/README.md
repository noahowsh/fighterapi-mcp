# FighterAPI examples

Runnable examples for the [FighterAPI API](https://fighterapi.com). Python uses only the standard library (`urllib` and `json`). Node uses the built-in `fetch` (Node 18 or newer). No packages to install.

UFC, PFL and Bellator fight data API. Every tool is a REST call: `POST https://mcp.fighterapi.com/v1/<tool_name>` with a JSON body and an `x-api-key` header. The same tools are available over MCP at `https://mcp.fighterapi.com/mcp`.

## Get a key

1. Sign up at https://fighterapi.com/signup. The free plan gives 500 credits every month, no card.
2. Copy a key from https://fighterapi.com/dashboard/keys.
3. Export it. The scripts read it from the environment and never print it.

```bash
export FIGHTERAPI_API_KEY=your_key
```

## What is here

| File | What it does | Tools | Credits |
| --- | --- | --- | --- |
| `python/quickstart.py` | Upcoming schedule plus one headline call, printed as small tables | `get_schedule`, `get_ratings` | about 4 |
| `python/mma_fighter_record_and_odds.py` | A fighter profile (UFC record by method, Elo, career strike and takedown rates), their recent fights with the median closing line, and every sportsbook's open and close moneyline for their latest fight. Defaults to Ilia Topuria. | `search_fighters`, `get_fighter`, `get_fighter_fights`, `get_odds` | about 16 |
| `node/quickstart.mjs` | Same as the Python quickstart, for Node | `get_schedule`, `get_ratings` | about 4 |

## Run

```bash
python3 python/quickstart.py
python3 python/mma_fighter_record_and_odds.py
node node/quickstart.mjs
```

The use-case script takes optional arguments. For example:

```bash
python3 mma_fighter_record_and_odds.py "El Matador"
```

Run any script with `--help` (Python) to see its options.

## Credits and errors

- Every call costs credits, priced per tool. The cost is shown next to each call in the script output, and the response header `X-Credits-Remaining` is printed at the end.
- To see what a call would cost without running it, send `"estimate_only": true` on the tools that accept it (see the tool schema).
- When you are out of credits the API returns HTTP 402 with `{"error": "insufficient_credits", "message": "...", "upgrade_url": "..."}`. The scripts print that message and the upgrade link.
- HTTP 401 means the key is missing or wrong. The scripts print a hint to check `FIGHTERAPI_API_KEY`.
- UFC is the default (`mma`). Pass `"league": "pfl"` or `"bellator"` in the request body for those promotions.
- The tool list with input schemas is public: `curl https://mcp.fighterapi.com/v1/tools`.

## More

- Docs and example responses for every tool: https://fighterapi.com/docs
- Full reference in one file: https://fighterapi.com/llms-full.txt
- Free key: https://fighterapi.com/signup
