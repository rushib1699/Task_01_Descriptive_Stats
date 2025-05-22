#!/usr/bin/env python3
"""
Features
--------
* Infers numeric vs categorical automatically.
* Understands the three range-encoded columns and expands them:
    * `estimated_audience_size`  →  `estimated_audience_lower`, `estimated_audience_upper`
    * `impressions`              →  `impressions_lower`, `impressions_upper`
    * `spend`                    →  `spend_lower`, `spend_upper`
* Emits a tidy report to **stdout** (optionally JSON via `--json`).

"""


from __future__ import annotations
import argparse, ast, csv, json, math, sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple


# Helpers


def to_number(s: str) -> Any:  
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            return s

def expand_range(val: str, base: str, row_out: Dict[str, Any]):
    """Convert "{'lower_bound': '100', 'upper_bound': '200'}" to two numeric columns."""
    try:
        data = ast.literal_eval(val)
        row_out[f"{base}_lower"] = to_number(data.get("lower_bound", ""))
        row_out[f"{base}_upper"] = to_number(data.get("upper_bound", ""))
    except (ValueError, SyntaxError):
        pass


# Stats containers

class NumStats:
    __slots__ = ("count", "_sum", "_sumsq", "min", "max")
    def __init__(self):
        self.count = 0
        self._sum = 0.0
        self._sumsq = 0.0
        self.min = math.inf
        self.max = -math.inf
    def add(self, x: float):
        self.count += 1
        self._sum += x
        self._sumsq += x * x
        self.min = x if x < self.min else self.min
        self.max = x if x > self.max else self.max

    def mean(self):
        return self._sum / self.count if self.count else math.nan
 
    def stdev(self):
        if self.count < 2:
            return math.nan
        var = (self._sumsq - (self._sum ** 2) / self.count) / (self.count - 1)
        return math.sqrt(var)


# Main


def compute_stats(path: Path) -> Tuple[Dict[str, NumStats], Dict[str, Counter]]:
    numeric: Dict[str, NumStats] = defaultdict(NumStats)
    categorical: Dict[str, Counter] = defaultdict(Counter)

    with path.open(newline="", encoding="utf‑8") as f:
        rows = csv.DictReader(f)
        for raw_row in rows:
            row: Dict[str, Any] = {}
            # First expand the three range columns
            for rng_col in ("estimated_audience_size", "impressions", "spend"):
                if rng_col in raw_row and raw_row[rng_col]:
                    expand_range(raw_row[rng_col], rng_col, row)
            # Copy everything else verbatim
            for k, v in raw_row.items():
                if k in ("estimated_audience_size", "impressions", "spend"):
                    continue  
                row[k] = v

            for col, val in row.items():
                val_conv = to_number(val) if isinstance(val, str) else val
                if isinstance(val_conv, (int, float)):
                    numeric[col].add(float(val_conv))
                else:
                    categorical[col][val_conv] += 1

    return numeric, categorical


def build_report(numeric: Dict[str, NumStats], categorical: Dict[str, Counter]):
    report = {"numeric": {}, "categorical": {}}
    for col, s in numeric.items():
        report["numeric"][col] = {
            "count": s.count,
            "mean": s.mean,
            "stdev": s.stdev,
            "min": s.min,
            "max": s.max,
        }
    for col, counter in categorical.items():
        report["categorical"][col] = {
            "unique": len(counter),
            "top": counter.most_common(1)[0] if counter else None,
        }
    return report


def cli():
    p = argparse.ArgumentParser(description="Compute descriptive stats (pure Python)")
    p.add_argument("csv", type=Path, help="CSV file to analyse")
    p.add_argument("--json", action="store_true", help="Emit full JSON report")
    args = p.parse_args()

    num, cat = compute_stats(args.csv)
    rep = build_report(num, cat)

    if args.json:
        json.dump(rep, sys.stdout, indent=2)
    else:
        print("\nNumeric columns:\n----------------")
        for col, d in rep["numeric"].items():
            print(f"{col:<35} n={d['count']:>6}  mean={d['mean']:.2f}  sd={d['stdev']:.2f}  min={d['min']:.2f}  max={d['max']:.2f}")
        print("\nCategorical columns:\n--------------------")
        for col, d in rep["categorical"].items():
            top_val, top_cnt = d["top"] if d["top"] else (None, 0)
            print(f"{col:<35} unique={d['unique']:<5}  top={top_val!r}  (n={top_cnt})")

if __name__ == "__main__":
    cli()