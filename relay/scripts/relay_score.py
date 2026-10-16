"""Relay scoring. Stdlib only, no installs.

One number per account, 0-100, higher is better.
Three inputs averaged: renewal time, account spend, account health.
Health starts at 100 and loses four named penalties.
"""
import csv, io, re

METRICS = {                      # renewal, spend, health
    "average contract value": (0.5, 1.6, 0.9),
    "renewal time":           (1.8, 0.6, 0.6),
    "account health":         (0.6, 0.6, 1.8),
    "current account spend":  (0.6, 1.8, 0.6),
}

def weights(picked):
    """Average the picked metric rows, normalised so the three still sum to 3."""
    rows = [METRICS[m] for m in picked if m in METRICS]
    if not rows:
        return (1.0, 1.0, 1.0)
    w = [sum(r[i] for r in rows) / len(rows) for i in range(3)]
    s = sum(w)
    return tuple(v * 3 / s for v in w)

def health(row):
    """100 minus stale next step, usage, tickets, service failures."""
    blob = " ".join([row.get("Adoption (Looker)", ""), row.get("Risk signals", ""),
                     row.get("Rep notes (Salesforce)", ""), row.get("Stage (Salesforce)", "")]).lower()
    pen = {}
    pen["stale next step"] = {"low": 25, "medium": 12, "high": 0}.get(row.get("Trust (CRM)", "").strip().lower(), 12)
    if re.search(r"usage (?:is )?down|down \d+%", blob):   pen["usage"] = 25
    elif "flat" in blob:                                    pen["usage"] = 10
    elif re.search(r"up \d+%", blob):                       pen["usage"] = 0
    else:                                                   pen["usage"] = 5
    pen["tickets"]          = 15 if re.search(r"ticket|escalation|sentiment|support", blob) else 0
    pen["service failures"] = 20 if re.search(r"sla|incident|outage|miss(?:es|ed)?\b", blob) else 0
    return max(0, 100 - sum(pen.values())), pen

def category(row, h, days):
    """Prefer the authored column. Only guess when a rep's own export lacks it."""
    given = row.get("Category", "").strip()
    if given:
        return given
    over = re.search(r"(\d+)% of commit", (row.get("Risk signals", "") + " " +
                                            row.get("Adoption (Looker)", "")).lower())
    if days < 60 and h < 70:             return "Run now"
    if h < 70:                           return "Protect"
    if over and int(over.group(1)) > 95: return "Expand"
    if h >= 85 and days > 120:           return "Watch"
    return "Expand" if h >= 85 else "Protect"

def load(path, picked=()):
    """Read a book CSV and return accounts scored and sorted weakest first."""
    wr, ws, wh = weights(picked)
    out = []
    with io.open(path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    arrs = sorted(float(r.get("ARR (USD thousands)", 0) or 0) for r in rows)
    for r in rows:
        arr = float(r.get("ARR (USD thousands)", 0) or 0)
        days = int(float(r.get("Days to renewal", 0) or 0))
        h, pen = health(r)
        # runway tops out at six months: past that, timing is not the problem
        renewal = round(min(days, 180) / 180 * 100)
        # spend is a rank inside this book, so the median account sits at fifty
        spend = (round(sum(1 for x in arrs if x < arr) / (len(arrs) - 1) * 100)
                 if len(arrs) > 1 else 50)
        out.append({
            "name": r.get("Account", "").strip(), "arr": arr, "days": days,
            "renewal": renewal, "spend": spend, "health": h, "penalties": pen,
            "score": round((renewal * wr + spend * ws + h * wh) / 3),
            "category": category(r, h, days), "trust": r.get("Trust (CRM)", "").strip() or "Medium",
            "row": r,
        })
    out.sort(key=lambda a: (a["score"], a["name"]))
    return out, (wr, ws, wh)

def band(score):
    return "low" if score < 40 else ("mid" if score < 70 else "high")
