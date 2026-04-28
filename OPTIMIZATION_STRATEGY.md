# CHIẾN LƯỢC TỐI ƯU HÓA TOÁN HỌC TIẾP THEO (MỤC TIÊU < 700,000 MAE)
Dựa trên thành công vang dội của v20 (đưa sai số xuống 783,383) bằng phương pháp Global Scale + Trend Projection thuần toán học, chúng ta sẽ **KHÔNG sử dụng Machine Learning**. Dưới đây là 4 mũi nhọn nâng cấp nội hàm mô hình toán học hiện tại:

### 1. Phân tách Lưới Siêu Tham Số (Decoupled Grid Search)
* **Vấn đề hiện tại:** Ở v20, thuật toán bắt buộc `Revenue` và `COGS` dùng chung 1 cấu hình (VD: cùng lấy `seasonal_years = 2`, `trend_years = 1`). 
* **Giải pháp:** Chạy Grid Search 2 lần độc lập. Rất có thể Revenue cần lấy 2 năm gần nhất để phản ánh độ nhạy thị trường, nhưng COGS (liên quan đến hợp đồng chuỗi cung ứng dài hạn) lại cần trung bình 4 năm để tối ưu. Việc tách riêng tham số chắc chắn sẽ xén thêm một khoản MAE đáng kể.

### 2. Bộ lọc Nhiễu Trung vị (Median Trend Robustness)
* **Vấn đề hiện tại:** Lực đẩy YoY (Year-over-Year) đang tính bằng giá trị Trung bình (Mean). Nếu giai đoạn 2020-2021 có một đợt bùng nổ bất thường do dịch COVID (+50%), giá trị Mean sẽ bị kéo lệch, dẫn đến dự báo 2023-2024 quá cao.
* **Giải pháp:** Đổi sang hàm Trung vị (`np.nanmedian`) khi tính gia tốc Trend. Trung vị sẽ tàng hình hoàn toàn trước các ngoại lệ đột biến, trả lại một véc-tơ tăng trưởng cốt lõi cực kỳ mượt mà.

### 3. Hệ số Hãm Gia tốc (Damped Trend Projection)
* **Vấn đề hiện tại:** Với công thức lãi kép `Trend ^ Years_Ahead`, nếu tăng trưởng đang là 15%, mô hình sẽ mặc định 2024 cũng tăng 15% so với 2023. Trong kinh tế học, đà tăng trưởng thực tế sẽ dần chững lại khi quy mô phình to.
* **Giải pháp:** Bổ sung tham số `damping_factor` (VD: 0.85). 
  - Tăng trưởng Năm 1: 15%
  - Tăng trưởng Năm 2: `15% * 0.85 = 12.75%`
  Kỹ thuật này bẻ cong đường xu hướng xuống một chút ở chóp, tránh over-prediction ở giai đoạn cuối năm 2024.

### 4. Bù trừ Ngày Khuyết Lễ (Holiday Calendar Shifting)
* **Vấn đề hiện tại:** Tết Âm Lịch (Lunar New Year) mỗi năm lệch nhau cả tháng. Hệ thống `Day-of-Year` tĩnh đang ghép ngày Tết của 2022 vào một ngày bình thường của 2023.
* **Giải pháp:** Chỉ lập bản đồ dịch chuyển khối lượng tịnh tiến (Delta Shift) thuần toán học cho 7 ngày Tết Âm Lịch mà không cần phải gọi các mô hình Cây Quyết Định (Tree Models).

---
**Nhận định:** Nếu áp dụng thuần thục 4 bước tinh chỉnh này, mô hình sẽ đạt đến cảnh giới cao nhất của lý thuyết dự báo chuỗi thời gian truyền thống (SARIMA-style), hoàn toàn có khả năng đâm xuyên mốc 700,000 MAE!
