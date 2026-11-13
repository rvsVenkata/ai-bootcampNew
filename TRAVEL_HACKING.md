# Award flight search with travel-hacking-toolkit

This repo enables the [borski/travel-hacking-toolkit](https://github.com/borski/travel-hacking-toolkit)
Claude Code plugin (`travel-hacker@borski`) via `.claude/settings.json`. When you open this
repo in Claude Code and trust it, you'll be prompted to install the plugin.

Manual install (any Claude Code session):

```
/plugin marketplace add borski/travel-hacking-toolkit
/plugin install travel-hacker@borski
```

## Free sources (no login, no API key)

| Source | What it gives | Endpoint |
|---|---|---|
| Seats.aero | Cached award availability, 27 mileage programs, departures today through +60 days | `https://seats.aero/mcp` |
| Kiwi.com | Cash fares | `https://mcp.kiwi.com` |
| Skiplagged | Cash fares, incl. hidden-city | `https://mcp.skiplagged.com/mcp` |

Also free: the plugin's local skills (transfer partners, trip calculator, award charts).

Optional paid extras (ignore unless needed): Seats.aero Pro for live search and dates beyond
60 days (`SEATS_AERO_API_KEY`); Chase/Amex/Southwest skills need Docker and your own logins.

## Try it

Ask Claude things like:

- "Find business class award seats SFO to Tokyo in December, cheapest miles first"
- "Which bank points transfer to JAL Mileage Bank?"
- "Compare cash vs points for LAX to London in January"

Verified working on 2026-11-13: an anonymous Seats.aero search SFO→NRT/HND in business
returned JAL JL1 at 70,000 miles + $414 (Dec 8) and ANA NH7 via United at 110,000 miles.

## Cloud sessions

The cloud environment's network must allow `seats.aero`, `mcp.skiplagged.com` and
`mcp.kiwi.com`. The personal environment **ai-bootcampNew** already allows them.

Note: availability is cached (check `minutes_old`) and can be phantom. Confirm on the
airline's site before transferring points, since transfers are usually irreversible.
