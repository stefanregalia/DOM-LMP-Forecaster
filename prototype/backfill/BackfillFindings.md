# Backfill Findings

## EIA Gas (Historical Actuals)
- 621 rows for 2024-01-01 to 2026-07-01 (daily, no weekends or holidays most likely)
- Single request

## Open-Meteo Weather (Forecasts)
- 21,912 rows (hourly, ~2.5 years)
- Needed timeout = 120 (default 30s timed out on the large pull)
- ~ 440 NaN rows (~18.3 days)
  - Will be removed when engineering features

## PJM Monthly LMP's (Historical Actuals)
- 30 monthly files (01/01/2024 - 07/01/2026) each with ~700 rows
- 20 seconds sleep between each request
- Retry logic added to the query_pjm function
- Need to watch out for 23hr/25/hr days (daylight savings) when building features
  
## PJM Monthly Load (Forecasts)
- 30 monthly files (01/01/2024 - 07/01/2026) each with ~5400-5500 rows
- 20 seconds sleep between each request
- Retry logic in query_pjm function
- Multiple forecasts versions per hour (will need to filter to the ones before 10 am but the one closest to 10 am)

## PJM Monthly Gen by Fuel (Historical Actuals)
- 30 monthly files (01/01/2024 - 07/01/2026), each with ~7000 rows
- 20 seconds sleep between each request
- Retry logic in query_pjm function
- Approximately 744 hours in a month x 10 fuel types