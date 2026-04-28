# Ke hoach toi uu train model tiep theo

Tai lieu nay khoa huong toi uu tiep theo cho bai forecast `Revenue` va `COGS`.
Muc tieu khong phai la thu them model ngau nhien, ma la giam rui ro overfit 2022
va tao cac submission co co so validation ro rang.

## 1. Trang thai hien tai

### Submission va model dang giu

| Version | Submission | Validation MAE_sum | Leaderboard/user score | Ket luan |
|---|---:|---:|---:|---|
| v3 | `submition/submission_train_forecasting_v3_optimized.csv` | `1,057,595.87512` | `887,452.65725` | Best leaderboard hien tai |
| v4 | `submition/submission_train_forecasting_v4_meta_residual.csv` | `1,055,118.89848` | `901,697.83031` | Residual model sach hon, nhung kem v3 |
| v5 | `submition/submission_train_forecasting_v5_breakthrough.csv` | `758,861.84619` | pending | Validation rat manh, rui ro overfit cao |
| v5 meta #2 | `submition/submission_v5_meta_2_base5_cal_lgbm_sh10.csv` | `773,342.46023` | `941,639.08418` | Da lo dau hieu overfit |
| v6 cat #1 | `submition/submission_v6_train_catboost_base_all_cal.csv` | `801,813.66734` | pending | Candidate CatBoost an toan hon LGBM residual |

### Ket luan ky thuat

- `v3` la anchor chinh vi da duoc leaderboard xac nhan tot nhat.
- `v5` LightGBM residual khong duoc dung full-strength neu khong co shrinkage hoac guardrail tot hon.
- `v6` CatBoost residual dang la huong can submit/kiem tra tiep vi co validation tot va ky vong muot hon LGBM.
- Moi toi uu tiep theo phai tranh viec chi fit tot nam 2022 roi hong tren public test.

## 2. Uu tien toi uu

### Priority 1 - Multi-fold guardrail

Dung them cac fold theo nam de phat hien overfit:

| Fold | Train | Validation |
|---|---|---|
| F2020 | `2012-07-04 -> 2019-12-31` | `2020-01-01 -> 2020-12-31` |
| F2021 | `2012-07-04 -> 2020-12-31` | `2021-01-01 -> 2021-12-31` |
| F2022 | `2012-07-04 -> 2021-12-31` | `2022-01-01 -> 2022-12-31` |

Decision rule:

- Giu candidate neu `MAE_sum` trung binh 3 fold tot hon `v3` hoac it nhat khong te hon qua `2%`, dong thoi F2022 van tot.
- Reject candidate neu chi thang manh F2022 nhung thua ro o F2020/F2021.
- Neu candidate manh nhung khong on dinh, dua vao nhom shrinkage thay vi submit ngay.

### Priority 2 - Residual shrinkage

Ap dung cho `ResidualMetaForecaster` voi LGBM va CatBoost:

```text
final_prediction = base_prediction + shrinkage * residual_prediction
```

Grid nen thu:

```text
shrinkage = [0.15, 0.25, 0.35, 0.50, 0.75, 1.00]
```

Thu tu uu tien:

1. CatBoost `base_all_cal`
2. CatBoost `base5_cal`
3. LightGBM `base_all_cal`
4. LightGBM `base5_cal`

Decision rule:

- `1.00` chi duoc giu neu multi-fold on dinh.
- Neu public score cua LGBM residual kem v3, uu tien shrinkage `0.15 -> 0.50`.
- CatBoost co the thu shrinkage cao hon LGBM vi model muot hon.

### Priority 3 - Month-level calibration co shrink

Global scale cua v3 da hieu qua, nhung bias co the khac nhau theo thang. Thu month-level scale nhung phai shrink ve global:

```text
month_scale_final = global_scale * (1 - alpha) + month_scale_2022 * alpha
```

Grid nen thu:

```text
alpha = [0.15, 0.25, 0.35, 0.50]
```

Ap dung rieng cho `Revenue` va `COGS`.

Decision rule:

- Chi submit neu month calibration cai thien `RMSE_sum` hoac giam loi o cac thang outlier ma khong lam tang `MAE_sum` qua nhieu.
- Neu month scale dao dong qua manh giua cac fold, reject.

### Priority 4 - COGS ratio model

Thay vi forecast `COGS` doc lap, forecast ratio:

```text
cogs_ratio = COGS / Revenue
COGS_pred = Revenue_pred * cogs_ratio_pred
```

Candidate:

- Revenue dung `v3` hoac candidate residual da shrink.
- Ratio dung seasonal profile theo `(month, day)` hoac `(weekofyear, dow)`.
- Ratio co clip hop ly theo percentile lich su, vi ratio bat thuong co the lam COGS vuot xa Revenue.

Decision rule:

- Giu neu `COGS MAE` giam ma `Revenue` khong doi.
- Reject neu ratio model lam margin qua phang hoac tao shape COGS kem hon seasonal COGS hien tai.

### Priority 5 - Ensemble nhe quanh anchor v3

Khong blend qua nhieu file. Chi thu cac ensemble co ly do:

```text
candidate = weight * v3 + (1 - weight) * safer_model
```

Grid nen thu:

```text
v3_weight = [0.60, 0.70, 0.80, 0.90]
```

Safer model:

- `submission_train_forecasting_v4_meta_residual.csv`
- `submission_v6_train_catboost_base_all_cal.csv`
- CatBoost residual shrinkage candidate moi

Decision rule:

- Ensemble phai giu mean level gan v3.
- Neu ensemble lam giam risk shape nhung public score kem, khong tiep tuc mo rong ensemble.

## 3. Thu tu thuc nghiem de chay

1. Submit/ghi score cho `submition/submission_v6_train_catboost_base_all_cal.csv` neu chua co.
2. Them multi-fold validation helper vao pipeline de tinh F2020/F2021/F2022 cho v3, v4, v5, v6.
3. Chay residual shrinkage grid cho CatBoost `base_all_cal` va `base5_cal`.
4. Chay residual shrinkage grid cho LightGBM `base_all_cal`, nhung chi submit neu shrinkage thap va multi-fold on dinh.
5. Thu month-level calibration shrink quanh v3.
6. Thu COGS ratio model voi Revenue anchor la v3.
7. Thu ensemble nhe `v3 + best_safe_candidate`.

## 4. Tieu chi chon submission

Mot candidate duoc phep submit khi thoa it nhat 3 dieu kien:

- Format hop le: dung cot `Date,Revenue,COGS`, dung 548 rows, dung thu tu `sample_submission.csv`, khong missing, khong negative.
- Validation F2022 tot hon hoac gan v3.
- Multi-fold khong collapse o F2020/F2021.
- Mean level cua `Revenue` va `COGS` tren test khong lech bat thuong so voi v3.
- Neu la residual model, correction khong duoc qua lon tren cac ngay spike.

Mot candidate bi reject ngay khi:

- Chi thang validation 2022 nhung public score kem v3 ro rang.
- `Revenue`/`COGS` mean ratio so voi v3 nam ngoai khoang an toan `0.97 -> 1.03` ma khong co ly do.
- Tao du bao am, missing, sai thu tu ngay, hoac sai row count.

## 5. Mau log moi experiment

Them block nay vao `TRAINING_OPTIMIZATION_LOG.md` sau moi lan chay:

```text
### YYYY-MM-DD - experiment name

Hypothesis:
- ...

Change:
- ...

Output:
- metrics file:
- backtest file:
- submission file:

Validation evidence:
- F2020 MAE_sum / RMSE_sum / R2_mean:
- F2021 MAE_sum / RMSE_sum / R2_mean:
- F2022 MAE_sum / RMSE_sum / R2_mean:
- Average MAE_sum:
- Test mean ratio vs v3:
  - Revenue:
  - COGS:

Leaderboard/user score:
- ...

Decision:
- Keep / reject / needs shrinkage

Reason:
- ...
```

## 6. Submission priority hien tai

Neu can chon file de submit ngay, dung thu tu:

1. `submition/submission_v6_train_catboost_base_all_cal.csv`
2. `submition/submission_v6_train_catboost_base5_cal.csv`
3. `submition/submission_v6_train_catboost_base5.csv`

Neu v6 kem v3 tren leaderboard, huong tiep theo khong phai them residual full-strength, ma la:

1. CatBoost residual shrinkage.
2. Ensemble nhe voi v3.
3. Month-level calibration shrink quanh v3.

## 7. Nguyen tac dung lai

Dung mot nhanh toi uu khi gap mot trong cac dau hieu sau:

- Validation tot len nhieu nhung leaderboard kem lien tiep.
- Candidate can qua nhieu rule tay de giai thich.
- Score chi cai thien khi scale/shift theo leaderboard thay vi hoc tu validation.
- Model khong con phuc vu duoc report ve reproducibility va leakage control.

Huong tot nhat hien tai la toi uu co guardrail quanh `v3`, khong thay doi manh forecast shape neu chua co bang chung multi-fold.
