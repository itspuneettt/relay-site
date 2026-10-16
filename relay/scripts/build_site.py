#!/usr/bin/env python3
"""Build dashboard.json for the Relay site from a book CSV, a brief and the plays.

  python3 relay/scripts/build_site.py relay/assets/sample-book.csv \
      --brief relay/brief.txt --plays relay/plays.json \
      --title "Puneet's inherited book" [--metrics "account health"] [--dummy]

Writes dashboard.json at the site root: every account with its record, notes,
score breakdown and play, so the page can open any row. index.html reads it,
together with episodes.json, which the Relay episode GitHub Action maintains.
"""
import argparse, datetime, io, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import relay_score as R

PEN_LABEL = {"stale next step": "Stale next step", "usage": "Usage",
             "tickets": "Tickets or support sentiment", "service failures": "Service failures"}

def money(k):
    return "$%.2fM" % (k / 1000) if k >= 1000 else "$%dK" % k

def split(s, sep):
    return [p.strip() for p in (s or "").split(sep) if p.strip()]

def ordinal(n):
    return "%d%s" % (n, "th" if 11 <= n % 100 <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th"))

def main():
    p = argparse.ArgumentParser()
    p.add_argument("csv")
    p.add_argument("--brief", default="relay/brief.txt")
    p.add_argument("--plays", default="relay/plays.json")
    p.add_argument("--title", default="Inherited book")
    p.add_argument("--metrics", default="")
    p.add_argument("--dummy", action="store_true", help="the book is a sample")
    p.add_argument("--out", default="dashboard.json")
    a = p.parse_args()

    picked = [m.strip().lower() for m in a.metrics.split(",") if m.strip()]
    book, (wr, ws, wh) = R.load(a.csv, picked)
    pct = lambda v: round(v / 3 * 100)
    weighting = ("Weighted for " + ", ".join(picked) if picked else "Even weighting") + \
                ". Renewal %d, spend %d, health %d." % (pct(wr), pct(ws), pct(wh))
    brief = io.open(a.brief, encoding="utf-8").read().strip() if os.path.exists(a.brief) else ""
    plays = json.load(io.open(a.plays, encoding="utf-8")) if os.path.exists(a.plays) else {}

    n = len(book)
    by_arr = sorted(book, key=lambda x: x["arr"])
    rows = []
    for i, x in enumerate(book, 1):
        r = x["row"]
        rank_arr = n - by_arr.index(x)  # 1 = largest
        pens = [{"label": PEN_LABEL.get(k, k), "cost": v} for k, v in x["penalties"].items() if v]
        trust = x["trust"]
        usage = "falling" if x["penalties"].get("usage") == 25 else ("flat" if x["penalties"].get("usage") == 10 else "growing")
        why = {
            "renewal": "%d days to renewal on a 180-day runway, so %d of 100." % (x["days"], x["renewal"])
                       if x["days"] < 180 else "Six months or more to renewal, so timing is not the problem: 100.",
            "spend": "%s is the %s largest contract of %d in this book, so %d of 100." % (money(x["arr"]), ordinal(rank_arr), n, x["spend"]),
            "health": "Starts at 100" + ("" if not pens else ", minus " + ", ".join("%d for %s" % (q["cost"], q["label"].lower()) for q in pens)) +
                      ". Trust is %s and usage is %s. Health %d." % (trust, usage, x["health"]),
        }
        play = plays.get(x["name"]) or {}
        rows.append({
            "rank": i, "score": x["score"], "band": R.band(x["score"]), "name": x["name"],
            "arr": money(x["arr"]), "arr_k": x["arr"], "days": x["days"],
            "renewal": x["renewal"], "spend": x["spend"], "health": x["health"],
            "category": x["category"], "trust": trust, "why": why, "penalties": pens,
            "record": {
                "Industry": r.get("Industry", ""), "Headquarters": r.get("Headquarters", ""),
                "Size": r.get("Employees", ""), "Products in use": r.get("Products in use", ""),
                "Contract value": money(x["arr"]) + " ARR", "Renewal": "%d days" % x["days"],
                "Stage": r.get("Stage (Salesforce)", ""), "Open opportunities": r.get("Open opportunities", ""),
                "Adoption (Looker)": r.get("Adoption (Looker)", ""),
            },
            "notes": split(r.get("Rep notes (Salesforce)", ""), "|"),
            "risks": split(r.get("Risk signals", ""), " / "),
            "champion": r.get("Champion", ""), "stakeholder": r.get("Key stakeholder", ""),
            "missing": r.get("Missing relationship", ""),
            "play": play if play else None,
        })

    doc = {
        "title": a.title, "generated": datetime.date.today().isoformat(),
        "accounts": n, "total": money(sum(x["arr"] for x in book)),
        "weighting": weighting, "weights": {"renewal": pct(wr), "spend": pct(ws), "health": pct(wh)},
        "dummy": a.dummy, "under40": sum(1 for x in book if x["score"] < 40),
        "tiles": [{"category": c, "total": money(sum(x["arr"] for x in book if x["category"] == c)),
                   "count": sum(1 for x in book if x["category"] == c)}
                  for c in ("Run now", "Protect", "Expand", "Watch")],
        "rows": rows, "brief": brief,
    }
    io.open(a.out, "w", encoding="utf-8").write(json.dumps(doc, indent=1, ensure_ascii=False))
    print("%s. %d accounts, %s. %s %d under forty." % (a.title, n, doc["total"], weighting, doc["under40"]))
    for x in book[:5]:
        print("  %-26s %3d  (renewal %d, spend %d, health %d)  %s" %
              (x["name"][:26], x["score"], x["renewal"], x["spend"], x["health"], x["category"]))
    missing = [x["name"] for x in book if x["name"] not in plays]
    if missing:
        print("No play written for: " + ", ".join(missing))
    print("Wrote %s" % a.out)

if __name__ == "__main__":
    sys.exit(main())
