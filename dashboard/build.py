"""Builds dashboard/index.html: aggregates the data to date x channel x category and inlines it in a
single self-contained page (no external requests). Run: python dashboard/build.py"""
import json
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parent.parent
raw = pd.read_csv(ROOT / "data/raw/retail_store_sales.csv", parse_dates=["Transaction Date"])
cl = pd.read_csv(ROOT / "data/clean/retail_store_sales_clean.csv", parse_dates=["transaction_date"])
d0, d1 = pd.Timestamp("2022-01-01"), raw["Transaction Date"].max()
days = (d1 - d0).days + 1
locs, cats = ["In-store", "Online"], sorted(raw["Category"].unique())
def grid(df, dcol, lcol, ccol, val=None):
    a = np.zeros((days, 2, len(cats)))
    g = df.groupby([(df[dcol] - d0).dt.days, df[lcol].map(locs.index), df[ccol].map(cats.index)])
    s = g.size() if val is None else g[val].sum()
    for (d, l, c), v in s.items(): a[d, l, c] = v
    return a
n = grid(raw, "Transaction Date", "Location", "Category").astype(int).ravel().tolist()
r = grid(cl, "transaction_date", "location", "category", "total_spent").round().astype(int).ravel().tolist()
data = json.dumps({"start": d0.strftime("%Y-%m-%d"), "days": days, "loc": locs, "cat": cats, "n": n, "r": r}, separators=(",", ":"))
html = (Path(__file__).parent / "template.html").read_text().replace("__DATA__", data)
(Path(__file__).parent / "index.html").write_text(html)
(ROOT / "docs").mkdir(exist_ok=True); (ROOT / "docs/index.html").write_text(html)
print(f"index.html {len(html)/1024:.0f} KB, {days} days")
