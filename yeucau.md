−→ĐỀTHIVÒNG1
DATATHON2026
THEGRIDBREAKER
BreakingBusinessBoundaries
Hostedby
VinTelligence
VinUniversityDataScience&AIClub
CuộcthiKhoahọcDữliệuđầutiêntạiVinUniversity
BiếnDữliệuthànhGiảiphápchoDoanhnghiệp
DATATHON2026—TheGridbreakers ĐượctổchứcbởiVinTelligence—VinUniDS&AIClub
Contents
1 MôtảDữliệu 2
1.1 Giới thiệu . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 2
1.2 Tổngquancácbảngdữliệu . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 2
1.3 BảngMaster . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 2
1.3.1 products.csv—Danhmụcsảnphẩm. . . . . . . . . . . . . . . . . . . . 2
1.3.2 customers.csv—Kháchhàng . . . . . . . . . . . . . . . . . . . . . . . . 3
1.3.3 promotions.csv—Chươngtrìnhkhuyếnmãi . . . . . . . . . . . . . . . 3
1.3.4 geography.csv—Địalý . . . . . . . . . . . . . . . . . . . . . . . . . . . 3
1.4 BảngTransaction. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3
1.4.1 orders.csv—Đơnhàng . . . . . . . . . . . . . . . . . . . . . . . . . . . 3
1.4.2 order_items.csv—Chi tiếtđơnhàng . . . . . . . . . . . . . . . . . . . 4
1.4.3 payments.csv—Thanhtoán. . . . . . . . . . . . . . . . . . . . . . . . . 4
1.4.4 shipments.csv—Vậnchuyển . . . . . . . . . . . . . . . . . . . . . . . . 4
1.4.5 returns.csv—Trảhàng . . . . . . . . . . . . . . . . . . . . . . . . . . . 4
1.4.6 reviews.csv—Đánhgiá . . . . . . . . . . . . . . . . . . . . . . . . . . . 4
1.5 BảngAnalytical . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 5
1.5.1 sales.csv—Dữliệudoanhthu . . . . . . . . . . . . . . . . . . . . . . . 5
1.6 BảngOperational . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 5
1.6.1 inventory.csv—Tồnkho . . . . . . . . . . . . . . . . . . . . . . . . . . 5
1.6.2 web_traffic.csv—Lưulượngtruycập . . . . . . . . . . . . . . . . . . 5
1.7 Quanhệgiữacácbảng . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 6
2 ĐềBài 7
2.1 Phần1—CâuhỏiTrắcnghiệm. . . . . . . . . . . . . . . . . . . . . . . . . . . . 7
2.2 Phần2—TrựcquanhoávàPhântíchDữliệu . . . . . . . . . . . . . . . . . . . 10
2.2.1 Yêucầu . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 10
2.3 Phần3—MôhìnhDựbáoDoanhthu(SalesForecasting) . . . . . . . . . . . . . 11
2.3.1 Bốicảnhkinhdoanh . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 11
2.3.2 Địnhnghĩabài toán . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 11
2.3.3 Dữliệu . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 11
2.3.4 Chỉsốđánhgiá. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 11
2.3.5 Địnhdạngfilenộp . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 11
2.3.6 Ràngbuộc . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 12
3 ThangđiểmChấmthi 13
4 HướngdẫnNộpbài 16
4.1 Checklistnộpbài . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 16
1
DATATHON2026—TheGridbreakers ĐượctổchứcbởiVinTelligence—VinUniDS&AIClub
MôtảDữliệu
Giới thiệu
Bộdữliệumôphỏnghoạtđộngcủamộtdoanhnghiệpthời trangthươngmạiđiệntửtạiViệt
Namtronggiaiđoạntừ04/07/2012đến31/12/2022. Dữliệubaogồm15fileCSV,được
chiathành4lớp:Master (dữliệuthamchiếu),Transaction(giaodịch),Analytical (phântích)
vàOperational (vậnhành).
Phânchiadữliệuchobàitoándựbáo:
•sales_train.csv: 04/07/2012→31/12/2022
•sales_test.csv: 01/01/2023→01/07/2024
Tổngquancácbảngdữliệu
Table1:Danhsáchcácfiledữliệu
# File Lớp Môtả
1 products.csv Master Danhmụcsảnphẩm
2 customers.csv Master Thôngtinkháchhàng
3 promotions.csv Master Cácchiếndịchkhuyếnmãi
4 geography.csv Master Danhsáchmãbưuchínhcácvùng
5 orders.csv Transaction Thôngtinđơnhàng
6 order_items.csv Transaction Chi tiếttừngdòngsảnphẩmtrongđơn
7 payments.csv Transaction Thôngtinthanhtoántươngứng1:1vớiđơnhàng
8 shipments.csv Transaction Thôngtinvậnchuyển
9 returns.csv Transaction Cácsảnphẩmbị trảlại
10 reviews.csv Transaction Đánhgiásảnphẩmsaugiaohàng
11 sales.csv Analytical Dữliệudoanhthuhuấnluyện
12 sample_submission.csv Analytical Địnhdạngfilenộpbài(mẫu)
13 inventory.csv Operational Ảnhchụptồnkhocuối tháng
14 web_traffic.csv Operational Lưulượngtruycậpwebsitehàngngày
BảngMaster
▶products.csv—Danhmụcsảnphẩm
Cột Kiểu Môtả
product_id int Khoáchính
product_name str Tênsảnphẩm
category str Danhmụcsảnphẩm
segment str Phânkhúcthị trườngcủasảnphẩm
size str Kíchcỡsảnphẩm
color str Nhãnmàusảnphẩm
price float Giábánlẻ
cogs float Giávốnhàngbán
Ràngbuộc: cogs<pricevớimọisảnphẩm.
2
DATATHON2026—TheGridbreakers ĐượctổchứcbởiVinTelligence—VinUniDS&AIClub
▶customers.csv—Kháchhàng
Cột Kiểu Môtả
customer_id int Khoáchính
zip int Mãbưuchính(FK→geography.zip)
city str Tênthànhphốcủakháchhàng
signup_date date Ngàyđăngkýtàikhoản
gender str Giới tínhkháchhàng(nullable)
age_group str Nhómtuổikháchhàng(nullable)
acquisition_channel str Kênhtiếpthịkháchhàngđăngkýqua(nullable)
▶promotions.csv—Chươngtrìnhkhuyếnmãi
Cột Kiểu Môtả
promo_id str Khoáchính
promo_name str Tênchiếndịchkèmnăm
promo_type str Loạigiảmgiá: theophầntrămhoặcsốtiềncốđịnh
discount_value float Giátrịgiảm(phầntrămhoặcsốtiềntùypromo_type)
start_date date Ngàybắtđầuchiếndịch
end_date date Ngàykếtthúcchiếndịch
applicable_category str Danhmụcápdụng,nullnếuápdụngtấtcả
promo_channel str Kênhphânphốiápdụngkhuyếnmãi (nullable)
stackable_flag int Cờchophépápdụngđồngthờinhiềukhuyếnmãi
min_order_value float Giátrịđơnhàngtối thiểuđểápdụngkhuyếnmãi (nullable)
Côngthứcgiảmgiá:
•percentage: discount_amount=quantity×unit_price×(discount_value/100)
•fixed: discount_amount=quantity×discount_value
▶geography.csv—Địalý
Cột Kiểu Môtả
zip int Khoáchính(mãbưuchính)
city str Tênthànhphố
region str Vùngđịalý
district str Tênquận/huyện
BảngTransaction
▶orders.csv—Đơnhàng
Cột Kiểu Môtả
order_id int Khoáchính
order_date date Ngàyđặthàng
customer_id int FK→customers.customer_id
zip int Mãbưuchínhgiaohàng(FK→geography.zip)
order_status str Trạngtháixửlýcủađơnhàng
payment_method str Phươngthứcthanhtoánđượcsửdụng
device_type str Thiếtbịkháchhàngdùngkhiđặthàng
order_source str Kênhmarketingdẫnđếnđơnhàng
3
DATATHON2026—TheGridbreakers ĐượctổchứcbởiVinTelligence—VinUniDS&AIClub
▶order_items.csv—Chi tiếtđơnhàng
Cột Kiểu Môtả
order_id int FK→orders.order_id
product_id int FK→products.product_id
quantity int Sốlượngsảnphẩmđặtmua
unit_price float Đơngiásaukhiápdụngkhuyếnmãi
discount_amount float Tổngsốtiềngiảmgiáchodòngsảnphẩmnày
promo_id str FK→promotions.promo_id(nullable)
promo_id_2 str FK→promotions.promo_id,khuyếnmãi thứhai (nullable)
▶payments.csv—Thanhtoán
Cột Kiểu Môtả
order_id int FK→orders.order_id(quanhệ1:1)
payment_method str Phươngthứcthanhtoán
payment_value float Tổnggiátrị thanhtoáncủađơnhàng
installments int Sốkỳtrảgóp
▶shipments.csv—Vậnchuyển
Cột Kiểu Môtả
order_id int FK→orders.order_id
ship_date date Ngàygửihàng
delivery_date date Ngàygiaohàngđếntaykhách
shipping_fee float Phívậnchuyển(0nếuđơnđượcmiễnphí)
Chỉ tồntạichođơnhàngcótrạngtháishipped,deliveredhoặcreturned.
▶returns.csv—Trảhàng
Cột Kiểu Môtả
return_id str Khoáchính
order_id int FK→orders.order_id
product_id int FK→products.product_id
return_date date Ngàykháchgửi trảhàng
return_reason str Lýdotrảhàng
return_quantity int Sốlượngsảnphẩmtrảlại
refund_amount float Sốtiềnhoànlạichokhách
▶reviews.csv—Đánhgiá
Cột Kiểu Môtả
review_id str Khoáchính
order_id int FK→orders.order_id
product_id int FK→products.product_id
customer_id int FK→customers.customer_id
review_date date Ngàykháchgửiđánhgiá
rating int Điểmđánhgiátừ1đến5
review_title str Tiêuđềđánhgiácủakháchhàng
4
DATATHON2026—TheGridbreakers ĐượctổchứcbởiVinTelligence—VinUniDS&AIClub
BảngAnalytical
▶sales.csv—Dữliệudoanhthu
Cột Kiểu Môtả
Date date Ngàyđặthàng
Revenue float Tổngdoanhthuthuần
COGS float Tổnggiávốnhàngbán
Split File Khoảngthờigian
Train sales.csv 04/07/2012–31/12/2022
Test sales_test.csv 01/01/2023–01/07/2024
Lưuý:Tậptestsẽkhôngđượccôngbốmàđượcdùngđểđánhgiákếtquảmôhìnhtrên
Kaggle.Cấutrúccủafiletestsẽgiốngvớisample_submission.csv
BảngOperational
▶inventory.csv—Tồnkho
Cột Kiểu Môtả
snapshot_date date Ngàychụpảnhtồnkho(cuối tháng)
product_id int FK→products.product_id
stock_on_hand int Sốlượngtồnkhocuối tháng
units_received int Sốlượngnhậpkhotrongtháng
units_sold int Sốlượngbánratrongtháng
stockout_days int Sốngàyhếthàngtrongtháng
days_of_supply float Sốngàytồnkhocóthểđápứngnhucầubán
fill_rate float Tỷlệđơnhàngđượcđápứngđủtừtồnkho
stockout_flag int Cờbáothángcóxảyrahếthàng
overstock_flag int Cờbáotồnkhovượtmứccầnthiết
reorder_flag int Cờbáocầntáiđặthàngsớm
sell_through_rate float Tỷlệhàngđãbánsovới tổnghàngsẵncó
product_name str Tênsảnphẩm
category str Danhmụcsảnphẩm
segment str Phânkhúcsảnphẩm
year int Nămtríchtừsnapshot_date
month int Thángtríchtừsnapshot_date
▶web_traffic.csv—Lưulượngtruycập
Cột Kiểu Môtả
date date Ngàyghinhậnlưulượng
sessions int Tổngsốphiêntruycậptrongngày
unique_visitors int Sốlượtkháchtruycậpduynhất
page_views int Tổngsốlượtxemtrang
bounce_rate float Tỷlệphiênchỉxemmộttrangrồi thoát
avg_session_duration_sec float Thờigiantrungbìnhmỗiphiên(giây)
traffic_source str Kênhnguồndẫntrafficvềwebsite
5
DATATHON 2026 — The Gridbreakers
Được tổ chức bởi VinTelligence — VinUni DS&AI Club
Quanhệ giữa các bảng
Table 2: Quy tắc quan hệ (Cardinality)
Quan hệ
Cardinality
orders ↔ payments
orders ↔ shipments
orders ↔ returns
orders ↔ reviews
1 : 1
1 : 0 hoặc 1 (trạng thái shipped/delivered/returned)
1 : 0 hoặc nhiều (trạng thái returned)
1 : 0 hoặc nhiều (trạng thái delivered, ∼20%)
order_items ↔ promotions nhiều : 0 hoặc 1
products ↔ inventory
1 : nhiều (1 dòng/sản phẩm/tháng)
6
DATATHON 2026 — The Gridbreakers
Được tổ chức bởi VinTelligence — VinUni DS&AI Club
Đề Bài
Phần1—Câuhỏi Trắc nghiệm
Chọn một đáp án đúng nhất cho mỗi câu hỏi. Các câu hỏi yêu cầu tính toán trực tiếp từ
dữ liệu được cung cấp.
Q1. Trong số các khách hàng có nhiều hơn một đơn hàng, trung vị số ngày giữa hai lần
mua liên tiếp (inter-order gap) xấp xỉ là bao nhiêu? (Tính từ orders.csv)
A) 30 ngày
B) 90 ngày
C) 180 ngày
D) 365 ngày
Q2. Phân khúc sản phẩm (segment) nào trong products.csv có tỷ suất lợi nhuận gộp
trung bình cao nhất, với công thức (price −cogs)/price?
A) Premium
B) Performance
C) Activewear
D) Standard
Q3. Trong các bản ghi trả hàng liên kết với sản phẩm thuộc danh mục Streetwear (join
returns với products theo product_id), lý do trả hàng nào xuất hiện nhiều nhất?
A) defective
B) wrong_size
C) changed_mind
D) not_as_described
Q4. Trong web_traffic.csv, nguồn truy cập (traffic_source) nào có tỷ lệ thoát trung
bình (bounce_rate) thấp nhấttrên tất cả các ngày xuất hiện nguồn đó trong cột traffic_source?
A) organic_search
B) paid_search
C) email_campaign
D) social_media
7
DATATHON 2026 — The Gridbreakers
Được tổ chức bởi VinTelligence — VinUni DS&AI Club
Q5. Tỷlệ phần trăm các dòng trong order_items.csv có áp dụng khuyến mãi (tức là promo_id
không null) xấp xỉ là bao nhiêu?
A) 12%
B) 25%
C) 39%
D) 54%
Q6. Trong customers.csv, xét các khách hàng có age_group khác null, nhóm tuổi nào có số
đơn hàng trung bình trên mỗi khách hàng cao nhất? (tổng số đơn / số khách hàng trong
nhóm)
A) 55+
B) 25–34
C) 35–44
D) 45–54
Q7. Vùng (region) nào trong geography.csv tạo ra tổng doanh thu cao nhất trong
sales_train.csv?
A) West
B) Central
C) East
D) Cả ba vùng có doanh thu xấp xỉ bằng nhau
Q8. Trong các đơn hàng có order_status = ’cancelled’ trong orders.csv, phương thức
thanh toán nào được sử dụng nhiều nhất?
A) credit_card
B) cod
C) paypal
D) bank_transfer
Q9. Trong bốn kích thước sản phẩm (S, M, L, XL), kích thước nào có tỷ lệ trả hàng cao
nhất, được định nghĩa là số bản ghi trong returns chia cho số dòng trong order_items (join
với products theo product_id)?
A) S
B) M
C) L
8
DATATHON 2026 — The Gridbreakers
Được tổ chức bởi VinTelligence — VinUni DS&AI Club
D) XL
Q10. Trong payments.csv, kế hoạch trả góp nào có giá trị thanh toán trung bình trên
mỗi đơn hàng cao nhất?
A) 1 kỳ (trả một lần)
B) 3 kỳ
C) 6 kỳ
D) 12 kỳ
9
DATATHON 2026 — The Gridbreakers
Được tổ chức bởi VinTelligence — VinUni DS&AI Club
Phần2—Trực quan hoá và Phân tích Dữ liệu
Khám phá bộ dữ liệu để tìm ra các insight có ý nghĩa kinh doanh. Phần này được đánh
giá dựa trên tính sáng tạo, chiều sâu phân tích và chất lượng trình bày. Không có
đáp án đúng duy nhất — ban giám khảo đánh giá khả năng kể chuyện bằng dữ liệu (data
storytelling) của các đội.
▶ Yêu cầu
Các đội thi tự do lựa chọn góc nhìn phân tích từ bộ dữ liệu. Bài nộp cần bao gồm hai thành
phần:
1. Trực quan hoá (Visualizations): Tạo các biểu đồ, đồ thị, bản đồ hoặc dashboard trực
quan để thể hiện các pattern, xu hướng và mối quan hệ trong dữ liệu. Mỗi hình ảnh cần
có tiêu đề, nhãn trục rõ ràng và chú thích phù hợp.
2. Phân tích (Analysis): Viết phần giải thích đi kèm mỗi trực quan hoá, bao gồm:
• Môtả những gì biểu đồ thể hiện và tại sao góc nhìn này quan trọng
• Các phát hiện chính (key findings) được hỗ trợ bởi số liệu cụ thể
• Ýnghĩa kinh doanh (business implications) hoặc đề xuất hành động (actionable rec
ommendations)
Tiêu chí đánh giá Phần 2: Bài nộp được đánh giá theo bốn cấp độ phân tích. Cấp độ
cao hơn bao gồm và nâng cao cấp độ thấp hơn.
Cấp độ
Câu hỏi
Ban giám khảo đánh giá
Descriptive What happened?
Diagnostic Why did it hap
pen?
Predictive
What is likely to
happen?
Prescriptive What should we
do?
Thống kê tổng hợp chính xác, biểu đồ có
nhãn rõ ràng, tổng hợp dữ liệu đúng
Giả thuyết nhân quả, so sánh phân khúc,
xác định bất thường có bằng chứng hỗ trợ
Ngoại suy xu hướng, phân tích tính mùa
vụ, phân tích chỉ số dẫn xuất
Đề xuất hành động kinh doanh được hỗ
trợ bởi dữ liệu; đánh đổi được định lượng
Các đội đạt cấp độ Prescriptive nhất quán trên nhiều phân tích sẽ đạt điểm cao nhất.
10
DATATHON 2026 — The Gridbreakers
Được tổ chức bởi VinTelligence — VinUni DS&AI Club
Phần3—Môhình Dự báo Doanh thu (Sales Forecasting)
▶ Bối cảnh kinh doanh
Bạn là nhà khoa học dữ liệu tại một công ty thương mại điện tử thời trang Việt Nam. Doanh
nghiệp cần dự báo nhu cầu chính xác ở mức chi tiết để tối ưu hoá phân bổ tồn kho, lập kế hoạch
khuyến mãi và quản lý logistics trên toàn quốc.
▶ Định nghĩa bài toán
Dự báo cột Revenue trong khoảng thời gian của sales_test.csv.
Mỗidòngtrong tập test là một bộ (Date,Revenue,COGS) duy nhất trong giai đoạn 01/01/2023– 01/07/2024.
▶ Dữ liệu
Split File
Khoảng thời gian
Train sales.csv
Test
04/07/2012– 31/12/2022
sales_test.csv 01/01/2023– 01/07/2024
▶ Chỉ số đánh giá
Bài nộp được đánh giá bằng ba chỉ số:
Mean Absolute Error (MAE):
MAE= 1
n 
n
i=1
|Fi −Ai|
Root Mean Squared Error (RMSE):
RMSE=
R2 (Coefficient of Determination):
R2 =1−
n
1
n
n
i=1
(Fi −Ai)2
i=1(Ai − Fi)2
n
i=1(Ai − ¯A)2
trong đó Fi là giá trị dự báo, Ai là giá trị thực, ¯A là trung bình giá trị thực. MAE đo độ
lệch tuyệt đối trung bình, RMSE phạt nặng hơn các sai số lớn, và R2 thể hiện tỷ lệ phương sai
được giải thích bởi mô hình.
MAE và RMSE càng thấp càng tốt. R2 càng cao càng tốt (lý tưởng gần 1).
▶ Định dạng file nộp
Nộp file submission.csv với các cột sau:
Các dòng trong submission.csv phải giữ đúng thứ tự như sample_submission.csv.
Không sắp xếp lại hoặc xáo trộn.
Ví dụ:
11
DATATHON 2026 — The Gridbreakers
Được tổ chức bởi VinTelligence — VinUni DS&AI Club
Date,Revenue,COGS
2023-01-01,26607.2,2585.15
2023-01-02,1007.89,163.0
2023-01-03,1089.51,821.12
...
▶ Ràng buộc
1. Không dùng dữ liệu ngoài: Tất cả đặc trưng phải được tạo từ các file dữ liệu được
cung cấp.
2. Tính tái lập (Reproducibility): Đính kèm toàn bộ mã nguồn. Đặt random seed khi
cần thiết.
3. Khả năng giải thích (Explainability): Trong report, bao gồm một mục giải thích các
yếu tố dẫn động doanh thu chính được mô hình xác định (vd: feature importances, SHAP
values, hoặc partial dependence plots). Giải thích những gì mô hình học được bằng ngôn
ngữ kinh doanh.
12
DATATHON 2026 — The Gridbreakers
Được tổ chức bởi VinTelligence — VinUni DS&AI Club
Thang điểm Chấm thi
Tổng điểm tối đa: 100 điểm, phân bổ theo ba phần thi. Điểm thành phần không làm
tròn cho đến khi tính tổng cuối cùng.
Table 3: Phân bổ điểm tổng quan
Phần Nội dung
Điểm Tỷ trọng
1
2
3
Câu hỏi Trắc nghiệm (MCQ)
Trực quan hoá & Phân tích (EDA)
Mô hình Dự báo Doanh thu (Forecasting)
20
60
20
20%
60%
20%
Tổng
100
100%
Phần1—Câuhỏi Trắc nghiệm (20 điểm)
Mỗi câu đúng được 2 điểm. Không trừ điểm cho câu trả lời sai.
Thành phần
Số câu
Điểm
Câu trả lời đúng 10 câu 2 điểm / câu
Câu trả lời sai
—
Không trả lời
—
0 điểm
0 điểm
Tổng tối đa
20 điểm
Phần2—Trực quan hoá & Phân tích EDA (60 điểm)
Phần này được chấm theo bốn tiêu chí độc lập, mỗi tiêu chí tương ứng với một cấp độ phân
tích trong rubric. Ban giám khảo chấm từng tiêu chí trên thang điểm thành phần, sau đó cộng
lại.
13
DATATHON 2026 — The Gridbreakers
Được tổ chức bởi VinTelligence — VinUni DS&AI Club
Tiêu chí
Mô tả
Điểm tối đa
Chất lượng trực
quan hoá
Chiều sâu phân
tích
Biểu đồ có tiêu đề, nhãn trục, chú
thích đầy đủ; lựa chọn loại biểu đồ
phù hợp; thẩm mỹ trình bày rõ ràng
Bao phủ đầy đủ bốn cấp độ Descrip
tive → Diagnostic → Predictive →
Prescriptive; lập luận logic, có số
liệu cụ thể hỗ trợ
Insight kinh doanh Phát hiện có giá trị thực tiễn; đề
xuất hành động khả thi; liên kết rõ
ràng giữa dữ liệu và quyết định kinh
doanh
Tính sáng tạo & kể
chuyện
Góc nhìn độc đáo, không lặp lại các
phân tích hiển nhiên; mạch trình
bày coherent; kết nối nhiều bảng dữ
liệu một cách có chủ đích
15
25
15
5
Tổng tối đa
60 điểm
Chi tiết thang điểm từng tiêu chí:
Tiêu chí
Mức
điểm
Mô tả
Chất lượng
trực quan hoá
(15đ)
13–15đ
8–12đ
0–7đ
Tất cả biểu đồ đều đạt chuẩn, lựa chọn loại
biểu đồ tối ưu cho từng insight
Phần lớn biểu đồ đạt yêu cầu, một số thiếu
nhãn hoặc chú thích
Biểu đồ thiếu thông tin, khó đọc hoặc không
phù hợp với dữ liệu
Chiều sâu
phân tích
(25đ)
21–25đ
14–20đ
7–13đ
0–6đ
Đạt cả bốn cấp độ Descriptive, Diagnostic,
Predictive, Prescriptive một cách nhất quán
Đạt ba cấp độ, cấp độ Prescriptive còn hời
hợt
Chủ yếu ở cấp Descriptive và Diagnostic
Chỉ mô tả bề mặt, thiếu phân tích
Insight
kinh doanh
(15đ)
13–15đ
8–12đ
0–7đ
Đề xuất cụ thể, định lượng được, áp dụng
được ngay
Có đề xuất nhưng còn chung chung
Thiếu kết nối với bối cảnh kinh doanh
Tính sáng tạo
(5đ)
4–5đ
2–3đ
0–1đ
Góc nhìn độc đáo, kết hợp nhiều nguồn dữ
liệu, mạch trình bày thuyết phục
Có điểm sáng tạo nhưng chưa nhất quán
Phân tích dự đoán được, không có điểm nổi
bật
Phần3—Môhình Dự báo Doanh thu (20 điểm)
Điểm Phần 3 được tính từ hai thành phần: hiệu suất mô hình trên Kaggle và chất lượng báo
cáo kỹ thuật.
14
DATATHON 2026 — The Gridbreakers
Được tổ chức bởi VinTelligence — VinUni DS&AI Club
Thành phần
Mô tả
Điểm tối đa
Hiệu suất mô hình
Báo cáo kỹ thuật
Dựa trên điểm MAE, RMSE,
R2 trên tập test (Kaggle leader
board); xếp hạng tương đối so
với các đội khác trong cuộc thi
Chất lượng pipeline (feature en
gineering, cross-validation, xử
lý leakage); giải thích mô hình
bằng SHAP / feature impor
tance; tuân thủ các ràng buộc
đã nêu
12
8
Tổng tối đa
20 điểm
Thành phần
Mức
điểm
Mô tả
Hiệu suất mô hình
(12đ)
10–12đ
5–9đ
3–4đ
Xếp hạng top leaderboard; MAE và
RMSE thấp, R2 cao
Hiệu suất trung bình; mô hình hoạt động
nhưng chưa tối ưu
Bài nộp hợp lệ nhưng hiệu suất thấp; mức
điểm sàn
Báo cáo kỹ thuật
(8đ)
7–8đ
4–6đ
0–3đ
Pipeline rõ ràng, cross-validation đúng
chiều thời gian, giải thích mô hình cụ thể
bằng SHAP hoặc tương đương, tuân thủ
đầy đủ ràng buộc
Pipeline đủ dùng, giải thích còn định tính,
một số ràng buộc chưa được xử lý tường
minh
Thiếu giải thích, không kiểm soát leakage,
hoặc không thể tái lập kết quả
Điều kiện loại bài: Bài nộp sẽ bị loại toàn bộ Phần 3 nếu vi phạm bất kỳ ràng buộc
nào sau đây: (1) sử dụng Revenue/COGS từ tập test làm đặc trưng; (2) sử dụng dữ liệu
ngoài bộ dữ liệu được cung cấp; (3) không đính kèm mã nguồn hoặc kết quả không thể tái
lập.
15
DATATHON 2026 — The Gridbreakers
Được tổ chức bởi VinTelligence — VinUni DS&AI Club
Hướng dẫn Nộp bài
Checklist nộp bài
Mỗi đội cần hoàn thành và nộp đầy đủ các mục sau:
1. Nộp kết quả dự báo trên Kaggle
2. Link Kaggle: https://www.kaggle.com/competitions/datathon-2026-round-1
Đảm bảo file submission.csv có đúng số lượng dòng và giữ nguyên thứ tự như
sample_submission.csv. File không đúng định dạng sẽ bị từ chối bởi hệ thống
Kaggle.
3. Báo cáo (Report)
Viết báo cáo sử dụng template LaTeX của NeurIPS, có thể tải tại:
https://neurips.cc/Conferences/2025/CallForPapers
Yêu cầu báo cáo:
• Giới hạn tối đa 4 trang (không tính references và appendix)
• Bao gồm các nội dung:– Trực quan hoá và phân tích dữ liệu (Phần 2)– Phương pháp tiếp cận, pipeline mô hình và kết quả thực nghiệm (Phần 3)
• Đính kèm link GitHub repository của nhóm trong báo cáo (chứa toàn bộ mã
nguồn, notebook, và file submission)
Lưu ý: GitHub repository cần được đặt ở chế độ public hoặc cấp quyền truy cập
cho ban tổ chức trước deadline nộp bài. Repository nên có README.md mô tả cấu trúc
thư mục và hướng dẫn chạy lại kết quả.
4. Form nộp bài thi Vòng 1
Điền đầy đủ thông tin trong form nộp bài chính thức (link sẽ được cung cấp). Form yêu
cầu:
• Chọn đáp án đúng cho câu hỏi trắc nghiệm
• Upload file báo cáo (PDF)
• Link GitHub repository
• Link submission trên Kaggle
• Ảnh chụp thẻ sinh viên của tất cả thành viên trong đội
• Tickbox xác nhận: Nhóm thi cam kết có ít nhất 1 thành viên có thể tham gia
trực tiếp Vòng Chung kết vào ngày 23/05/2026 tại Đại học VinUni, Hà Nội
Quan trọng: Các đội không xác nhận khả năng tham gia trực tiếp Vòng Chung kết
hoặc không cung cấp đầy đủ ảnh thẻ học sinh sẽ không đủ điều kiện để được xét
vào vòng tiếp theo.
16