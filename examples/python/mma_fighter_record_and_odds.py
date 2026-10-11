#!/usr/bin/env python3
"""MMA fighter record, recent fights against the closing line, and sportsbook odds for the latest fight. Usage: python3 mma_fighter_record_and_odds.py [name]. Costs 16 credits (search_fighters 1 + get_fighter 5 + get_fighter_fights 5 + get_odds 5)."""
import json
import os
import sys
import urllib.error
import urllib.request
import argparse

BRAND = "FighterAPI"
KEY_ENV = "FIGHTERAPI_API_KEY"
BASE_URL = "https://mcp.fighterapi.com/v1"
SIGNUP_URL = "https://fighterapi.com/signup"
LAST_REMAINING = None


class ApiError(Exception):
    pass


def require_key():
    key = os.environ.get(KEY_ENV, "").strip()
    if not key:
        sys.exit(
            f"Set {KEY_ENV} first:\n"
            f"  export {KEY_ENV}=your_key\n"
            f"Get a free key (500 credits every month, no card): {SIGNUP_URL}"
        )
    return key


def call(key, tool, args=None):
    """POST /v1/<tool> with a JSON body and return the parsed response."""
    global LAST_REMAINING
    req = urllib.request.Request(
        f"{BASE_URL}/{tool}",
        data=json.dumps(args or {}).encode(),
        headers={
            "Content-Type": "application/json",
            "x-api-key": key,
            "User-Agent": "fighterapi.com-examples/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            LAST_REMAINING = resp.headers.get("X-Credits-Remaining", LAST_REMAINING)
            return json.load(resp)
    except urllib.error.HTTPError as err:
        raise ApiError(describe(err, tool)) from None
    except urllib.error.URLError as err:
        raise ApiError(f"Network error calling {tool}: {err.reason}") from None


def describe(err, tool):
    try:
        body = json.loads(err.read().decode() or "{}")
    except ValueError:
        body = {}
    message = body.get("message") or body.get("error") or err.reason
    if err.code == 401:
        return f"401 unauthorized. Check {KEY_ENV}. {message}"
    if err.code == 402:
        upgrade = body.get("upgrade_url") or SIGNUP_URL
        return f"402 out of credits. {message} Upgrade or wait for the monthly reset: {upgrade}"
    return f"HTTP {err.code} from {tool}: {message}"


def fmt(value, digits=None):
    if value is None:
        return "-"
    if digits is not None and isinstance(value, (int, float)):
        return f"{value:.{digits}f}"
    return str(value)


def pct(value, digits=1):
    return "-" if value is None else f"{value * 100:.{digits}f}%"


def table(headers, rows):
    rows = [["-" if c is None else str(c) for c in r] for r in rows]
    widths = [max([len(h)] + [len(r[i]) for r in rows]) for i, h in enumerate(headers)]
    line = lambda cells: "  ".join(c.ljust(w) for c, w in zip(cells, widths)).rstrip()
    print(line(headers))
    print("  ".join("-" * w for w in widths))
    for r in rows:
        print(line(r))


def finish():
    if LAST_REMAINING is not None:
        print(f"\nCredits remaining: {LAST_REMAINING}")

def main():
    ap = argparse.ArgumentParser(description="Fighter record, form against the closing line, and fight odds.")
    ap.add_argument("name", nargs="?", default="topuria", help="name or nickname (default: topuria)")
    ap.add_argument("--fights", type=int, default=5, help="recent fights to list")
    args = ap.parse_args()
    key = require_key()

    found = call(key, "search_fighters", {"query": args.name, "limit": 1}).get("fighters") or []
    if not found:
        sys.exit(f"No fighter found for {args.name!r}.")
    fid = found[0]["fighter_id"]

    prof = call(key, "get_fighter", {"fighter_id": fid})
    f = prof.get("fighter") or {}
    rec = prof.get("ufc_record") or prof.get("record") or {}
    rates = prof.get("career_rates") or {}
    rating = prof.get("rating") or {}
    print(f"{f.get('name')} ({f.get('nickname')}), {f.get('weight_class')}, {f.get('country')}")
    print(f"UFC record {rec.get('wins')}-{rec.get('losses')}-{rec.get('draws')} "
          f"(KO {rec.get('wins_ko')}, SUB {rec.get('wins_sub')}, DEC {rec.get('wins_dec')})")
    print(f"Elo {rating.get('current')} (peak {rating.get('peak')}), reach {fmt(f.get('reach_in'))} in, "
          f"{fmt(rates.get('sig_landed_per_15'), 1)} sig strikes landed per 15 min, "
          f"striking accuracy {pct(rates.get('sig_accuracy'))}, takedown defense {pct(rates.get('td_defense'))}")

    hist = call(key, "get_fighter_fights", {"fighter_id": fid, "limit": args.fights})
    fights = hist.get("fights") or []
    print("\nRecent fights")
    table(["Date", "Opponent", "Result", "Method", "Rd", "Elo after", "Closing line"],
          [[x.get("event_date"),
            x.get("fighter_b_name") if x.get("fighter_a") == fid else x.get("fighter_a_name"),
            x.get("result"), x.get("method_display"), x.get("end_round"), x.get("rating_after"),
            fmt(x.get("median_closing_line"))] for x in fights])

    if not fights:
        finish()
        return
    bout_id = fights[0]["bout_id"]
    odds = (call(key, "get_odds", {"bout_id": bout_id}).get("bouts") or [{}])[0]
    print(f"\nSportsbook moneylines, {odds.get('fighter_a_name')} (A) v {odds.get('fighter_b_name')} (B), "
          f"{odds.get('event_name')}")
    books = odds.get("books") or []
    if books:
        table(["Book", "A open", "A close", "B open", "B close", "A close prob"],
              [[b.get("provider"), fmt(b.get("a_open")), fmt(b.get("a_close")), fmt(b.get("b_open")),
                fmt(b.get("b_close")), pct(b.get("a_close_prob"))] for b in books])
    else:
        print("No sportsbook lines stored for this fight.")
    finish()


if __name__ == "__main__":
    try:
        main()
    except ApiError as err:
        sys.exit(f"Error: {err}")
