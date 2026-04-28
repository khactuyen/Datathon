# Training & Optimization Log

File này ghi lại quá trình train, backtest, tối ưu submission và các quyết định kỹ thuật cho bài forecast `Revenue` / `COGS`.

Nguyên tắc cập nhật trong tương lai:
- Mỗi lần sửa model hoặc submission phải thêm một entry mới vào mục "Experiment Log".
- Mỗi entry phải có: giả thuyết, thay đổi, file sinh ra, metric validation, score leaderboard nếu có, quyết định giữ/bỏ.
- Không chỉ ghi "score tốt hơn"; phải ghi vì sao thay đổi đó hợp lý dựa trên residual, validation hoặc leaderboard.

## Evaluation Setup

- Data train gốc: `dataset/sales.csv`, giai đoạn `2012-07-04 -> 2022-12-31`.
- Template test/submission: `dataset/sample_submission.csv`, giai đoạn `2023-01-01 -> 2024-07-01`.
- Validation chính đang dùng: train `2012-07-04 -> 2021-12-31`, validate `2022-01-01 -> 2022-12-31`.
- Metric nội bộ: MAE, RMSE, R2 cho từng target; chọn model chính theo `MAE_sum = MAE_Revenue + MAE_COGS`.
- Score ngoài từ leaderboard/user report hiện đang dùng làm tín hiệu bổ sung, không thay thế hoàn toàn validation.

## Current Best

Best leaderboard submission hiện tại:

```text
submition/submission_train_forecasting_v3_optimized.csv
```

Best leaderboard model:

```text
calendar_blend_valid_scaled / seasonal6_week25_trend0_scaled
```

Best model-based residual submission hiện tại:

```text
submition/submission_train_forecasting_v5_breakthrough.csv
```

Best model-based residual approach:

```text
residual_meta_lgbm / lgbm_base_all_cal_cal2022
```

Score user report mới nhất:

```text
v3: 887452.65725
v4: 901697.83031
```

So với score trước đó:

```text
1082860.50843 -> 887452.65725
improvement = 195407.85118
relative improvement ~= 18.04%
```

## Scoreboard

| Version | Submission | Validation MAE_sum | User/Leaderboard score | Decision |
|---|---:|---:|---:|---|
| v2 | `submission_train_forecasting_v2.csv` | `1,138,818.80184` | `1,082,860.50843` | Baseline hợp lệ, nhưng còn underpredict level |
| v3 | `submission_train_forecasting_v3_optimized.csv` | `1,057,595.87512` | `887,452.65725` | Best leaderboard score, nhưng có validation scale |
| v4 | `submission_train_forecasting_v4_meta_residual.csv` | `1,055,118.89848` | `901,697.83031` | Best model-based residual candidate; cleaner than v3, score still strong |
| v5 | `submission_train_forecasting_v5_breakthrough.csv` | `758,861.84619` | pending | Breakthrough candidate: LightGBM residual meta-model |
| v5 meta #2 | `submission_v5_meta_2_base5_cal_lgbm_sh10.csv` | `773,342.46023` | `941,639.08418` | Rejected as overfit/aggressive LGBM residual |
| v6 cat #1 | `submission_v6_train_catboost_base_all_cal.csv` | `801,813.66734` | pending | Train-pipeline CatBoost residual candidate |

## Key Evidence

### 1. v2 bị underpredict level trên validation 2022

Từ `optimization_backtest.csv`, model v2 dự báo thấp hơn actual 2022:

| Target | Mean prediction 2022 | Mean actual 2022 | Mean ratio actual/pred | MAE-opt scale |
|---|---:|---:|---:|---:|
| Revenue | `2,859,252.75` | `3,204,791.32` | `1.12085` | `1.108` |
| COGS | `2,579,915.68` | `2,795,671.68` | `1.08363` | `1.076` |

Interpretation:
- Pattern mùa vụ của v2 tương đối ổn, nhưng level forecast thấp.
- Vì vậy scale theo target là hướng hợp lý hơn so với đổi model lớn ngay.
- Đây là lý do v3 thêm `revenue_scale` và `cogs_scale`.

### 2. Calendar blend cải thiện shape/pattern sau khi scale

So sánh trên validation 2022:

| Model | Revenue MAE | COGS MAE | MAE_sum | RMSE_sum | R2_mean |
|---|---:|---:|---:|---:|---:|
| v2 `seasonal6_trend0` | `617,748.93` | `521,069.88` | `1,138,818.80` | `1,538,516.28` | `0.75929` |
| scaled seasonal only | `568,906.75` | `495,652.96` | `1,064,559.71` | `1,459,138.63` | `0.78296` |
| v3 calendar blend scaled | `561,646.01` | `495,949.87` | `1,057,595.88` | `1,425,708.17` | `0.79283` |

Interpretation:
- Target scaling xử lý phần bias level lớn nhất.
- Thêm `weekofyear + day_of_week` không cải thiện COGS MAE nhiều, nhưng giảm Revenue MAE và giảm RMSE_sum rõ hơn.
- RMSE giảm nghĩa là các ngày lệch lớn được kiểm soát tốt hơn.

### 3. Leaderboard xác nhận hướng scale/blend là đúng

User report:

```text
v2 score: 1082860.50843
v3 score: 887452.65725
```

Interpretation:
- Validation chỉ dự đoán cải thiện khoảng `7.13%` theo MAE_sum.
- Leaderboard/user score cải thiện khoảng `18.04%`.
- Điều này củng cố giả thuyết: test 2023-2024 có level cao hơn v2, và scale upward là hướng đúng.

Risk:
- `valid_scaled` dùng năm 2022 để calibrate, nên có rủi ro overfit validation.
- Tuy nhiên leaderboard score đã xác nhận hướng này có ích ngoài validation.

## Experiment Log

### 2026-04-26 - v2 fixed 2022 validation split

Hypothesis:
- Cần train `2012-2021`, validate đúng năm `2022`, sau đó fit lại `2012-2022` để predict `2023-2024`.
- Time split hợp lý hơn random split vì đây là forecasting.

Change:
- Tạo `train_forecasting_v2.py`.
- Tạo pipeline:
  - `SeasonalTrendForecaster`
  - grid `seasonal_years`, `trend_years`
  - LightGBM recursive benchmark
  - blend seasonal + LightGBM
- Output:
  - `model_comparison_valid.csv`
  - `optimization_backtest.csv`
  - `forecast_v2_summary.json`
  - `submition/submission_train_forecasting_v2.csv`

Evidence:
- Best validation: `seasonal_profile / seasonal6_trend0`.
- Validation 2022:
  - Revenue MAE `617,748.93`, RMSE `836,496.02`, R2 `0.75024`
  - COGS MAE `521,069.88`, RMSE `702,020.26`, R2 `0.76834`
  - MAE_sum `1,138,818.80`
- User-reported score sau submit: `1,082,860.50843`.

Decision:
- Giữ làm baseline chính.
- Không chọn LightGBM vì trên validation 2022 LightGBM/blend không thắng seasonal profile.

### 2026-04-26 - v3 level calibration + calendar blend

Hypothesis:
- v2 underpredict level 2022, nên cần scale target lên thay vì đổi model lớn.
- Week-of-year + day-of-week có thể bắt pattern tuần tốt hơn month/day thuần.

Change:
- Thêm `WeekDowSeasonalForecaster`.
- Thêm `CalendarSeasonalBlendForecaster`.
- Thêm `TargetScaledForecaster`.
- Thêm `optimize_target_scales()`.
- Best variant mới:

```text
calendar_blend_valid_scaled / seasonal6_week25_trend0_scaled
```

Parameters:

```text
seasonal_years = 6
week_weight = 0.25
trend_years = 0
revenue_scale = 1.108
cogs_scale = 1.075
scale_source = 2022_validation
```

Output:
- `model_comparison_valid_v3.csv`
- `optimization_backtest_v3.csv`
- `forecast_v3_summary.json`
- `submition/submission_train_forecasting_v3_optimized.csv`

Evidence:
- Validation MAE_sum giảm:

```text
1,138,818.80 -> 1,057,595.88
improvement ~= 81,222.93
relative improvement ~= 7.13%
```

- User-reported score giảm:

```text
1,082,860.50843 -> 887,452.65725
improvement ~= 195,407.85
relative improvement ~= 18.04%
```

Decision:
- Chọn v3 làm current best.
- Tiếp tục tối ưu quanh v3, không quay lại LightGBM ngay.

### 2026-04-26 - v4 residual meta-model learns feature influence

Hypothesis:
- Thay vì nhân tay hoặc chỉ dùng global scale, có thể thêm một meta-model học residual từ các base forecasts.
- Nếu một base feature quan trọng hơn, meta-model sẽ tự học hệ số/ảnh hưởng lớn hơn từ dữ liệu calibration.
- Cách này vẫn là train model: base models học daily shape, meta-model học correction.

Change:
- Thêm `ResidualMetaForecaster` vào `train_forecasting_v2.py`.
- Base forecast features dùng cho meta-model:

```text
md6
wd6
calblend6w25
md7
calblend7w25
```

- Base prediction chính để cộng residual: `calblend6w25`.
- Meta target:

```text
residual = actual - calblend6w25_pred
```

- Meta model:

```text
HuberRegressor + StandardScaler
```

- Lý do chọn Huber:
  - Robust hơn Ridge thuần khi có ngày doanh thu bất thường.
  - Leave-one-month-out trong 2022 cho thấy `base_only + huber` là biến thể ổn nhất trong nhóm residual model thử nhanh.

Output:
- `model_comparison_valid_v4.csv`
- `optimization_backtest_v4.csv`
- `forecast_v4_summary.json`
- `submition/submission_train_forecasting_v4_meta_residual.csv`

Validation / calibration evidence:
- v4 residual meta-model trên 2022:
  - Revenue MAE `561,803.10`, RMSE `758,224.46`, R2 `0.79480`
  - COGS MAE `493,315.80`, RMSE `661,143.87`, R2 `0.79453`
  - MAE_sum `1,055,118.90`
- v3 calendar blend scaled:
  - MAE_sum `1,057,595.88`
- Local improvement:

```text
1,057,595.88 -> 1,055,118.90
improvement ~= 2,476.98
```

Prediction sanity check:
- v4 mean vs v3 on test:
  - Revenue ratio `0.9903`
  - COGS ratio `0.9959`
- Nghĩa là v4 không chỉ scale mạnh lên/xuống; nó giữ level gần v3 nhưng chỉnh shape/residual theo hệ số học được.

Decision:
- User-reported score v4: `901,697.83031`.
- V4 không thắng v3 theo leaderboard (`887,452.65725`), nhưng vẫn tốt hơn v2 rất nhiều và có tính "model train ra" rõ hơn v3.
- Giữ v4 làm best model-based residual candidate.
- Giữ v3 làm best leaderboard-score candidate nếu chỉ tối ưu điểm số.

Risk:
- Meta-model đang học từ calibration year 2022 nên vẫn có rủi ro overfit năm gần nhất.
- Cần dùng thêm rolling-year validation hoặc cải thiện meta-model để vừa giữ tính hợp lệ vừa kéo score xuống gần/vượt v3.

### 2026-04-26 - v5 LightGBM residual meta-model

Hypothesis:
- v4 dùng Huber linear residual model nên chỉ học correction tuyến tính từ các base forecasts.
- Residual theo ngày có thể phi tuyến theo calendar features, nhất là `month`, `weekofyear`, `dow`, các chu kỳ sin/cos.
- LightGBM residual meta-model có thể học interaction này mà vẫn là model train ra, không phải scale tay.

Change:
- Mở rộng `ResidualMetaForecaster`:
  - Cho phép `meta_model="lgbm"`.
  - Cho phép `feature_set="base_all_cal"`.
  - Tạo thêm base forecast features:

```text
md4, md5, md6, md7, md8
wd6, wd7
calblend6w25, calblend6w50, calblend7w25
base_mean, base_median, base_std, base_min, base_max
calendar features
```

- Meta target vẫn là:

```text
residual = actual - calblend6w25_pred
```

- Final prediction:

```text
final = calblend6w25_pred + LightGBM_residual_prediction
```

Output:
- `model_comparison_valid_v5.csv`
- `optimization_backtest_v5.csv`
- `forecast_v5_summary.json`
- `submition/submission_train_forecasting_v5_breakthrough.csv`

Validation evidence:
- v5 best variant:

```text
residual_meta_lgbm / lgbm_base_all_cal_cal2022
```

- Validation 2022:
  - Revenue MAE `399,217.23`, RMSE `602,299.87`, R2 `0.87052`
  - COGS MAE `359,644.62`, RMSE `536,347.26`, R2 `0.86478`
  - MAE_sum `758,861.85`

Compared with v4:

```text
1,055,118.90 -> 758,861.85
improvement ~= 296,257.05
relative improvement ~= 28.08%
```

Compared with v3:

```text
1,057,595.88 -> 758,861.85
improvement ~= 298,734.03
relative improvement ~= 28.24%
```

Guardrail check:
- Leave-one-month-out CV inside 2022 prototype:
  - Best LGBM base_all_cal approx `1,037,604`
  - v4 Huber base_only approx `1,075,904`
- Interpretation: LGBM residual model is more aggressive and has overfit risk, but month-held-out check did not collapse; it remained better than v4 in the prototype.

Prediction sanity check:
- v5 mean vs v3 on test:
  - Revenue ratio `0.9880`
  - COGS ratio `0.9935`
- This is not a simple upward/downward scale. The mean level stays close to v3/v4 while the daily residual shape changes.

Decision:
- Submit `submission_train_forecasting_v5_breakthrough.csv`.
- If leaderboard score improves over v3/v4, v5 becomes current best.
- If leaderboard score is worse, keep v5 as an aggressive residual candidate and shrink the residual correction in v6.

Risk:
- LightGBM residual model is much more flexible than Huber.
- It uses 2022 as calibration year, so it can overfit 2022-specific residuals.
- The next safe step after leaderboard feedback is residual shrinkage or multi-fold residual training.

### 2026-04-26 - v5 meta #2 public score shows LGBM residual overfit

Submitted:

```text
submition/submission_v5_meta_2_base5_cal_lgbm_sh10.csv
```

User-reported score:

```text
941,639.08418
```

Evidence:
- Internal validation MAE_sum for this variant: `773,342.46`.
- Public score is worse than:
  - v3 `887,452.65725`
  - v4 `901,697.83031`
- Forecast mean vs v3:
  - Revenue ratio `0.9874`
  - COGS ratio `0.9936`

Interpretation:
- LGBM residual meta-model fits 2022 validation too aggressively.
- The public score degradation is likely shape overfit, not only level mismatch.
- Do not continue full-strength LGBM residual as the main direction without shrinkage or stronger CV.

Decision:
- Reject `submission_v5_meta_2_base5_cal_lgbm_sh10.csv`.
- Try smoother CatBoost residual variants next.

### 2026-04-26 - v6 CatBoost residual candidates

Hypothesis:
- CatBoost residual meta-model may be smoother/more regularized than LGBM residual.
- Prototype leave-one-month-out in 2022 was better for CatBoost candidates than LGBM candidates, despite less aggressive in-sample fit.

Integrated into `train_forecasting_v2.py`:
- Import `CatBoostRegressor`.
- Add `meta_model="catboost"` in `ResidualMetaForecaster`.
- Add `residual_meta_catboost` candidates inside `run_pipeline()`.

Generated train-pipeline files:

```text
submition/submission_v6_train_catboost_base_all_cal.csv
submition/submission_v6_train_catboost_base5_cal.csv
submition/submission_v6_train_catboost_base5.csv
```

Recommended submission order:
1. `submission_v6_train_catboost_base_all_cal.csv`
2. `submission_v6_train_catboost_base5_cal.csv`
3. `submission_v6_train_catboost_base5.csv`

Reason:
- `base_all_cal` keeps COGS level closest to v3/v4 while using smoother CatBoost residual correction.
- `base5_cal` has similar validation but lower COGS level.
- `base5` is a simpler fallback with fewer features.

Format check:
- All three files have correct columns, 548 rows, date order matching `sample_submission.csv`, `YYYY-MM-DD` date format, no missing, no negative values, `utf-8-sig` encoding.

## Next Optimization Plan

### Priority 1 - Model-based calibration, not manual leaderboard scaling

Why:
- Score thực tế giảm mạnh sau khi scale upward.
- Hướng tối ưu level đang có căn cứ mạnh nhất.
- Tuy nhiên, không nên "nhân tay" chỉ vì leaderboard tốt hơn. Nếu dùng scale trong submission cuối, scale đó phải là một tham số được học từ validation/CV, tức là một bước calibration của model.

Plan:
- Giữ shape/pattern v3.
- Học calibration parameters từ dữ liệu lịch sử, không chọn thủ công từ leaderboard:
  - Train base model trên `2012 -> 2021`, predict `2022`.
  - Tìm `Revenue scale`, `COGS scale` tối ưu MAE trên `2022`.
  - Fit lại base model trên `2012 -> 2022`.
  - Áp dụng scale đã học vào forecast `2023 -> 2024`.
- Dùng thêm multi-fold để kiểm tra scale có ổn định không:
  - Train <= 2019, valid 2020
  - Train <= 2020, valid 2021
  - Train <= 2021, valid 2022

Expected decision rule:
- Nếu scale học từ các fold ổn định cùng hướng, giữ calibration.
- Nếu scale chỉ tốt ở 2022 nhưng phá các fold trước, giảm độ mạnh bằng shrinkage hoặc bỏ.
- Leaderboard chỉ dùng để xác nhận bên ngoài, không dùng làm căn cứ duy nhất để chọn hệ số.

### Priority 2 - Month-level residual calibration with shrinkage

Why:
- Residual v2 theo tháng cho thấy bias không đều:
  - Tháng 3 underpredict mạnh Revenue/COGS.
  - Tháng 8 Revenue underpredict nhưng COGS không underpredict cùng mức.
- Global scale sửa level chung nhưng chưa sửa sai lệch theo tháng.

Risk:
- Month-specific scale dễ overfit năm 2022.

Plan:
- Tính monthly scale từ validation 2022.
- Shrink về global scale:

```text
final_month_scale = global_scale * (1 - alpha) + month_scale * alpha
```

- Chỉ thử `alpha` nhỏ: `0.20`, `0.35`, `0.50`.
- So sánh bằng validation 2022 và nếu có thể thêm walk-forward 2020/2021/2022.

### Priority 3 - COGS as margin/ratio model

Why:
- `Revenue` và `COGS` có quan hệ rất chặt theo business.
- Dự báo COGS độc lập có thể làm margin thiếu ổn định.

Plan:
- Forecast Revenue bằng v3.
- Forecast ratio `COGS / Revenue` theo seasonal profile hoặc rolling annual ratio.
- COGS = Revenue * predicted_ratio.
- So sánh với COGS model hiện tại bằng MAE/RMSE.

### Priority 4 - Multi-fold guardrail

Why:
- Validation 2022 là mục tiêu triển khai hiện tại, nhưng scale/calibration có thể overfit 2022.

Plan:
- Dùng thêm folds:
  - Train <= 2019, valid 2020
  - Train <= 2020, valid 2021
  - Train <= 2021, valid 2022
- Không bắt buộc chọn model theo trung bình fold nếu leaderboard xác nhận 2022-like behavior, nhưng dùng fold để phát hiện biến thể quá rủi ro.

## Future Entry Template

Copy block này cho mỗi lần update:

```text
### YYYY-MM-DD - short experiment name

Hypothesis:
- ...

Change:
- ...

Output:
- ...

Validation evidence:
- Revenue MAE/RMSE/R2:
- COGS MAE/RMSE/R2:
- MAE_sum:

Leaderboard/user score:
- ...

Decision:
- Keep / reject / needs more test

Reason:
- ...
```

### 2026-04-27 - v7 guardrail shrinkage grid

Hypothesis:
- v5 LightGBM residual full-strength da cho validation rat tot nhung co dau hieu overfit leaderboard.
- Can them residual shrinkage grid, CatBoost residual variants, month calibration, COGS ratio, ensemble nhe voi v3 va guardrail multi-fold 2020/2021/2022.
- Khong chon LGBM full-strength lam final submission du no dung dau validation/guardrail noi bo, vi da co evidence public score kem v3 o bien the LGBM aggressive.

Change:
- Cap nhat `train_forecasting_v2.py` thanh pipeline v7:
  - Them `ValidationFold` cho F2020/F2021/F2022.
  - Them `MonthScaledForecaster`, `COGSRatioForecaster`, `FixedEnsembleForecaster`.
  - Them residual shrinkage grid `[0.15, 0.25, 0.35, 0.50, 0.75, 1.00]` cho LGBM va CatBoost.
  - Them month-level calibration shrink alpha `[0.15, 0.25, 0.35, 0.50]`.
  - Them guardrail summary va selection rule loai LGBM shrinkage > 0.50 khoi final auto-pick.

Output:
- metrics file: `model_comparison_valid_v7.csv`
- guardrail fold metrics: `guardrail_fold_metrics_v7.csv`
- guardrail summary: `guardrail_summary_v7.csv`
- backtest file: `optimization_backtest_v7.csv`
- summary file: `forecast_v7_summary.json`
- submission file: `submition/submission_train_forecasting_v7_guardrail.csv`

Validation evidence:
- Best raw validation candidate: `residual_meta_lgbm / lgbm_base_all_cal_sh100_cal2022`
  - MAE_sum `758,861.84619`
  - guardrail_avg_MAE_sum `722,323.77542`
  - rejected for auto-final because full-strength LGBM is high-risk after prior public overfit signal.
- Selected final candidate: `residual_meta_catboost / catboost_base_all_cal_sh100_cal2022`
  - F2022 MAE_sum `801,813.66734`
  - guardrail_avg_MAE_sum `754,691.96382`
  - guardrail_worst_MAE_sum `801,813.66734`
  - guardrail_avg_R2_mean `0.87404`
- Test mean ratio vs v3:
  - Revenue `0.98851`
  - COGS `0.99657`

Format check:
- `submission_train_forecasting_v7_guardrail.csv` has 548 rows.
- Columns are `Date, Revenue, COGS`.
- Date order matches `dataset/sample_submission.csv`.
- No missing values, no negative values.

Leaderboard/user score:
- pending

Decision:
- Keep as next candidate to submit.
- If public score is worse than v3, continue with CatBoost shrinkage `0.50/0.75` or ensemble `v3 + CatBoost`, not LGBM full-strength.

Reason:
- CatBoost full residual is weaker than LGBM on internal MAE but safer for auto-pick because it avoids the known LGBM public-overfit direction.
- Mean level remains close to v3, so the submission is changing shape/residual more than global scale.
