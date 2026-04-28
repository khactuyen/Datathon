# CHIẾN LƯỢC XÂY DỰNG MỌ HÌNH MACHINE LEARNING

## TIP 2 - MACHINE LEARNING: XÂY DỰNG CHIẾN LƯỢC PHÙ HỢP

Khi bước vào phần mô hình, sự khác biệt không nằm ở việc chọn model "xịn" nhất, mà ở cách bạn xây dựng chiến lược và kiểm soát toàn bộ pipeline. Đây là lúc tư duy hệ thống quyết định chất lượng bài làm.

### 🔹 Baseline trước, tối ưu sau

**Quy trình:**
1. Bắt đầu với model đơn giản (Linear Regression, Logistic Regression, Decision Tree)
2. Đánh giá performance baseline
3. Sau đó mới nâng cấp (Random Forest, XGBoost, LightGBM)

**Lợi ích:**
- Hiểu rõ mức cơ sở để đánh giá cải thiện
- Phát hiện vấn đề dữ liệu sớm
- Tiết kiệm thời gian tính toán

### 🔹 Feature Engineering là yếu tố then chốt

**Các kỹ thuật chính:**
- **Tạo feature có ý nghĩa**: tổng (sum), tỉ lệ (ratio), chênh lệch (difference), trung bình động (rolling mean)
- **Xử lý missing values**: KNNImputer, mean/median imputation, forward fill, backward fill
- **Encoding cẩn thận**:
  - One-Hot Encoding cho categorical features
  - TargetEncoder cho high-cardinality features
  - Label Encoding cho ordinal features

**Nguyên tắc:**
- Luôn kiểm tra EDA trước khi tạo feature
- Loại bỏ feature có correlation cao (multicollinearity)
- Validate feature importance

### 🔹 Cross-validation để tránh overfitting

**Không chỉ dựa vào một train/test split**

**Lựa chọn phương pháp:**
- **StratifiedKFold**: Dùng cho classification, đảm bảo tỷ lệ class balanced
- **TimeSeriesSplit**: Dùng cho time series forecasting, không xáo trộn thứ tự thời gian
- **KFold**: Dùng cho regression thông thường
- **GroupKFold**: Khi có groups riêng biệt

**Thực hành tốt:**
```python
# Ví dụ TimeSeriesSplit cho forecasting
from sklearn.model_selection import TimeSeriesSplit
tscv = TimeSeriesSplit(n_splits=5)
for train_idx, val_idx in tscv.split(X):
    X_train, X_val = X[train_idx], X[val_idx]
    y_train, y_val = y[train_idx], y[val_idx]
    # Train & evaluate
```

### 🔹 Giải thích mô hình rõ ràng

**Các công cụ quan trọng:**
- **Feature Importance**: Xác định feature nào ảnh hưởng nhất
- **SHAP Values**: Giải thích contribution của từng feature cho prediction
- **Partial Dependence Plot**: Mối quan hệ giữa feature và prediction

**Tác dụng:**
- Tăng độ thuyết phục khi trình bày
- Phát hiện bias & anomaly
- Xác nhận model học đúng pattern

---

## TIP 3 – TỐI ƯU TOÀN BỘ BÀI LÀM

### ✨ Hiểu đúng evaluation metric

**Các metric phổ biến:**
| Bài toán | Metric | Khi nào dùng |
|----------|--------|-------------|
| **Classification** | Accuracy | Data balanced |
| | Precision | False Positive cost cao |
| | Recall | False Negative cost cao |
| | F1-Score | Cân bằng Precision & Recall |
| | AUC-ROC | Probabilistic predictions |
| **Regression** | MSE/RMSE | Penalize lỗi lớn |
| | MAE | Robust với outliers |
| | MAPE | Lỗi tương đối (%) |
| | Log-loss | Probabilistic targets |

**Cách chọn metric:**
- Đọc kỹ đề bài / evaluation criteria
- Lựa chọn metric phù hợp với business goal
- Sử dụng metric đó để tune hyperparameters

### ✨ Giữ code clean & reproducible

**Các nguyên tắc:**
1. **Set random_state mọi nơi**
   ```python
   np.random.seed(42)
   model = XGBRegressor(random_state=42)
   cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
   ```

2. **Sử dụng Pipeline**
   ```python
   from sklearn.pipeline import Pipeline
   pipe = Pipeline([
       ('preprocessing', StandardScaler()),
       ('model', XGBRegressor())
   ])
   ```

3. **Tránh Data Leakage**
   - Fit scaler/imputer chỉ trên training set
   - Không sử dụng test set info khi preprocessing
   - Cẩn thận với time-based splits

### ✨ Khi gặp bế tắc

**Quay lại dữ liệu và bài toán:**
- Một insight đúng có thể mở ra hướng đi hiệu quả hơn mọi thử nghiệm phức tạp
- Kiểm tra EDA lại: distribution, outliers, missing patterns
- Đọc lại problem statement, tìm hidden patterns
- Phân tích error cases: model sai ở đâu, tại sao?

**Debugging strategy:**
1. Kiểm tra data quality
2. So sánh baseline vs current model
3. Analyze feature importance
4. Check residuals (nếu regression)
5. Xem confusion matrix (nếu classification)

---

## CHECKLIST HOÀN THIỆN

- [ ] Baseline model đã được xây dựng và đánh giá
- [ ] Feature Engineering được thực hiện có hệ thống
- [ ] Cross-validation được áp dụng đúng cách
- [ ] Random state được set ở mọi nơi
- [ ] Code sử dụng Pipeline để tránh data leakage
- [ ] Metric evaluation phù hợp với bài toán
- [ ] Model interpretability được kiểm tra (Feature Importance/SHAP)
- [ ] Error analysis được thực hiện
- [ ] Hyperparameter tuning được optimize dựa trên đúng metric
- [ ] Final submission được validate trước khi submit

---

**Ghi nhớ:** Chất lượng bài làm phụ thuộc vào hệ thống & sự cẩn thận, không phải sử dụng model phức tạp nhất.
