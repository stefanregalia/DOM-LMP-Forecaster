# Feature Build Findings

## Approach
- Built entirely in DuckDB
- Pipeline: load data and normalize per source -> join on date key -> feature engineer (calendar features, lag features, rolling features) -> combine engineered features to raw features -> drop nulls from left joins -> export to parquet

## Leakage Verification
- Load collapse: kept latest evaluated_at before 10am day-before-target, per hour
- Lag construction: self-joined on explicit timestamps to be gap-proof. Offsets are 2/4/8 days before target (= 1/3/7 days before prediction time, since prediction happens 1 day before target)

## Weather Adjustment
- Open-Meteo's `_previous_day1` is a flat 24h lead time, not tied to a fixed daily issue time
- For target hours after 10am, a 24h-ahead forecast is issued after the 10am deadline, which would be leakage
- Fix: pulled both _previous_day1 and _previous_day2 and selected day1 for hours < 10am and day2 for hours ≥ 10am 

## Data Quality Adjustments
- DST duplicate timestamps (from daylight savings) deduplicated using QUALIFY ROW_NUMBER()
- Gas forward-filled across weekends/holidays since prices are not generated on weekends (LAST_VALUE ... IGNORE NULLS)
- Fuel mix pivoted (10 rows/hour into 10 columns, one per fuel type)

## Final table
- 76 columns: label (total_lmp_rt) + 4 raw features (load, 3 weather features) + 5 calendar features + 63 lags + 2 rolling
- 20,815 rows, zero nulls (verified across ALL columns, not sampled)
- Nulls dropped were from lagged values at the start of the timeframe and daylight savings time
- Saved to data/training_table.parquet