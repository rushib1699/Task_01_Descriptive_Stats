#!/usr/bin/env python3
import argparse
import pandas as pd
import ast

def parse_range_columns(df, cols):
    def safe_parse(x):
        # if x is NaN or not a string, skip it
        if pd.isna(x):
            return None, None
        try:
            d = ast.literal_eval(x)
            return float(d.get('lower_bound', 0)), float(d.get('upper_bound', 0))
        except Exception:
            return None, None

    for col in cols:
        lowers, uppers = zip(*df[col].apply(safe_parse))
        df[f"{col}_lower"] = pd.Series(lowers, index=df.index)
        df[f"{col}_upper"] = pd.Series(uppers, index=df.index)
    return df

def load_csv(path):
    df = pd.read_csv(path, encoding='utf-8')
    range_cols = ['estimated_audience_size', 'impressions', 'spend']
    df = parse_range_columns(df, range_cols)
    return df

def summarize(df):
    numeric_cols = df.select_dtypes(include='number').columns
    categorical_cols = df.select_dtypes(exclude='number').columns

    print("Numeric columns:")
    print(df[numeric_cols].describe().T[['count','mean','std','min','max']].to_string(float_format="%.2f"))
    print()
    print("Categorical columns:")
    for col in categorical_cols:
        unique = df[col].nunique(dropna=True)
        top3 = df[col].value_counts(dropna=True).head(3)
        print(f"{col}")
        print(f"  • unique = {unique}")
        print("  • top values:")
        for val, cnt in top3.items():
            print(f"      {val!r}  (n={cnt})")
        print()

def cli():
    p = argparse.ArgumentParser(description="Descriptive stats (pandas-safe)")
    p.add_argument("csv", help="path to ads CSV file")
    args = p.parse_args()
    df = load_csv(args.csv)
    summarize(df)

if __name__ == "__main__":
    cli()
