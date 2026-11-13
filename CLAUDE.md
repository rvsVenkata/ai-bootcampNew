# CLAUDE.md

AI learning repo. Main use so far: finding award flights (points/miles) with free, no-login tools.

## Award flight search

- The `travel-hacker@borski` plugin ([borski/travel-hacking-toolkit](https://github.com/borski/travel-hacking-toolkit))
  is enabled in `.claude/settings.json`. Setup and examples are in `TRAVEL_HACKING.md`.
- The user wants **free sources with no forced logins**. Don't suggest paid tools or account sign-ins
  unless asked, and say so clearly when a request can't be met for free.
- For quick searches, use `scripts/award_search.py` (stdlib Python, no install):

  ```bash
  # Multi-leg itineraries: searches each leg via hub airports and pairs them by layover
  python3 scripts/award_search.py route --from AUS,DFW,IAH --to HYD,BLR \
      --start 2026-12-01 --end 2027-01-10 --cabin business --seats 3 --card chaseus

  # Any Seats.aero MCP tool directly
  python3 scripts/award_search.py call get_capabilities '{}'
  ```

## Seats.aero MCP (`https://seats.aero/mcp`), anonymous tier

Learned by testing; don't rediscover these:

- **Dates: today through today+60 days only.** Later dates return an error. Searching further out
  needs Seats.aero Pro (`SEATS_AERO_API_KEY`), which costs money: ask first.
- **Nonstop segments only.** A pair with no nonstop returns `ERROR_INDIRECT_ROUTE`. For connections,
  search origin→hub and hub→destination separately (`route` does this). Default hubs:
  DOH, DXB, AUH, IST, LHR, FRA, CDG, AMS, MUC, ZRH.
- `origins` / `destinations` must be **JSON arrays**, not comma strings.
- At most 50 results per call; narrow by hub or date to see more.
- Card filter `transfer_partners`: `chaseus`, `amexus`, `capitalone`, `bilt`, `citius`, `usbank`, `wellsfargo`.
  Chase partners seen in results: aeroplan, united, flyingblue, british, virginatlantic, jetblue.
- `list_routes` needs exactly two of origin / destination / mileage_program, and `limit` ≤ 100.
- Results are cached. Check `minutes_old`. `remaining_seats` is missing for some programs.

## Interpreting results for the user

- Legs from different programs are **separate tickets**, so a missed connection isn't protected.
  Prefer one-program itineraries. Aeroplan prices a whole trip by distance, usually less than the
  sum of its legs.
- Watch fees: BA Avios on American transatlantic flights adds about $1,500 in surcharges.
- Always tell the user to confirm seats on the airline's site before transferring points
  (transfers are irreversible).

## Cloud sessions

The network must allow `seats.aero`, `mcp.kiwi.com`, `mcp.skiplagged.com`. The personal cloud
environment **ai-bootcampNew** already does.

## Git

Keep personal trip details (home airports, dates, balances) out of committed files.
