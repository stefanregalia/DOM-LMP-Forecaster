# Findings from Data Exploration

## Search for DOM Unique Identifier
    - DOM zone pnode_id (unique identifier) is 34964545
    - Feed lags several days: "Yesterday"/recent dates return 0, but last week worked

## Real-time Hourly LMP Exploration (target, goal is to predict this by ~10 am the day before)
    - Target variable named total_lmp_rt (average of the 5-minute real time prices and arrives hourly)
      - Derived by system_energy_price_rt + congestion_price_rt + marginal_loss_price_rt
      - Used for live scoring (revised version below is used for training)
    - UTC and EPT timestamps (using EPT for this project)
    - Versioning:
      - version_nbr: first publication = 1, max number is the last revision of LMP for the hour
      - row_is_current (True/False): Flags which is the latest version (True is the latest)
  
  
## Day-ahead LMP Forecast Exploration (benchmark, publishes at ~1:30 pm the day before, derived from ~11 am bid deadline)
  - Structurally identical to the real time LMP forecast, just with _da suffixes
  - Used as a live benchmark (revised version below is used for training)

## Load Forecasting Exploration
  - Current forecasts:
    - Feature to use: forecast_load_mw (predicted demand in MW/hr)
    - Evaluated_at_datetime_ept: when the forecast was made (not to be used as a feature, will be used as the threshold to ensure forecasts are issued before the 10 am deadline)
    - forecast_datetime_beginning_ept: the hour being forecasted 
  - Historical forecasts:
    - Evaluated_at data goes back to 2011
    - Field names differ from current feed (to be normalized in ingestion):
      - issue-time: evaluated_at_ept (vs evaluated_at_datetime_ept)
      - target-hour: forecast_hour_beginning_ept (vs forecast_datetime_beginning_ept)
      - area value: 'DOM' (vs 'DOMINION')
    - Load in 2011: ~9.8k; Load in 2026: ~16-17k

## Energy Generation by Fuel Type Exploration
  - PJM-wide (Not specific to DOM zone)
  - Gas/Nuclear/coal dominate
  - Actual values (will need to use lagged values and pivot into columns per fuel type for training)
  - Key feature: fuel_percentage_of_total

## Revised RT and DA LMP Price Exploration
  - Contains the truth regarding RT and DA prices
  - No versioning 
  - Lags weeks (used for training only)

## Open-Meteo Weather API Exploration
  - Forecast data stored in a dictionary of parallel arrays, as opposed to PJM's use of row dictionaries
    - Will need to zip into rows
  - 'temperature_2m_previous_day1' (Temperature) in celsius
  - 'temperature_2m_previous_day1', 'wind_speed_10m_previous_day1', and 'cloud_cover_previous_day1' all forecasted and available day before, so not lagged for training

## EIA Gas Pricing Exploration
  - 'value' is the variable (stored as a string, need to cast to float)
  - Not updated every day, a bit of a lag so use the most recent value at 10 am
  - Use lagged value since the actual value for day-ahead is unknown at 10 am

## Original Features to Use for Training

    - Target label to learn in training: total_lmp_rt for the target hour (settled RT price, in 'rt_da_monthly_lmps')
  
    - Raw: 
      - PJM 'load_frcstd_hist': Historical forecasted MW demand values (kept as 'forecast_load_mw')
      - Open-Meteo API: Temperature forecast at 2 meters elevation 24 hours before (called 'temperature_2m_previous_day1')
      - Open-Meteo API: Wind speed forecast at 10 meters elevation (called 'wind_speed_10m_previous_day1')
      - Open-Meteo API: Cloud cover forecast (called 'cloud_cover_previous_day1')
    - Features to Engineer: 
      - PJM 'rt_da_monthly_lmps': Lagged total_lmp_rt for the same hour over the last day, three days, and week (called lagged_lmp_rt) 
      - PJM 'rt_da_monthly_lmps': Lagged system_energy_price_rt, congestion_price_rt, and marginal_loss_price_rt for the same hour over the last day, three days, and week (called lagged_system_energy_price_rt, lagged_congestion_price_rt, and lagged_marginal_loss_price_rt, respectively)
      - PJM 'rt_da_monthly_lmps': Rolling mean and standard deviation for RT (total_lmp_rt) LMP over the last week for the same hour (called rolling_rt_mean and rolling_rt_std)
      - PJM 'rt_da_monthly_lmps': Lagged total_lmp_da for the same hour over the last day, three days, and week (called lagged_lmp_da) 
      - PJM 'rt_da_monthly_lmps': Lagged system_energy_price_da, congestion_price_da, and marginal_loss_price_da for the same hour over the last day, three days, and week (called lagged_system_energy_price_da, lagged_congestion_price_da, and lagged_marginal_loss_price_da, respectively)
      - PJM 'rt_da_monthly_lmps': Lagged difference between DA (total_lmp_da) and RT (total_lmp_rt) LMP (called lagged_da_rt_lmp_difference)
      - PJM 'rt_da_monthly_lmps': Lagged difference between DA congestion (congestion_price_da) and RT congestion (congestion_price_rt) (called lagged_da_rt_congestion_difference)
      - PJM 'gen_by_fuel': Lagged % of 'fuel_percentage_of_total' columns pivoted by 'fuel_type' (%gas, %coal, %hydro, %multiplefuels, %nuclear, %oil, %otherrenewables, %solar, %storage, %wind)(all lagged features by last day, 3 days, and one week)
      - All data: Date features engineered from 'datetime_beginning_ept' (called hour, day, month, is_weekend, is_holiday)
      - EIA Gas: Lagged price of natural gas ('lagged_gas_price')