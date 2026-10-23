"""Money stated in public developer talk: every dollar amount, credit figure, token count and time lost (no model).

Usage: <analysis venv>/python -I analysis/money.py

Scans every pooled item (title plus text) with fixed patterns, classifies each amount by the words around it, and
writes reports/money.json and reports/tables/money_*.csv. Amounts are what people say, not verified spend.
"""

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "collect"))
import sample  # noqa: E402

PER = r"(?:\s?(?:/|per|a|an|each)\s?(mo|month|monthly|yr|year|annual|annually|day|daily|week|weekly|hr|hour|seat|user))?"
USD = re.compile(r"(?<![\w$])\$\s?(\d{1,3}(?:,\d{3})+|\d+)(?:\.(\d{1,2}))?\s?(k|K)?\b" + PER, re.I)
USD_WORD = re.compile(r"\b(\d{1,3}(?:,\d{3})+|\d+)\s?(?:usd|dollars|bucks)\b" + PER, re.I)
CREDITS = re.compile(r"\b(\d{1,3}(?:,\d{3})+|\d+)\s?(k|K)?\s?credits?\b", re.I)
TOKENS = re.compile(r"\b(\d+(?:\.\d+)?)\s?(k|m|million|b|billion)?\s?tokens?\b", re.I)
TIME = re.compile(r"\b(\d+(?:\.\d+)?)\s?(hours?|hrs?|days?|weeks?|minutes?|mins?)\b", re.I)
LOST = re.compile(r"\b(lost|wast\w*|spent|spend|burn\w*|took|takes|stuck|waiting|debug\w*|fixing|blocked)\b", re.I)
PLAN = re.compile(r"\b(pro\+|pro plus|max|ultra|plus|pro|team|business|enterprise|premium)\b", re.I)
OVERAGE = re.compile(r"\b(overage|bill(?:ed)?|charged|invoice|usage[- ]based|extra|on[- ]demand|api cost|api bill|spent)\b", re.I)
SUB = re.compile(r"\b(plan|subscription|subscribe|tier|seat|per month|a month|/mo|monthly)\b", re.I)
SALARY = re.compile(r"\b(salary|salaries|comp|tc|raise|hourly rate|per hour rate|freelanc\w*|client paid|charge clients|revenue|mrr|arr|valuation|funding|raised|making|makes|earn\w*|profit|sales|income)\b", re.I)  # earn/making added after the Oct 23 precision check


def num(s, k=None):
    v = float(s.replace(",", ""))
    return v * 1000 if k else v


def window_text(text, start, end, width=80):
    return text[max(0, start - width):min(len(text), end + width)]


def classify_usd(ctx, per):
    if SALARY.search(ctx):
        return "income_or_business"
    p = (per or "").lower()
    if p.startswith(("mo", "month")):
        return "per_month"
    if p.startswith(("yr", "year", "annual")):
        return "per_year"
    if p.startswith(("day", "week", "hr", "hour")):
        return "per_" + ("day" if p.startswith("day") else "week" if p.startswith("week") else "hour")
    if p in ("seat", "user"):
        return "per_seat"
    if OVERAGE.search(ctx):
        return "bill_or_overage"
    if SUB.search(ctx):
        return "plan_price"
    return "one_off_or_unclear"


def main():
    pool = sample.load_pool()
    rows = []
    for r in pool:
        text = (r.get("title") or "") + "\n" + (r.get("text") or "")
        base = {"id": r["id"], "src": r["src"], "community": r["community"], "cluster": sample.cluster_for_match(r)
                if r["src"] != "reddit" else r["cluster"], "window": r["window"], "families": ",".join(r["families"]),
                "score": r.get("score")}
        for m in USD.finditer(text):
            v = num(m.group(1), m.group(3)) + (float("0." + m.group(2)) if m.group(2) else 0)
            if not 0.5 <= v <= 1_000_000:
                continue
            ctx = window_text(text, m.start(), m.end())
            rows.append({**base, "kind": "usd", "value": v, "unit": classify_usd(ctx, m.group(4)),
                         "plan_word": (PLAN.search(ctx).group(1).lower() if PLAN.search(ctx) else None),
                         "context": ctx.replace("\n", " ")[:200]})
        for m in USD_WORD.finditer(text):
            v = num(m.group(1))
            if not 0.5 <= v <= 1_000_000:
                continue
            ctx = window_text(text, m.start(), m.end())
            rows.append({**base, "kind": "usd", "value": v, "unit": classify_usd(ctx, m.group(2)),
                         "plan_word": (PLAN.search(ctx).group(1).lower() if PLAN.search(ctx) else None),
                         "context": ctx.replace("\n", " ")[:200]})
        for m in CREDITS.finditer(text):
            v = num(m.group(1), m.group(2))
            if 1 <= v <= 10_000_000:
                rows.append({**base, "kind": "credits", "value": v, "unit": "credits", "plan_word": None,
                             "context": window_text(text, m.start(), m.end()).replace("\n", " ")[:200]})
        for m in TOKENS.finditer(text):
            mult = {"k": 1e3, "m": 1e6, "million": 1e6, "b": 1e9, "billion": 1e9}.get((m.group(2) or "").lower(), 1)
            v = float(m.group(1)) * mult
            if 1 <= v <= 1e12:
                rows.append({**base, "kind": "tokens", "value": v, "unit": "tokens", "plan_word": None,
                             "context": window_text(text, m.start(), m.end()).replace("\n", " ")[:200]})
        for m in TIME.finditer(text):
            ctx = window_text(text, m.start(), m.end(), 60)
            if not LOST.search(ctx):
                continue
            u = m.group(2).lower()
            hours = float(m.group(1)) * (1 / 60 if u.startswith("min") else 24 if u.startswith("day")
                                         else 168 if u.startswith("week") else 1)
            if 0 < hours <= 2000:
                rows.append({**base, "kind": "time_lost", "value": hours, "unit": "hours", "plan_word": None,
                             "context": ctx.replace("\n", " ")[:200]})
    df = pd.DataFrame(rows)
    out = {"items_scanned": len(pool), "mentions": len(df)}
    tab = ROOT / "reports" / "tables"
    tab.mkdir(parents=True, exist_ok=True)
    df.to_csv(tab / "money_mentions.csv", index=False)
    items_with = df.groupby("kind")["id"].nunique().to_dict()
    out["items_with_mention"] = items_with
    out["share_of_items_with_usd"] = round(items_with.get("usd", 0) / len(pool), 4)

    def desc(v):
        v = pd.Series(v)
        if not len(v):
            return {}
        return {"n": int(len(v)), "median": round(float(v.median()), 2), "q1": round(float(v.quantile(.25)), 2),
                "q3": round(float(v.quantile(.75)), 2), "p90": round(float(v.quantile(.9)), 2), "mean": round(float(v.mean()), 2)}

    usd = df[df["kind"] == "usd"]
    out["usd_by_unit"] = {u: desc(g["value"]) for u, g in usd.groupby("unit")}
    # One value per item and unit (the item's median), so a long post with many prices does not dominate.
    per_item = usd.groupby(["id", "unit", "cluster", "window", "src"])["value"].median().reset_index()
    out["usd_per_item_by_unit"] = {u: desc(g["value"]) for u, g in per_item.groupby("unit")}
    out["per_month_by_cluster"] = {c: desc(g["value"]) for c, g in per_item[per_item["unit"] == "per_month"].groupby("cluster")}
    out["per_month_by_window"] = {w: desc(g["value"]) for w, g in per_item[per_item["unit"] == "per_month"].groupby("window")}
    out["bill_by_window"] = {w: desc(g["value"]) for w, g in per_item[per_item["unit"] == "bill_or_overage"].groupby("window")}
    pm = per_item[per_item["unit"] == "per_month"]["value"]
    bins = [0, 10, 20, 21, 50, 100, 101, 200, 201, 500, 1000, 1e9]
    out["per_month_price_points"] = pm.round().value_counts().head(15).to_dict()
    plans = usd[usd["unit"].isin(["per_month", "plan_price"])].dropna(subset=["plan_word"])
    out["plan_word_median_usd"] = {p: desc(g["value"]) for p, g in plans.groupby("plan_word") if len(g) >= 20}
    out["credits"] = desc(df[df["kind"] == "credits"].groupby("id")["value"].median())
    out["tokens"] = desc(df[df["kind"] == "tokens"].groupby("id")["value"].median())
    tl = df[df["kind"] == "time_lost"].groupby(["id", "cluster", "window"])["value"].max().reset_index()
    out["time_lost_hours_per_item"] = desc(tl["value"])
    out["time_lost_by_cluster"] = {c: desc(g["value"]) for c, g in tl.groupby("cluster")}
    # Share of items stating any money, by cluster and window (denominator: pooled items in that cell)
    pdf = pd.DataFrame([{"id": r["id"], "cluster": sample.cluster_for_match(r) if r["src"] != "reddit" else r["cluster"],
                         "window": r["window"]} for r in pool])
    den = pdf.groupby(["cluster", "window"]).size()
    num_ = usd.drop_duplicates("id").groupby(["cluster", "window"]).size()
    share = (num_ / den).fillna(0).round(4).unstack()
    share.to_csv(tab / "money_usd_share_by_cluster_window.csv")
    out["usd_share_by_cluster_window"] = share.to_dict(orient="index")
    (ROOT / "reports" / "money.json").write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps({k: out[k] for k in ("items_scanned", "mentions", "items_with_mention", "share_of_items_with_usd")}))


if __name__ == "__main__":
    main()
