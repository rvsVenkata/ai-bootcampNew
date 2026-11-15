#!/usr/bin/env python3
"""Free award-flight search via the Seats.aero MCP endpoint (no login, no API key).

Usage:
  # Raw tool call
  python3 scripts/award_search.py call get_capabilities '{}'

  # Connecting itineraries: searches each nonstop leg via hubs, then pairs them
  python3 scripts/award_search.py route --from AUS,DFW,IAH --to HYD,BLR \
      --start 2026-12-01 --end 2027-01-10 --cabin business --seats 3 [--card chaseus]

Anonymous limits: departures today..today+60 days, nonstop segments only, 50 results per call.
"""
import argparse, datetime as dt, json, sys, urllib.request

URL = "https://seats.aero/mcp"
DEFAULT_HUBS = "DOH,DXB,AUH,IST,LHR,FRA,CDG,AMS,MUC,ZRH"


def call(name, args):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                       "params": {"name": name, "arguments": args}}).encode()
    req = urllib.request.Request(URL, body, {"Content-Type": "application/json",
                                             "Accept": "application/json, text/event-stream"})
    res = json.load(urllib.request.urlopen(req, timeout=90))["result"]
    text = "\n".join(c.get("text", "") for c in res["content"])
    if res.get("isError"):
        raise RuntimeError(text)
    return text


def flights(args):
    try:
        text = call("get_flights", args)
    except RuntimeError as e:
        if "INDIRECT_ROUTE" in str(e):  # no tracked nonstop for this pair
            return []
        raise
    return [json.loads(l) for l in text.splitlines() if l.startswith("{")]


def usd(taxes):
    t = taxes.split()
    return float(t[0].lstrip("$").replace(",", "")) if t and t[0].startswith("$") and t[-1] == "USD" else 0.0


def route(a):
    base = dict(start_date=a.start, end_date=a.end, cabin=a.cabin, min_seats=a.seats, max_results=50)
    if a.card:
        base["transfer_partners"] = [a.card]
    org, dst, hubs = a.origins.split(","), a.dests.split(","), a.hubs.split(",")
    leg1, leg2 = [], []
    for h in hubs:
        leg1 += flights(dict(base, origins=org, destinations=[h]))
        leg2 += flights(dict(base, origins=[h], destinations=dst))
    direct = flights(dict(base, origins=org, destinations=dst))
    p = lambda s: dt.datetime.strptime(s, "%Y-%m-%d %H:%M")
    trips = [dict(miles=r["miles_price"], usd=usd(r["taxes"]), legs=[r], lay=None) for r in direct]
    for x in leg1:
        for y in leg2:
            if x["destination"] != y["origin"]:
                continue
            lay = (p(y["departs_at"]) - p(x["arrives_at"])).total_seconds() / 3600  # both local hub time
            if a.min_layover <= lay <= a.max_layover:
                trips.append(dict(miles=x["miles_price"] + y["miles_price"], usd=usd(x["taxes"]) + usd(y["taxes"]),
                                  legs=[x, y], lay=lay))
    trips.sort(key=lambda t: t["miles"])
    seen, n = set(), 0
    for t in trips:
        key = tuple((l["flights"], l["mileage_program"]) for l in t["legs"])
        if key in seen:
            continue
        seen.add(key); n += 1
        path = "-".join([t["legs"][0]["origin"]] + [l["destination"] for l in t["legs"]])
        legs = " -> ".join(f'{l["flights"]} [{l["mileage_program"]} {l["miles_price"]:,}, '
                           f'{l.get("remaining_seats", "?")} seats, {l["minutes_old"] // 60}h old]' for l in t["legs"])
        lay = f'  layover {t["lay"]:.1f}h' if t["lay"] is not None else ""
        other = [l["taxes"] for l in t["legs"] if not l["taxes"].endswith("USD")]
        fees = f'+${t["usd"]:,.0f}' + "".join(f" +{x}" for x in other)
        print(f'{t["miles"]:>8,} mi/person {fees}  {path}  {t["legs"][0]["departs_at"]}  {legs}{lay}')
        if n >= a.top:
            break
    if not trips:
        print("No itineraries found.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("call"); c.add_argument("tool"); c.add_argument("args", nargs="?", default="{}")
    r = sub.add_parser("route")
    r.add_argument("--from", dest="origins", required=True)
    r.add_argument("--to", dest="dests", required=True)
    r.add_argument("--start", required=True); r.add_argument("--end", required=True)
    r.add_argument("--cabin", default="business", choices=["economy", "premium", "business", "first"])
    r.add_argument("--seats", type=int, default=1)
    r.add_argument("--card", help="transfer program filter, e.g. chaseus, amexus, capitalone, bilt, citius")
    r.add_argument("--hubs", default=DEFAULT_HUBS)
    r.add_argument("--min-layover", type=float, default=2); r.add_argument("--max-layover", type=float, default=24)
    r.add_argument("--top", type=int, default=15)
    a = ap.parse_args()
    if a.cmd == "call":
        print(call(a.tool, json.loads(a.args)))
    else:
        route(a)


if __name__ == "__main__":
    sys.exit(main())
