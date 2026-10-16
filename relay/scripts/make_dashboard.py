#!/usr/bin/env python3
"""Build the Relay dashboard from a book CSV.

  python3 make_dashboard.py ../assets/sample-book.csv --metrics "account health"

Writes a self-contained relay-dashboard.html and prints the ranked book to
stdout so it can be read aloud without opening the file.
"""
import argparse, datetime, html, io, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import relay_score as R

CAT = {"Run now": "#C2573A", "Protect": "#D9A23B", "Expand": "#4E8F6A", "Watch": "#8A867E"}
BAND = {"low": "#C2573A", "mid": "#D9A23B", "high": "#4E8F6A"}

def money(k):
    return "$%.2fM" % (k / 1000) if k >= 1000 else "$%dK" % k

def main():
    p = argparse.ArgumentParser()
    p.add_argument("csv")
    p.add_argument("--metrics", default="", help='comma separated, e.g. "renewal time,account health"')
    p.add_argument("--out", default="relay-dashboard.html")
    p.add_argument("--title", default="Inherited book")
    a = p.parse_args()

    picked = [m.strip().lower() for m in a.metrics.split(",") if m.strip()]
    book, (wr, ws, wh) = R.load(a.csv, picked)
    total = sum(x["arr"] for x in book)
    pct = lambda v: round(v / 3 * 100)
    wtxt = ("Weighted for " + ", ".join(picked) if picked else "Even weighting") + \
           ". Renewal %d, spend %d, health %d." % (pct(wr), pct(ws), pct(wh))

    # ---- what gets read aloud ----
    print("%s. %d accounts, %s. %s" % (a.title, len(book), money(total), wtxt))
    print("%d under forty.\n" % sum(1 for x in book if x["score"] < 40))
    print("%-3s %-26s %5s %6s %6s %6s  %s" % ("#", "ACCOUNT", "SCORE", "RENEW", "SPEND", "HEALTH", "CATEGORY"))
    for i, x in enumerate(book[:12], 1):
        print("%-3d %-26s %5d %6d %6d %6d  %s" % (i, x["name"][:26], x["score"], x["renewal"],
                                                  x["spend"], x["health"], x["category"]))
    if len(book) > 12:
        print("... %d more" % (len(book) - 12))

    # ---- the file ----
    tiles = "".join(
        '<div class="tile"><b style="color:%s">%s</b><span>%s</span></div>' %
        (CAT[c], money(sum(x["arr"] for x in book if x["category"] == c)), c)
        for c in ("Run now", "Protect", "Expand", "Watch"))
    rows = "".join(
        '<tr><td class="rk">%d</td><td class="sc" style="color:%s">%d</td>'
        '<td><b>%s</b><span>%s &middot; renews in %d days</span></td>'
        '<td class="n">%d</td><td class="n">%d</td><td class="n">%d</td>'
        '<td class="ct" style="color:%s">%s</td></tr>' %
        (i, BAND[R.band(x["score"])], x["score"], html.escape(x["name"]),
         money(x["arr"]), x["days"], x["renewal"], x["spend"], x["health"],
         CAT[x["category"]], x["category"])
        for i, x in enumerate(book, 1))
    doc = DOC % {"title": html.escape(a.title), "n": len(book), "total": money(total),
                 "w": html.escape(wtxt), "tiles": tiles, "rows": rows,
                 "stamp": datetime.date.today().isoformat()}
    io.open(a.out, "w", encoding="utf-8").write(doc)
    print("\nWrote %s" % a.out)

DOC = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Relay &middot; %(title)s</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600;700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap">
<style>
*{box-sizing:border-box}
:root{--bg:#FAF9F5;--ink:#141413;--surface:#fff;--line:#E8E5DC;--muted:#5E5D59;--glaze:#F2EFE6;
--d:"Instrument Sans",Arial,sans-serif;--s:"Source Serif 4",Georgia,serif}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--s);font-size:17px}
.wrap{max-width:980px;margin:0 auto;padding:36px 22px 60px}
.mono{font-family:var(--d);font-size:11px;font-weight:600;letter-spacing:.09em;text-transform:uppercase;color:var(--muted)}
h1{font-family:var(--d);font-size:38px;font-weight:600;letter-spacing:-.03em;margin:6px 0 4px}
.sub{font-family:var(--d);font-size:14px;color:var(--muted);margin:0 0 20px}
.tiles{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin-bottom:18px}
@media(max-width:620px){.tiles{grid-template-columns:repeat(2,minmax(0,1fr))}}
.tile{border:1px solid var(--line);border-radius:12px;background:var(--surface);padding:11px 13px}
.tile b{display:block;font-family:var(--d);font-size:20px;font-weight:600;letter-spacing:-.02em}
.tile span{font-family:var(--d);font-size:10px;font-weight:600;letter-spacing:.07em;text-transform:uppercase;color:var(--muted)}
table{width:100%%;border-collapse:collapse;background:var(--surface);border:1px solid var(--line);border-radius:12px;overflow:hidden}
th{font-family:var(--d);font-size:10px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);text-align:left;padding:9px 10px;border-bottom:1px solid var(--line)}
td{padding:9px 10px;border-top:1px solid var(--line);font-family:var(--d);font-size:13.5px;vertical-align:middle}
tr:first-child td{border-top:0}
td.rk{color:#A5A199;font-size:10px;width:30px;text-align:right}
td.sc{font-size:16px;font-weight:600;width:44px;text-align:right;font-variant-numeric:tabular-nums}
td b{display:block;font-size:14px;font-weight:600}
td span{font-size:11.5px;color:var(--muted)}
td.n{width:62px;text-align:right;font-variant-numeric:tabular-nums;color:var(--muted)}
td.ct{width:84px;font-size:9.5px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;text-align:right}
.foot{margin-top:16px;font-family:var(--d);font-size:11.5px;color:var(--muted)}
.dummy{display:inline-block;border:1px solid #C2573A;color:#C2573A;border-radius:999px;padding:1px 9px;font-family:var(--d);font-size:10px;font-weight:600;letter-spacing:.08em;text-transform:uppercase}
</style></head><body><div class="wrap">
<div class="mono">Relay &middot; generated %(stamp)s</div>
<h1>%(title)s</h1>
<p class="sub">%(n)d accounts &middot; %(total)s &middot; %(w)s Higher is better, so the book opens on its weakest accounts.</p>
<div class="tiles">%(tiles)s</div>
<table><tr><th></th><th>Score</th><th>Account</th><th>Renew</th><th>Spend</th><th>Health</th><th></th></tr>
%(rows)s</table>
<p class="foot"><span class="dummy">Check the data</span> Relay scores what it is given. Where the record and the rep notes disagree, trust the notes and verify before the call.</p>
</div></body></html>
"""

if __name__ == "__main__":
    sys.exit(main())
