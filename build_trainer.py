"""Build a single-file KOSPI200 futures training app from the minute-bar CSV.

Usage:  python build_trainer.py
Input:  minute_bars_rows.csv  (same folder)
Output: kospi200_trainer.html (self-contained, double-click to run)
"""
import csv
import json
import os
from collections import defaultdict
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(HERE, "minute_bars_rows.csv")
TPL_PATH = os.path.join(HERE, "trainer_template.html")
OUT_PATH = os.path.join(HERE, "kospi200_trainer.html")


def main():
    rows = list(csv.DictReader(open(CSV_PATH, encoding="utf-8-sig")))
    by_day = defaultdict(list)
    for r in rows:
        by_day[r["trading_date"]].append(r)

    dates, days = [], []
    for date in sorted(by_day):
        rs = sorted(by_day[date], key=lambda r: r["bar_time"])
        base = datetime.fromisoformat(rs[0]["bar_time"])
        bars = []
        for r in rs:
            t = datetime.fromisoformat(r["bar_time"])
            minute = int((t - base).total_seconds() // 60)
            bars.append([
                minute,
                round(float(r["open"]), 2),
                round(float(r["high"]), 2),
                round(float(r["low"]), 2),
                round(float(r["close"]), 2),
                int(float(r["volume"] or 0)),
            ])
        dates.append(date)
        days.append(bars)

    payload = json.dumps({"dates": dates, "days": days}, separators=(",", ":"))
    tpl = open(TPL_PATH, encoding="utf-8").read()
    if "__DATA__" not in tpl:
        raise SystemExit("template missing __DATA__ placeholder")
    html = tpl.replace("__DATA__", payload, 1)
    open(OUT_PATH, "w", encoding="utf-8").write(html)

    total = sum(len(d) for d in days)
    print(f"days={len(days)} bars={total}")
    print(f"wrote {OUT_PATH} ({os.path.getsize(OUT_PATH) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
