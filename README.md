<div align="center">
  <h1>🏆 Vintelligence DataThon 2026 - The Gridbreakers</h1>
  <h3>Giải pháp Dự báo Doanh thu lai (Hybrid Forecasting) & Trực quan hoá Dữ liệu</h3>
  <p><em>Sản phẩm dự thi Vòng 1 của Đội: <b>AI Dream</b> 
</div>

---

## 📖 Tổng quan Dự án (Project Overview)

Trong bối cảnh thị trường thương mại điện tử thời trang đầy biến động sau đại dịch, việc quản lý và dự báo doanh thu/chi phí đóng vai trò quyết định trong việc tối ưu hóa chuỗi cung ứng. 

Dự án này giải quyết bài toán cốt lõi của vòng 1 DataThon 2026 bằng một pipeline khoa học dữ liệu toàn diện:
1. **Trắc nghiệm Phân tích Dữ liệu (Phần 1):** Khai phá các chỉ số vĩ mô (Inter-order gap, Conversion Rate, Gross Margin...).
2. **Phân tích EDA & Trực quan hoá (Phần 2):** Phác họa bức tranh toàn cảnh về hành vi khách hàng, mùa vụ và các cú sốc cung cầu (Dashboards).
3. **Mô hình Dự báo Doanh thu (Phần 3):** Xây dựng kiến trúc mô hình học máy kết hợp (Ensemble) để dự báo `Revenue` và `COGS` hàng ngày.

---

## 🎯 Hiệu năng Mô hình (Model Performance)

Mô hình của chúng tôi tự hào đạt được hiệu năng vượt trội trên tập Validation nội bộ (01/07/2022 - 31/12/2022) thông qua chiến lược đánh giá Time-Series Cross-Validation chặt chẽ:

| Kiến trúc Mô hình | MAE | RMSE | R² Score |
|:---|:---:|:---:|:---:|
| **M1:** Ridge Regression (Trend-catcher) | 543,799 | 773,416 | 0.6012 |
| **M2:** LightGBM Two-Stage | 444,073 | 607,048 | 0.7543 |
| **M3:** Q-Specialists (Phân rã theo quý) | ~430,000 | ~590,000 | ~0.7650 |
| 🚀 **Ensemble (Kết quả nộp bài)** | **~415,000** | **~575,000** | **~0.7750** |

---

## ⚙️ Kiến trúc Giải pháp (Solution Architecture)

Để giải quyết tính phi tuyến tính cao và các biến động mạnh từ các đợt khuyến mãi, mùa vụ Tết, chúng tôi đề xuất kiến trúc lai **Mixture of Experts (MoE)** gồm 3 tầng:

- **Feature Engineering:** Thiết kế ~70 đặc trưng vĩ mô bao gồm Fourier Terms (bắt mùa vụ), Countdown Tết (sự kiện tĩnh), t_days (đà tăng trưởng tuyến tính) và các cờ Regime (đại dịch COVID).
- **Khối Base Models:** 
  - `Ridge Regression` đóng vai trò duy trì đà ngoại suy.
  - `LightGBM` là lõi dự báo khai thác tối đa phi tuyến.
  - `Q-Specialists` chia nhỏ tập dữ liệu để tập trung học vi hành vi của từng Quý riêng biệt.
- **Ensemble & Calibration:** Kết hợp sức mạnh của 3 mô hình trên và áp dụng Scale Calibration bù trừ đà phục hồi bùng nổ Post-COVID. Phân tích **SHAP** minh bạch hóa quyết định của mô hình.

---

## 📁 Cấu trúc Repository

Dự án được tái cấu trúc tuân thủ nghiêm ngặt các tiêu chuẩn MLOps và khả năng tái lập (Reproducibility):

```text
/
├── README.md                           <- Tổng quan dự án (File này)
├── requirements.txt                    <- Danh sách thư viện Python cần thiết
├── .gitignore                          <- Cấu hình loại bỏ file rác và dataset khổng lồ
├── dataset/                            <- Thư mục chứa dữ liệu gốc từ BTC (Ngoại trừ trên Git)
├── notebooks/                          <- Toàn bộ mã nguồn Jupyter Notebook
│   ├── part1_MCQ_answers.ipynb         <- Lời giải Phần 1 (Tính toán động)
│   └── Part3_Model.ipynb               <- Pipeline huấn luyện & xuất file
├── EDA_Dashboard/                      <- Phân tích trực quan, Dashboard (Phần 2)
├── src/                                <- Chứa các file Python hỗ trợ dọn dẹp repo
├── report/                             <- Chứa báo cáo kỹ thuật (LaTeX, PDF)
└── submissions/                        <- Các file kết quả định dạng CSV
    └── submission_DA_Master_Breakthrough.csv
```

> **Lưu ý:** Thư mục `dataset/` đã được thiết lập đường dẫn động (Relative Path: `../dataset`) bên trong các Notebook để đảm bảo mã nguồn chạy thành công trên mọi máy tính của Ban Giám Khảo mà không cần sửa code.

---

## 🚀 Hướng dẫn Cài đặt & Chạy lại mã nguồn (Reproducibility)

Đảm bảo bạn đang sử dụng **Python 3.9+**.

### 1. Cài đặt thư viện phụ thuộc
Mở Terminal/Command Prompt và chạy lệnh sau:
```bash
pip install -r requirements.txt
```

### 2. Chuẩn bị Dữ liệu
Giải nén bộ dữ liệu do BTC cung cấp và đặt tất cả các file CSV (`orders.csv`, `sales.csv`,...) vào thư mục `dataset/` tại thư mục gốc của dự án.

### 3. Chạy Notebook Trắc Nghiệm (Phần 1)
Mở file `notebooks/part1_MCQ_answers.ipynb` bằng Jupyter Notebook hoặc VS Code. Bấm **Run All**. Mã nguồn sẽ tự động load dữ liệu và in ra kết quả cho 10 câu hỏi bằng tính toán động (dynamic evaluation).

### 4. Xem Phân tích EDA (Phần 2)
Mở thư mục `EDA_Dashboard/` để truy cập các tệp tin báo cáo trực quan hóa, phân tích phân khúc khách hàng, và các đề xuất kinh doanh.

### 5. Chạy Pipeline Mô hình & Dự báo (Phần 3)
Mở file `notebooks/Part3_Model.ipynb` và bấm **Run All**. Pipeline sẽ tự động thực hiện Feature Engineering, huấn luyện toàn bộ kiến trúc Ensemble, và tự động xuất file dự báo vào thư mục `submissions/`.

---

## 👥 Đội thi
- **Nguyễn Trần Anh Tú** (Data Analyst / Feature Engineer)
- **Võ Khắc Tuyên** (Machine Learning Engineer)
- **Nguyễn Duy Anh** (Business Analyst / Dashboard Creator)

*Chúng tôi xin cam kết toàn bộ dữ liệu sử dụng là dữ liệu nội bộ (không rò rỉ dữ liệu ngoài) và mô hình có khả năng tái lập 100% đúng theo thể lệ của cuộc thi.*
