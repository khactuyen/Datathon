TÀI LIỆU HƯỚNG DẪN TRAIN MÔ HÌNH DỰ BÁO DOANH THU
Chỉ giữ các phương pháp tốt nhất cho bài toán forecasting trong đề Datathon

Mục tiêu của tài liệu này là đưa ra một pipeline ngắn gọn, thực dụng và đủ mạnh để dùng trực tiếp cho bài forecast Revenue theo ngày. Tài liệu chỉ giữ những lựa chọn nên dùng thật sự; các phương án yếu hơn hoặc không phù hợp được lược bỏ.
1. Kết luận ngắn gọn
•	Target chính: dự báo Revenue theo ngày cho giai đoạn test 2023–2024.
•	Mô hình chính nên dùng: LightGBM Regressor.
•	Mô hình so sánh nên giữ: CatBoost Regressor.
•	Baseline bắt buộc: Seasonal Naive và Ridge Regression.
•	Validation đúng nhất: walk-forward / expanding window theo thời gian.
•	Hàm tối ưu trong train: regression objective; metric theo dõi chính là MAE và RMSE, đồng thời báo cáo thêm R².
•	Tuyệt đối tránh leakage từ tương lai khi tạo feature rolling, lag, aggregate hoặc khi chuẩn hóa dữ liệu.
2. Dùng dữ liệu nào
Chỉ nên dùng các bảng thật sự giúp tăng chất lượng dự báo và có thể tổng hợp theo ngày. Bộ dữ liệu khuyến nghị như sau:
Bảng	Mức ưu tiên	Dùng để làm gì	Có nên đưa vào model?
sales.csv	Bắt buộc	Target Revenue, COGS, lag và rolling statistics	Có
orders.csv	Bắt buộc	Số đơn, status, payment, device, source theo ngày	Có
order_items.csv	Bắt buộc	Quantity, discount, promo usage, mix sản phẩm theo ngày	Có
products.csv	Cao	Join category, segment, price band, cogs cho item-level aggregate	Có
promotions.csv	Cao	Biến event promo, loại discount, độ sâu discount, stackable	Có
web_traffic.csv	Cao	Sessions, page views, bounce rate, session duration	Có
inventory.csv	Cao	Stockout, fill rate, days of supply, reorder signals	Có
customers.csv	Trung bình	Cấu trúc khách hàng mới/quay lại, acquisition mix	Có nếu kịp
payments.csv	Trung bình	Payment value, installments theo ngày	Có nếu kịp
shipments.csv	Trung bình	Delivery lag, shipping fee summary	Có nếu kịp
returns.csv	Trung bình	Refund, return count, return reason summary	Có nếu kịp
reviews.csv	Thấp	Rating/review volume có độ trễ	Chỉ thêm nếu còn thời gian
geography.csv	Thấp	Regional mix theo ngày	Chỉ thêm nếu đã ổn pipeline chính
Nguyên tắc chọn dữ liệu: ưu tiên những bảng có thể tổng hợp thành feature theo ngày và có tác động trực tiếp đến Revenue. Không cố đưa mọi bảng vào model nếu làm tăng độ phức tạp mà không tạo thêm tín hiệu.
3. Pipeline tốt nhất nên dùng
•	Bước 1: dựng daily master table theo Date.
•	Bước 2: join toàn bộ feature ngoại sinh theo ngày.
•	Bước 3: tạo lag, rolling, seasonal và interaction features chỉ từ dữ liệu quá khứ.
•	Bước 4: train baseline đơn giản trước để có mốc so sánh.
•	Bước 5: train LightGBM làm model chính bằng walk-forward validation.
•	Bước 6: train CatBoost làm model phụ để benchmark hoặc blend nhẹ.
•	Bước 7: khóa cấu hình tốt nhất rồi fit lại trên toàn bộ train trước khi suy luận cho test.
4. Feature engineering nên giữ
Chỉ nên giữ bốn nhóm feature mạnh nhất dưới đây. Đây là nhóm có giá trị thực tế cao nhất cho bài toán forecast daily revenue.
Nhóm feature	Ví dụ nên dùng	Vì sao mạnh
Calendar	day_of_week, week_of_year, month, quarter, weekend, month_start/end	Bắt seasonality cơ bản
Lag & rolling	lag_1, lag_7, lag_14, lag_28, rolling_mean_7/28, rolling_std_7/28	Mạnh nhất cho time-series tabular
External daily aggregates	sessions, page_views, orders_count, items_count, promo_lines, avg_discount, stockout_rate	Mang tín hiệu business trực tiếp
Seasonal / cyclic	sin-cos month, sin-cos dow, Fourier terms cơ bản	Giúp model học chu kỳ mượt hơn
Không nên nhồi quá nhiều feature hiếm, quá chi tiết hoặc khó giải thích ở vòng đầu. Hãy ưu tiên bộ feature ngắn, sạch và ổn định.
5. Những feature cụ thể nên làm
•	Revenue lags: lag_1, lag_7, lag_14, lag_28, lag_56.
•	Revenue rolling: mean/std/min/max cho cửa sổ 7, 14, 28 ngày.
•	COGS lags và rolling: cùng cấu trúc với Revenue nếu dùng như biến giải thích.
•	Order aggregates: tổng số đơn, delivered ratio, cancelled ratio, average items per order.
•	Promotion aggregates: số line có promo, average discount amount, tỷ lệ line có promo, fixed vs percentage ratio.
•	Web traffic: sessions, unique visitors, page views, bounce rate, avg session duration và các lag 1/7/14.
•	Inventory: fill_rate trung bình, stockout_days tổng, reorder_flag count, overstock_flag count, days_of_supply trung bình.
•	Category mix: tỷ trọng Streetwear/Outdoor/Premium hoặc top 3 category share theo ngày.
•	Calendar encoding: day_of_week, is_weekend, month, quarter, sin/cos tuần và tháng.
6. Chia train / validation / test tốt nhất
Vì đây là bài forecast theo thời gian, tuyệt đối không dùng random split. Cách chia tốt nhất là theo thời gian, sao cho validation mô phỏng đúng điều kiện dự báo thật.
Tập	Khoảng thời gian khuyến nghị	Mục đích
Train chính	2012-07-04 đến 2020-12-31	Học pattern dài hạn
Validation 1	2021-01-01 đến 2021-12-31	Chọn feature và mô hình
Validation 2	2022-01-01 đến 2022-12-31	Tuning và kiểm tra độ ổn định cuối
Test thật	2023-01-01 đến 2024-07-01	Kaggle / submission
Nếu muốn chuẩn hơn nữa, hãy dùng walk-forward validation với nhiều fold mở rộng:
Fold	Train	Validation
Fold 1	2012-07-04 → 2018-12-31	2019-01-01 → 2019-12-31
Fold 2	2012-07-04 → 2019-12-31	2020-01-01 → 2020-12-31
Fold 3	2012-07-04 → 2020-12-31	2021-01-01 → 2021-12-31
Fold 4	2012-07-04 → 2021-12-31	2022-01-01 → 2022-12-31
Cách này tốt hơn một split duy nhất vì giúp kiểm tra mô hình có bền khi đi qua các giai đoạn business khác nhau, đặc biệt khi dữ liệu có biến động mạnh và inflection points.
7. Mô hình nên chọn
Mô hình	Vai trò	Có nên dùng	Lý do
Seasonal Naive	Baseline 1	Bắt buộc	Mốc tối thiểu để so sánh
Ridge Regression	Baseline 2	Nên dùng	Dễ giải thích, kiểm tra chất lượng feature
LightGBM Regressor	Model chính	Nên dùng nhất	Mạnh, nhanh, hợp tabular time-series
CatBoost Regressor	Model phụ / benchmark	Nên dùng	Ổn với categorical và aggregate phức tạp
Không cần đưa thêm quá nhiều mô hình ở vòng đầu. Chỉ cần baseline sạch + 1 model chính + 1 model phụ là đủ mạnh cho bài này.
8. Vì sao chọn LightGBM làm model chính
•	Học tốt quan hệ phi tuyến giữa Revenue và các feature ngoại sinh như traffic, promo, inventory.
•	Tận dụng rất tốt lag, rolling và aggregate features dạng tabular.
•	Train nhanh, dễ tuning, phù hợp khi phải thử nhiều fold theo thời gian.
•	Dễ giải thích bằng feature importance và SHAP, phù hợp với yêu cầu report.
•	Thực tế thường mạnh hơn linear model và linh hoạt hơn mô hình chuỗi thời gian cổ điển trong bài toán nhiều bảng dữ liệu.
9. Objective, metric và hàm tối ưu
Đây là phần nên chốt rất rõ để cả team không lệch hướng.
Thành phần	Khuyến nghị tốt nhất	Ghi chú
Objective khi train LightGBM	regression hoặc l2	Dễ ổn định, phù hợp tối ưu RMSE
Metric theo dõi khi CV	MAE + RMSE + R²	Báo cáo đủ bộ theo đề
Metric ưu tiên để chọn model	MAE trước, RMSE sau	MAE bền hơn với outlier; RMSE phạt lỗi lớn
Early stopping	Có	Giúp tránh overfit trên validation time-based
Thực tế nên chọn cấu hình dựa trên MAE trung bình qua các fold, rồi dùng RMSE và độ ổn định giữa các fold để phân xử nếu hai cấu hình gần nhau.
10. Hyperparameter nên thử đầu tiên
Tham số	Giá trị khởi đầu tốt
n_estimators	1000–3000 (kèm early stopping)
learning_rate	0.01–0.05
num_leaves	31, 63, 127
max_depth	-1 hoặc 6–10
min_data_in_leaf	20–100
feature_fraction	0.7–0.95
bagging_fraction	0.7–0.95
bagging_freq	1–5
lambda_l1 / lambda_l2	0–5
Không nên grid search quá rộng. Hãy bắt đầu từ một vùng tham số hẹp, chọn cấu hình ổn định, rồi mới tinh chỉnh tiếp.
11. Quy trình train tốt nhất
•	Dựng daily master table một lần duy nhất, lưu ra file parquet/csv sạch.
•	Viết riêng hàm tạo feature chỉ dùng dữ liệu quá khứ.
•	Train Seasonal Naive và Ridge trước để lấy mốc.
•	Train LightGBM với 4 fold walk-forward.
•	Giữ lại top 2–3 cấu hình tốt nhất theo MAE trung bình.
•	Chạy CatBoost trên cùng fold để benchmark.
•	Nếu CatBoost không thắng rõ, giữ LightGBM là model cuối.
•	Fit model cuối trên toàn bộ giai đoạn train 2012–2022 rồi suy luận cho test.
•	Lưu model, feature list, config và seed để tái lập.
12. Những lỗi cần tránh
Lỗi	Tại sao nguy hiểm	Cách tránh
Random split	Làm validation ảo, score đẹp giả	Chỉ dùng time split
Rolling dùng cả tương lai	Leakage trực tiếp	Shift trước khi rolling
Chuẩn hóa trên toàn bộ dữ liệu	Leak thông tin validation/test	Fit scaler trong train fold
Join aggregate vượt qua mốc thời gian	Leak hành vi tương lai	Aggregate theo cutoff date
Nhồi quá nhiều feature yếu	Tăng overfit, khó giải thích	Giữ bộ feature ngắn và mạnh
13. Cấu hình nộp bài khuyến nghị
Nếu cần một cấu hình gần như đủ dùng để triển khai ngay, hãy dùng cấu hình sau:
Hạng mục	Lựa chọn cuối cùng
Target	Revenue
Main model	LightGBM Regressor
Benchmark model	CatBoost Regressor
Baselines	Seasonal Naive + Ridge
Validation	4-fold expanding window
Selection metric	MAE trung bình qua các fold
Supporting metrics	RMSE, R²
Feature groups	Calendar + lag/rolling + traffic + promo + inventory + order aggregates
Leakage control	Shift tất cả lag/rolling; aggregate theo cutoff date
14. Kết luận
Pipeline tốt nhất cho bài này không phải là pipeline phức tạp nhất, mà là pipeline ổn định nhất: dữ liệu theo ngày sạch, feature mạnh, validation đúng chiều thời gian, LightGBM làm model chính, CatBoost để benchmark, và MAE làm tiêu chí chọn mô hình. Chỉ cần làm đúng các bước này, chất lượng forecast đã ở mức cạnh tranh rất tốt.
