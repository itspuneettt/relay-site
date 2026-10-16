#!/usr/bin/env python3
"""Build dashboard.json for the Relay site from a book CSV and a brief.

  python3 relay/scripts/build_site.py relay/assets/sample-book.csv \
      --brief relay/brief.txt --title "Puneet's inherited book" \
      --metrics "account health" --dummy

Writes dashboard.json at the site root. index.html reads it, together with
episodes.json, which the Relay episode GitHub Action maintains.
"""
import argparse, datetime, io, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import relay_score as R

def money(k):
    return "$%.2fM" % (k / 1000) if k >= 1000 else "$%dK" % k

def main():
    p = argparse.ArgumentParser()
    p.add_argument("csv")
    p.add_argument("--brief", default="relay/brief.txt")
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
    brief = ""
    if os.path.exists(a.brief):
        brief = io.open(a.brief, encoding="utf-8").read().strip()

    doc = {
        "title": a.title,
        "generated": datetime.date.today().isoformat(),
        "accounts": len(book),
        "total": money(sum(x["arr"] for x in book)),
        "weighting": weighting,
        "dummy": a.dummy,
        "under40": sum(1 for x in book if x["score"] < 40),
        "tiles": [{"category": c, "total": money(sum(x["arr"] for x in book if x["category"] == c))}
                  for c in ("Run now", "Protect", "Expand", "Watch")],
        "rows": [{"rank": i, "score": x["score"], "band": R.band(x["score"]), "name": x["name"],
                  "arr": money(x["arr"]), "days": x["days"], "renewal": x["renewal"],
                  "spend": x["spend"], "health": x["health"], "category": x["category"],
                  "trust": x["trust"]}
                 for i, x in enumerate(book, 1)],
        "brief": brief,
    }
    io.open(a.out, "w", encoding="utf-8").write(json.dumps(doc, indent=2, ensure_ascii=False))
    print("%s. %d accounts, %s. %s %d under forty." % (a.title, len(book), doc["total"], weighting, doc["under40"]))
    for x in book[:5]:
        print("  %-26s %3d  (renewal %d, spend %d, health %d)  %s" %
              (x["name"][:26], x["score"], x["renewal"], x["spend"], x["health"], x["category"]))
    print("Wrote %s" % a.out)

if __name__ == "__main__":
    sys.exit(main())
