# DataThon - Data Summary

Dưới đây là tóm tắt các tệp dữ liệu trong dự án DataThon, với tên cột được dịch sang tiếng Việt và giải thích chi tiết.

## 1. customers.csv (Khách hàng)
- **customer_id** : ID Khách hàng - Mã định danh duy nhất cho mỗi khách hàng (để liên kết với bảng orders, reviews).
- **zip** : Mã bưu điện - Mã bưu điện nơi khách hàng sinh sống (để liên kết với bảng geography).
- **city** : Thành phố - Tên thành phố của khách hàng.
- **signup_date** : Ngày đăng ký - Ngày khách hàng tạo tài khoản.
- **gender** : Giới tính - Giới tính của khách hàng (Female, Male).
- **age_group** : Nhóm tuổi - Phân khúc độ tuổi của khách hàng (ví dụ: 18-24, 35-44).
- **acquisition_channel** : Kênh thu hút - Kênh marketing mang khách hàng này tới (social_media, email_campaign, referral, organic_search...).

## 2. geography.csv (Địa lý)
- **zip** : Mã bưu điện - Mã bưu điện (khóa chính để liên kết).
- **city** : Thành phố - Tên thành phố.
- **region** : Khu vực - Vùng địa lý lớn (ví dụ: East).
- **district** : Quận/Huyện - Khu vực hành chính nhỏ hơn (ví dụ: District #13).

## 3. inventory.csv (Kho hàng)
- **snapshot_date** : Ngày chốt số liệu kho - Ngày ghi nhận tình trạng kho hàng.
- **product_id** : ID Sản phẩm - Mã định danh sản phẩm.
- **stock_on_hand** : Tồn kho hiện tại - Số lượng sản phẩm đang có sẵn trong kho.
- **units_received** : Số lượng nhập - Số lượng sản phẩm mới nhận vào kho.
- **units_sold** : Số lượng đã bán - Số lượng sản phẩm bán ra được báo cáo.
- **stockout_days** : Số ngày hết hàng - Số ngày sản phẩm không có sẵn trong kho.
- **days_of_supply** : Số ngày cung ứng còn lại - Ước tính số ngày lượng tồn kho hiện tại có thể đủ bán.
- **fill_rate** : Tỷ lệ đáp ứng - Tỷ lệ phần trăm nhu cầu của khách hàng được đáp ứng ngay lập tức từ tồn kho.
- **stockout_flag** : Cờ hết hàng - Đánh dấu (1 hoặc 0) xem sản phẩm có bị hết hàng hay không.
- **overstock_flag** : Cờ thừa hàng - Đánh dấu xem sản phẩm có bị tồn kho quá nhiều không.
- **reorder_flag** : Cờ tái đặt hàng - Đánh dấu xem đến lúc cần nhập thêm hàng chưa.
- **sell_through_rate** : Tỷ lệ bán ra - Tỷ lệ phần trăm lượng hàng tồn kho đã được bán.
- **product_name**, **category**, **segment**, **year**, **month** : Tên sản phẩm, Danh mục, Phân khúc, Năm, Tháng.

## 4. order_items.csv (Chi tiết Đơn hàng)
- **order_id** : ID Đơn hàng - Mã định danh đơn hàng.
- **product_id** : ID Sản phẩm - Mã sản phẩm được mua trong đơn này.
- **quantity** : Số lượng - Số lượng sản phẩm cụ thể được mua.
- **unit_price** : Đơn giá - Giá của 1 sản phẩm tại thời điểm mua.
- **discount_amount** : Số tiền giảm giá - Số tiền được giảm cho món hàng này.
- **promo_id** : ID Khuyến mãi 1 - Mã khuyến mãi áp dụng (nếu có).
- **promo_id_2** : ID Khuyến mãi 2 - Mã khuyến mãi thứ hai áp dụng (nếu có).

## 5. orders.csv (Đơn hàng)
- **order_id** : ID Đơn hàng - Mã định danh duy nhất của đơn.
- **order_date** : Ngày đặt hàng - Ngày khách tạo đơn.
- **customer_id** : ID Khách hàng - Mã người mua.
- **zip** : Mã bưu điện - Nơi giao hàng.
- **order_status** : Trạng thái đơn hàng - Tình trạng hiện tại (delivered, returned, shipped, cancelled...).
- **payment_method** : Phương thức thanh toán - Cách khách hàng trả tiền (credit_card, cod, paypal...).
- **device_type** : Loại thiết bị - Thiết bị khách dùng để đặt (desktop, mobile, tablet).
- **order_source** : Nguồn đơn hàng - Kênh mang đơn hàng tới (như acquisition_channel).

## 6. payments.csv (Thanh toán)
- **order_id** : ID Đơn hàng - Liên kết tới đơn hàng.
- **payment_method** : Phương thức thanh toán.
- **payment_value** : Giá trị thanh toán - Số tiền thực tế thanh toán.
- **installments** : Số tháng trả góp - Số kỳ hạn trả góp (1 nghĩa là trả thẳng).

## 7. products.csv (Sản phẩm)
- **product_id** : ID Sản phẩm.
- **product_name** : Tên sản phẩm.
- **category** : Danh mục - Nhóm ngành hàng lớn (ví dụ: Streetwear).
- **segment** : Phân khúc - Dòng sản phẩm (ví dụ: Everyday).
- **size** : Kích cỡ - Size sản phẩm (S, M, L, XL).
- **color** : Màu sắc.
- **price** : Giá bán lẻ - Giá niêm yết của sản phẩm.
- **cogs** : Giá vốn hàng bán (Cost of Goods Sold) - Chi phí sản xuất/nhập vào của sản phẩm.

## 8. promotions.csv (Khuyến mãi)
- **promo_id** : ID Khuyến mãi.
- **promo_name** : Tên chương trình khuyến mãi.
- **promo_type** : Loại khuyến mãi - Cách tính giảm giá (percentage: phần trăm, fixed: cố định).
- **discount_value** : Giá trị giảm giá - Mức \% hoặc số tiền giảm.
- **start_date** : Ngày bắt đầu.
- **end_date** : Ngày kết thúc.
- **applicable_category** : Danh mục áp dụng - Các nhóm ngành hàng được hưởng khuyến mãi.
- **promo_channel** : Kênh khuyến mãi - Kênh tung deal (online, in_store, email...).
- **stackable_flag** : Cờ áp dụng chồng - Cho phép dùng chung với mã khác hay không.
- **min_order_value** : Giá trị đơn hàng tối thiểu - Mức tiền tối thiểu để được dùng mã.

## 9. returns.csv (Trả hàng)
- **return_id** : ID Trả hàng - Mã phiếu trả.
- **order_id** : ID Đơn hàng.
- **product_id** : ID Sản phẩm.
- **return_date** : Ngày trả hàng.
- **return_reason** : Lý do trả hàng - (wrong_size, defective, late_delivery...).
- **return_quantity** : Số lượng trả.
- **refund_amount** : Số tiền hoàn lại.

## 10. reviews.csv (Đánh giá)
- **review_id** : ID Đánh giá.
- **order_id** : ID Đơn hàng.
- **product_id** : ID Sản phẩm.
- **customer_id** : ID Khách hàng.
- **review_date** : Ngày đánh giá.
- **rating** : Điểm đánh giá - Phân mức sao (1-5).
- **review_title** : Tiêu đề đánh giá - Tóm tắt nội dung đánh giá của khách.

## 11. sales.csv (Doanh số)
- **Date** : Ngày - Chứa thông tin lịch.
- **Revenue** : Doanh thu - Tổng tiền kiếm được trong ngày đó.
- **COGS** : Tổng Giá vốn hàng bán - Chi phí sản xuất hàng bán ra trong ngày đó.

## 12. shipments.csv (Giao hàng)
- **order_id** : ID Đơn hàng.
- **ship_date** : Ngày lấy hàng/Gửi hàng - Ngày bắt đầu vận chuyển.
- **delivery_date** : Ngày giao dịch thành công/Dự kiến.
- **shipping_fee** : Phí vận chuyển - Chi phí ship nội bộ hoặc trả cho đối tác.

## 13. web_traffic.csv (Lưu lượng Web)
- **date** : Ngày.
- **sessions** : Số phiên truy cập - Tổng số lượt vào web.
- **unique_visitors** : Số lượng người dùng độc nhất - Người dùng thực tế vào web.
- **page_views** : Số lượt xem trang - Tổng lượng trang được load.
- **bounce_rate** : Tỷ lệ thoát - Tỷ lệ người truy cập chỉ xem 1 trang rồi thoát.
- **avg_session_duration_sec** : Thời lượng phiên truy cập trung bình (Giây).
- **traffic_source** : Nguồn truy cập - Từ kênh nào tới web (direct, organic_search, social_media...).
