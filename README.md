

## Usage

1. **Pure-Python stats**

   ```bash
   python3 pure_python_stats.py path/to/ads.csv [--json]
   ```

2. **Pandas stats**

   ```bash
   python3 pandas_stats.py path/to/ads.csv
   ```

3. **Visualisations**

   ```bash
   python3 visualisations.py path/to/ads.csv
   ```


## Summary



* **`pure_python_stats.py`**

  * **No dependencies** beyond the standard library.
  * Parses the JSON-ish range columns (`estimated_audience_size`, `impressions`, `spend`) with `ast.literal_eval` (skipping `NaN`s).
  * Splits each into `_lower` and `_upper` numeric fields.
  * Auto-detects numeric vs. categorical columns.
  * Prints counts, mean, std, min, max for numerics; unique count and top values for categoricals.


* **`pandas_stats.py`**

  * Requires **pandas** (and optionally matplotlib if you add charts).
  * Same range-parsing logic, but vectorized via `pd.Series.apply` with a `safe_parse` helper.
  * Numeric summary via `df.describe()`.


* **`visualisations.py`**

  * Requires **pandas**, **numpy**, and **matplotlib**.
  * Builds on the same `safe_parse` to unpack ranges.
  * **Histogram** of `impressions_lower` (log-scaled bins).
  * **Boxplot** of `spend_upper` by each exploded `publisher_platforms` (after `ast.literal_eval`).


