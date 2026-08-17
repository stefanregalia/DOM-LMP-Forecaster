# Model Findings

## Target transform

Raw `total_lmp_rt` is heavily right-skewed (mean $58.68, median $33.92, max $2014, min -$41.84). RMSE >> MAE on early baseline runs confirmed spikes were dominating squared-error metrics.

Went with `arcsinh` over a log transform because it handles the negative prices natively and requires no shift parameter. Behaves log-like on large values, near-linear near zero, so the dense typical-price region isn't distorted.

## Evaluation methodology

Expanding-window walk-forward CV, monthly folds, 27 folds total (min 3 months training history before the first fold). 

## Hyperparameter search

Full grid search across LightGBM and XGBoost separately. Tested MAE, MSE, and Huber loss (with alpha searched too), since the skewed target made this an interesting question.

**LightGBM winner:** `n_estimators=200, learning_rate=0.05, max_depth=-1, num_leaves=50, reg_alpha=0, reg_lambda=0, objective='huber', alpha=0.5` : CV MAE $29.28.

**XGBoost winner:** `n_estimators=200, learning_rate=0.05, max_depth=6, min_child_weight=5, reg_alpha=0, reg_lambda=0, objective='reg:absoluteerror'` : CV MAE $29.44.

Essentially a tie. Went with LightGBM as it had a marginally better MAE.

## Benchmarking (hourly, full validation set)

| | MAE | Win rate vs DA |
|---|---|---|
| Naive (2 days prior, same hour) | $43.52 | — |
| Naive (8 days prior, same hour) | $48.91 | — |
| XGBoost | $29.58 | 42.36% |
| **LightGBM (deployed)** | **$29.42** | **41.56%** |
| DA (actual market) | $26.51 | — |

The Light GBM model beats both naive baselines by 35-40%. Trails DA by about $3/MWh on average, wins roughly 2 of every 5 hours.

Plotted monthly MAE for the model against DA's monthly MAE over the same 27 months and the two lines track almost exactly, same peaks (Jan 2026, May 2026, Oct 2025), same troughs. This held for both LightGBM and XGBoost independently. 

## Feature importance (final model)

Top drivers, in order: `forecast_load_mw`, `temperature_2m_selected`, `lagged_gas_price`, calendar features (month, day-of-week, hour), `lagged_coal_percentage`. 

## Known limitation: train/validation gap

Train MAE $17.75 vs validation MAE $29.42 

## Retraining

Retraining will be quarterly (every 3 months), driven by the observed seasonal spike clustering and the year-over-year growth in both load and spike severity. Each retrain: champion/challenger validation with significance test against the currently-deployed model before promoting.

**To potentially be tested for the v2 model retraining:**
- Wider regularization search range
- Early stopping
- Sample weighting by price magnitude 

## Deployed artifact

`models/lgbm_v1.pkl` + `models/lgbm_v1_metadata.pkl` (feature list/order, transform notes, reference performance numbers). Next model version at first quarterly retrain becomes `lgbm_v2`.
