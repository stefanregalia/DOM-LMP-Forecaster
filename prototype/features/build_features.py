"""
Script to build tables and engineer features for prototype model training   
"""

### Loading Tables ###

# Using duckdb to load parquet files and perform feature engineering
import duckdb

con = duckdb.connect() # Connecting to duckdb

# Monthly LMP data
MONTHLY_LMP_DIR = str("../../data/rt_da_*.parquet") 

# Creating table for monthly LMP (prices) data
con.sql(f"CREATE TABLE prices AS SELECT * FROM '{MONTHLY_LMP_DIR}'")

# Sanity check to confirm the prices parquet files loaded correctly
con.sql("SELECT COUNT(*) FROM prices").show()
con.sql("SELECT * FROM prices LIMIT 5").show()

# Monthly load data

MONTHLY_LOAD_DIR = str("../../data/load_*.parquet")

# Creating table for monthly load data
con.sql(f"CREATE TABLE load_fcst AS SELECT * FROM '{MONTHLY_LOAD_DIR}'")

# Sanity check to confirm the load parquet files loaded correctly

con.sql("SELECT COUNT(*) FROM load_fcst").show()
con.sql("SELECT * FROM load_fcst LIMIT 5").show()

# Weather data

WEATHER_DIR = str("../../data/weather_data.parquet")

# Creating table for weather data
con.sql(f"CREATE TABLE weather AS SELECT * FROM '{WEATHER_DIR}'")

# Sanity check on weather data loading
con.sql(f"SELECT COUNT(*) FROM weather").show()
con.sql("SELECT * FROM weather LIMIT 5").show()

# Gas data

GAS_DIR = str("../../data/eia_gas_data.parquet")

# Create table for gas data
con.sql(f"CREATE TABLE gas AS SELECT * FROM '{GAS_DIR}'")

# Sanity check on gas data

con.sql("SELECT COUNT(*) FROM gas").show()
con.sql("SELECT * FROM gas LIMIT 5").show()

# Fuel data

FUEL_DIR = str("../../data/gen_by_fuel_*.parquet")

# Creating table for fuel data

con.sql(f"CREATE TABLE fuel AS SELECT * FROM '{FUEL_DIR}'")

# Sanity check on gen by fuel data

con.sql("SELECT COUNT(*) FROM fuel").show()
con.sql("SELECT * FROM fuel LIMIT 5").show()


### Normalizing Tables ###

# Normalizing price table

con.sql("""
CREATE TABLE prices_clean AS
SELECT
    CAST(datetime_beginning_ept AS TIMESTAMP) AS datetime_ept, 
    total_lmp_rt,
    system_energy_price_rt,
    congestion_price_rt,
    marginal_loss_price_rt,
    total_lmp_da,
    system_energy_price_da,
    congestion_price_da,
    marginal_loss_price_da
FROM prices
""")

# Sanity check on normalized price table
con.sql("SELECT COUNT(*) FROM prices_clean").show()
con.sql("SELECT * FROM prices_clean LIMIT 5").show()

# Normalizing load table (keeping the latest forecast before 10 am the day before the forecasted hour)
con.sql("""
CREATE TABLE load_clean AS
WITH ranked_cte AS (
    SELECT
        CAST(forecast_hour_beginning_ept AS TIMESTAMP) AS datetime_ept,
        CAST(evaluated_at_ept AS TIMESTAMP) AS evaluated_at,
        forecast_load_mw,
        ROW_NUMBER() OVER(
            PARTITION BY forecast_hour_beginning_ept 
            ORDER BY CAST(evaluated_at_ept AS TIMESTAMP) DESC) AS rn
    FROM load_fcst
    WHERE CAST(evaluated_at_ept AS TIMESTAMP) <= CAST(forecast_hour_beginning_ept AS TIMESTAMP)::DATE - INTERVAL 1 DAY + INTERVAL 10 HOUR
)   
SELECT 
    datetime_ept, 
    forecast_load_mw,
FROM ranked_cte
WHERE rn = 1       
""")

# Sanity check on normalized load table
con.sql("SELECT COUNT(*) FROM load_clean").show()
con.sql("SELECT * FROM load_clean ORDER BY datetime_ept LIMIT 5").show()
con.sql("SELECT MIN(datetime_ept), MAX(datetime_ept) FROM load_clean").show()

# Normalizing weather table

con.sql("""
CREATE OR REPLACE TABLE weather_clean AS
SELECT
    CAST(time AS TIMESTAMP) AS datetime_ept,
    CASE WHEN HOUR(CAST(time AS TIMESTAMP)) < 10
         THEN temperature_2m_previous_day1
         ELSE temperature_2m_previous_day2
    END AS temperature_2m_selected,
    CASE WHEN HOUR(CAST(time AS TIMESTAMP)) < 10
         THEN wind_speed_10m_previous_day1
         ELSE wind_speed_10m_previous_day2
    END AS wind_speed_10m_selected,
    CASE WHEN HOUR(CAST(time AS TIMESTAMP)) < 10
         THEN cloud_cover_previous_day1
         ELSE cloud_cover_previous_day2
    END AS cloud_cover_selected
FROM weather
WHERE
    (HOUR(CAST(time AS TIMESTAMP)) < 10 AND temperature_2m_previous_day1 IS NOT NULL
        AND wind_speed_10m_previous_day1 IS NOT NULL AND cloud_cover_previous_day1 IS NOT NULL)
    OR
    (HOUR(CAST(time AS TIMESTAMP)) >= 10 AND temperature_2m_previous_day2 IS NOT NULL
        AND wind_speed_10m_previous_day2 IS NOT NULL AND cloud_cover_previous_day2 IS NOT NULL)
""")

# Sanity check on normalized weather table
con.sql("SELECT COUNT(*) FROM weather_clean").show()
con.sql("SELECT * FROM weather_clean LIMIT 5").show()

# Normalizing gas table

con.sql("""
CREATE TABLE gas_clean AS 
SELECT
    CAST(period AS DATE) AS gas_date,
    CAST(value AS DOUBLE) AS gas_price
FROM gas    
""")

# Sanity check on normalized gas table
con.sql("SELECT COUNT(*) FROM gas_clean").show()
con.sql("SELECT * FROM gas_clean LIMIT 5").show()

# Normalizing fuel table

con.sql("""
CREATE TABLE fuel_clean AS 
SELECT
    CAST(datetime_beginning_ept AS TIMESTAMP) AS datetime_ept,
    MAX(CASE WHEN fuel_type = 'Coal' THEN fuel_percentage_of_total ELSE 0 END) AS coal_percentage,
    MAX(CASE WHEN fuel_type = 'Gas' THEN fuel_percentage_of_total ELSE 0 END) AS gas_percentage,
    MAX(CASE WHEN fuel_type = 'Hydro' THEN fuel_percentage_of_total ELSE 0 END) AS hydro_percentage,
    MAX(CASE WHEN fuel_type = 'Multiple Fuels' THEN fuel_percentage_of_total ELSE 0 END) AS multiple_fuels_percentage,
    MAX(CASE WHEN fuel_type = 'Nuclear' THEN fuel_percentage_of_total ELSE 0 END) AS nuclear_percentage,
    MAX(CASE WHEN fuel_type = 'Oil' THEN fuel_percentage_of_total ELSE 0 END) AS oil_percentage,
    MAX(CASE WHEN fuel_type = 'Other Renewables' THEN fuel_percentage_of_total ELSE 0 END) AS other_renewables_percentage,
    MAX(CASE WHEN fuel_type = 'Solar' THEN fuel_percentage_of_total ELSE 0 END) AS solar_percentage,
    MAX(CASE WHEN fuel_type = 'Wind' THEN fuel_percentage_of_total ELSE 0 END) AS wind_percentage,
    MAX(CASE WHEN fuel_type = 'Storage' THEN fuel_percentage_of_total ELSE 0 END) AS storage_percentage
FROM fuel
GROUP BY datetime_beginning_ept
""")

# Sanity check on normalized fuel table
con.sql("SELECT COUNT(*) FROM fuel_clean").show()
con.sql("SELECT * FROM fuel_clean ORDER BY datetime_ept LIMIT 5").show()

### Joining Tables ###

# Left join and then filtering if necessary to examine where data might be missing

con.sql("""
CREATE TABLE joined_data AS
SELECT
    p.datetime_ept,
    p.total_lmp_rt,
    p.system_energy_price_rt,
    p.congestion_price_rt,
    p.marginal_loss_price_rt,
    p.total_lmp_da,
    p.system_energy_price_da,
    p.congestion_price_da,
    p.marginal_loss_price_da,
    l.forecast_load_mw,
    w.temperature_2m_selected,
    w.wind_speed_10m_selected,
    w.cloud_cover_selected,
    g.gas_price,
    f.coal_percentage,
    f.gas_percentage,
    f.hydro_percentage,
    f.multiple_fuels_percentage,
    f.nuclear_percentage,
    f.oil_percentage,
    f.other_renewables_percentage,
    f.solar_percentage,
    f.wind_percentage,
    f.storage_percentage
FROM prices_clean p
LEFT JOIN load_clean l
    ON p.datetime_ept = l.datetime_ept
LEFT JOIN weather_clean w
    ON p.datetime_ept = w.datetime_ept
LEFT JOIN gas_clean g
    ON CAST(p.datetime_ept AS DATE) = g.gas_date
LEFT JOIN fuel_clean f
    ON p.datetime_ept = f.datetime_ept        
""")

# Checking for any missing value using proxies
con.sql("""
SELECT
    COUNT(*) AS total_rows,
    COUNT(forecast_load_mw) AS has_load,
    COUNT(temperature_2m_selected) AS has_weather,
    COUNT(gas_price) AS has_gas,
    COUNT(coal_percentage) AS has_fuel
FROM joined_data
""").show()

# Handling missing values
# Dropping weather nulls, load nulls (5 days of missing values), and fuel nulls, but filling gas nulls with that of the previous day (weekends are null)

con.sql("""
CREATE TABLE joined_filled AS 
WITH filled_gas AS (
    SELECT   
    datetime_ept,
    total_lmp_rt,
    system_energy_price_rt,
    congestion_price_rt,
    marginal_loss_price_rt,
    total_lmp_da,
    system_energy_price_da,
    congestion_price_da,
    marginal_loss_price_da,
    forecast_load_mw,
    temperature_2m_selected,
    wind_speed_10m_selected,
    cloud_cover_selected,
    LAST_VALUE(gas_price IGNORE NULLS) OVER(ORDER BY datetime_ept) AS gas_price,
    coal_percentage,
    gas_percentage,
    hydro_percentage,
    multiple_fuels_percentage,
    nuclear_percentage,
    oil_percentage,
    other_renewables_percentage,
    solar_percentage,
    wind_percentage,
    storage_percentage
FROM joined_data
)      
SELECT *
FROM filled_gas
WHERE forecast_load_mw IS NOT NULL
    AND temperature_2m_selected IS NOT NULL
    AND coal_percentage IS NOT NULL
QUALIFY ROW_NUMBER() OVER (PARTITION BY datetime_ept ORDER BY datetime_ept) = 1
""")

# Sanity check again for missing values after filling gas nulls and dropping other nulls
con.sql("""
SELECT
    COUNT(*) AS total_rows,
    COUNT(forecast_load_mw) AS has_load,
    COUNT(temperature_2m_selected) AS has_weather,
    COUNT(gas_price) AS has_gas,
    COUNT(coal_percentage) AS has_fuel
FROM joined_filled
""").show()

### Feature Engineering ###

# Calendar features creation
con.sql("""
CREATE TABLE calendar_features AS 
    SELECT 
        datetime_ept,
        MONTH(datetime_ept) AS month,
        DAYOFWEEK(datetime_ept) AS day_of_week,
        HOUR(datetime_ept) AS hour_of_day,
        CASE WHEN DAYOFWEEK(datetime_ept) IN (0, 6) THEN 1 ELSE 0 END AS is_weekend
    FROM joined_filled   
""")

# Sanity checkings calendar features table
con.sql("SELECT COUNT(*) FROM calendar_features").show()
con.sql("SELECT * FROM calendar_features LIMIT 5").show()

# Lagged features quick test (1, 3, 7 days before prediction is made (2, 4, 8 days before the forecasted hour))

con.sql("""
CREATE OR REPLACE TABLE lag_features AS
SELECT
    base.datetime_ept,
    lag2.total_lmp_rt AS lagged_lmp_rt_1,
    lag4.total_lmp_rt AS lagged_lmp_rt_3,
    lag8.total_lmp_rt AS lagged_lmp_rt_7
FROM joined_filled base
LEFT JOIN joined_filled lag2 ON lag2.datetime_ept = base.datetime_ept - INTERVAL 2 DAY
LEFT JOIN joined_filled lag4 ON lag4.datetime_ept = base.datetime_ept - INTERVAL 4 DAY
LEFT JOIN joined_filled lag8 ON lag8.datetime_ept = base.datetime_ept - INTERVAL 8 DAY
""")

# Sanity checking lagged features table counts
con.sql("SELECT COUNT(*) FROM lag_features").show()

# Sanity checking values are correct
con.sql("""
SELECT datetime_ept, lagged_lmp_rt_1, lagged_lmp_rt_3, lagged_lmp_rt_7
FROM lag_features
WHERE datetime_ept = '2026-02-01 15:00:00'
""").show()

con.sql("""
SELECT datetime_ept, total_lmp_rt
FROM joined_filled
WHERE datetime_ept IN (
    '2026-01-30 15:00:00',
    '2026-01-28 15:00:00',
    '2026-01-24 15:00:00'
)
ORDER BY datetime_ept
""").show()

# Full lag features table

con.sql("""
CREATE OR REPLACE TABLE lag_features AS
SELECT
    base.datetime_ept,
    lag2.total_lmp_rt AS lagged_lmp_rt_1,
    lag4.total_lmp_rt AS lagged_lmp_rt_3,
    lag8.total_lmp_rt AS lagged_lmp_rt_7,
    lag2.system_energy_price_rt AS lagged_system_energy_price_rt_1,
    lag4.system_energy_price_rt AS lagged_system_energy_price_rt_3,
    lag8.system_energy_price_rt AS lagged_system_energy_price_rt_7,
    lag2.congestion_price_rt AS lagged_congestion_price_rt_1,
    lag4.congestion_price_rt AS lagged_congestion_price_rt_3,
    lag8.congestion_price_rt AS lagged_congestion_price_rt_7,
    lag2.total_lmp_da - lag2.total_lmp_rt AS lagged_da_rt_lmp_difference_1,
    lag4.total_lmp_da - lag4.total_lmp_rt AS lagged_da_rt_lmp_difference_3,
    lag8.total_lmp_da - lag8.total_lmp_rt AS lagged_da_rt_lmp_difference_7,
    lag2.congestion_price_da - lag2.congestion_price_rt AS lagged_da_rt_congestion_difference_1,
    lag4.congestion_price_da - lag4.congestion_price_rt AS lagged_da_rt_congestion_difference_3,
    lag8.congestion_price_da - lag8.congestion_price_rt AS lagged_da_rt_congestion_difference_7,
    lag2.marginal_loss_price_rt AS lagged_marginal_loss_price_rt_1,
    lag4.marginal_loss_price_rt AS lagged_marginal_loss_price_rt_3,
    lag8.marginal_loss_price_rt AS lagged_marginal_loss_price_rt_7,
    lag2.total_lmp_da AS lagged_lmp_da_1,
    lag4.total_lmp_da AS lagged_lmp_da_3,
    lag8.total_lmp_da AS lagged_lmp_da_7,
    lag2.system_energy_price_da AS lagged_system_energy_price_da_1,
    lag4.system_energy_price_da AS lagged_system_energy_price_da_3,
    lag8.system_energy_price_da AS lagged_system_energy_price_da_7,
    lag2.congestion_price_da AS lagged_congestion_price_da_1,
    lag4.congestion_price_da AS lagged_congestion_price_da_3,
    lag8.congestion_price_da AS lagged_congestion_price_da_7,
    lag2.marginal_loss_price_da AS lagged_marginal_loss_price_da_1,
    lag4.marginal_loss_price_da AS lagged_marginal_loss_price_da_3,
    lag8.marginal_loss_price_da AS lagged_marginal_loss_price_da_7,
    lag2.gas_price AS lagged_gas_price_1,
    lag4.gas_price AS lagged_gas_price_3,
    lag8.gas_price AS lagged_gas_price_7,
    lag2.coal_percentage AS lagged_coal_percentage_1,
    lag4.coal_percentage AS lagged_coal_percentage_3,
    lag8.coal_percentage AS lagged_coal_percentage_7,
    lag2.gas_percentage AS lagged_gas_percentage_1,
    lag4.gas_percentage AS lagged_gas_percentage_3,
    lag8.gas_percentage AS lagged_gas_percentage_7,
    lag2.hydro_percentage AS lagged_hydro_percentage_1,
    lag4.hydro_percentage AS lagged_hydro_percentage_3,
    lag8.hydro_percentage AS lagged_hydro_percentage_7,
    lag2.multiple_fuels_percentage AS lagged_multiple_fuels_percentage_1,
    lag4.multiple_fuels_percentage AS lagged_multiple_fuels_percentage_3,
    lag8.multiple_fuels_percentage AS lagged_multiple_fuels_percentage_7,
    lag2.nuclear_percentage AS lagged_nuclear_percentage_1,
    lag4.nuclear_percentage AS lagged_nuclear_percentage_3,
    lag8.nuclear_percentage AS lagged_nuclear_percentage_7,
    lag2.oil_percentage AS lagged_oil_percentage_1,
    lag4.oil_percentage AS lagged_oil_percentage_3,
    lag8.oil_percentage AS lagged_oil_percentage_7,
    lag2.other_renewables_percentage AS lagged_other_renewables_percentage_1,
    lag4.other_renewables_percentage AS lagged_other_renewables_percentage_3,
    lag8.other_renewables_percentage AS lagged_other_renewables_percentage_7,
    lag2.solar_percentage AS lagged_solar_percentage_1,
    lag4.solar_percentage AS lagged_solar_percentage_3,
    lag8.solar_percentage AS lagged_solar_percentage_7,
    lag2.wind_percentage AS lagged_wind_percentage_1,
    lag4.wind_percentage AS lagged_wind_percentage_3,
    lag8.wind_percentage AS lagged_wind_percentage_7,
    lag2.storage_percentage AS lagged_storage_percentage_1,
    lag4.storage_percentage AS lagged_storage_percentage_3,
    lag8.storage_percentage AS lagged_storage_percentage_7,  
FROM joined_filled base
LEFT JOIN joined_filled lag2 ON lag2.datetime_ept = base.datetime_ept - INTERVAL 2 DAY
LEFT JOIN joined_filled lag4 ON lag4.datetime_ept = base.datetime_ept - INTERVAL 4 DAY
LEFT JOIN joined_filled lag8 ON lag8.datetime_ept = base.datetime_ept - INTERVAL 8 DAY
""")

# Sanity checking full lag features table counts and columns
con.sql("SELECT COUNT(*) FROM lag_features").show() 
con.sql("SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'lag_features'").show()

# Rolling features table

con.sql("""
CREATE TABLE rolling_features AS
WITH rolling AS (
    SELECT base.datetime_ept, d.total_lmp_rt AS hist_value
    FROM joined_filled base
    JOIN joined_filled d ON d.datetime_ept = base.datetime_ept - INTERVAL 2 DAY

    UNION ALL

    SELECT base.datetime_ept, d.total_lmp_rt
    FROM joined_filled base
    JOIN joined_filled d ON d.datetime_ept = base.datetime_ept - INTERVAL 3 DAY

    UNION ALL
        
    SELECT base.datetime_ept, d.total_lmp_rt
    FROM joined_filled base
    JOIN joined_filled d ON d.datetime_ept = base.datetime_ept - INTERVAL 4 DAY

    UNION ALL

    SELECT base.datetime_ept, d.total_lmp_rt
    FROM joined_filled base
    JOIN joined_filled d ON d.datetime_ept = base.datetime_ept - INTERVAL 5 DAY

    UNION ALL
        
    SELECT base.datetime_ept, d.total_lmp_rt
    FROM joined_filled base
    JOIN joined_filled d ON d.datetime_ept = base.datetime_ept - INTERVAL 6 DAY

    UNION ALL
        
    SELECT base.datetime_ept, d.total_lmp_rt
    FROM joined_filled base
    JOIN joined_filled d ON d.datetime_ept = base.datetime_ept - INTERVAL 7 DAY

    UNION ALL
        
    SELECT base.datetime_ept, d.total_lmp_rt
    FROM joined_filled base
    JOIN joined_filled d ON d.datetime_ept = base.datetime_ept - INTERVAL 8 DAY
)
        
SELECT 
    datetime_ept,
    AVG(hist_value) AS rolling_rt_mean,
    STDDEV(hist_value) AS rolling_rt_stddev
FROM rolling
GROUP BY datetime_ept
""")

# Sanity checking rolling features table 
con.sql("SELECT COUNT(*) FROM rolling_features").show()
con.sql("SELECT * FROM rolling_features ORDER BY datetime_ept DESC LIMIT 5").show()

### Combining all features into final table

con.sql("""
CREATE OR REPLACE TABLE final_features AS
SELECT 
    j.datetime_ept,
    c.month,
    c.day_of_week,
    c.hour_of_day,
    c.is_weekend,
    j.temperature_2m_selected,
    j.wind_speed_10m_selected,
    j.cloud_cover_selected,
    j.forecast_load_mw,
    l.* EXCLUDE (datetime_ept),
    r.rolling_rt_mean,
    r.rolling_rt_stddev,
    j.total_lmp_rt
FROM joined_filled j
LEFT JOIN calendar_features c
    ON j.datetime_ept = c.datetime_ept
LEFT JOIN lag_features l
    ON j.datetime_ept = l.datetime_ept
LEFT JOIN rolling_features r
    ON j.datetime_ept = r.datetime_ept   
""")

# Sanity checking final features table
con.sql("SELECT COUNT(*) FROM final_features").show()
con.sql("SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'final_features'").show()
con.sql("SELECT * FROM final_features ORDER BY datetime_ept DESC LIMIT 10").show()


# Dropping Nulls that result from the lagged features from beginning days or daylight savings
con.sql("""
CREATE OR REPLACE TABLE final_features AS
SELECT * FROM final_features
WHERE lagged_lmp_rt_7 IS NOT NULL
""")
con.sql("SELECT COUNT(*) FROM final_features").show()

# Confirming no more nulls

con.sql("""
SELECT COUNT(*) FROM final_features
WHERE NOT (COLUMNS(* EXCLUDE (datetime_ept)) IS NOT NULL)::BOOL
""").show()

# Converting to parquet for modeling

con.sql("COPY final_features TO '../../data/training_table.parquet' (FORMAT PARQUET)")