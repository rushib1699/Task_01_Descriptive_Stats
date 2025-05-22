#!/usr/bin/env python3
import argparse
import pandas as pd
import ast
import matplotlib.pyplot as plt
import numpy as np

def safe_parse(x):
    """
    Turn a string like "{'lower_bound':'100','upper_bound':'200'}"
    into a (float, float) tuple, or (np.nan, np.nan) on any failure.
    """
    if pd.isna(x):
        return np.nan, np.nan
    try:
        d = ast.literal_eval(x)
        lb = float(d.get("lower_bound", np.nan))
        ub = float(d.get("upper_bound", np.nan))
        return lb, ub
    except Exception:
        return np.nan, np.nan

def parse_ranges(df, cols):
    for col in cols:
        # apply safe_parse and unzip into two lists
        lowers, uppers = zip(*(safe_parse(val) for val in df[col]))
        df[f"{col}_lower"] = np.array(lowers, dtype=float)
        df[f"{col}_upper"] = np.array(uppers, dtype=float)
    return df

def load_data(path):
    df = pd.read_csv(path, encoding="utf-8")
    return parse_ranges(df, ["estimated_audience_size", "impressions", "spend"])

def hist_impressions(df):
    data = df["impressions_lower"].dropna()
    plt.figure()
    plt.hist(data, bins=30, log=True)
    plt.title("Histogram of Impressions (lower bound, log scale)")
    plt.xlabel("Impressions (lower)")
    plt.ylabel("Count (log)")
    plt.tight_layout()
    plt.show()

def boxplot_spend_by_platform(df):
    # some rows have lists like "['facebook','instagram']"; ast.literal_eval them first
    df = df.copy()
    df["publisher_platforms"] = df["publisher_platforms"].apply(ast.literal_eval)
    df2 = df.explode("publisher_platforms")
    plt.figure()
    df2.boxplot(column="spend_upper", by="publisher_platforms", grid=False)
    plt.title("Spend (upper bound) by Publisher Platform")
    plt.suptitle("")  # remove default
    plt.xlabel("Publisher Platform")
    plt.ylabel("Spend (upper)")
    plt.tight_layout()
    plt.show()

def cli():
    p = argparse.ArgumentParser(description="Basic visualisations for ads data")
    p.add_argument("csv", help="path to ads CSV file")
    args = p.parse_args()

    df = load_data(args.csv)
    hist_impressions(df)
    boxplot_spend_by_platform(df)

if __name__ == "__main__":
    cli()
