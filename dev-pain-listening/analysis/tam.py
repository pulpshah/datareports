"""TAM, SAM and SOM for loosethreads as an MCP offering, with ranges (Monte Carlo over stated input ranges).

Usage: <analysis venv>/python -I analysis/tam.py

Every input is a triangular range (low, mode, high) labeled measured (this study), external (cited source) or
assumed (a judgment for Shah to confirm or replace). Writes reports/tam.json. Never a forecast: a sizing under stated
assumptions, which change when the assumptions change.
"""

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
N = 200_000
rng = np.random.default_rng(20261023)

INPUTS = {
    # name: (low, mode, high, kind, source)
    "developers_worldwide": (40.2e6, 47.2e6, 48.4e6, "external", "IDC 2025 projection 40.2M; SlashData 2025 47.2M; Q3 2025 48.4M (secondary)"),
    "share_using_ai_weekly": (0.51, 0.62, 0.65, "external", "Stack Overflow 2025: 51% of professionals daily; 47.1% daily plus 17.7% weekly of all respondents"),
    "nondev_ai_builders_active": (2e6, 5e6, 10e6, "assumed", "Lovable ~8M users, Bolt 5M+, Replit 40M (mostly free, overlapping); active non-developer builders"),
    "price_per_seat_month": (15, 25, 50, "assumed", "anchored by the measured $20 entry tier; loosethreads as an add-on to AI tool spend"),
    "entrant_share": (0.25, 0.32, 0.40, "assumed", "developers with under about 5 years; Stack Overflow 2025 reports early career (1 to 5 years) as a large group"),
    "web_frontend_share": (0.40, 0.48, 0.55, "assumed", "developers doing web front end or full stack"),
    "paying_or_influencing_share": (0.30, 0.45, 0.60, "assumed", "share who pay for AI tools themselves or choose them"),
    "paying_vibe_builders": (0.8e6, 1.2e6, 1.8e6, "external", "Lovable ~$400M ARR / $30 to $50 a month = 0.67M to 1.1M; Replit 175K paying (Sacra); Bolt ~0.1M"),
    "high_end_share_of_paying_vibe": (0.30, 0.45, 0.60, "assumed", "ship real products, pay for several tools, talk architecture or debt"),
    "reachable_share": (0.50, 0.60, 0.70, "assumed", "English-first, web-first markets reachable at launch"),
    "som_penetration_3yr": (0.005, 0.015, 0.03, "assumed", "share of SAM paying within 3 years, typical early devtools range"),
    "ai_coding_spend_2026_usd": (6e9, 8e9, 11e9, "external", "Cursor >$2B annualized (Bloomberg via TechCrunch); Claude Code $2.5B run rate (Anthropic claim); Lovable ~$0.4B; Replit, Bolt, Copilot and others (Copilot assumed $1.5B to $4B)"),
    # pain pool reference (heavily assumed)
    "incidents_per_month": (1, 2, 4, "assumed", "stated time-loss incidents per active builder per month"),
    "hours_per_incident": (1, 3, 8, "measured", "median 3 hours lost per stated incident (n = 5,435 items; IQR 20 minutes to 48 hours, capped here)"),
    "hourly_value_usd": (25, 45, 75, "assumed", "value of an hour of builder time"),
    "share_addressable": (0.2, 0.3, 0.5, "assumed", "share of that time loss that contracts and gates address (drift, platform breaks, rework)"),
}


def tri(name):
    lo, mo, hi = INPUTS[name][:3]
    return rng.triangular(lo, mo, hi, N)


def q(x):
    return {"p10": float(np.percentile(x, 10)), "median": float(np.median(x)), "p90": float(np.percentile(x, 90))}


def main():
    v = {k: tri(k) for k in INPUTS}
    tam_people = v["developers_worldwide"] * v["share_using_ai_weekly"] + v["nondev_ai_builders_active"]
    annual_price = v["price_per_seat_month"] * 12
    tam = tam_people * annual_price
    entrant_fe = v["developers_worldwide"] * v["entrant_share"] * v["web_frontend_share"] * v["paying_or_influencing_share"]
    high_end_vibe = v["paying_vibe_builders"] * v["high_end_share_of_paying_vibe"]
    sam_people = (entrant_fe + high_end_vibe) * v["reachable_share"]
    sam = sam_people * annual_price
    som_people = sam_people * v["som_penetration_3yr"]
    som = som_people * annual_price
    pain_pool = (tam_people * v["incidents_per_month"] * 12 * v["hours_per_incident"] * v["hourly_value_usd"]
                 * v["share_addressable"])
    out = {
        "draws": N,
        "inputs": {k: {"low": a, "mode": b, "high": c, "kind": d, "source": e} for k, (a, b, c, d, e) in INPUTS.items()},
        "tam_people": q(tam_people), "tam_usd_per_year": q(tam),
        "tam_vs_current_ai_coding_spend": q(tam / v["ai_coding_spend_2026_usd"]),
        "sam_people": q(sam_people), "sam_entrant_fe_people": q(entrant_fe * v["reachable_share"]),
        "sam_high_end_vibe_people": q(high_end_vibe * v["reachable_share"]), "sam_usd_per_year": q(sam),
        "som_paying_seats": q(som_people), "som_usd_per_year": q(som),
        "pain_pool_usd_per_year_reference": q(pain_pool),
    }
    # Which assumptions move SOM most: rank correlation of each input with SOM
    def rank(x):
        return np.argsort(np.argsort(x))
    rs = rank(som)
    out["som_sensitivity_spearman"] = {k: round(float(np.corrcoef(rank(v[k]), rs)[0, 1]), 3) for k in INPUTS}
    (ROOT / "reports" / "tam.json").write_text(json.dumps(out, indent=1))
    fmt = lambda d, s=1e6: {k: round(x / s, 2) for k, x in d.items()}  # noqa: E731
    print("TAM people (M)", fmt(out["tam_people"]), "TAM $B/yr", fmt(out["tam_usd_per_year"], 1e9))
    print("TAM / current AI coding spend", {k: round(x, 2) for k, x in out["tam_vs_current_ai_coding_spend"].items()})
    print("SAM people (M)", fmt(out["sam_people"]), "entrant FE (M)", fmt(out["sam_entrant_fe_people"]),
          "high-end vibe (M)", fmt(out["sam_high_end_vibe_people"]), "SAM $M/yr", fmt(out["sam_usd_per_year"]))
    print("SOM seats (K)", fmt(out["som_paying_seats"], 1e3), "SOM $M/yr", fmt(out["som_usd_per_year"]))
    print("pain pool $B/yr (reference)", fmt(out["pain_pool_usd_per_year_reference"], 1e9))
    print("SOM sensitivity", dict(sorted(out["som_sensitivity_spearman"].items(), key=lambda kv: -abs(kv[1]))[:6]))


if __name__ == "__main__":
    main()
