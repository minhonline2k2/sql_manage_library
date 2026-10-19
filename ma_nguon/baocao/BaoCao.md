# LỜI MỞ ĐẦU

Báo cáo trình bày toàn bộ quá trình xây dựng hệ cơ sở dữ liệu quản lý thư viện theo kịch bản được giao: phân tích yêu cầu, thiết kế mức khái niệm (lược đồ E-R), thiết kế mức logic và chuẩn hóa về dạng BCNF, cài đặt trên hệ quản trị MariaDB với đầy đủ ràng buộc, 8 trigger và 7 transaction nghiệp vụ, dữ liệu vận hành 3 tháng, các truy vấn báo cáo theo yêu cầu, giao diện kết nối CSDL, và cuối cùng là phân tích, thiết kế cơ sở dữ liệu phân tán cho 3 chi nhánh.

Nguyên tắc xuyên suốt: **mọi luật nghiệp vụ nằm trong CSDL** (ràng buộc, trigger, stored procedure); giao diện chỉ gọi procedure và hiển thị kết quả, nên mọi ràng buộc vẫn được đảm bảo khi thao tác trực tiếp bằng SQL. Toàn bộ mã nguồn được chạy và kiểm thử tự động: 47/47 ca kiểm thử nghiệp vụ, 36/36 ca kiểm tra phân mảnh và 23/23 thao tác trên giao diện đều đạt.

# CHƯƠNG 1. PHÂN TÍCH YÊU CẦU

## 1.1 Mô tả nghiệp vụ

Thư viện có 3 chi nhánh (CN01 Cầu Giấy, CN02 Hà Đông, CN03 Hoàn Kiếm), mở cửa 07:00–21:00. Mỗi chi nhánh có các phòng đựng sách (phòng kho), trong đó đặt các giá sách; mỗi giá chỉ chứa sách của **một thể loại**, tối đa 100 cuốn. Sách được quản lý theo **đầu sách** (một tựa sách); mỗi đầu sách có nhiều **cuốn sách** vật lý. Mã đầu sách có dạng `TR0012`, trong đó 2 ký tự đầu là mã thể loại; mã cuốn có dạng `TR0012-003` (đầu sách + số thứ tự), nên mã cuốn luôn chứa thông tin đầu sách và thể loại như đề yêu cầu.

Thủ thư làm việc tại một chi nhánh, có thể có thủ thư quản lý trực tiếp; mỗi chi nhánh có đúng một thủ thư trưởng. Độc giả đăng ký tại một chi nhánh và được cấp thẻ có hiệu lực 1 năm (gia hạn mỗi lần 1 năm).

**Mượn sách:** thủ thư lập phiếu mượn cho độc giả; mỗi phiếu tối đa **10 cuốn**; tại mọi thời điểm một độc giả giữ tối đa **50 cuốn** chưa trả. Mỗi cuốn trong phiếu có hạn trả riêng = ngày mượn + số ngày mượn của thể loại, hoặc số ngày riêng của đầu sách nếu có (sách quý, ít bản). Thẻ hết hạn thì không được mượn. Khi mượn, số lượng sách trên giá giảm và tuổi thọ cuốn sách giảm 1 tháng.

**Trả sách:** mỗi lần trả, độc giả trả 1 đến nhiều cuốn (có thể thuộc nhiều phiếu mượn khác nhau); số lượng trên giá tăng lại. Trả muộn bị phạt theo thể loại: tiền phạt = phạt cơ bản/cuốn + phạt mỗi ngày × số ngày trễ (Truyện 100.000đ + 10.000đ/ngày; Tham khảo 200.000đ + 30.000đ/ngày; các thể loại khác do nhóm quy định). Bảng phí phạt có ngày áp dụng để thư viện thay đổi chính sách mà không làm sai các phiếu phạt cũ.

**Tuổi thọ sách:** mỗi thể loại có tuổi thọ (Truyện 15 năm, Tham khảo 10 năm, …), lưu theo tháng; mỗi lần mượn giảm 1 tháng. Cuốn về 0 chuyển trạng thái chờ thanh lý; khi thanh lý được chuyển sang bảng **SACH_THANH_LY** và xóa khỏi kho đang quản lý.

**Phòng đọc:** độc giả thuê phòng học nhóm (4–10 người, 50.000đ/giờ, 1–4 giờ) hoặc phòng hội thảo (20–60 người, 300.000đ/giờ, 2–8 giờ); thuê theo giờ tròn trong giờ mở cửa, đặt trước tối đa 14 ngày, không trùng giờ, số người không vượt sức chứa; thủ thư duyệt phiếu thuê. Độc giả còn nợ phạt hoặc thẻ hết hạn không được thuê.

## 1.2 Thông tin cần lưu trữ

| Nhóm | Thông tin |
| --- | --- |
| Chi nhánh | Mã, tên, địa chỉ, giờ mở/đóng cửa, thủ thư trưởng |
| Người (chung cho độc giả, thủ thư) | Mã, họ tên (họ, đệm, tên), ngày sinh, giới tính, địa chỉ (số nhà, phường, quận, tỉnh/thành), email, các số điện thoại |
| Độc giả | Chi nhánh đăng ký, ngày đăng ký, trạng thái; thẻ (số thẻ, ngày cấp, ngày hết hạn) |
| Thủ thư | Chi nhánh làm việc, ngày vào làm, người quản lý |
| Thể loại | Mã, tên, số ngày mượn, tuổi thọ (năm); bảng phí phạt theo ngày áp dụng |
| Đầu sách | Mã, tên, nhà xuất bản, năm xuất bản, số ngày mượn riêng, các tác giả |
| Cuốn sách | Mã, số thứ tự, giá đang đặt, ngày nhập, tuổi thọ còn lại (tháng), trạng thái |
| Phòng kho, giá sách | Mã, tên, tầng; giá: thể loại, sức chứa, số lượng hiện có |
| Mượn – trả | Phiếu mượn (ngày, độc giả, thủ thư); chi tiết (cuốn, hạn trả, phiếu trả); phiếu trả (ngày, độc giả, thủ thư) |
| Phạt | Cuốn trả muộn, số ngày trễ, số tiền, đã thanh toán, ngày thanh toán |
| Phòng đọc | Loại phòng (giá/giờ, số giờ tối thiểu/tối đa), phòng (tên, sức chứa, chi nhánh); phiếu thuê (độc giả, phòng, thủ thư duyệt, bắt đầu, kết thúc, số người, mục đích, tổng tiền, trạng thái) |
| Thanh lý | Cuốn đã thanh lý, ngày, lý do |

## 1.3 Các ứng dụng triển khai trên CSDL

Tại mỗi chi nhánh:

1. Thêm/xóa/sửa/tìm kiếm độc giả, thủ thư, chi nhánh, đầu sách, cuốn sách, giá sách, phòng kho, phòng đọc (stored procedure, kèm ràng buộc).
2. Mượn sách (1–10 cuốn/lần), trả sách (1–n cuốn/lần), thanh toán phạt; số sách trên giá tự giảm/tăng.
3. Nhập lô sách mới; thanh lý sách hết niên hạn.
4. Đăng ký độc giả, gia hạn thẻ; thuê phòng đọc.
5. Báo cáo theo đề:
   - Sách đang được mượn, sắp theo hạn trả.
   - Sách quá hạn, sắp theo số ngày quá hạn.
   - Đầu sách theo lượt mượn nhiều nhất.
   - Độc giả có sách trả muộn, sắp theo tổng tiền phạt rồi số sách trả muộn (giảm dần).
   - Sách sắp hết hạn sử dụng (còn dưới 2 năm).
   - Phòng đọc đang có / chưa có người dùng tại một thời điểm.

## 1.4 Ràng buộc về số lượng bản ghi

| Ràng buộc | Nguồn | Cách cài đặt |
| --- | --- | --- |
| Mỗi phiếu mượn 1–10 cuốn | Đề | Trigger TRG1 (≤ 10), transaction TX1 (≥ 1) |
| Mỗi độc giả ≤ 50 cuốn chưa trả | Đề | Trigger TRG2 |
| Mỗi phiếu trả ≥ 1 cuốn | Đề | Transaction TX2 |
| Mỗi giá ≤ sức chứa (100) | Nhóm | CHECK + trigger TRG6 |
| Số người thuê ≤ sức chứa phòng | Nhóm | Transaction TX7 |
| Mỗi chi nhánh đúng 1 thủ thư trưởng; 1 thủ thư trưởng 1 chi nhánh | Nhóm | UNIQUE + FK; cột tạm cho phép NULL vì khóa ngoại vòng CHI_NHANH ↔ THU_THU (MariaDB không có ràng buộc trì hoãn), được gán ngay sau khi tạo thủ thư; không xóa được thủ thư đang là trưởng (E403) |
| Mỗi độc giả đúng 1 thẻ | Nhóm | UNIQUE trên khóa ngoại |
| Mỗi người ≥ 1 số điện thoại | Nhóm | Transaction TX6 |

# CHƯƠNG 2. LƯỢC ĐỒ THỰC THỂ – LIÊN KẾT

## 2.1 Tập thực thể

| Tập thực thể | Loại | Khóa | Thuộc tính |
| --- | --- | --- | --- |
| CHI_NHANH | Mạnh | MaChiNhanh | TenChiNhanh, DiaChi, GioMo, GioDong |
| NGUOI | Mạnh, lớp cha | MaNguoi | HoTen *(kép: Ho, Dem, Ten)*, NgaySinh, Tuoi *(dẫn xuất)*, GioiTinh, DiaChi *(kép: SoNha, Phuong, Quan, TinhTP)*, Email, SoDienThoai *(đa trị)* |
| DOC_GIA | Lớp con ISA | (kế thừa MaNguoi) | NgayDangKy, TrangThai |
| THU_THU | Lớp con ISA | (kế thừa MaNguoi) | NgayVaoLam |
| THE_DOC_GIA | Mạnh | SoThe | NgayCap, NgayHetHan, ConHan *(dẫn xuất)* |
| THE_LOAI | Mạnh | MaTheLoai | TenTheLoai, SoNgayMuon, TuoiThoNam |
| BANG_PHI_PHAT | **Yếu** (chủ: THE_LOAI) | khóa bán phần NgayApDung | PhatCoBan, PhatMoiNgay |
| TAC_GIA | Mạnh | MaTacGia | TenTacGia, QuocTich |
| DAU_SACH | Mạnh | MaDauSach | TenSach, NhaXuatBan, NamXuatBan, SoNgayMuonRieng *(rỗng được)*, SoLuotMuon *(dẫn xuất)* |
| CUON_SACH | **Yếu** (chủ: DAU_SACH) | khóa bán phần STT | NgayNhap, TuoiThoConLaiThang, TrangThai |
| PHONG_KHO | Mạnh | MaPhongKho | TenPhong, Tang |
| GIA_SACH | Mạnh | MaGia | SucChua, SoLuongHienCo *(dẫn xuất, lưu để tăng/giảm như đề)* |
| SACH_THANH_LY | Mạnh (danh mục lưu trữ) | MaCuonSach | NgayNhap, NgayThanhLy, LyDo |
| PHIEU_MUON | Mạnh | MaPhieuMuon | NgayMuon |
| PHIEU_TRA | Mạnh | MaPhieuTra | NgayTra |
| PHIEU_PHAT | Mạnh | MaPhieuPhat | SoNgayTre, SoTien *(dẫn xuất, lưu lại)*, DaThanhToan, NgayThanhToan *(rỗng được)* |
| LOAI_PHONG | Mạnh | MaLoaiPhong | TenLoai, GiaMoiGio, SoGioToiThieu, SoGioToiDa |
| PHONG_DOC | Mạnh | MaPhongDoc | TenPhong, SucChua |
| PHIEU_THUE_PHONG | Mạnh | MaPhieuThue | BatDau, KetThuc, SoNguoi, MucDich, TongTien *(dẫn xuất)*, TrangThai |

## 2.2 Liên kết

| Liên kết | Tập tham gia | Lực lượng | Tham gia | Thuộc tính / ghi chú |
| --- | --- | --- | --- | --- |
| ISA | NGUOI → DOC_GIA, THU_THU | — | Toàn bộ, **disjoint** (phân biệt bằng LoaiNguoi = 'DG'/'TT') | Cụ thể hóa |
| truong_chi_nhanh | THU_THU – CHI_NHANH | **1:1** | CHI_NHANH toàn bộ, THU_THU một phần | Thủ thư trưởng |
| lam_viec_tai | THU_THU – CHI_NHANH | N:1 | Toàn bộ phía THU_THU | |
| quan_ly | THU_THU – THU_THU | 1:N **đệ quy** | Một phần | Vai trò: người quản lý / nhân viên |
| dang_ky_tai | DOC_GIA – CHI_NHANH | N:1 | Toàn bộ phía DOC_GIA | |
| so_huu_the | DOC_GIA – THE_DOC_GIA | 1:1 | Toàn bộ hai phía | |
| thuoc_the_loai | DAU_SACH – THE_LOAI | N:1 | Toàn bộ phía DAU_SACH | |
| ap_dung_phi | THE_LOAI – BANG_PHI_PHAT | 1:N | **Liên kết xác định** (thực thể yếu) | |
| viet | DAU_SACH – TAC_GIA | **N:N** | | Từ thuộc tính đa trị "tác giả" |
| gom_cuon | DAU_SACH – CUON_SACH | 1:N | **Liên kết xác định** | |
| dat_tai | CUON_SACH – GIA_SACH | N:1 | Toàn bộ phía CUON_SACH | |
| chua_the_loai | GIA_SACH – THE_LOAI | N:1 | Toàn bộ phía GIA_SACH | Giá chỉ chứa 1 thể loại |
| nam_trong | GIA_SACH – PHONG_KHO | N:1 | Toàn bộ | |
| thuoc_chi_nhanh | PHONG_KHO – CHI_NHANH | N:1 | Toàn bộ | |
| **muon** | THU_THU – DOC_GIA – CUON_SACH | **3 ngôi** | | Ở mức khái niệm: một lần mượn liên quan đồng thời thủ thư, độc giả, cuốn sách; được hiện thực hóa bằng thực thể PHIEU_MUON + liên kết gom_sach |
| lap_phieu_muon | THU_THU – PHIEU_MUON | 1:N | | |
| muon_boi | DOC_GIA – PHIEU_MUON | 1:N | | |
| gom_sach | PHIEU_MUON – CUON_SACH | **N:N** | Ràng buộc **(1,10)** phía PHIEU_MUON | Thuộc tính HanTra |
| tra_lai | PHIEU_TRA – [gom_sach] | 1:N | **Kết hợp (aggregation)**: phiếu trả liên kết với cặp (phiếu mượn, cuốn sách) | Mỗi dòng mượn được trả đúng một lần |
| bi_phat | PHIEU_PHAT – [gom_sach] | 1:1 | **Kết hợp** | Chỉ dòng trả muộn |
| lap_phieu_tra | THU_THU – PHIEU_TRA | 1:N | | |
| tra_boi | DOC_GIA – PHIEU_TRA | 1:N | | |
| giu_sach | DOC_GIA – CUON_SACH | ràng buộc **(0,50)** | | Số cuốn chưa trả tại một thời điểm (suy ra từ gom_sach) |
| thuoc_loai | PHONG_DOC – LOAI_PHONG | N:1 | Toàn bộ | |
| phong_cua | PHONG_DOC – CHI_NHANH | N:1 | Toàn bộ | |
| **thue_phong** | DOC_GIA – PHONG_DOC – THU_THU | **3 ngôi** M:N:1 | | Vẽ trực tiếp trên ERD: mỗi lần thuê gắn một độc giả, một phòng và **một** thủ thư duyệt; thuộc tính của liên kết: NgayDat, BatDau, KetThuc, SoNguoi, MucDich, TrangThai, TongTien (dẫn xuất). Một độc giả có thể thuê cùng một phòng nhiều lần ở các khung giờ khác nhau |
| thanh_ly_tu | SACH_THANH_LY – DAU_SACH | N:1 | | Giữ được thông tin đầu sách sau khi thanh lý |

## 2.3 Đối chiếu yêu cầu "đầy đủ các loại" của đề

| Loại | Có trong lược đồ |
| --- | --- |
| Tập thực thể mạnh | CHI_NHANH, DAU_SACH, PHIEU_MUON, … |
| Tập thực thể yếu | CUON_SACH (của DAU_SACH), BANG_PHI_PHAT (của THE_LOAI) |
| Thuộc tính đơn, đơn trị | TenSach, NgayMuon, … |
| Thuộc tính kép | HoTen, DiaChi |
| Thuộc tính đa trị | SoDienThoai; tác giả của đầu sách |
| Thuộc tính dẫn xuất | Tuoi, ConHan, SoLuotMuon, SoTien, TongTien |
| Thuộc tính rỗng | SoNgayMuonRieng, NgayThanhToan, phiếu trả của dòng mượn chưa trả |
| Khóa chính, khóa bán phần | MaDauSach; STT, NgayApDung |
| Liên kết 1:1, 1:N, N:N | truong_chi_nhanh; thuoc_the_loai; viet, gom_sach |
| Liên kết đệ quy | quan_ly |
| Liên kết 3 ngôi | thue_phong (DOC_GIA – PHONG_DOC – THU_THU, vẽ trên ERD); muon (mức khái niệm, hiện thực bằng PHIEU_MUON + gom_sach) |
| Liên kết xác định | gom_cuon, ap_dung_phi |
| ISA (disjoint, toàn bộ) | NGUOI → DOC_GIA, THU_THU |
| Kết hợp (aggregation) | tra_lai, bi_phat trên [gom_sach] |
| Ràng buộc (min,max) | (1,10) cuốn/phiếu; (0,50) cuốn/độc giả |
| Tham gia toàn bộ / một phần | CHI_NHANH – truong_chi_nhanh (toàn bộ: hai vạch ở đầu THU_THU); THU_THU (một phần: vòng tròn ở đầu CHI_NHANH) |

## 2.4 Sơ đồ E-R

Sơ đồ dùng ký hiệu Chen như bài giảng: chữ nhật = tập thực thể, chữ nhật kép = thực thể yếu, thoi = liên kết, thoi kép = liên kết xác định, ellipse = thuộc tính (gạch chân = khóa, gạch chân mảnh = khóa bán phần, nét đứt = dẫn xuất, viền kép = đa trị), tam giác ISA có chữ d = phân tách (disjoint), thoi nét đứt gom_sach = kết hợp (aggregation), thoi màu cam thue_phong = liên kết 3 ngôi giữa DOC_GIA, PHONG_DOC và THU_THU (thủ thư duyệt) mang các thuộc tính của lượt thuê. Ký hiệu đường nối theo chuẩn chân gà (crow's foot), đặt ở đầu sát thực thể và đọc ngang qua liên kết (số thực thể phía đó ứng với một thực thể phía bên kia): vạch + vòng tròn = không hoặc một (0..1); hai vạch = một và chỉ một (1); chân gà + vòng tròn = không hoặc nhiều (0..N); chân gà + vạch = một hoặc nhiều (1..N). Vạch (min = 1) ở đầu bên kia thể hiện thực thể tham gia toàn bộ, vòng tròn (min = 0) là tham gia một phần. Giới hạn cụ thể ghi kèm: tối đa 10 cuốn mỗi phiếu (gom_sach), tối đa 50 cuốn mỗi độc giả (giu_sach). Riêng tổng quát hóa ISA dùng đường đôi = tổng quát hóa đầy đủ.

![Hình 2.1. Lược đồ E-R của hệ thống quản lý thư viện](../erd/erd_doc.png)

# CHƯƠNG 3. LƯỢC ĐỒ QUAN HỆ VÀ CHUẨN HÓA

Ký hiệu: khóa chính in **đậm**, khóa ngoại ghi `FK → BẢNG`. Thuộc tính dẫn xuất không lưu (Tuoi, ConHan, SoLuotMuon) được tính bằng function/view; SoLuongHienCo, SoTien, TongTien được lưu lại có chủ đích (giải thích ở 3.4).

## 3.1 Quy tắc ánh xạ đã dùng

| Thành phần ERD | Quy tắc (chương 3b) | Kết quả |
| --- | --- | --- |
| Thực thể mạnh | Mỗi tập thực thể → 1 quan hệ, định danh → PK | CHI_NHANH, THE_LOAI, TAC_GIA, DAU_SACH, PHONG_KHO, GIA_SACH, … |
| Thuộc tính kép HoTen, DiaChi | Chỉ giữ các thành phần đơn | Ho, Dem, Ten; SoNha, Phuong, Quan, TinhTP |
| Thuộc tính đa trị SoDienThoai | Tách quan hệ mới (PK chủ + giá trị) | SDT_NGUOI |
| Thuộc tính đa trị tác giả → liên kết N:N viet | Quan hệ liên kết, PK = tổ hợp 2 PK | DAU_SACH_TAC_GIA |
| Thực thể yếu CUON_SACH, BANG_PHI_PHAT | PK = PK thực thể xác định + khóa bán phần | CUON_SACH(MaDauSach, STT) – thay bằng mã ghép MaCuonSach làm PK, (MaDauSach, STT) giữ làm khóa dự bị; BANG_PHI_PHAT(MaTheLoai, NgayApDung) |
| ISA disjoint toàn bộ | Bảng cha + bảng con dùng chung PK (FK → cha, ON DELETE CASCADE) + thuộc tính phân biệt | NGUOI(LoaiNguoi), DOC_GIA, THU_THU |
| 1:1 truong_chi_nhanh | FK đặt ở bên tham gia toàn bộ (CHI_NHANH), thêm UNIQUE | CHI_NHANH.MaThuThuTruong |
| 1:1 so_huu_the | FK + UNIQUE ở THE_DOC_GIA | THE_DOC_GIA.MaDocGia UNIQUE |
| 1:N | PK phía 1 thành FK phía N | DAU_SACH.MaTheLoai, CUON_SACH.MaGia, … |
| Đệ quy 1:N quan_ly | FK đệ quy tham chiếu chính bảng | THU_THU.MaQuanLy → THU_THU |
| N:N gom_sach có thuộc tính | Quan hệ mới, PK = (MaPhieuMuon, MaCuonSach), thêm HanTra | CT_MUON |
| Kết hợp tra_lai (1:N vào [gom_sach]) | FK phía nhiều đặt vào quan hệ của kết hợp | CT_MUON.MaPhieuTra (NULL khi chưa trả) |
| Kết hợp bi_phat (1:1 vào [gom_sach]) | Quan hệ mới tham chiếu PK của kết hợp + UNIQUE | PHIEU_PHAT(MaPhieuMuon, MaCuonSach) |
| Liên kết 3 ngôi muon | Thực thể kết hợp PHIEU_MUON giữ FK tới DOC_GIA, THU_THU; chi tiết tới CUON_SACH | PHIEU_MUON + CT_MUON |
| Liên kết 3 ngôi thue_phong (M:N:1) có thuộc tính | Quan hệ mới chứa PK của cả 3 tập thực thể làm FK + thuộc tính của liên kết. Khóa tự nhiên (MaDocGia, MaPhongDoc, BatDau) vì một độc giả thuê cùng phòng nhiều lần; dùng khóa thay thế MaPhieuThue cho gọn, còn ràng buộc "không trùng giờ trên một phòng" kiểm tra trong TX7. Phía THU_THU là 1 nên MaThuThuDuyet không cần nằm trong khóa | PHIEU_THUE_PHONG(MaPhieuThue, MaDocGia, MaPhongDoc, MaThuThuDuyet, …) |

## 3.2 Tập lược đồ quan hệ (23 quan hệ)

| # | Lược đồ | Khóa ngoại | Khóa dự bị khác |
| --- | --- | --- | --- |
| 1 | CHI_NHANH(**MaChiNhanh**, TenChiNhanh, DiaChi, GioMo, GioDong, MaThuThuTruong) | MaThuThuTruong → THU_THU | TenChiNhanh; MaThuThuTruong |
| 2 | NGUOI(**MaNguoi**, Ho, Dem, Ten, NgaySinh, GioiTinh, SoNha, Phuong, Quan, TinhTP, Email, LoaiNguoi) | — | Email |
| 3 | SDT_NGUOI(**MaNguoi, SoDienThoai**) | MaNguoi → NGUOI | — |
| 4 | DOC_GIA(**MaNguoi**, MaChiNhanh, NgayDangKy, TrangThai) | MaNguoi → NGUOI; MaChiNhanh → CHI_NHANH | — |
| 5 | THE_DOC_GIA(**SoThe**, MaDocGia, NgayCap, NgayHetHan) | MaDocGia → DOC_GIA | MaDocGia |
| 6 | THU_THU(**MaNguoi**, MaChiNhanh, NgayVaoLam, MaQuanLy) | MaNguoi → NGUOI; MaChiNhanh → CHI_NHANH; MaQuanLy → THU_THU | — |
| 7 | THE_LOAI(**MaTheLoai**, TenTheLoai, SoNgayMuon, TuoiThoNam) | — | TenTheLoai |
| 8 | BANG_PHI_PHAT(**MaTheLoai, NgayApDung**, PhatCoBan, PhatMoiNgay) | MaTheLoai → THE_LOAI | — |
| 9 | TAC_GIA(**MaTacGia**, TenTacGia, QuocTich) | — | — |
| 10 | DAU_SACH(**MaDauSach**, MaTheLoai, TenSach, NhaXuatBan, NamXuatBan, SoNgayMuonRieng) | MaTheLoai → THE_LOAI | — |
| 11 | DAU_SACH_TAC_GIA(**MaDauSach, MaTacGia**) | → DAU_SACH; → TAC_GIA | — |
| 12 | PHONG_KHO(**MaPhongKho**, MaChiNhanh, TenPhong, Tang) | MaChiNhanh → CHI_NHANH | (MaChiNhanh, TenPhong) |
| 13 | GIA_SACH(**MaGia**, MaPhongKho, MaTheLoai, SucChua, SoLuongHienCo) | → PHONG_KHO; → THE_LOAI | — |
| 14 | CUON_SACH(**MaCuonSach**, MaDauSach, STT, MaGia, NgayNhap, TuoiThoConLaiThang, TrangThai) | → DAU_SACH; → GIA_SACH | (MaDauSach, STT) |
| 15 | SACH_THANH_LY(**MaCuonSach**, MaDauSach, STT, NgayNhap, NgayThanhLy, LyDo) | MaDauSach → DAU_SACH | (MaDauSach, STT) |
| 16 | PHIEU_MUON(**MaPhieuMuon**, MaDocGia, MaThuThu, NgayMuon) | → DOC_GIA; → THU_THU | — |
| 17 | PHIEU_TRA(**MaPhieuTra**, MaDocGia, MaThuThu, NgayTra) | → DOC_GIA; → THU_THU | — |
| 18 | CT_MUON(**MaPhieuMuon, MaCuonSach**, HanTra, MaPhieuTra) | → PHIEU_MUON; → CUON_SACH; MaPhieuTra → PHIEU_TRA (NULL được) | — |
| 19 | PHIEU_PHAT(**MaPhieuPhat**, MaPhieuMuon, MaCuonSach, SoNgayTre, SoTien, DaThanhToan, NgayThanhToan) | (MaPhieuMuon, MaCuonSach) → CT_MUON | (MaPhieuMuon, MaCuonSach) |
| 20 | LOAI_PHONG(**MaLoaiPhong**, TenLoai, GiaMoiGio, SoGioToiThieu, SoGioToiDa) | — | TenLoai |
| 21 | PHONG_DOC(**MaPhongDoc**, MaChiNhanh, MaLoaiPhong, TenPhong, SucChua) | → CHI_NHANH; → LOAI_PHONG | (MaChiNhanh, TenPhong) |
| 22 | PHIEU_THUE_PHONG(**MaPhieuThue**, MaDocGia, MaPhongDoc, MaThuThuDuyet, NgayDat, BatDau, KetThuc, SoNguoi, MucDich, TongTien, TrangThai) | → DOC_GIA; → PHONG_DOC; MaThuThuDuyet → THU_THU | — |
| 23 | CT_MUON_LUU_TRU(**MaPhieuMuon, MaCuonSach**, HanTra, MaPhieuTra, TienPhat) | → PHIEU_MUON; → PHIEU_TRA; MaCuonSach → SACH_THANH_LY | — |

Quan hệ 23 là bảng lưu trữ: khi thanh lý, cuốn sách bị xóa khỏi CUON_SACH nên các dòng CT_MUON của nó (và tiền phạt đã nộp) được chuyển sang đây, giữ lịch sử mượn mà không vi phạm khóa ngoại.

Ghi chú: khóa ngoại vòng CHI_NHANH ↔ THU_THU được tạo bằng `ALTER TABLE` sau khi có cả hai bảng; MaThuThuTruong cho phép NULL trong lúc khởi tạo dữ liệu.

## 3.3 Phụ thuộc hàm, khóa và kiểm tra BCNF từng lược đồ

Phương pháp (chương 3c): với mỗi lược đồ, liệt kê tập F đã tối thiểu (vế phải 1 thuộc tính được gộp cho gọn), tính bao đóng của vế trái để tìm khóa, rồi kiểm tra định nghĩa BCNF: *mọi PTH không hiển nhiên X → A đều có X là siêu khóa*.

| # | Tập F | Khóa (từ bao đóng) | BCNF? |
| --- | --- | --- | --- |
| 1 CHI_NHANH | MaChiNhanh → TenChiNhanh, DiaChi, GioMo, GioDong, MaThuThuTruong; TenChiNhanh → MaChiNhanh; MaThuThuTruong → MaChiNhanh | {MaChiNhanh}⁺ = {TenChiNhanh}⁺ = {MaThuThuTruong}⁺ = toàn bộ → 3 khóa dự bị | Có: mọi vế trái là khóa |
| 2 NGUOI | MaNguoi → mọi thuộc tính; Email → MaNguoi | MaNguoi, Email | Có |
| 3 SDT_NGUOI | Không có PTH không hiển nhiên | Toàn bộ thuộc tính | Có |
| 4 DOC_GIA | MaNguoi → MaChiNhanh, NgayDangKy, TrangThai | MaNguoi | Có |
| 5 THE_DOC_GIA | SoThe → MaDocGia, NgayCap, NgayHetHan; MaDocGia → SoThe | SoThe, MaDocGia | Có |
| 6 THU_THU | MaNguoi → MaChiNhanh, NgayVaoLam, MaQuanLy | MaNguoi | Có |
| 7 THE_LOAI | MaTheLoai → TenTheLoai, SoNgayMuon, TuoiThoNam; TenTheLoai → MaTheLoai | MaTheLoai, TenTheLoai | Có |
| 8 BANG_PHI_PHAT | MaTheLoai, NgayApDung → PhatCoBan, PhatMoiNgay | (MaTheLoai, NgayApDung) | Có |
| 9 TAC_GIA | MaTacGia → TenTacGia, QuocTich | MaTacGia | Có |
| 10 DAU_SACH | MaDauSach → MaTheLoai, TenSach, NhaXuatBan, NamXuatBan, SoNgayMuonRieng | MaDauSach | Có |
| 11 DAU_SACH_TAC_GIA | Không có | Toàn bộ | Có |
| 12 PHONG_KHO | MaPhongKho → MaChiNhanh, TenPhong, Tang; MaChiNhanh, TenPhong → MaPhongKho | MaPhongKho; (MaChiNhanh, TenPhong) | Có |
| 13 GIA_SACH | MaGia → MaPhongKho, MaTheLoai, SucChua, SoLuongHienCo | MaGia | Có |
| 14 CUON_SACH | MaCuonSach → MaDauSach, STT, MaGia, NgayNhap, TuoiThoConLaiThang, TrangThai; MaDauSach, STT → MaCuonSach | MaCuonSach; (MaDauSach, STT) | Có |
| 15 SACH_THANH_LY | MaCuonSach → MaDauSach, STT, NgayNhap, NgayThanhLy, LyDo; MaDauSach, STT → MaCuonSach | MaCuonSach; (MaDauSach, STT) | Có |
| 16 PHIEU_MUON | MaPhieuMuon → MaDocGia, MaThuThu, NgayMuon | MaPhieuMuon | Có |
| 17 PHIEU_TRA | MaPhieuTra → MaDocGia, MaThuThu, NgayTra | MaPhieuTra | Có |
| 18 CT_MUON | MaPhieuMuon, MaCuonSach → HanTra, MaPhieuTra | (MaPhieuMuon, MaCuonSach) | Có |
| 19 PHIEU_PHAT | MaPhieuPhat → mọi thuộc tính; MaPhieuMuon, MaCuonSach → MaPhieuPhat | MaPhieuPhat; (MaPhieuMuon, MaCuonSach) | Có |
| 20 LOAI_PHONG | MaLoaiPhong → TenLoai, GiaMoiGio, SoGioToiThieu, SoGioToiDa; TenLoai → MaLoaiPhong | MaLoaiPhong, TenLoai | Có |
| 21 PHONG_DOC | MaPhongDoc → MaChiNhanh, MaLoaiPhong, TenPhong, SucChua; MaChiNhanh, TenPhong → MaPhongDoc | MaPhongDoc; (MaChiNhanh, TenPhong) | Có |
| 22 PHIEU_THUE_PHONG | MaPhieuThue → mọi thuộc tính | MaPhieuThue | Có |
| 23 CT_MUON_LUU_TRU | MaPhieuMuon, MaCuonSach → HanTra, MaPhieuTra, TienPhat | (MaPhieuMuon, MaCuonSach) | Có |

**Các PTH đã cân nhắc và bác bỏ** (cần nêu trong báo cáo vì đây là chỗ dễ bị hỏi):

- NGUOI: *Phuong → Quan*, *Quan → TinhTP* không đúng ở Việt Nam (nhiều quận/huyện có phường trùng tên, nhiều tỉnh có quận/huyện trùng tên), nên địa chỉ không gây phụ thuộc bắc cầu. Nếu nhóm quyết định coi chúng là PTH thì phải tách bảng PHUONG, QUAN, TINH.
- CUON_SACH: *MaGia → MaTheLoai* và *MaDauSach → MaTheLoai* đều đúng về nghiệp vụ, nhưng MaTheLoai **không** nằm trong CUON_SACH nên không vi phạm. Ràng buộc "giá và đầu sách cùng thể loại" là ràng buộc liên bảng, cài bằng trigger TRG6.
- CT_MUON: HanTra được tính từ NgayMuon và thể loại tại thời điểm mượn, nhưng sau đó là một **sự kiện được lưu** (có thể gia hạn), không phải PTH trên các thuộc tính của CT_MUON.

## 3.4 Thuộc tính dẫn xuất được lưu

| Thuộc tính | Lý do lưu | Cách giữ đúng |
| --- | --- | --- |
| GIA_SACH.SoLuongHienCo | Đề yêu cầu "số lượng sách trên giá giảm/tăng" khi mượn/trả | Trigger TRG4 |
| PHIEU_PHAT.SoTien | Ảnh chụp số tiền tại thời điểm trả; phí phạt có thể đổi theo NgayApDung | Trigger TRG3 dùng fn_TinhTienPhat |
| PHIEU_THUE_PHONG.TongTien | Giá phòng có thể thay đổi sau khi đặt | Tính trong TX7 |
| CUON_SACH.TuoiThoConLaiThang | Trạng thái của cuốn, giảm theo số lần mượn | Trigger TRG5 |

## 3.5 Ví dụ quá trình chuẩn hóa từ dạng chưa chuẩn

Để minh họa phương pháp, xét "phiếu mượn" dạng giấy, ghi chung mọi thông tin:

PM(MaPhieuMuon, NgayMuon, MaDocGia, TenDocGia, SoDienThoai, MaThuThu, TenThuThu, {MaCuonSach, MaDauSach, TenSach, MaTheLoai, SoNgayMuon, HanTra})

**N1NF → 1NF.** Nhóm lặp {…} (một phiếu nhiều cuốn) và SoDienThoai đa trị vi phạm 1NF. Tách SĐT ra SDT_NGUOI; trải phẳng nhóm lặp, mỗi cuốn một dòng:

R(MaPhieuMuon, NgayMuon, MaDocGia, TenDocGia, MaThuThu, TenThuThu, MaCuonSach, MaDauSach, TenSach, MaTheLoai, SoNgayMuon, HanTra)

F = { MaPhieuMuon → NgayMuon, MaDocGia, MaThuThu;
      MaDocGia → TenDocGia;  MaThuThu → TenThuThu;
      MaCuonSach → MaDauSach;  MaDauSach → TenSach, MaTheLoai;  MaTheLoai → SoNgayMuon;
      MaPhieuMuon, MaCuonSach → HanTra }

**Tìm khóa** bằng thuật toán Closure: MaPhieuMuon và MaCuonSach không xuất hiện ở vế phải của PTH nào nên phải thuộc mọi khóa.
{MaPhieuMuon, MaCuonSach}⁺: khởi tạo {MaPhieuMuon, MaCuonSach} → thêm NgayMuon, MaDocGia, MaThuThu → TenDocGia, TenThuThu → MaDauSach → TenSach, MaTheLoai → SoNgayMuon → HanTra = toàn bộ R. Không tập con thực sự nào đủ ⇒ **K = (MaPhieuMuon, MaCuonSach)** là khóa duy nhất. Thuộc tính khóa: MaPhieuMuon, MaCuonSach.

**1NF → 2NF.** Có PTH bộ phận: MaPhieuMuon → NgayMuon, MaDocGia, MaThuThu (và theo bắc cầu TenDocGia, TenThuThu); MaCuonSach → MaDauSach (và TenSach, MaTheLoai, SoNgayMuon). Tách theo phần khóa mà chúng phụ thuộc:
- R1(MaPhieuMuon, NgayMuon, MaDocGia, TenDocGia, MaThuThu, TenThuThu)
- R2(MaCuonSach, MaDauSach, TenSach, MaTheLoai, SoNgayMuon)
- R3(MaPhieuMuon, MaCuonSach, HanTra)

**2NF → 3NF.** R1 có bắc cầu MaPhieuMuon → MaDocGia → TenDocGia và MaPhieuMuon → MaThuThu → TenThuThu; R2 có MaCuonSach → MaDauSach → MaTheLoai → SoNgayMuon. Theo cách 2 (tổng hợp từ phủ tối thiểu), mỗi PTH của phủ tối thiểu một lược đồ:
- PHIEU_MUON(MaPhieuMuon, NgayMuon, MaDocGia, MaThuThu)
- DOC_GIA(MaDocGia, TenDocGia), THU_THU(MaThuThu, TenThuThu)
- CUON_SACH(MaCuonSach, MaDauSach)
- DAU_SACH(MaDauSach, TenSach, MaTheLoai)
- THE_LOAI(MaTheLoai, SoNgayMuon)
- CT_MUON(MaPhieuMuon, MaCuonSach, HanTra) — chứa khóa K của R nên không cần thêm lược đồ khóa.

**3NF → BCNF.** Trong mỗi lược đồ trên, vế trái của mọi PTH đều là khóa của lược đồ đó ⇒ tất cả ở BCNF. Phép tách bảo toàn PTH (mỗi PTH nằm trọn trong một lược đồ) và kết nối không mất thông tin (CT_MUON chứa khóa của R). Kết quả trùng với các quan hệ 16, 18, 14, 10, 7 ở mục 3.2.

## 3.6 Ví dụ tìm phủ tối thiểu (thuật toán MinCover)

Phương án ban đầu của nhóm lưu cả MaTheLoai trong CUON_SACH, với tập PTH:

G = { MaCuonSach → MaDauSach, STT, MaTheLoai;  MaDauSach → MaTheLoai;  MaDauSach, STT → MaCuonSach;  MaDauSach, STT, MaTheLoai → MaCuonSach }

1. **Tách vế phải:** MaCuonSach → MaDauSach; MaCuonSach → STT; MaCuonSach → MaTheLoai; MaDauSach → MaTheLoai; MaDauSach, STT → MaCuonSach; MaDauSach, STT, MaTheLoai → MaCuonSach.
2. **Left-Reduce:** ở MaDauSach, STT, MaTheLoai → MaCuonSach, thử bỏ MaTheLoai: {MaDauSach, STT}⁺ = {MaDauSach, STT, MaCuonSach, MaTheLoai} chứa MaCuonSach ⇒ MaTheLoai thừa, PTH trở thành MaDauSach, STT → MaCuonSach (trùng PTH đã có). Ở MaDauSach, STT → MaCuonSach: {MaDauSach}⁺ = {MaDauSach, MaTheLoai}, {STT}⁺ = {STT}, đều không chứa MaCuonSach ⇒ không bỏ được.
3. **Nonredundant:** MaCuonSach → MaTheLoai: tính {MaCuonSach}⁺ trên G bỏ PTH này = {MaCuonSach, MaDauSach, STT, MaTheLoai} vẫn chứa MaTheLoai (bắc cầu qua MaDauSach) ⇒ loại.

**Phủ tối thiểu:** { MaCuonSach → MaDauSach; MaCuonSach → STT; MaDauSach → MaTheLoai; MaDauSach, STT → MaCuonSach }.

**Khóa:** {MaCuonSach}⁺ và {MaDauSach, STT}⁺ đều là toàn bộ lược đồ ⇒ hai khóa dự bị.

**Kiểm tra BCNF:** MaDauSach → MaTheLoai có vế trái không phải siêu khóa ⇒ vi phạm BCNF (cũng vi phạm 2NF, vì MaTheLoai là thuộc tính không khóa phụ thuộc bộ phận vào khóa (MaDauSach, STT)).

**Tách BCNF:** chọn PTH vi phạm MaDauSach → MaTheLoai, tính {MaDauSach}⁺ = {MaDauSach, MaTheLoai}: R1(MaDauSach, MaTheLoai) gộp vào DAU_SACH; R2 = CUON_SACH bỏ MaTheLoai. Đây là lý do thiết kế cuối cùng của CUON_SACH không có cột MaTheLoai; thể loại vẫn đọc được từ 2 ký tự đầu của mã.

## 3.7 Sơ đồ lược đồ quan hệ

Sơ đồ được sinh tự động từ `information_schema` của CSDL đã cài đặt (script `gen_tudien.py`): mỗi khung là một quan hệ, khóa chính in đậm gạch chân, khóa ngoại in nghiêng, mỗi cạnh nối cột khóa ngoại với khóa chính được tham chiếu và dùng ký hiệu chân gà suy ra từ ràng buộc thật: đầu bảng chứa khóa ngoại là không hoặc nhiều (không hoặc một nếu cột khóa ngoại là UNIQUE), đầu bảng được tham chiếu là một và chỉ một (không hoặc một nếu khóa ngoại cho phép NULL). Màu nền tiêu đề chia 4 nhóm nghiệp vụ: con người (xanh dương), sách và kho (xanh lá), mượn trả (cam), phòng đọc (vàng).

![Hình 3.1. Sơ đồ lược đồ quan hệ với các liên kết khóa chính – khóa ngoại](../erd/luoc_do_quan_he.png)

## 3.8 Từ điển dữ liệu

Từ điển dữ liệu được trích tự động từ `information_schema` của CSDL đã cài đặt (kiểu dữ liệu, cho phép NULL, khóa, giá trị mặc định). Ký hiệu cột Khóa: **PK** khóa chính, **FK → Bảng** khóa ngoại, **UQ** thuộc ràng buộc UNIQUE. Các ràng buộc CHECK của từng bảng liệt kê ở mục 4.4.

**1. CHI_NHANH** – Chi nhánh thư viện

| Cột | Kiểu dữ liệu | NULL | Khóa | Mặc định | Mô tả |
| --- | --- | --- | --- | --- | --- |
| MaChiNhanh | char(4) | Không | PK |  | Mã chi nhánh, dạng CN01 |
| TenChiNhanh | varchar(100) | Không | UQ |  | Tên chi nhánh |
| DiaChi | varchar(200) | Không |  |  | Địa chỉ chi nhánh |
| GioMo | time | Không |  | 07:00:00 | Giờ mở cửa |
| GioDong | time | Không |  | 21:00:00 | Giờ đóng cửa |
| MaThuThuTruong | varchar(10) | Có | FK → THU_THU, UQ |  | Thủ thư trưởng chi nhánh (1:1) |

**2. NGUOI** – Người – lớp cha của độc giả và thủ thư (ISA)

| Cột | Kiểu dữ liệu | NULL | Khóa | Mặc định | Mô tả |
| --- | --- | --- | --- | --- | --- |
| MaNguoi | varchar(10) | Không | PK |  | Mã người: DGxxxx (độc giả) hoặc TTxxx (thủ thư) |
| Ho | varchar(30) | Không |  |  | Họ |
| Dem | varchar(30) | Có |  |  | Tên đệm |
| Ten | varchar(30) | Không |  |  | Tên |
| NgaySinh | date | Không |  |  | Ngày sinh |
| GioiTinh | char(1) | Không |  |  | Giới tính M/F |
| SoNha | varchar(50) | Có |  |  | Số nhà |
| Phuong | varchar(50) | Có |  |  | Phường |
| Quan | varchar(50) | Có |  |  | Quận |
| TinhTP | varchar(50) | Không |  |  | Tỉnh/thành phố |
| Email | varchar(100) | Có | UQ |  | Thư điện tử |
| LoaiNguoi | char(2) | Không |  |  | Thuộc tính phân biệt ISA: DG / TT |

**3. SDT_NGUOI** – Số điện thoại của người (thuộc tính đa trị)

| Cột | Kiểu dữ liệu | NULL | Khóa | Mặc định | Mô tả |
| --- | --- | --- | --- | --- | --- |
| MaNguoi | varchar(10) | Không | PK, FK → NGUOI |  | Mã người: DGxxxx (độc giả) hoặc TTxxx (thủ thư) |
| SoDienThoai | varchar(10) | Không | PK |  | Một số điện thoại |

**4. DOC_GIA** – Độc giả (lớp con)

| Cột | Kiểu dữ liệu | NULL | Khóa | Mặc định | Mô tả |
| --- | --- | --- | --- | --- | --- |
| MaNguoi | varchar(10) | Không | PK, FK → NGUOI |  | Mã người: DGxxxx (độc giả) hoặc TTxxx (thủ thư) |
| MaChiNhanh | char(4) | Không | FK → CHI_NHANH |  | Chi nhánh đăng ký |
| NgayDangKy | date | Không |  |  | Ngày đăng ký độc giả |
| TrangThai | varchar(10) | Không |  | HoatDong | Trạng thái độc giả |

**5. THE_DOC_GIA** – Thẻ độc giả

| Cột | Kiểu dữ liệu | NULL | Khóa | Mặc định | Mô tả |
| --- | --- | --- | --- | --- | --- |
| SoThe | varchar(12) | Không | PK |  | Số thẻ, dạng THExxxx |
| MaDocGia | varchar(10) | Không | FK → DOC_GIA, UQ |  | Độc giả |
| NgayCap | date | Không |  |  | Ngày cấp thẻ |
| NgayHetHan | date | Không |  |  | Ngày hết hạn thẻ |

**6. THU_THU** – Thủ thư (lớp con)

| Cột | Kiểu dữ liệu | NULL | Khóa | Mặc định | Mô tả |
| --- | --- | --- | --- | --- | --- |
| MaNguoi | varchar(10) | Không | PK, FK → NGUOI |  | Mã người: DGxxxx (độc giả) hoặc TTxxx (thủ thư) |
| MaChiNhanh | char(4) | Không | FK → CHI_NHANH |  | Chi nhánh làm việc |
| NgayVaoLam | date | Không |  |  | Ngày vào làm |
| MaQuanLy | varchar(10) | Có | FK → THU_THU |  | Thủ thư quản lý trực tiếp (đệ quy) |

**7. THE_LOAI** – Thể loại sách

| Cột | Kiểu dữ liệu | NULL | Khóa | Mặc định | Mô tả |
| --- | --- | --- | --- | --- | --- |
| MaTheLoai | char(2) | Không | PK |  | Mã thể loại |
| TenTheLoai | varchar(50) | Không | UQ |  | Tên thể loại |
| SoNgayMuon | smallint(6) | Không |  |  | Số ngày được mượn mặc định |
| TuoiThoNam | tinyint(4) | Không |  |  | Tuổi thọ (năm) của sách thuộc thể loại |

**8. BANG_PHI_PHAT** – Biểu phí phạt theo thể loại (thực thể yếu)

| Cột | Kiểu dữ liệu | NULL | Khóa | Mặc định | Mô tả |
| --- | --- | --- | --- | --- | --- |
| MaTheLoai | char(2) | Không | PK, FK → THE_LOAI |  | Mã thể loại |
| NgayApDung | date | Không | PK |  | Ngày biểu phí bắt đầu có hiệu lực (khóa bán phần) |
| PhatCoBan | decimal(12,0) | Không |  |  | Tiền phạt cơ bản mỗi lần trả muộn (đ) |
| PhatMoiNgay | decimal(12,0) | Không |  |  | Tiền phạt mỗi ngày trễ (đ) |

**9. TAC_GIA** – Tác giả

| Cột | Kiểu dữ liệu | NULL | Khóa | Mặc định | Mô tả |
| --- | --- | --- | --- | --- | --- |
| MaTacGia | int(11) | Không | PK | tự tăng | Mã tác giả |
| TenTacGia | varchar(100) | Không |  |  | Tên tác giả |
| QuocTich | varchar(50) | Có |  |  | Quốc tịch |

**10. DAU_SACH** – Đầu sách

| Cột | Kiểu dữ liệu | NULL | Khóa | Mặc định | Mô tả |
| --- | --- | --- | --- | --- | --- |
| MaDauSach | char(6) | Không | PK |  | Mã đầu sách, dạng TR0012 |
| MaTheLoai | char(2) | Không | FK → THE_LOAI |  | Mã thể loại |
| TenSach | varchar(200) | Không |  |  | Tên sách |
| NhaXuatBan | varchar(100) | Có |  |  | Nhà xuất bản |
| NamXuatBan | smallint(6) | Có |  |  | Năm xuất bản |
| SoNgayMuonRieng | smallint(6) | Có |  |  | Số ngày mượn riêng của đầu sách (NULL = theo thể loại) |

**11. DAU_SACH_TAC_GIA** – Liên kết N:N đầu sách – tác giả

| Cột | Kiểu dữ liệu | NULL | Khóa | Mặc định | Mô tả |
| --- | --- | --- | --- | --- | --- |
| MaDauSach | char(6) | Không | PK, FK → DAU_SACH |  | Mã đầu sách, dạng TR0012 |
| MaTacGia | int(11) | Không | PK, FK → TAC_GIA |  | Mã tác giả |

**12. PHONG_KHO** – Phòng đựng sách

| Cột | Kiểu dữ liệu | NULL | Khóa | Mặc định | Mô tả |
| --- | --- | --- | --- | --- | --- |
| MaPhongKho | varchar(8) | Không | PK |  | Mã phòng kho, dạng CN01-K1 |
| MaChiNhanh | char(4) | Không | FK → CHI_NHANH, UQ |  | Mã chi nhánh, dạng CN01 |
| TenPhong | varchar(50) | Không | UQ |  | Tên phòng |
| Tang | tinyint(4) | Không |  | 1 | Tầng |

**13. GIA_SACH** – Giá sách

| Cột | Kiểu dữ liệu | NULL | Khóa | Mặc định | Mô tả |
| --- | --- | --- | --- | --- | --- |
| MaGia | varchar(12) | Không | PK |  | Mã giá sách, dạng CN01-K1-TR1 |
| MaPhongKho | varchar(8) | Không | FK → PHONG_KHO |  | Mã phòng kho, dạng CN01-K1 |
| MaTheLoai | char(2) | Không | FK → THE_LOAI |  | Thể loại duy nhất của giá |
| SucChua | smallint(6) | Không |  | 100 | Số cuốn tối đa (≤ 100) |
| SoLuongHienCo | smallint(6) | Không |  | 0 | Số cuốn đang nằm trên giá (trigger TRG4 duy trì) |

**14. CUON_SACH** – Cuốn sách (thực thể yếu của đầu sách)

| Cột | Kiểu dữ liệu | NULL | Khóa | Mặc định | Mô tả |
| --- | --- | --- | --- | --- | --- |
| MaCuonSach | varchar(10) | Không | PK |  | Mã cuốn, dạng TR0012-003 |
| MaDauSach | char(6) | Không | FK → DAU_SACH, UQ |  | Mã đầu sách, dạng TR0012 |
| STT | smallint(6) | Không | UQ |  | Số thứ tự cuốn trong đầu sách (khóa bán phần) |
| MaGia | varchar(12) | Không | FK → GIA_SACH |  | Giá đang đặt cuốn sách |
| NgayNhap | date | Không |  |  | Ngày nhập sách |
| TuoiThoConLaiThang | smallint(6) | Không |  |  | Tuổi thọ còn lại (tháng), giảm 1 mỗi lần mượn |
| TrangThai | varchar(12) | Không |  | TrenGia | TrenGia / DangMuon / ChoThanhLy |

**15. SACH_THANH_LY** – Sách đã thanh lý

| Cột | Kiểu dữ liệu | NULL | Khóa | Mặc định | Mô tả |
| --- | --- | --- | --- | --- | --- |
| MaCuonSach | varchar(10) | Không | PK |  | Mã cuốn đã thanh lý |
| MaDauSach | char(6) | Không | FK → DAU_SACH, UQ |  | Mã đầu sách, dạng TR0012 |
| STT | smallint(6) | Không | UQ |  | Số thứ tự cuốn trong đầu sách (khóa bán phần) |
| NgayNhap | date | Không |  |  | Ngày nhập sách |
| NgayThanhLy | date | Không |  |  | Ngày thanh lý |
| LyDo | varchar(200) | Không |  | Hết niên hạn sử dụng | Lý do thanh lý |

**16. PHIEU_MUON** – Phiếu mượn

| Cột | Kiểu dữ liệu | NULL | Khóa | Mặc định | Mô tả |
| --- | --- | --- | --- | --- | --- |
| MaPhieuMuon | int(11) | Không | PK | tự tăng | Số phiếu mượn |
| MaDocGia | varchar(10) | Không | FK → DOC_GIA |  | Độc giả mượn |
| MaThuThu | varchar(10) | Không | FK → THU_THU |  | Thủ thư lập phiếu |
| NgayMuon | date | Không |  |  | Ngày mượn |

**17. PHIEU_TRA** – Phiếu trả

| Cột | Kiểu dữ liệu | NULL | Khóa | Mặc định | Mô tả |
| --- | --- | --- | --- | --- | --- |
| MaPhieuTra | int(11) | Không | PK | tự tăng | Số phiếu trả (NULL khi chưa trả) |
| MaDocGia | varchar(10) | Không | FK → DOC_GIA |  | Độc giả trả sách |
| MaThuThu | varchar(10) | Không | FK → THU_THU |  | Thủ thư nhận trả |
| NgayTra | date | Không |  |  | Ngày trả |

**18. CT_MUON** – Chi tiết mượn – liên kết N:N phiếu mượn – cuốn sách

| Cột | Kiểu dữ liệu | NULL | Khóa | Mặc định | Mô tả |
| --- | --- | --- | --- | --- | --- |
| MaPhieuMuon | int(11) | Không | PK, FK → PHIEU_MUON |  | Số phiếu mượn |
| MaCuonSach | varchar(10) | Không | PK, FK → CUON_SACH |  | Mã cuốn, dạng TR0012-003 |
| HanTra | date | Không |  |  | Hạn trả của cuốn trong phiếu |
| MaPhieuTra | int(11) | Có | FK → PHIEU_TRA |  | Số phiếu trả (NULL khi chưa trả) |

**19. PHIEU_PHAT** – Phiếu phạt trả muộn

| Cột | Kiểu dữ liệu | NULL | Khóa | Mặc định | Mô tả |
| --- | --- | --- | --- | --- | --- |
| MaPhieuPhat | int(11) | Không | PK | tự tăng | Số phiếu phạt |
| MaPhieuMuon | int(11) | Không | FK → CT_MUON, UQ |  | Số phiếu mượn |
| MaCuonSach | varchar(10) | Không | FK → CT_MUON, UQ |  | Mã cuốn, dạng TR0012-003 |
| SoNgayTre | smallint(6) | Không |  |  | Số ngày trả trễ |
| SoTien | decimal(12,0) | Không |  |  | Tiền phạt (đ), tính theo biểu phí có hiệu lực |
| DaThanhToan | tinyint(1) | Không |  | 0 | Đã thanh toán (0/1) |
| NgayThanhToan | date | Có |  |  | Ngày thanh toán phạt |

**20. CT_MUON_LUU_TRU** – Lịch sử mượn của sách đã thanh lý

| Cột | Kiểu dữ liệu | NULL | Khóa | Mặc định | Mô tả |
| --- | --- | --- | --- | --- | --- |
| MaPhieuMuon | int(11) | Không | PK, FK → PHIEU_MUON |  | Số phiếu mượn |
| MaCuonSach | varchar(10) | Không | PK, FK → SACH_THANH_LY |  | Mã cuốn, dạng TR0012-003 |
| HanTra | date | Không |  |  | Hạn trả của cuốn trong phiếu |
| MaPhieuTra | int(11) | Không | FK → PHIEU_TRA |  | Số phiếu trả (NULL khi chưa trả) |
| TienPhat | decimal(12,0) | Không |  | 0 | Tiền phạt (đ) đã phát sinh |

**21. LOAI_PHONG** – Loại phòng đọc

| Cột | Kiểu dữ liệu | NULL | Khóa | Mặc định | Mô tả |
| --- | --- | --- | --- | --- | --- |
| MaLoaiPhong | varchar(8) | Không | PK |  | Mã loại phòng |
| TenLoai | varchar(50) | Không | UQ |  | Tên loại phòng |
| GiaMoiGio | decimal(12,0) | Không |  |  | Giá thuê mỗi giờ (đ) |
| SoGioToiThieu | tinyint(4) | Không |  |  | Số giờ thuê tối thiểu |
| SoGioToiDa | tinyint(4) | Không |  |  | Số giờ thuê tối đa |

**22. PHONG_DOC** – Phòng đọc

| Cột | Kiểu dữ liệu | NULL | Khóa | Mặc định | Mô tả |
| --- | --- | --- | --- | --- | --- |
| MaPhongDoc | varchar(8) | Không | PK |  | Mã phòng đọc, dạng CN01-N1 |
| MaChiNhanh | char(4) | Không | FK → CHI_NHANH, UQ |  | Mã chi nhánh, dạng CN01 |
| MaLoaiPhong | varchar(8) | Không | FK → LOAI_PHONG |  | Mã loại phòng |
| TenPhong | varchar(50) | Không | UQ |  | Tên phòng |
| SucChua | smallint(6) | Không |  |  | Số người tối đa |

**23. PHIEU_THUE_PHONG** – Phiếu thuê phòng (liên kết 3 ngôi thue_phong)

| Cột | Kiểu dữ liệu | NULL | Khóa | Mặc định | Mô tả |
| --- | --- | --- | --- | --- | --- |
| MaPhieuThue | int(11) | Không | PK | tự tăng | Số phiếu thuê (khóa thay thế) |
| MaDocGia | varchar(10) | Không | FK → DOC_GIA |  | Độc giả |
| MaPhongDoc | varchar(8) | Không | FK → PHONG_DOC |  | Mã phòng đọc, dạng CN01-N1 |
| MaThuThuDuyet | varchar(10) | Không | FK → THU_THU |  | Thủ thư duyệt phiếu thuê |
| NgayDat | date | Không |  |  | Ngày đặt |
| BatDau | datetime | Không |  |  | Thời điểm bắt đầu thuê |
| KetThuc | datetime | Không |  |  | Thời điểm kết thúc thuê |
| SoNguoi | smallint(6) | Không |  |  | Số người sử dụng |
| MucDich | varchar(20) | Không |  |  | Mục đích thuê |
| TongTien | decimal(12,0) | Không |  |  | Tổng tiền thuê (đ), lưu tại thời điểm đặt |
| TrangThai | varchar(10) | Không |  | DaDuyet | DaDuyet / DaHuy |

# CHƯƠNG 4. CÀI ĐẶT CƠ SỞ DỮ LIỆU VÀ ỨNG DỤNG

## 4.1 Môi trường và quy trình cài đặt

- Hệ quản trị: **MariaDB** (kiểm thử trên 10.11 LTS, tương thích 11.4 LTS), engine InnoDB, bảng mã `utf8mb4`, collation `utf8mb4_unicode_ci`.
- Giao diện: Python 3 + Streamlit + PyMySQL (chỉ gọi stored procedure / view).
- Mã nguồn chia thành các script chạy theo thứ tự, dựng lại toàn bộ CSDL bằng một lệnh `sh build_all.sh -uroot -p`:

| File | Nội dung |
| --- | --- |
| 01_schema.sql | Tạo database QLTV, 23 bảng và toàn bộ ràng buộc PK, FK, UNIQUE, CHECK, DEFAULT |
| 02_function_procedure.sql | 8 function nghiệp vụ, các procedure thêm/xóa/sửa/tìm kiếm |
| 03_trigger.sql | 8 trigger nghiệp vụ (18 trigger con) |
| 04_transaction.sql | 7 transaction nghiệp vụ dạng procedure |
| 05_seed.sql | Dữ liệu 3 tháng, sinh bởi gen_seed.py bằng cách gọi chính các transaction |
| 06_view_baocao.sql | 6 truy vấn hiển thị theo yêu cầu đề (view + procedure) |
| 07_index_baomat.sql | Chỉ mục tối ưu, vai trò và phân quyền |
| 08_test.sql | 47 ca kiểm thử tự động |
| 09_phan_tan.sql | Minh họa phân mảnh, cấp phát, nhân bản trên 3 site |

Dữ liệu mẫu không nhập tay mà được sinh bằng chương trình mô phỏng thư viện chạy từng ngày từ 01/07 đến 30/09/2026: mỗi ngày phát sinh lời gọi đăng ký độc giả, mượn sách (TX1), trả sách (TX2), nộp phạt (TX3), gia hạn thẻ, thuê phòng (TX7), và thanh lý sách (TX5) giữa kỳ. Nhờ đó mọi bản ghi đều đi qua trigger và kiểm tra nghiệp vụ, dữ liệu luôn hợp lệ; hạt giống ngẫu nhiên cố định giúp mọi lần dựng cho ra cùng một bộ dữ liệu.

## 4.2 Một số lưu ý khi cài đặt trên MariaDB

Bài giảng chương 6 minh họa trigger bằng SQL Server; nhóm cài đặt trên MariaDB nên có các điểm tương ứng sau:

| Slide (SQL Server) | Cài đặt trên MariaDB |
| --- | --- |
| Bảng logic `inserted` / `deleted` | Bản ghi `NEW` / `OLD` trong trigger `FOR EACH ROW` |
| `INSTEAD OF`, `ROLLBACK TRANSACTION` trong trigger | Trigger `BEFORE` + `SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Exxx: …'` (hủy câu lệnh, transaction gọi nó sẽ ROLLBACK) |
| `IF UPDATE(cot)` | `IF NEW.cot <> OLD.cot THEN … END IF` |
| `BEGIN TRAN … COMMIT` | `START TRANSACTION … COMMIT` + `DECLARE EXIT HANDLER FOR SQLEXCEPTION BEGIN ROLLBACK; RESIGNAL; END` |
| Tham số bảng (table-valued parameter) | Chuỗi JSON đọc bằng `JSON_TABLE` |
| `WITH (UPDLOCK, HOLDLOCK)` | `SELECT … FOR UPDATE` |
| `DENY` | Không có; chỉ `GRANT` quyền tối thiểu |

Ba giới hạn của MariaDB ảnh hưởng đến thiết kế:
- Ràng buộc CHECK không được dùng cột thuộc khóa ngoại có `ON UPDATE/DELETE CASCADE` hoặc `SET NULL` (lỗi 1901). Các khóa ngoại có CHECK đi kèm vì vậy để mặc định RESTRICT; việc xóa dây chuyền (độc giả, thủ thư) được làm trong procedure.
- Trigger không được sửa chính bảng đã kích hoạt nó (lỗi 1442): thay đổi dòng đang ghi dùng trigger `BEFORE` + `SET NEW.cot`, thay đổi bảng khác dùng trigger `AFTER`; nhiều trigger cùng sự kiện được sắp thứ tự bằng `FOLLOWS`.
- Cột của `JSON_TABLE` mặc định theo collation của kết nối; nhóm khai báo `CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci` cho cột và `SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci` ở đầu mọi script để tránh lỗi trộn collation (1267).

## 4.3 Minh chứng dữ liệu đã nạp

Số bản ghi của từng bảng sau khi chạy `05_seed.sql` (thư viện vận hành 01/07/2026 – 30/09/2026), đếm bằng `SELECT COUNT(*)`:

| Bảng | Nội dung | Số bản ghi |
| --- | --- | --- |
| CHI_NHANH | Chi nhánh thư viện | 3 |
| NGUOI | Người (lớp cha ISA) | 215 |
| SDT_NGUOI | Số điện thoại (đa trị) | 273 |
| DOC_GIA | Độc giả (lớp con) | 200 |
| THE_DOC_GIA | Thẻ độc giả | 200 |
| THU_THU | Thủ thư (lớp con) | 15 |
| THE_LOAI | Thể loại sách | 6 |
| BANG_PHI_PHAT | Biểu phí phạt (thực thể yếu) | 7 |
| TAC_GIA | Tác giả | 28 |
| DAU_SACH | Đầu sách | 300 |
| DAU_SACH_TAC_GIA | Đầu sách – tác giả (N:N) | 391 |
| PHONG_KHO | Phòng đựng sách | 6 |
| GIA_SACH | Giá sách | 27 |
| CUON_SACH | Cuốn sách (thực thể yếu) | 1369 |
| SACH_THANH_LY | Sách đã thanh lý | 254 |
| PHIEU_MUON | Phiếu mượn | 831 |
| PHIEU_TRA | Phiếu trả | 1568 |
| CT_MUON | Chi tiết mượn (N:N, kết hợp) | 2201 |
| PHIEU_PHAT | Phiếu phạt | 315 |
| CT_MUON_LUU_TRU | Lịch sử mượn của sách đã thanh lý | 16 |
| LOAI_PHONG | Loại phòng đọc | 2 |
| PHONG_DOC | Phòng đọc | 21 |
| PHIEU_THUE_PHONG | Phiếu thuê phòng | 150 |

Một số chỉ số vận hành trong 3 tháng:

| Chỉ số | Giá trị |
| --- | --- |
| Số lượt mượn (cuốn) | 2217 |
| Số cuốn đang được mượn ngày 30/09/2026 | 452 |
| Số cuốn quá hạn ngày 30/09/2026 | 205 |
| Số phiếu phạt / tổng tiền phạt (đ) | 315 / 111,849,000 |
| Số cuốn sắp hết hạn sử dụng (< 24 tháng) | 141 |
| Số cuốn đã thanh lý | 254 |
| Độc giả giữ nhiều sách nhất | DG0001 (50 cuốn) |
| Lượt thuê phòng / doanh thu (đ) | 150 / 65,000,000 |

Dữ liệu mẫu (5 dòng đầu) của một số bảng chính:

**DAU_SACH**

| MaDauSach | MaTheLoai | TenSach | NhaXuatBan | NamXuatBan |
| --- | --- | --- | --- | --- |
| GT0001 | GT | Giáo trình Toán cao cấp | NXB Kim Đồng | 2018 |
| GT0002 | GT | Nhập môn Mạng máy tính | O'Reilly | 2013 |
| GT0003 | GT | Giáo trình Hệ điều hành (tập 2) | NXB Kim Đồng | 2020 |
| GT0004 | GT | Giáo trình Lập trình C | NXB Thông tin và Truyền thông | 2014 |
| GT0005 | GT | Bài giảng Triết học | Pearson | 2014 |

**CUON_SACH**

| MaCuonSach | STT | MaGia | NgayNhap | TuoiThoConLaiThang | TrangThai |
| --- | --- | --- | --- | --- | --- |
| GT0001-001 | 1 | CN01-K1-GT1 | 2024-04-21 | 67 | DangMuon |
| GT0001-002 | 2 | CN01-K1-GT1 | 2024-04-21 | 67 | DangMuon |
| GT0001-003 | 3 | CN02-K1-GT1 | 2023-11-20 | 62 | DangMuon |
| GT0001-004 | 4 | CN02-K1-GT1 | 2023-11-20 | 63 | DangMuon |
| GT0001-005 | 5 | CN03-K1-GT1 | 2021-11-23 | 39 | DangMuon |

**NGUOI / DOC_GIA**

| MaNguoi | CONCAT_WS(' ',n.Ho,n.Dem,n.Ten) | NgaySinh | Quan | MaChiNhanh | SoThe | NgayHetHan |
| --- | --- | --- | --- | --- | --- | --- |
| DG0001 | Võ Hồng Hà | 2008-10-14 | Nam Từ Liêm | CN01 | THE0001 | 2027-06-01 |
| DG0002 | Nguyễn Thu Giang | 1965-07-15 | Hà Đông | CN02 | THE0002 | 2027-09-03 |
| DG0003 | Vũ Bảo Giang | 1968-02-02 | Hoàn Kiếm | CN03 | THE0003 | 2026-10-25 |
| DG0004 | Hồ Công Hoàng | 1963-09-22 | Cầu Giấy | CN01 | THE0004 | 2026-08-20 |
| DG0005 | Lê Hồng Quỳnh | 1980-10-20 | Hà Đông | CN02 | THE0005 | 2026-09-27 |

**PHIEU_MUON + CT_MUON**

| MaPhieuMuon | MaDocGia | MaThuThu | NgayMuon | MaCuonSach | HanTra | MaPhieuTra |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | DG0109 | TT005 | 2026-07-01 | GT0008-001 | 2026-07-31 | 541 |
| 2 | DG0092 | TT010 | 2026-07-01 | GT0003-004 | 2026-07-31 | 747 |
| 2 | DG0092 | TT010 | 2026-07-01 | NV0016-004 | 2026-07-04 | 11 |
| 2 | DG0092 | TT010 | 2026-07-01 | NV0022-003 | 2026-07-22 | 58 |
| 2 | DG0092 | TT010 | 2026-07-01 | TC0019-002 | 2026-07-08 | 40 |

**PHIEU_PHAT**

| MaPhieuPhat | MaPhieuMuon | MaCuonSach | SoNgayTre | SoTien | DaThanhToan | NgayThanhToan |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 10 | NV0010-003 | 2 | 260000 | 1 | 2026-07-08 |
| 2 | 6 | TC0008-002 | 6 | 80000 | 1 | 2026-07-21 |
| 4 | 32 | TK0014-002 | 5 | 350000 | 0 |  |
| 5 | 34 | TC0008-001 | 5 | 75000 | 1 | 2026-07-23 |
| 6 | 39 | TK0005-005 | 4 | 320000 | 0 |  |

**PHIEU_THUE_PHONG**

| MaPhieuThue | MaDocGia | MaPhongDoc | BatDau | KetThuc | SoNguoi | TongTien |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | DG0039 | CN03-H1 | 2026-07-02 07:00:00 | 2026-07-02 11:00:00 | 21 | 1200000 |
| 2 | DG0052 | CN01-N5 | 2026-07-16 19:00:00 | 2026-07-16 20:00:00 | 4 | 50000 |
| 3 | DG0148 | CN01-N4 | 2026-07-16 16:00:00 | 2026-07-16 20:00:00 | 10 | 200000 |
| 4 | DG0124 | CN01-N1 | 2026-07-11 14:00:00 | 2026-07-11 18:00:00 | 3 | 200000 |
| 5 | DG0108 | CN03-N4 | 2026-07-12 16:00:00 | 2026-07-12 17:00:00 | 4 | 50000 |

## 4.4 Toàn bộ ràng buộc toàn vẹn cài đặt bằng SQL

Tổng cộng: 23 khóa chính, 34 khóa ngoại, 11 ràng buộc UNIQUE, 44 ràng buộc CHECK, cùng các ràng buộc NOT NULL và DEFAULT (xem mã DDL ở Phụ lục A). Bảng dưới được trích tự động từ `information_schema`.

| Bảng | Tên ràng buộc | Loại | Nội dung |
| --- | --- | --- | --- |
| CHI_NHANH | PRIMARY | PK | PRIMARY KEY (MaChiNhanh) |
| CHI_NHANH | UQ_CHI_NHANH_Ten | UNIQUE | UNIQUE (TenChiNhanh) |
| CHI_NHANH | UQ_CHI_NHANH_Truong | UNIQUE | UNIQUE (MaThuThuTruong) |
| CHI_NHANH | FK_CHINHANH_TRUONG | FK | (MaThuThuTruong) → THU_THU(MaNguoi) ON DELETE SET NULL |
| CHI_NHANH | CK_CHI_NHANH_Gio | CHECK | GioMo < GioDong |
| CHI_NHANH | CK_CHI_NHANH_Ma | CHECK | MaChiNhanh regexp '^CN[0-9]{2}$' |
| NGUOI | PRIMARY | PK | PRIMARY KEY (MaNguoi) |
| NGUOI | UQ_NGUOI_Email | UNIQUE | UNIQUE (Email) |
| NGUOI | CK_NGUOI_Email | CHECK | Email is null or Email like '%_@_%._%' |
| NGUOI | CK_NGUOI_GioiTinh | CHECK | GioiTinh in ('M','F') |
| NGUOI | CK_NGUOI_Loai | CHECK | LoaiNguoi in ('DG','TT') |
| NGUOI | CK_NGUOI_Ma | CHECK | LoaiNguoi = 'DG' and MaNguoi regexp '^DG[0-9]{4}$' or LoaiNguoi = 'TT' and MaNguoi regexp '^TT[0-9]{3}$' |
| NGUOI | CK_NGUOI_NgaySinh | CHECK | NgaySinh >= '1920-01-01' |
| SDT_NGUOI | PRIMARY | PK | PRIMARY KEY (MaNguoi, SoDienThoai) |
| SDT_NGUOI | FK_SDT_NGUOI | FK | (MaNguoi) → NGUOI(MaNguoi) ON DELETE CASCADE ON UPDATE CASCADE |
| SDT_NGUOI | CK_SDT_Dang | CHECK | SoDienThoai regexp '^0[0-9]{9}$' |
| DOC_GIA | PRIMARY | PK | PRIMARY KEY (MaNguoi) |
| DOC_GIA | FK_DOCGIA_CHINHANH | FK | (MaChiNhanh) → CHI_NHANH(MaChiNhanh) |
| DOC_GIA | FK_DOCGIA_NGUOI | FK | (MaNguoi) → NGUOI(MaNguoi) |
| DOC_GIA | CK_DOCGIA_Ma | CHECK | MaNguoi like 'DG%' |
| DOC_GIA | CK_DOCGIA_TrangThai | CHECK | TrangThai in ('HoatDong','Khoa') |
| THE_DOC_GIA | PRIMARY | PK | PRIMARY KEY (SoThe) |
| THE_DOC_GIA | UQ_THE_DocGia | UNIQUE | UNIQUE (MaDocGia) |
| THE_DOC_GIA | FK_THE_DOCGIA | FK | (MaDocGia) → DOC_GIA(MaNguoi) ON DELETE CASCADE ON UPDATE CASCADE |
| THE_DOC_GIA | CK_THE_Han | CHECK | NgayHetHan > NgayCap |
| THU_THU | PRIMARY | PK | PRIMARY KEY (MaNguoi) |
| THU_THU | FK_THUTHU_CHINHANH | FK | (MaChiNhanh) → CHI_NHANH(MaChiNhanh) |
| THU_THU | FK_THUTHU_NGUOI | FK | (MaNguoi) → NGUOI(MaNguoi) |
| THU_THU | FK_THUTHU_QUANLY | FK | (MaQuanLy) → THU_THU(MaNguoi) |
| THU_THU | CK_THUTHU_Ma | CHECK | MaNguoi like 'TT%' |
| THU_THU | CK_THUTHU_QuanLy | CHECK | MaQuanLy is null or MaQuanLy <> MaNguoi |
| THE_LOAI | PRIMARY | PK | PRIMARY KEY (MaTheLoai) |
| THE_LOAI | UQ_THE_LOAI_Ten | UNIQUE | UNIQUE (TenTheLoai) |
| THE_LOAI | CK_THELOAI_Ma | CHECK | MaTheLoai regexp '^[A-Z]{2}$' |
| THE_LOAI | CK_THELOAI_SoNgay | CHECK | SoNgayMuon between 1 and 90 |
| THE_LOAI | CK_THELOAI_TuoiTho | CHECK | TuoiThoNam between 1 and 50 |
| BANG_PHI_PHAT | PRIMARY | PK | PRIMARY KEY (MaTheLoai, NgayApDung) |
| BANG_PHI_PHAT | FK_PHIPHAT_THELOAI | FK | (MaTheLoai) → THE_LOAI(MaTheLoai) ON DELETE CASCADE |
| BANG_PHI_PHAT | CK_PHIPHAT_Tien | CHECK | PhatCoBan >= 0 and PhatMoiNgay >= 0 |
| TAC_GIA | PRIMARY | PK | PRIMARY KEY (MaTacGia) |
| DAU_SACH | PRIMARY | PK | PRIMARY KEY (MaDauSach) |
| DAU_SACH | FK_DAUSACH_THELOAI | FK | (MaTheLoai) → THE_LOAI(MaTheLoai) |
| DAU_SACH | CK_DAUSACH_Ma | CHECK | MaDauSach regexp '^[A-Z]{2}[0-9]{4}$' |
| DAU_SACH | CK_DAUSACH_Nam | CHECK | NamXuatBan is null or NamXuatBan between 1900 and 2100 |
| DAU_SACH | CK_DAUSACH_SoNgay | CHECK | SoNgayMuonRieng is null or SoNgayMuonRieng between 1 and 90 |
| DAU_SACH | CK_DAUSACH_TheLoai | CHECK | MaTheLoai = left(MaDauSach,2) |
| DAU_SACH_TAC_GIA | PRIMARY | PK | PRIMARY KEY (MaDauSach, MaTacGia) |
| DAU_SACH_TAC_GIA | FK_DSTG_DAUSACH | FK | (MaDauSach) → DAU_SACH(MaDauSach) ON DELETE CASCADE ON UPDATE CASCADE |
| DAU_SACH_TAC_GIA | FK_DSTG_TACGIA | FK | (MaTacGia) → TAC_GIA(MaTacGia) ON DELETE CASCADE |
| PHONG_KHO | PRIMARY | PK | PRIMARY KEY (MaPhongKho) |
| PHONG_KHO | UQ_PHONGKHO_Ten | UNIQUE | UNIQUE (MaChiNhanh, TenPhong) |
| PHONG_KHO | FK_PHONGKHO_CHINHANH | FK | (MaChiNhanh) → CHI_NHANH(MaChiNhanh) |
| PHONG_KHO | CK_PHONGKHO_Tang | CHECK | Tang between 0 and 20 |
| GIA_SACH | PRIMARY | PK | PRIMARY KEY (MaGia) |
| GIA_SACH | FK_GIASACH_PHONGKHO | FK | (MaPhongKho) → PHONG_KHO(MaPhongKho) |
| GIA_SACH | FK_GIASACH_THELOAI | FK | (MaTheLoai) → THE_LOAI(MaTheLoai) |
| GIA_SACH | CK_GIASACH_SoLuong | CHECK | SoLuongHienCo between 0 and SucChua |
| GIA_SACH | CK_GIASACH_SucChua | CHECK | SucChua between 1 and 100 |
| CUON_SACH | PRIMARY | PK | PRIMARY KEY (MaCuonSach) |
| CUON_SACH | UQ_CUONSACH_DauSach_STT | UNIQUE | UNIQUE (MaDauSach, STT) |
| CUON_SACH | FK_CUONSACH_DAUSACH | FK | (MaDauSach) → DAU_SACH(MaDauSach) |
| CUON_SACH | FK_CUONSACH_GIASACH | FK | (MaGia) → GIA_SACH(MaGia) |
| CUON_SACH | CK_CUONSACH_Ma | CHECK | MaCuonSach = concat(MaDauSach,'-',lpad(STT,3,'0')) |
| CUON_SACH | CK_CUONSACH_STT | CHECK | STT between 1 and 999 |
| CUON_SACH | CK_CUONSACH_TrangThai | CHECK | TrangThai in ('TrenGia','DangMuon','ChoThanhLy') |
| CUON_SACH | CK_CUONSACH_TuoiTho | CHECK | TuoiThoConLaiThang >= 0 |
| SACH_THANH_LY | PRIMARY | PK | PRIMARY KEY (MaCuonSach) |
| SACH_THANH_LY | UQ_THANHLY_DauSach_STT | UNIQUE | UNIQUE (MaDauSach, STT) |
| SACH_THANH_LY | FK_THANHLY_DAUSACH | FK | (MaDauSach) → DAU_SACH(MaDauSach) |
| SACH_THANH_LY | CK_THANHLY_Ngay | CHECK | NgayThanhLy >= NgayNhap |
| PHIEU_MUON | PRIMARY | PK | PRIMARY KEY (MaPhieuMuon) |
| PHIEU_MUON | FK_PHIEUMUON_DOCGIA | FK | (MaDocGia) → DOC_GIA(MaNguoi) |
| PHIEU_MUON | FK_PHIEUMUON_THUTHU | FK | (MaThuThu) → THU_THU(MaNguoi) |
| PHIEU_TRA | PRIMARY | PK | PRIMARY KEY (MaPhieuTra) |
| PHIEU_TRA | FK_PHIEUTRA_DOCGIA | FK | (MaDocGia) → DOC_GIA(MaNguoi) |
| PHIEU_TRA | FK_PHIEUTRA_THUTHU | FK | (MaThuThu) → THU_THU(MaNguoi) |
| CT_MUON | PRIMARY | PK | PRIMARY KEY (MaPhieuMuon, MaCuonSach) |
| CT_MUON | FK_CTMUON_CUONSACH | FK | (MaCuonSach) → CUON_SACH(MaCuonSach) |
| CT_MUON | FK_CTMUON_PHIEUMUON | FK | (MaPhieuMuon) → PHIEU_MUON(MaPhieuMuon) ON DELETE CASCADE |
| CT_MUON | FK_CTMUON_PHIEUTRA | FK | (MaPhieuTra) → PHIEU_TRA(MaPhieuTra) |
| PHIEU_PHAT | PRIMARY | PK | PRIMARY KEY (MaPhieuPhat) |
| PHIEU_PHAT | UQ_PHIEUPHAT_CTMuon | UNIQUE | UNIQUE (MaPhieuMuon, MaCuonSach) |
| PHIEU_PHAT | FK_PHIEUPHAT_CTMUON | FK | (MaPhieuMuon, MaCuonSach) → CT_MUON(MaPhieuMuon, MaCuonSach) ON DELETE CASCADE |
| PHIEU_PHAT | CK_PHIEUPHAT_ThanhToan | CHECK | DaThanhToan = 0 and NgayThanhToan is null or DaThanhToan = 1 and NgayThanhToan is not null |
| PHIEU_PHAT | CK_PHIEUPHAT_Tien | CHECK | SoTien >= 0 |
| PHIEU_PHAT | CK_PHIEUPHAT_Tre | CHECK | SoNgayTre > 0 |
| CT_MUON_LUU_TRU | PRIMARY | PK | PRIMARY KEY (MaPhieuMuon, MaCuonSach) |
| CT_MUON_LUU_TRU | FK_LUUTRU_PHIEUMUON | FK | (MaPhieuMuon) → PHIEU_MUON(MaPhieuMuon) |
| CT_MUON_LUU_TRU | FK_LUUTRU_PHIEUTRA | FK | (MaPhieuTra) → PHIEU_TRA(MaPhieuTra) |
| CT_MUON_LUU_TRU | FK_LUUTRU_THANHLY | FK | (MaCuonSach) → SACH_THANH_LY(MaCuonSach) |
| CT_MUON_LUU_TRU | CK_LUUTRU_Tien | CHECK | TienPhat >= 0 |
| LOAI_PHONG | PRIMARY | PK | PRIMARY KEY (MaLoaiPhong) |
| LOAI_PHONG | UQ_LOAIPHONG_Ten | UNIQUE | UNIQUE (TenLoai) |
| LOAI_PHONG | CK_LOAIPHONG_Gia | CHECK | GiaMoiGio > 0 |
| LOAI_PHONG | CK_LOAIPHONG_Gio | CHECK | SoGioToiThieu >= 1 and SoGioToiThieu <= SoGioToiDa |
| PHONG_DOC | PRIMARY | PK | PRIMARY KEY (MaPhongDoc) |
| PHONG_DOC | UQ_PHONGDOC_Ten | UNIQUE | UNIQUE (MaChiNhanh, TenPhong) |
| PHONG_DOC | FK_PHONGDOC_CHINHANH | FK | (MaChiNhanh) → CHI_NHANH(MaChiNhanh) |
| PHONG_DOC | FK_PHONGDOC_LOAI | FK | (MaLoaiPhong) → LOAI_PHONG(MaLoaiPhong) |
| PHONG_DOC | CK_PHONGDOC_SucChua | CHECK | SucChua between 1 and 200 |
| PHIEU_THUE_PHONG | PRIMARY | PK | PRIMARY KEY (MaPhieuThue) |
| PHIEU_THUE_PHONG | FK_THUE_DOCGIA | FK | (MaDocGia) → DOC_GIA(MaNguoi) |
| PHIEU_THUE_PHONG | FK_THUE_PHONGDOC | FK | (MaPhongDoc) → PHONG_DOC(MaPhongDoc) |
| PHIEU_THUE_PHONG | FK_THUE_THUTHU | FK | (MaThuThuDuyet) → THU_THU(MaNguoi) |
| PHIEU_THUE_PHONG | CK_THUE_DatTruoc | CHECK | cast(BatDau as date) >= NgayDat and to_days(BatDau) - to_days(NgayDat) <= 14 |
| PHIEU_THUE_PHONG | CK_THUE_GioMoCua | CHECK | cast(BatDau as time) >= '07:00:00' and cast(KetThuc as time) <= '21:00:00' |
| PHIEU_THUE_PHONG | CK_THUE_GioTron | CHECK | minute(BatDau) = 0 and second(BatDau) = 0 and minute(KetThuc) = 0 and second(KetThuc) = 0 |
| PHIEU_THUE_PHONG | CK_THUE_MucDich | CHECK | MucDich in ('HocNhom','HoiThao') |
| PHIEU_THUE_PHONG | CK_THUE_SoNguoi | CHECK | SoNguoi > 0 |
| PHIEU_THUE_PHONG | CK_THUE_ThoiGian | CHECK | KetThuc > BatDau and cast(KetThuc as date) = cast(BatDau as date) |
| PHIEU_THUE_PHONG | CK_THUE_Tien | CHECK | TongTien >= 0 |
| PHIEU_THUE_PHONG | CK_THUE_TrangThai | CHECK | TrangThai in ('DaDuyet','DaHuy') |

## 4.5 Danh sách trigger

| Nhóm | Trigger | Thời điểm, sự kiện | Bảng |
| --- | --- | --- | --- |
| TRG1 | trg_CTMuon_ToiDa10 | BEFORE INSERT | CT_MUON |
| TRG2 | trg_CTMuon_ToiDa50 | BEFORE INSERT | CT_MUON |
| TRG3 | trg_CTMuon_KiemTraTra | BEFORE UPDATE | CT_MUON |
| TRG3 | trg_CTMuon_LapPhieuPhat | AFTER UPDATE | CT_MUON |
| TRG4 | trg_CTMuon_Muon | AFTER INSERT | CT_MUON |
| TRG4 | trg_CTMuon_Tra | AFTER UPDATE | CT_MUON |
| TRG4 | trg_CuonSach_DemGia_Sua | AFTER UPDATE | CUON_SACH |
| TRG4 | trg_CuonSach_DemGia_Them | AFTER INSERT | CUON_SACH |
| TRG4 | trg_CuonSach_DemGia_Xoa | AFTER DELETE | CUON_SACH |
| TRG5 | trg_CTMuon_GiamTuoiTho | AFTER INSERT | CT_MUON |
| TRG6 | trg_CuonSach_DungGia_Sua | BEFORE UPDATE | CUON_SACH |
| TRG6 | trg_CuonSach_DungGia_Them | BEFORE INSERT | CUON_SACH |
| TRG7 | trg_ThuePhong_KhongTrung_Sua | BEFORE UPDATE | PHIEU_THUE_PHONG |
| TRG7 | trg_ThuePhong_KhongTrung_Them | BEFORE INSERT | PHIEU_THUE_PHONG |
| TRG8 | trg_DocGia_ChanSuaMa | BEFORE UPDATE | DOC_GIA |
| TRG8 | trg_DocGia_ChanXoa | BEFORE DELETE | DOC_GIA |
| TRG8 | trg_DocGia_DungLoai | BEFORE INSERT | DOC_GIA |
| TRG8 | trg_ThuThu_DungLoai | BEFORE INSERT | THU_THU |

## 4.6 Danh sách function và stored procedure

8 function: `fn_HanTra`, `fn_MaNguoiMoi`, `fn_NoPhat`, `fn_SoSachDangMuon`, `fn_TheConHan`, `fn_TienThuePhong`, `fn_TinhTienPhat`, `fn_Tuoi`.

- **Transaction nghiệp vụ (TX1–TX7)** (7): `sp_DangKyDocGia`, `sp_MuonSach`, `sp_NhapLoSach`, `sp_ThanhLySach`, `sp_ThanhToanPhat`, `sp_ThuePhong`, `sp_TraSach`
- **Báo cáo** (7): `sp_BC_DauSachLuotMuon`, `sp_BC_DocGiaTraMuon`, `sp_BC_PhongTaiThoiDiem`, `sp_BC_SachDaMuon`, `sp_BC_SachDangMuon`, `sp_BC_SachQuaHan`, `sp_BC_SachSapHetHan`
- **Thêm / xóa / sửa / tìm kiếm** (32): `sp_ChiNhanh_Sua`, `sp_ChiNhanh_Them`, `sp_ChiNhanh_TimKiem`, `sp_ChiNhanh_Xoa`, `sp_CuonSach_ChuyenGia`, `sp_CuonSach_TimKiem`, `sp_CuonSach_Xoa`, `sp_DauSach_Sua`, `sp_DauSach_Them`, `sp_DauSach_TimKiem`, `sp_DauSach_Xoa`, `sp_DocGia_GiaHanThe`, `sp_DocGia_Sua`, `sp_DocGia_TimKiem`, `sp_DocGia_Xoa`, `sp_GiaSach_Sua`, `sp_GiaSach_Them`, `sp_GiaSach_TimKiem`, `sp_GiaSach_Xoa`, `sp_PhongDoc_Sua`, `sp_PhongDoc_Them`, `sp_PhongDoc_TimKiem`, `sp_PhongDoc_Xoa`, `sp_PhongKho_Sua`, `sp_PhongKho_Them`, `sp_PhongKho_TimKiem`, `sp_PhongKho_Xoa`, `sp_ThuePhong_BaoGia`, `sp_ThuThu_Sua`, `sp_ThuThu_Them`, `sp_ThuThu_TimKiem`, `sp_ThuThu_Xoa`

## 4.7 Đặc tả trigger và transaction nghiệp vụ

| Mã | Đối tượng | Luật nghiệp vụ | Cách xử lý |
| --- | --- | --- | --- |
| TRG1 | trg_CTMuon_ToiDa10 (CT_MUON, BEFORE INSERT) | Mỗi lần mượn tối đa 10 cuốn | Đếm số cuốn của phiếu, ≥ 10 thì SIGNAL E101 |
| TRG2 | trg_CTMuon_ToiDa50 (CT_MUON, BEFORE INSERT) | Mỗi độc giả giữ tối đa 50 cuốn; chỉ mượn cuốn đang trên giá | fn_SoSachDangMuon ≥ 50 → E102; trạng thái khác TrenGia → E104 |
| TRG3 | trg_CTMuon_KiemTraTra (BEFORE UPDATE), trg_CTMuon_LapPhieuPhat (AFTER UPDATE) | Trả muộn bị phạt theo thể loại | Kiểm tra cùng độc giả (E107), ngày trả ≥ ngày mượn (E105), không sửa dòng đã trả (E106); trả muộn → INSERT PHIEU_PHAT với fn_TinhTienPhat theo biểu phí có hiệu lực |
| TRG4 | trg_CTMuon_Muon, trg_CTMuon_Tra, trg_CuonSach_DemGia_Them/Sua/Xoa | Mượn thì số sách trên giá giảm, trả thì tăng | Mượn/trả đổi trạng thái cuốn; mọi thay đổi trạng thái, vị trí, thêm/xóa cuốn cập nhật GIA_SACH.SoLuongHienCo |
| TRG5 | trg_CTMuon_GiamTuoiTho (AFTER INSERT, FOLLOWS trg_CTMuon_Muon) | Mỗi lần mượn tuổi thọ giảm 1 tháng | TuoiThoConLaiThang − 1 (không âm) |
| TRG6 | trg_CuonSach_DungGia_Them/Sua (CUON_SACH, BEFORE) | Giá chỉ chứa sách cùng thể loại, không vượt sức chứa; sách hết tuổi thọ tách khỏi lưu thông | Sai thể loại → E301; giá đầy (tính cả cuốn đang mượn) → E304; không sửa mã → E305; tuổi thọ = 0 và đang trên giá → SET NEW.TrangThai = 'ChoThanhLy' |
| TRG7 | trg_ThuePhong_KhongTrung_Them/Sua (BEFORE) | Một phòng không có 2 lượt thuê trùng giờ | Tồn tại lượt đã duyệt giao khoảng [BatDau, KetThuc) → E201 |
| TRG8 | trg_DocGia_ChanXoa, trg_DocGia_ChanSuaMa, trg_DocGia_DungLoai, trg_ThuThu_DungLoai | Toàn vẹn độc giả và ISA | Còn giữ sách → E404; còn nợ phạt → E405; sửa mã → E406; bảng con không khớp LoaiNguoi → E407 |
| TX1 | sp_MuonSach | Lập phiếu mượn 1–10 cuốn | Kiểm tra thẻ (E103), khóa dòng độc giả và các cuốn bằng FOR UPDATE, lập phiếu, chèn chi tiết với hạn trả fn_HanTra; mọi lỗi → ROLLBACK cả phiếu |
| TX2 | sp_TraSach | Trả 1 đến nhiều cuốn | Lập phiếu trả, cập nhật chi tiết mượn; số dòng cập nhật khác số cuốn → E108 và ROLLBACK; trả về tổng phạt |
| TX3 | sp_ThanhToanPhat | Thu toàn bộ phạt chưa thanh toán | Khóa các phiếu phạt, đánh dấu đã thanh toán; không có nợ → E109 |
| TX4 | sp_NhapLoSach | Nhập đầu sách mới, tác giả, n cuốn | Tạo đầu sách + tác giả (nếu mới), sinh mã cuốn liên tiếp, xếp lên giá; giá sai thể loại hoặc đầy → ROLLBACK toàn bộ lô |
| TX5 | sp_ThanhLySach | Sách hết niên hạn tách khỏi CSDL đang quản lý | Chuyển cuốn sang SACH_THANH_LY, lịch sử mượn sang CT_MUON_LUU_TRU, rồi xóa khỏi CUON_SACH |
| TX6 | sp_DangKyDocGia | Đăng ký độc giả | Chèn NGUOI, SDT_NGUOI (≥ 1 số, E408), DOC_GIA, THE_DOC_GIA trong một giao dịch |
| TX7 | sp_ThuePhong | Thuê phòng đọc | Khóa phòng, kiểm tra thẻ, nợ phạt (E110), sức chứa (E202), số giờ theo loại phòng (E203), giờ mở cửa (E204); tính tiền và lập phiếu |

Đoạn mã minh họa (TRG1 và khung transaction TX1):

```sql
CREATE OR REPLACE TRIGGER trg_CTMuon_ToiDa10
BEFORE INSERT ON CT_MUON FOR EACH ROW
BEGIN
  IF (SELECT COUNT(*) FROM CT_MUON WHERE MaPhieuMuon = NEW.MaPhieuMuon) >= 10 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'E101: Mỗi lần mượn tối đa 10 cuốn sách';
  END IF;
END //

CREATE OR REPLACE PROCEDURE sp_MuonSach(IN p_MaDocGia VARCHAR(10), IN p_MaThuThu VARCHAR(10),
       IN p_DsCuon JSON, IN p_NgayMuon DATE, OUT p_MaPhieuMuon INT)
BEGIN
  DECLARE EXIT HANDLER FOR SQLEXCEPTION BEGIN ROLLBACK; RESIGNAL; END;
  START TRANSACTION;
    -- kiểm tra số cuốn, thẻ; khóa độc giả và các cuốn bằng SELECT ... FOR UPDATE
    INSERT INTO PHIEU_MUON(MaDocGia, MaThuThu, NgayMuon) VALUES (p_MaDocGia, p_MaThuThu, p_NgayMuon);
    SET p_MaPhieuMuon = LAST_INSERT_ID();
    INSERT INTO CT_MUON(MaPhieuMuon, MaCuonSach, HanTra)        -- TRG1, 2, 4, 5 chạy tại đây
    SELECT p_MaPhieuMuon, j.Ma, fn_HanTra(j.Ma, p_NgayMuon)
    FROM JSON_TABLE(p_DsCuon, '$[*]' COLUMNS (Ma VARCHAR(10) PATH '$')) j;
  COMMIT;
END //
```

## 4.8 Truy vấn hiển thị theo yêu cầu đề

Mỗi yêu cầu được cài đặt bằng một VIEW (tái sử dụng) và một procedure `sp_BC_*` có tham số chi nhánh (NULL = toàn hệ thống) để sắp xếp đúng yêu cầu. Ký hiệu đại số quan hệ theo chương 4: σ chọn, π chiếu, ⋈ kết nối tự nhiên, ⟕ kết nối ngoài trái, ∪ hợp, − trừ; phép gom nhóm γ và sắp xếp τ là phép mở rộng dùng để biểu diễn GROUP BY, ORDER BY.

Viết tắt: CT = CT_MUON, PM = PHIEU_MUON, CS = CUON_SACH, DS = DAU_SACH, TL = THE_LOAI, DG = DOC_GIA, N = NGUOI, PP = PHIEU_PHAT, LT = CT_MUON_LUU_TRU, STL = SACH_THANH_LY, TT = THU_THU, PD = PHONG_DOC, TP = PHIEU_THUE_PHONG.

| # | Yêu cầu | Đối tượng SQL | Biểu thức đại số quan hệ |
| --- | --- | --- | --- |
| 1 | Sách đang được mượn, sắp theo hạn trả | `v_SachDangMuon`, `sp_BC_SachDangMuon(p_MaChiNhanh)` | τ_HanTra( π_MaCuonSach, TenSach, MaDocGia, HoTen, NgayMuon, HanTra( σ_MaPhieuTra = NULL( CT ⋈ PM ⋈ CS ⋈ DS ⋈ DG ⋈ N ) ) ) |
| 1b | Sách đã được mượn trong khoảng [từ, đến] (cả đã trả và chưa trả), sắp theo hạn trả | `sp_BC_SachDaMuon(p_MaChiNhanh, p_TuNgay, p_DenNgay)` | τ_HanTra( π_MaCuonSach, TenSach, MaDocGia, HoTen, NgayMuon, HanTra, NgayTra( σ_TuNgay ≤ NgayMuon ≤ DenNgay( CT ⋈ PM ⋈ CS ⋈ DS ⋈ DG ⋈ N ) ⟕ PT ) ) |
| 2 | Sách quá hạn, sắp theo số ngày quá hạn | `sp_BC_SachQuaHan(p_MaChiNhanh, p_Ngay)` | τ_SoNgayQuaHan↓( π_…, SoNgayQuaHan = p_Ngay − HanTra( σ_MaPhieuTra = NULL ∧ HanTra < p_Ngay( CT ⋈ PM ⋈ CS ⋈ DS ⋈ DG ⋈ N ) ) ) |
| 3 | Đầu sách theo lượt mượn nhiều nhất | `v_LuotMuonDauSach`, `sp_BC_DauSachLuotMuon(p_MaChiNhanh)` | M = π_MaPhieuMuon, MaDauSach(CT ⋈ CS) ∪ π_MaPhieuMuon, MaDauSach(LT ⋈ STL); τ_LuotMuon↓( DS ⟕ γ_MaDauSach; COUNT(*)→LuotMuon( M ⋈ PM ⋈ TT ) ) |
| 4 | Độc giả trả muộn, sắp theo tổng phạt rồi số sách trả muộn | `v_PhatTraMuon`, `sp_BC_DocGiaTraMuon(p_MaChiNhanh)` | P = π_MaDocGia, SoTien(PP ⋈ PM) ∪ π_MaDocGia, TienPhat(σ_TienPhat > 0(LT ⋈ PM)); τ_TongPhat↓, SoSach↓( γ_MaDocGia; SUM(SoTien)→TongPhat, COUNT(*)→SoSach(P) ⋈ N ) |
| 5 | Sách sắp hết hạn sử dụng (dưới 2 năm) | `v_SachSapHetHan`, `sp_BC_SachSapHetHan(p_MaChiNhanh)` | τ_TuoiTho( π_MaCuonSach, TenSach, MaChiNhanh, TuoiThoConLaiThang( σ_TuoiThoConLaiThang < 24( CS ⋈ DS ⋈ GIA_SACH ⋈ PHONG_KHO ) ) ) |
| 6 | Phòng đọc có / chưa có người dùng tại một thời điểm t | `sp_BC_PhongTaiThoiDiem(p_MaChiNhanh, p_ThoiDiem)` | Đang dùng: D = π_MaPhongDoc( σ_TrangThai='DaDuyet' ∧ BatDau ≤ t < KetThuc(TP) ); Trống: π_MaPhongDoc(PD) − D. SQL dùng PD ⟕ σ_…(TP) để trả cả hai nhóm trong một bảng. |

Cách hiểu yêu cầu 1: đề ghi "danh sách sách đã được mượn, sắp xếp theo thời gian hạn trả". Vì chỉ sách **chưa trả** mới còn ý nghĩa theo dõi hạn trả, nhóm lấy cách hiểu chính là sách đang được mượn (σ MaPhieuTra = NULL, procedure `sp_BC_SachDangMuon`). Để không bỏ sót cách hiểu theo nghĩa rộng (mọi lượt mượn, kể cả đã trả), nhóm cài đặt thêm `sp_BC_SachDaMuon` có lọc theo khoảng ngày mượn; trên giao diện, ô "Chỉ sách đang được mượn (chưa trả)" chuyển giữa hai cách hiểu (Hình 4.1 và 4.1b).

Ghi chú: báo cáo 3 và 4 hợp (∪) thêm dữ liệu từ bảng lưu trữ để lượt mượn và tiền phạt của các cuốn đã thanh lý không bị mất khỏi thống kê. Ví dụ phạt dự kiến của báo cáo 2: sách tham khảo quá hạn 84 ngày = 200.000 + 30.000 × 84 = 2.720.000đ.

![Hình 4.1. Báo cáo 1: Sách đang được mượn, sắp theo hạn trả](../anh/11_bao_cao_1.png)

![Hình 4.1b. Báo cáo 1 theo nghĩa rộng: mọi sách đã được mượn trong khoảng ngày (cả đã trả), gọi sp_BC_SachDaMuon](../anh/11b_bao_cao_1_ca_da_tra.png)

![Hình 4.2. Báo cáo 2: Sách quá hạn, sắp theo số ngày quá hạn](../anh/12_bao_cao_2.png)

![Hình 4.3. Báo cáo 3: Đầu sách theo lượt mượn](../anh/13_bao_cao_3.png)

![Hình 4.4. Báo cáo 4: Độc giả trả muộn theo tổng tiền phạt và số sách](../anh/14_bao_cao_4.png)

![Hình 4.5. Báo cáo 5: Sách sắp hết hạn sử dụng](../anh/15_bao_cao_5.png)

![Hình 4.6. Báo cáo 6: Tình trạng phòng đọc tại một thời điểm](../anh/16_bao_cao_6.png)

## 4.9 Tối ưu truy vấn bằng chỉ mục

InnoDB tự tạo chỉ mục cho PK, UNIQUE và mọi khóa ngoại. Nhóm bổ sung 6 chỉ mục phục vụ điều kiện lọc và sắp xếp:

| Chỉ mục | Phục vụ |
| --- | --- |
| IX_CTMUON_ChuaTra_HanTra (MaPhieuTra, HanTra) | Báo cáo 1, 2; fn_SoSachDangMuon trong TRG2 |
| IX_CUONSACH_TuoiTho (TuoiThoConLaiThang) | Báo cáo 5 |
| IX_THUE_Phong_ThoiGian (MaPhongDoc, TrangThai, BatDau, KetThuc) | TRG7 kiểm tra trùng giờ; báo cáo 6 |
| IX_PHIEUPHAT_ChuaTT (DaThanhToan) | fn_NoPhat, TX3 |
| IX_NGUOI_Ten, IX_DAUSACH_TenSach | Tìm kiếm độc giả, đầu sách |

Kết quả `EXPLAIN` đo trên dữ liệu 3 tháng:

| Truy vấn | Trước khi có chỉ mục | Sau khi có chỉ mục |
| --- | --- | --- |
| Sách đang mượn sắp theo hạn trả | Bắt đầu từ DOC_GIA (quét index 200 dòng), *Using temporary; Using filesort* | Bắt đầu từ CT_MUON qua IX_CTMUON_ChuaTra_HanTra (ref const, 452 dòng, *Using index*), không còn bảng tạm và sắp xếp ngoài |
| Sách tuổi thọ < 24 tháng | type ALL, quét 1.369 dòng | type range trên IX_CUONSACH_TuoiTho, 141 dòng |

## 4.10 An toàn bảo mật

- Hai vai trò: **r_ThuThu** (thực thi các procedure nghiệp vụ hằng ngày, tra cứu, 6 báo cáo; SELECT 2 view) và **r_QuanLy** (kế thừa r_ThuThu, thực thi mọi procedure và đọc mọi bảng).
- Không cấp quyền INSERT/UPDATE/DELETE trên bảng cho ai: mọi thay đổi đi qua procedure (SQL SECURITY DEFINER), nên trigger, ràng buộc và kiểm tra trong transaction không thể bị bỏ qua. MariaDB không có DENY, nên nguyên tắc là cấp quyền tối thiểu.
- Tài khoản mẫu: `tt_cn01` (r_ThuThu), `ql_thuvien` (r_QuanLy). Kiểm chứng: `tt_cn01` gọi `sp_BC_SachSapHetHan` thành công, nhưng `SELECT … FROM CUON_SACH` bị từ chối (ERROR 1142).

## 4.11 Kiểm thử ràng buộc, trigger và transaction

`08_test.sql` chạy 47 ca tự động. Mỗi ca thực thi một lệnh qua thủ tục kiểm thử (dynamic SQL + EXIT HANDLER bắt lỗi), so mã lỗi hoặc giá trị thực tế với kỳ vọng và ghi vào bảng KET_QUA_KIEM_THU. Kết quả: **47/47 PASS**.

| Nhóm | Ca hợp lệ | Ca bị chặn / kiểm tra |
| --- | --- | --- |
| TRG1 + TX1 | Mượn đúng 10 cuốn | 11 cuốn qua TX1 → E101 và không phiếu nào được tạo (ROLLBACK); chèn tay cuốn thứ 11 → E101 |
| TRG2 | — | Mượn cuốn đang được mượn → E104; DG0001 đang giữ 50 cuốn mượn thêm → E102 |
| TRG3 + TX2 | Trả muộn 5 ngày 2 cuốn trong 1 phiếu trả; phiếu phạt = cơ bản + 5 × phạt/ngày | Trả cuốn không mượn → E108; sửa phiếu trả đã trả → E106; ngày trả trước ngày mượn → E105 |
| TRG4 | Số lượng trên giá giảm/tăng đúng bằng số cuốn của giá đó được mượn/trả | Toàn hệ thống: SoLuongHienCo khớp 100% |
| TRG5 | Tuổi thọ giảm 1 tháng sau khi mượn | — |
| TRG6 + TX4 | Nhập lô 3 cuốn, mã TR0901-001…003; cuốn hết tuổi thọ tự chuyển ChoThanhLy | Sách TK vào giá TR → E301 và đầu sách mới không được tạo (ROLLBACK); giá đầy → E304; chuyển giá sai thể loại → E301 |
| TX5 | Thanh lý: cuốn chuyển sang SACH_THANH_LY, rời CUON_SACH | — |
| TRG7 + TX7 | Thuê 2 giờ = 100.000đ | Trùng giờ → E201; vượt sức chứa → E202; hội thảo 1 giờ → E203; còn nợ phạt → E110; lẻ phút → CHECK |
| TRG8 | Xóa độc giả không giữ sách, không nợ | Đang giữ sách → E404; còn nợ phạt → E405; sửa mã → E406 |
| TX3 | Thanh toán phạt | Không còn nợ → E109 |
| TX6 | Đăng ký với 2 SĐT, thẻ hết hạn sau 1 năm | SĐT sai → CHECK và không còn bản ghi NGUOI (ROLLBACK); không có SĐT → E408 |
| Ràng buộc | — | Đầu sách mã TK nhưng thể loại TR → CHECK; không phiếu > 10 cuốn; không độc giả > 50 cuốn; không 2 lượt thuê trùng giờ |

Chi tiết từng ca:

Kết quả: **47/47 ca PASS**.

| Mã ca | Mô tả | Kỳ vọng | Thực tế | Kết quả |
| --- | --- | --- | --- | --- |
| TX1-a | Mượn 11 cuốn trong 1 phiếu bị chặn | E101 | E101 | PASS |
| TX1-b | Sau khi bị chặn không có phiếu mượn nào được tạo (ROLLBACK) | 0 | 0 | PASS |
| TX1-c | Mượn đúng 10 cuốn hợp lệ | OK | OK | PASS |
| TRG1 | Chèn trực tiếp cuốn thứ 11 vào phiếu đã có 10 cuốn | E101 | E101 | PASS |
| TRG4-a | Số lượng trên giá giảm đúng bằng số cuốn của giá đó vừa được mượn | 27 | 27 | PASS |
| TRG5 | Tuổi thọ cuốn sách giảm 1 tháng sau khi mượn | 5 | 5 | PASS |
| TX1-d | Hạn trả = ngày mượn + số ngày mượn của thể loại/đầu sách | 1 | 1 | PASS |
| TRG2-a | Mượn cuốn đang được người khác mượn | E104 | E104 | PASS |
| TRG2-b | Độc giả DG0001 đang giữ 50 cuốn mượn thêm 1 cuốn | E102 | E102 | PASS |
| TX2-a | Trả cuốn mà độc giả không mượn | E108 | E108 | PASS |
| TX2-b | Trả muộn 5 ngày 2 cuốn (1 phiếu trả, nhiều cuốn) | OK | OK | PASS |
| TRG3-a | Phiếu phạt tự lập cho cuốn trả muộn, tiền = cơ bản + 5 × phạt/ngày | 1 | 1 | PASS |
| TRG4-b | Số lượng trên giá tăng đúng bằng số cuốn của giá đó vừa được trả | 29 | 29 | PASS |
| TRG3-b | Sửa phiếu trả của dòng mượn đã trả | E106 | E106 | PASS |
| TRG3-c | Ngày trả trước ngày mượn | E105 | E105 | PASS |
| TX7-a | Độc giả còn nợ phạt thuê phòng bị chặn | E110 | E110 | PASS |
| TRG8-b | Xóa độc giả không giữ sách nhưng còn nợ tiền phạt | E405 | E405 | PASS |
| TX3-a | Thanh toán phạt | OK | OK | PASS |
| TX3-b | Thanh toán khi không còn khoản nợ | E109 | E109 | PASS |
| TX7-b | Thuê phòng nhóm 2 giờ hợp lệ | OK | OK | PASS |
| TX7-c | Tiền thuê = 2 giờ × 50.000đ | 100000 | 100000 | PASS |
| TRG7 | Thuê trùng khung giờ 10:00–12:00 | E201 | E201 | PASS |
| TX7-d | Số người vượt sức chứa | E202 | E202 | PASS |
| TX7-e | Thuê phòng hội thảo 1 giờ (tối thiểu 2 giờ) | E203 | E203 | PASS |
| CK-THUE | Thuê lẻ phút (CHECK giờ tròn) | CK | CK | PASS |
| TX6-a | Đăng ký độc giả mới với 2 số điện thoại | OK | OK | PASS |
| TX6-b | Độc giả mới có thẻ hết hạn sau 1 năm | 2027-10-05 | 2027-10-05 | PASS |
| TX6-c | Đăng ký với số điện thoại sai định dạng | CK | CK | PASS |
| TX6-d | Sau lỗi SĐT không còn bản ghi NGUOI nào được thêm (ROLLBACK) | 216 | 216 | PASS |
| TX6-e | Đăng ký không có số điện thoại | E408 | E408 | PASS |
| TRG8-a | Xóa độc giả DG0001 đang giữ sách | E404 | E404 | PASS |
| TRG8-c | Sửa mã độc giả | E406 | E406 | PASS |
| TRG8-d | Xóa độc giả mới đăng ký (không giữ sách, không nợ) | OK | OK | PASS |
| TX4-a | Nhập lô 3 cuốn đầu sách mới vào giá đúng thể loại | OK | OK | PASS |
| TX4-b | Mã cuốn sinh đúng định dạng đầu sách + STT | TR0901-001,TR0901-002,TR0901-003 | TR0901-001,TR0901-002,TR0901-003 | PASS |
| TX4-c | Nhập sách tham khảo vào giá truyện | E301 | E301 | PASS |
| TX4-d | Đầu sách TK0901 không được tạo vì giao dịch bị ROLLBACK | 0 | 0 | PASS |
| TRG6-a | Chuyển cuốn truyện sang giá tham khảo | E301 | E301 | PASS |
| TRG6-b | Nhập thêm vào giá đã đầy | E304 | E304 | PASS |
| CK-DAUSACH | Đầu sách mã TK nhưng thể loại TR (CHECK) | CK | CK | PASS |
| TRG6-c | Cuốn trên giá hết tuổi thọ tự chuyển ChoThanhLy | ChoThanhLy | ChoThanhLy | PASS |
| TX5-a | Thanh lý sách hết niên hạn | OK | OK | PASS |
| TX5-b | Cuốn đã chuyển sang SACH_THANH_LY và rời khỏi CUON_SACH | 10 | 10 | PASS |
| TV-1 | SoLuongHienCo của mọi giá khớp số cuốn không đang mượn | 0 | 0 | PASS |
| TV-2 | Không độc giả nào giữ quá 50 cuốn | 1 | 1 | PASS |
| TV-3 | Không phiếu mượn nào quá 10 cuốn | 0 | 0 | PASS |
| TV-4 | Không có 2 lượt thuê đã duyệt trùng giờ cùng phòng | 0 | 0 | PASS |

## 4.12 Bảng mã lỗi nghiệp vụ

| Mã | Ý nghĩa | Nơi phát sinh |
| --- | --- | --- |
| E100 | Phiếu mượn/trả không có cuốn nào | TX1, TX2 |
| E101 | Quá 10 cuốn mỗi lần mượn | TRG1, TX1 |
| E102 | Độc giả đã giữ 50 cuốn | TRG2 |
| E103 | Thẻ hết hạn | TX1, TX7 |
| E104 | Cuốn không có trên giá | TRG2, TX1 |
| E105 | Ngày trả trước ngày mượn | TRG3 |
| E106 | Sửa phiếu trả của dòng đã trả | TRG3 |
| E107 | Phiếu trả và phiếu mượn khác độc giả | TRG3 |
| E108 | Cuốn không do độc giả mượn hoặc đã trả | TX2 |
| E109 | Không có khoản phạt chưa thanh toán | TX3 |
| E110 | Còn nợ phạt, không được thuê phòng | TX7 |
| E201 | Phòng trùng giờ | TRG7 |
| E202 | Vượt sức chứa phòng | TX7 |
| E203 | Số giờ thuê sai quy định loại phòng | TX7 |
| E204 | Ngoài giờ mở cửa chi nhánh | TX7 |
| E205 | Không tìm thấy phòng | TX7 |
| E301 | Giá chỉ chứa sách cùng thể loại | TRG6 |
| E302 | Đầu sách còn cuốn, không xóa được | sp_DauSach_Xoa |
| E303 | Cuốn đã có lịch sử mượn, phải thanh lý | sp_CuonSach_Xoa |
| E304 | Giá sách đã đầy | TRG6 |
| E305 | Sửa mã cuốn sách | TRG6 |
| E306 | Số lượng nhập < 1 | TX4 |
| E401 | Thủ thư trưởng không thuộc chi nhánh | sp_ChiNhanh_Sua |
| E402 | Không tìm thấy / độc giả bị khóa | nhiều procedure |
| E403 | Xóa thủ thư đang là trưởng chi nhánh | sp_ThuThu_Xoa |
| E404 | Xóa độc giả còn giữ sách | TRG8 |
| E405 | Xóa độc giả còn nợ phạt | TRG8 |
| E406 | Sửa mã độc giả | TRG8 |
| E407 | Bảng con ISA không khớp LoaiNguoi | TRG8 |
| E408 | Độc giả phải có ít nhất 1 SĐT | TX6 |

## 4.13 Giao diện ứng dụng

Ứng dụng có 7 chức năng ở thanh bên trái (mượn sách; trả sách và phạt; phòng đọc; độc giả; sách và kho; thủ thư và chi nhánh; báo cáo); người dùng chọn chi nhánh và thủ thư thao tác. Mỗi đối tượng chính đều có đủ thêm, sửa, xóa, tìm kiếm trên giao diện: độc giả, thủ thư, chi nhánh (đổi thủ thư trưởng), đầu sách, cuốn sách (chuyển giá, xóa, thanh lý), giá sách, phòng kho, phòng đọc. Các bảng dữ liệu bấm chọn được cả hàng: form sửa/xóa lấy theo hàng đang chọn và bảng tự nạp lại, bỏ chọn sau mỗi thao tác; các mã đã có trong CSDL (độc giả, cuốn sách khi mượn/trả, phòng, giá, đầu sách khi nhập lô) được chọn từ danh sách có ô gõ để lọc thay vì gõ tay. Trang phòng đọc hiện tiền thuê dự kiến (procedure `sp_ThuePhong_BaoGia`, dùng chung function `fn_TienThuePhong` với TX7) cùng cảnh báo E202/E203 ngay khi đổi phòng, khung giờ hoặc số người. Mỗi nút bấm gọi đúng một stored procedure; khi CSDL từ chối (SIGNAL, CHECK, khóa ngoại), giao diện hiển thị nguyên văn thông báo lỗi, chứng tỏ luật nghiệp vụ nằm hoàn toàn trong CSDL. Kết nối dùng tài khoản `ql_thuvien` (vai trò r_QuanLy), không có quyền ghi trực tiếp vào bảng.

Giao diện được kiểm thử tự động bằng Playwright (script `app/chup_man_hinh.py`): trình duyệt mở từng màn hình, nhập dữ liệu, bấm nút và đọc thông báo trả về. Kết quả: **23/23 thao tác đúng kỳ vọng**.

| # | Thao tác (nút bấm) | Kỳ vọng | Thông báo của hệ thống | Kết quả |
| --- | --- | --- | --- | --- |
| 1 | Lập phiếu mượn | Thành công | Đã lập phiếu mượn số: 832 | PASS |
| 2 | Lập phiếu mượn | Bị chặn | E101: Mỗi lần mượn tối đa 10 cuốn sách | PASS |
| 3 | Lập phiếu trả | Thành công | Đã trả: phiếu 1569, tiền phạt 3230000 đ | PASS |
| 4 | Thanh toán toàn bộ phạt | Thành công | Đã thu: 3,230,000 đ | PASS |
| 5 | Thêm phòng | Thành công | Đã thêm phòng CN01-N6 | PASS |
| 6 | Sửa tên / sức chứa | Thành công | Đã sửa phòng CN01-N6 | PASS |
| 7 | Xóa phòng | Thành công | Đã xóa phòng CN01-N6 | PASS |
| 8 | Đăng ký | Thành công | Đã đăng ký: mã DG0201, thẻ THE0201 | PASS |
| 9 | Lưu sửa | Thành công | Đã sửa DG0201 | PASS |
| 10 | Gia hạn thẻ 1 năm | Thành công | Đã gia hạn thẻ DG0201 | PASS |
| 11 | Xóa độc giả | Thành công | Đã xóa DG0201 | PASS |
| 12 | Xóa độc giả | Bị chặn | E404: Độc giả còn giữ sách, không xóa được | PASS |
| 13 | Thêm phòng kho | Thành công | Đã thêm CN01-K3 | PASS |
| 14 | Thêm giá | Thành công | Đã thêm giá CN01-K1-TR9 | PASS |
| 15 | Sửa sức chứa | Thành công | Đã sửa giá CN01-K1-TR9 | PASS |
| 16 | Xóa giá | Thành công | Đã xóa giá CN01-K1-TR9 | PASS |
| 17 | Xóa phòng kho | Thành công | Đã xóa CN01-K3 | PASS |
| 18 | Xóa cuốn sách | Thành công | Đã xóa GT0026-001 | PASS |
| 19 | Xóa cuốn sách | Bị chặn | E303: Cuốn sách đã có lịch sử mượn, hãy dùng thanh lý thay vì xóa | PASS |
| 20 | Thêm thủ thư | Thành công | Đã thêm thủ thư mã: TT016 | PASS |
| 21 | Lưu sửa thủ thư | Thành công | Đã sửa TT016 | PASS |
| 22 | Xóa thủ thư | Thành công | Đã xóa TT016 | PASS |
| 23 | Xóa thủ thư | Bị chặn | E403: Thủ thư đang là trưởng chi nhánh, đổi trưởng trước khi xóa | PASS |

![Hình 4.7. Màn hình mượn sách](../anh/01_muon_sach.png)

![Hình 4.8. Lập phiếu mượn 3 cuốn thành công](../anh/02a_muon_thanh_cong.png)

![Hình 4.9. Mượn 11 cuốn bị CSDL chặn, hiển thị nguyên văn lỗi E101](../anh/02_muon_qua_10_cuon.png)

![Hình 4.10. Màn hình trả sách: danh sách sách đang giữ và nợ phạt của độc giả](../anh/03_tra_sach.png)

![Hình 4.11. Trả sách quá hạn, trigger tự lập phiếu phạt](../anh/03a_tra_co_phat.png)

![Hình 4.12. Thanh toán toàn bộ phạt (TX3)](../anh/03b_thanh_toan_phat.png)

![Hình 4.13. Màn hình thuê phòng đọc: tiền thuê dự kiến cập nhật theo phòng, khung giờ và tình trạng phòng](../anh/04_thue_phong.png)

![Hình 4.14. Quản lý phòng đọc: thêm phòng mới thành công](../anh/04a_them_phong_doc.png)

![Hình 4.15. Quản lý độc giả: danh sách, bấm chọn hàng để sửa, gia hạn, xóa](../anh/05_doc_gia.png)

![Hình 4.16. Đăng ký độc giả mới (TX6) thành công](../anh/05a_dang_ky_doc_gia.png)

![Hình 4.17. Xóa độc giả còn giữ sách bị trigger chặn (E404)](../anh/05b_xoa_doc_gia_bi_chan.png)

![Hình 4.18. Quản lý sách và kho: tìm kiếm đầu sách](../anh/06_sach_kho.png)

![Hình 4.19. Thêm phòng kho thành công](../anh/06a_them_phong_kho.png)

![Hình 4.20. Thêm giá sách thành công](../anh/06b_them_gia_sach.png)

![Hình 4.21. Xóa cuốn sách đã có lịch sử mượn bị chặn (E303)](../anh/06c_xoa_cuon_bi_chan.png)

![Hình 4.22. Tìm kiếm thủ thư](../anh/07_thu_thu.png)

![Hình 4.23. Thêm thủ thư mới thành công](../anh/07a_them_thu_thu.png)

![Hình 4.24. Xóa thủ thư đang là trưởng chi nhánh bị chặn (E403)](../anh/07b_xoa_truong_bi_chan.png)

# CHƯƠNG 5. PHÂN TÍCH VÀ THIẾT KẾ CƠ SỞ DỮ LIỆU PHÂN TÁN

## 5.1 Bối cảnh và kiến trúc

Thư viện có 3 chi nhánh, mỗi chi nhánh là một **site** có máy chủ CSDL riêng, nối với nhau qua mạng WAN: S1 = CN01 Cầu Giấy (trụ sở), S2 = CN02 Hà Đông, S3 = CN03 Hoàn Kiếm. Phần lớn nghiệp vụ (mượn, trả, thuê phòng, tra cứu kho) diễn ra tại chi nhánh nơi độc giả đăng ký, nên dữ liệu được đặt tại chỗ để giảm truyền thông và cho phép mỗi chi nhánh vẫn hoạt động khi đường mạng tới chi nhánh khác gặp sự cố.

Kiến trúc: **hệ CSDL phân tán thuần nhất** (cùng MariaDB ở mọi site), mô hình tham chiếu nhiều mức của chương 7a:

| Mức | Nội dung trong thiết kế |
| --- | --- |
| Lược đồ toàn cục | 23 quan hệ của mục 3 (database `QLTV`) |
| Lược đồ phân mảnh | Mục 5.3–5.5: ngang nguyên thủy, ngang dẫn xuất, dọc, lai |
| Lược đồ cấp phát | Mục 5.6: mảnh nào đặt ở site nào, mảnh nào nhân bản |
| Lược đồ ánh xạ cục bộ | Mỗi site là một database MariaDB `QLTV_CN0k`; view `pt_*` ánh xạ ngược về quan hệ toàn cục |

Mức trong suốt hướng tới: **trong suốt phân mảnh** – ứng dụng chỉ làm việc với quan hệ toàn cục, thông qua các view tái thiết `pt_*`.

## 5.2 Số liệu giả định dùng cho thiết kế

| Thông số | S1 CN01 | S2 CN02 | S3 CN03 | Ghi chú |
| --- | --- | --- | --- | --- |
| Độc giả | 2.400 | 1.800 | 1.800 | Tổng 6.000 khi hệ thống đầy đủ (dữ liệu demo: 200) |
| Tỷ lệ độc giả bị khóa | 5% | 5% | 5% | Thẻ vi phạm, nợ lâu |
| Cuốn sách | 6.000 | 4.500 | 4.500 | |
| Phiếu mượn mỗi ngày | 120 | 90 | 90 | |
| Đầu sách (danh mục) | 3.000, dùng chung | | | Cập nhật ~5 đầu sách mới/ngày tại S1 |
| Băng thông giữa các site | 20 Mbps, chi phí 1 đơn vị/thông điệp | | | |

## 5.3 Phân mảnh ngang nguyên thủy DOC_GIA

**Ứng dụng:**
- UD1 (chạy tại cả 3 site, ~300 lượt/ngày mỗi site): thủ thư tra cứu, mượn/trả cho độc giả đăng ký tại chi nhánh mình → `WHERE MaChiNhanh = 'CN0k'`.
- UD2 (chạy tại S1, ~4 lượt/tháng): bộ phận quản lý rà soát độc giả bị khóa để mở khóa hoặc xóa → `WHERE TrangThai = 'Khoa'`.

**Tập vị từ đơn giản:** Pr = { p1: MaChiNhanh = 'CN01'; p2: MaChiNhanh = 'CN02'; p3: MaChiNhanh = 'CN03'; p4: TrangThai = 'Khoa' }.

**Thuật toán COM_MIN:**
1. Chọn p1: p1 phân hoạch DOC_GIA thành {CN01} và {còn lại}, hai phần được UD1 truy nhập khác nhau (S1 chỉ truy nhập phần CN01) → p1 liên đới. Pr' = {p1}, F = {f1}.
2. Thêm p2: tách phần "còn lại" thành CN02 và CN03, S2 chỉ truy nhập phần CN02 → liên đới. Pr' = {p1, p2}.
3. Thêm p3: tương tự, S3 chỉ truy nhập phần CN03 → liên đới. Pr' = {p1, p2, p3}.
4. Thêm p4: tách mỗi mảnh theo trạng thái. Xét mi = p1 ∧ p4 (CN01, khóa, 120 bộ) và mj = p1 ∧ ¬p4 (CN01, hoạt động, 2.280 bộ). UD1 truy nhập đều các bộ CN01 (9.000 lượt/tháng) nên phân cho mi 9.000 × 120/2.400 = 450 lượt và mj 8.550 lượt; UD2 thêm 4 lượt/tháng chỉ vào mi. acc(mi)/card(fi) = 454/120 ≈ 3,78 ≠ acc(mj)/card(fj) = 8.550/2.280 = 3,75 → có ứng dụng (UD2) truy nhập hai mảnh khác nhau → p4 liên đới. Pr' = {p1, p2, p3, p4}.
5. Không còn vị từ; kiểm tra lại không vị từ nào trong Pr' mất tính liên đới → **Pr' đầy đủ và cực tiểu**.

*Ví dụ không cực tiểu:* nếu thêm p5: GioiTinh = 'M', p5 chia mỗi mảnh thành 2 phần nhưng không ứng dụng nào truy nhập hai phần này khác nhau (acc/card bằng nhau) → p5 không liên đới, Pr' ∪ {p5} không cực tiểu, nên loại p5.

**Thuật toán PHORIZONTAL:**
- Số vị từ hội sơ cấp lý thuyết: 2⁴ = 16 (mỗi pi ở dạng khẳng định hoặc phủ định).
- Tập phép kéo theo I: p1 ⇒ ¬p2 ∧ ¬p3; p2 ⇒ ¬p1 ∧ ¬p3; p3 ⇒ ¬p1 ∧ ¬p2; ¬p1 ∧ ¬p2 ⇒ p3 (miền MaChiNhanh chỉ có 3 giá trị).
- Loại các minterm mâu thuẫn với I (hai chi nhánh cùng lúc, hoặc không chi nhánh nào) → còn **6 minterm**:

| Mảnh | Vị từ hội sơ cấp | Biểu thức | Số bộ giả định | Số bộ dữ liệu demo |
| --- | --- | --- | --- | --- |
| DOC_GIA_1 | p1 ∧ ¬p4 | σ MaChiNhanh='CN01' ∧ TrangThai='HoatDong' (DOC_GIA) | 2.280 | 67 |
| DOC_GIA_2 | p1 ∧ p4 | σ MaChiNhanh='CN01' ∧ TrangThai='Khoa' (DOC_GIA) | 120 | 0 |
| DOC_GIA_3 | p2 ∧ ¬p4 | σ MaChiNhanh='CN02' ∧ TrangThai='HoatDong' (DOC_GIA) | 1.710 | 67 |
| DOC_GIA_4 | p2 ∧ p4 | σ MaChiNhanh='CN02' ∧ TrangThai='Khoa' (DOC_GIA) | 90 | 0 |
| DOC_GIA_5 | p3 ∧ ¬p4 | σ MaChiNhanh='CN03' ∧ TrangThai='HoatDong' (DOC_GIA) | 1.710 | 66 |
| DOC_GIA_6 | p3 ∧ p4 | σ MaChiNhanh='CN03' ∧ TrangThai='Khoa' (DOC_GIA) | 90 | 0 |

Các mảnh "Khoa" rỗng trong dữ liệu demo (chưa có độc giả bị khóa), tương tự PROJ2, PROJ5 trong ví dụ của slide; chúng vẫn được giữ trong lược đồ vì ràng buộc nghiệp vụ cho phép phát sinh.

Tương tự, **THU_THU, PHONG_KHO, PHONG_DOC** được phân mảnh ngang nguyên thủy theo vị từ MaChiNhanh = 'CN0k' (ứng dụng duy nhất là truy nhập theo chi nhánh) → mỗi quan hệ 3 mảnh.

## 5.4 Phân mảnh ngang dẫn xuất

Đường liên kết (owner → member) và các mảnh dẫn xuất bằng phép bán kết nối ⋉:

| Quan hệ member | Owner | Mảnh dẫn xuất (k = 1..3 theo chi nhánh) |
| --- | --- | --- |
| SDT_NGUOI (độc giả), THE_DOC_GIA | DOC_GIA | SDT_k = SDT_NGUOI ⋉ (DOC_GIA_{2k-1} ∪ DOC_GIA_{2k}); THE_k tương tự |
| PHIEU_MUON | DOC_GIA | PHIEU_MUON_k = PHIEU_MUON ⋉_{MaDocGia = MaNguoi} DOC_GIA_k |
| PHIEU_TRA | DOC_GIA | PHIEU_TRA_k = PHIEU_TRA ⋉ DOC_GIA_k |
| CT_MUON | PHIEU_MUON | CT_MUON_k = CT_MUON ⋉ PHIEU_MUON_k |
| PHIEU_PHAT | CT_MUON | PHIEU_PHAT_k = PHIEU_PHAT ⋉ CT_MUON_k |
| GIA_SACH | PHONG_KHO | GIA_SACH_k = GIA_SACH ⋉ PHONG_KHO_k |
| CUON_SACH | GIA_SACH | CUON_SACH_k = CUON_SACH ⋉ GIA_SACH_k |
| PHIEU_THUE_PHONG | PHONG_DOC | THUE_k = PHIEU_THUE_PHONG ⋉ PHONG_DOC_k |
| NGUOI (thủ thư) | THU_THU | NGUOI_TT_k = NGUOI ⋉ THU_THU_k |

Nhận xét:
- Xảy ra **phân mảnh dây chuyền** giống ví dụ PAY → EMP → ASG trong slide: DOC_GIA → PHIEU_MUON → CT_MUON → PHIEU_PHAT và PHONG_KHO → GIA_SACH → CUON_SACH.
- CT_MUON có hai owner có thể chọn (PHIEU_MUON và CUON_SACH). Nhóm chọn PHIEU_MUON vì (1) đặc tính kết nối tốt hơn: các truy vấn mượn/trả và báo cáo luôn kết nối CT_MUON với PHIEU_MUON và độc giả; (2) phục vụ nhiều ứng dụng hơn (mượn, trả, phạt, báo cáo 1, 2, 4). Theo số liệu, độc giả mượn sách tại chi nhánh mình đăng ký (dữ liệu demo: 0 lượt mượn khác chi nhánh), nên CT_MUON_k ⋈ CUON_SACH_k hoàn toàn cục bộ.
- Nghiệp vụ vẫn **cho phép mượn liên chi nhánh** (CSDL không cấm). Khi đó dòng CT_MUON thuộc mảnh của chi nhánh độc giả (dẫn xuất theo PHIEU_MUON), còn cuốn sách nằm ở mảnh CUON_SACH của site khác: giao tác mượn/trả phải cập nhật hai site (trạng thái cuốn, số lượng trên giá) nên cần giao tác phân tán (cam kết hai pha); truy vấn ghép CT_MUON với CUON_SACH khi đó phải truy cập site xa. Vì tần suất thấp, nhóm chấp nhận chi phí này thay vì nhân bản CUON_SACH.

## 5.5 Phân mảnh dọc và phân mảnh lai NGUOI (phần độc giả)

Quan hệ NGUOI chứa thông tin cá nhân độc giả, nhưng các ứng dụng chỉ dùng từng nhóm thuộc tính. Khóa MaNguoi có mặt ở mọi mảnh nên không đưa vào ma trận lực hút (theo Özsu & Valduriez). Gom thuộc tính kép thành một thuộc tính khi phân tích: A1 = HoTen (Ho, Dem, Ten), A2 = NgaySinh (+ GioiTinh), A3 = DiaChi (SoNha, Phuong, Quan, TinhTP), A4 = Email.

**Ứng dụng và tần suất (lượt/ngày, ref = 1):**

| Ứng dụng | Câu truy vấn | S1 | S2 | S3 |
| --- | --- | --- | --- | --- |
| q1 | Tra cứu tên độc giả khi mượn/trả: SELECT HoTen WHERE MaNguoi = ? | 45 | 30 | 25 |
| q2 | Gửi email nhắc hạn trả: SELECT HoTen, Email WHERE MaNguoi IN (…) | 25 | 20 | 15 |
| q3 | Thống kê độ tuổi theo khu vực: SELECT NgaySinh, DiaChi | 40 | 30 | 30 |
| q4 | In/cấp lại thẻ: SELECT HoTen, NgaySinh, DiaChi WHERE MaNguoi = ? | 5 | 3 | 2 |

**Ma trận sử dụng A** (hàng q1..q4, cột A1..A4): q1 = [1,0,0,0]; q2 = [1,0,0,1]; q3 = [0,1,1,0]; q4 = [1,1,1,0].

**Ma trận lực hút AA**, aff(Ai, Aj) = Σ_{qk dùng cả Ai, Aj} Σ_sites acc:

|  | A1 | A2 | A3 | A4 |
| --- | --- | --- | --- | --- |
| A1 | 170 | 10 | 10 | 60 |
| A2 | 10 | 110 | 110 | 0 |
| A3 | 10 | 110 | 110 | 0 |
| A4 | 60 | 0 | 0 | 60 |

Ví dụ: aff(A1, A1) = q1 + q2 + q4 = 100 + 60 + 10 = 170; aff(A2, A3) = q3 + q4 = 100 + 10 = 110.

**Thuật toán BEA** (bond(Ax, Ay) = Σz aff(Az, Ax)·aff(Az, Ay); cont(Ai, Ak, Aj) = 2·bond(Ai, Ak) + 2·bond(Ak, Aj) − 2·bond(Ai, Aj); A0, A5 là cột biên bằng 0):

1. Khởi tạo CA với cột A1, A2.
2. Đặt A3: cont(A0, A3, A1) = 7.800; cont(A1, A3, A2) = 48.600; cont(A2, A3, A5) = 48.600 → chọn vị trí đầu tiên đạt max: giữa A1 và A2 → thứ tự A1, A3, A2.
3. Đặt A4: cont(A0, A4, A1) = 27.600; cont(A1, A4, A3) = 21.000; cont(A3, A4, A2) = −46.200; cont(A2, A4, A5) = 1.200 → đặt A4 bên trái A1 → thứ tự **A4, A1, A3, A2**.
4. Sắp hàng theo thứ tự cột, được ma trận CA hai khối rõ rệt:

|  | A4 | A1 | A3 | A2 |
| --- | --- | --- | --- | --- |
| A4 | 60 | 60 | 0 | 0 |
| A1 | 60 | 170 | 10 | 10 |
| A3 | 0 | 10 | 110 | 110 |
| A2 | 0 | 10 | 110 | 110 |

**Chọn điểm chia** (z = CTQ·CBQ − COQ², lấy max):

| x | TA | BA | TQ | BQ | OQ | CTQ | CBQ | COQ | z |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | {A4} | {A1, A3, A2} | — | q1, q3, q4 | q2 | 0 | 210 | 60 | −3.600 |
| **2** | **{A4, A1}** | **{A3, A2}** | q1, q2 | q3 | q4 | 160 | 100 | 10 | **15.900** |
| 3 | {A4, A1, A3} | {A2} | q1, q2 | — | q3, q4 | 160 | 0 | 110 | −12.100 |

**Kết quả:** NGUOI_DG_A(MaNguoi, Ho, Dem, Ten, Email, LoaiNguoi) và NGUOI_DG_B(MaNguoi, NgaySinh, GioiTinh, SoNha, Phuong, Quan, TinhTP). Chỉ q4 (10 lượt/ngày) phải kết nối hai mảnh.

**Phân mảnh lai:** NGUOI (độc giả) trước hết được phân mảnh ngang dẫn xuất theo DOC_GIA của từng chi nhánh, rồi mỗi mảnh ngang được phân mảnh dọc như trên → 6 mảnh: NGUOI_DG_A_k, NGUOI_DG_B_k (k = 1..3). Tái thiết: NGUOI_DG = ∪_k (NGUOI_DG_A_k ⋈ NGUOI_DG_B_k).

## 5.6 Kiểm tra tính đúng đắn của phân mảnh

| Quy tắc | Phân mảnh ngang (DOC_GIA và các mảnh dẫn xuất) | Phân mảnh dọc (NGUOI_DG_A, NGUOI_DG_B) |
| --- | --- | --- |
| Đầy đủ | Mỗi bộ có MaChiNhanh ∈ {CN01, CN02, CN03} và TrangThai ∈ {HoatDong, Khoa} (CHECK) nên thuộc đúng một minterm; mảnh dẫn xuất đầy đủ nhờ ràng buộc khóa ngoại | A ∪ B = toàn bộ thuộc tính của NGUOI |
| Tái thiết | DOC_GIA = ∪ DOC_GIA_i | NGUOI_DG = A ⋈_MaNguoi B |
| Tách biệt | Các minterm loại trừ nhau; mỗi phiếu thuộc đúng một độc giả nên mảnh dẫn xuất cũng rời nhau | A ∩ B = {MaNguoi} (chỉ chung khóa) |

Kiểm chứng trên dữ liệu bằng `09_phan_tan.sql`: dùng EXCEPT (đầy đủ), so sánh số bộ của hợp các mảnh với quan hệ gốc (tái thiết), đếm khóa trùng giữa các mảnh (tách biệt) cho 12 quan hệ → **36/36 PASS**.

## 5.7 Cấp phát và nhân bản

**Phân tích chi phí cho quyết định nhân bản** (chi phí truyền thông, 1 đơn vị/thông điệp, theo ngày):

| Quan hệ | Đọc/ngày | Ghi/ngày | Phương án 1 bản tại S1 | Nhân bản tại 3 site | Quyết định |
| --- | --- | --- | --- | --- | --- |
| DAU_SACH, TAC_GIA, DAU_SACH_TAC_GIA | 1.500 mỗi site (tra cứu, tính hạn trả) | 5 (S1) | Đọc từ xa của S2, S3: 3.000 | Đồng bộ ghi tới 2 site: 5 × 2 = 10 | Nhân bản toàn phần |
| THE_LOAI, BANG_PHI_PHAT, LOAI_PHONG, CHI_NHANH | ~800 mỗi site (TRG3, TX1, TX7) | ~0 | 1.600 | ≈ 0 | Nhân bản toàn phần |
| CUON_SACH_k | 1.200 tại site k, 60 từ site khác (tìm sách liên chi nhánh) | 250 tại site k | 60 | 250 × 2 = 500 | Không nhân bản, đặt tại site k |
| SACH_THANH_LY, CT_MUON_LUU_TRU | Vài lượt/tháng | Vài lần/năm | Gần 0 | — | Một bản tại S1 |

**Lược đồ cấp phát** (Rij = mảnh i đặt tại site j; số bộ theo dữ liệu demo):

| Site | Mảnh cấp phát (không nhân bản) | Số bộ demo |
| --- | --- | --- |
| S1 (CN01) | DOC_GIA_1, DOC_GIA_2; NGUOI_DG_A_1, NGUOI_DG_B_1; THE_1; PHIEU_MUON_1; CT_MUON_1; PHIEU_TRA_1; PHIEU_PHAT_1; THU_THU_1, NGUOI_TT_1; PHONG_KHO_1; GIA_SACH_1; CUON_SACH_1; PHONG_DOC_1; THUE_1; SACH_THANH_LY; CT_MUON_LUU_TRU | độc giả 67, phiếu mượn 272, chi tiết mượn 751, phiếu trả 531, phiếu phạt 111, cuốn 475, giá 9, thủ thư 5, phòng 7, lượt thuê 51 |
| S2 (CN02) | Các mảnh k = 2 tương ứng | độc giả 67, phiếu mượn 281, chi tiết 737, phiếu trả 512, phạt 107, cuốn 434, giá 10, thủ thư 5, phòng 7, lượt thuê 51 |
| S3 (CN03) | Các mảnh k = 3 tương ứng | độc giả 66, phiếu mượn 278, chi tiết 713, phiếu trả 525, phạt 97, cuốn 460, giá 8, thủ thư 5, phòng 7, lượt thuê 48 |
| S1, S2, S3 | **Bản sao toàn phần:** CHI_NHANH, THE_LOAI, BANG_PHI_PHAT, LOAI_PHONG, DAU_SACH, TAC_GIA, DAU_SACH_TAC_GIA | 3, 6, 7, 2, 300, 28, 391 |

Mô hình cấp phát tổng quát (chương 7c): biến quyết định x_ij = 1 nếu mảnh Fi đặt tại Sj; cực tiểu Tổng chi phí = Σ lưu trữ (USC_k · size(Fj) · x_jk) + Σ truy vấn (xử lý PC_i + truyền thông TC_i), với ràng buộc thời gian đáp ứng, dung lượng lưu trữ và năng lực xử lý từng site. Bài toán là NP-complete nên nhóm dùng heuristic: (1) bỏ qua nhân bản, đặt mỗi mảnh tại site truy cập nhiều nhất (site của chi nhánh); (2) xét nhân bản cho từng quan hệ theo bảng chi phí trên.

## 5.8 Sơ đồ tổng thể hệ thống

![Hình 5.1. Sơ đồ tổng thể hệ CSDL phân tán của thư viện](../phan_tan/so_do_tong_the.png)

ba site S1, S2, S3 nối qua WAN; mỗi site gồm DBMS cục bộ MariaDB, CSDL cục bộ chứa các mảnh của chi nhánh và bản sao danh mục; tầng trên là lược đồ toàn cục + lược đồ phân mảnh + lược đồ cấp phát; ứng dụng thủ thư ở mỗi chi nhánh truy cập qua lớp trong suốt phân tán.

**Xử lý truy vấn phân tán (ví dụ):** báo cáo "độc giả trả muộn" toàn hệ thống = ∪_k γ_MaDocGia(PHIEU_PHAT_k ⋈ PHIEU_MUON_k): mỗi site tính cục bộ phần của mình rồi gửi kết quả gộp (vài chục bộ) về site yêu cầu, thay vì gửi toàn bộ bảng phạt. Truy vấn tìm sách liên chi nhánh dùng bán kết nối: gửi π_MaDauSach của kết quả tìm kiếm tới site khác, chỉ nhận về các cuốn khớp, giảm khối lượng truyền như mục đích của phép ⋉ ở chương 4.

## 5.9 Minh họa cài đặt trên MariaDB

`btl/sql/09_phan_tan.sql` (sinh bởi `btl/phan_tan/gen_phantan.py`) tạo 3 database `QLTV_CN01..03` trên cùng một máy chủ để mô phỏng 3 site, dùng `CREATE TABLE … AS SELECT … WHERE` (phép chọn), `… WHERE MaX IN (SELECT …)` (bán kết nối) và chọn cột (phép chiếu) để tạo mảnh; tạo view `pt_*` bằng UNION ALL / JOIN để tái thiết; bảng KIEM_TRA_PHAN_TAN ghi kết quả kiểm tra 3 quy tắc. Trên hệ thống thật, mỗi database đặt trên một máy chủ riêng và các view tái thiết dùng engine CONNECT/FederatedX hoặc lớp ứng dụng để truy cập site xa.

# KẾT LUẬN

Nhóm đã xây dựng hoàn chỉnh hệ CSDL quản lý thư viện theo kịch bản được giao:

- Lược đồ E-R có đủ các loại tập thực thể (mạnh, yếu, ISA), thuộc tính (đơn, kép, đa trị, dẫn xuất, rỗng) và liên kết (1:1, 1:N, N:N, đệ quy, 3 ngôi, xác định, kết hợp, ràng buộc min-max).
- 23 lược đồ quan hệ ở dạng chuẩn BCNF, có phụ thuộc hàm, khóa, quá trình chuẩn hóa minh họa, sơ đồ khóa chính – khóa ngoại và từ điển dữ liệu.
- Cài đặt trên MariaDB với 23 khóa chính, 34 khóa ngoại, 11 UNIQUE, 44 CHECK; 8 trigger, 7 transaction, 8 function và các procedure thêm/xóa/sửa/tìm kiếm cho mọi đối tượng.
- Dữ liệu vận hành 3 tháng ở 3 chi nhánh (300 đầu sách, 1.623 cuốn, 200 độc giả, 831 phiếu mượn, 2.217 lượt mượn); 6 truy vấn hiển thị theo đúng yêu cầu sắp xếp của đề; chỉ mục, phân quyền và 47 ca kiểm thử tự động đều đạt.
- Giao diện có đủ thêm/xóa/sửa/tìm kiếm cho các đối tượng chính, 23 thao tác được kiểm thử tự động bằng trình duyệt đều cho kết quả đúng kỳ vọng.
- Thiết kế phân tán cho 3 site: phân mảnh ngang nguyên thủy (COM_MIN, PHORIZONTAL), dẫn xuất, dọc (BEA), lai; cấp phát, nhân bản; minh họa cài đặt và kiểm chứng 3 quy tắc phân mảnh (36/36 đạt).

Hướng phát triển: triển khai các site trên máy chủ thật với nhân bản MariaDB (replication) cho các bảng danh mục, bổ sung đặt trước sách và thông báo hạn trả tự động qua email.

# PHỤ LỤC A. MÃ NGUỒN SQL

Mã nguồn đầy đủ của các script chính (các file 05_seed.sql, 08_test.sql, 09_phan_tan.sql dài và được sinh tự động, nộp kèm theo).

## A.1 Tạo bảng và ràng buộc (01_schema.sql)

```sql
-- =====================================================================
-- 01_schema.sql  –  Hệ thống quản lý thư viện  (MariaDB 10.11+ / 11.4)
-- Tạo CSDL, 23 bảng và toàn bộ ràng buộc PK, FK, UNIQUE, CHECK, DEFAULT
-- =====================================================================
SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;
DROP DATABASE IF EXISTS QLTV;
CREATE DATABASE QLTV CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE QLTV;
SET default_storage_engine = InnoDB;
-- Lưu ý MariaDB: CHECK không được dùng cột thuộc khóa ngoại có ON UPDATE/DELETE CASCADE
-- hoặc SET NULL (lỗi 1901). Các khóa ngoại có CHECK đi kèm vì vậy để mặc định RESTRICT;
-- việc xóa dây chuyền độc giả/thủ thư được xử lý trong procedure.

-- ---------------------------------------------------------------------
-- 1. Con người và chi nhánh
-- ---------------------------------------------------------------------
CREATE TABLE CHI_NHANH (
  MaChiNhanh      CHAR(4)      NOT NULL,
  TenChiNhanh     VARCHAR(100) NOT NULL,
  DiaChi          VARCHAR(200) NOT NULL,
  GioMo           TIME         NOT NULL DEFAULT '07:00:00',
  GioDong         TIME         NOT NULL DEFAULT '21:00:00',
  MaThuThuTruong  VARCHAR(10)  NULL,            -- FK vòng, thêm sau bằng ALTER TABLE
  CONSTRAINT PK_CHI_NHANH PRIMARY KEY (MaChiNhanh),
  CONSTRAINT UQ_CHI_NHANH_Ten UNIQUE (TenChiNhanh),
  CONSTRAINT UQ_CHI_NHANH_Truong UNIQUE (MaThuThuTruong),       -- liên kết 1:1
  CONSTRAINT CK_CHI_NHANH_Ma CHECK (MaChiNhanh REGEXP '^CN[0-9]{2}$'),
  CONSTRAINT CK_CHI_NHANH_Gio CHECK (GioMo < GioDong)
);

CREATE TABLE NGUOI (                               -- lớp cha của ISA
  MaNguoi    VARCHAR(10)  NOT NULL,
  Ho         VARCHAR(30)  NOT NULL,               -- thuộc tính kép HoTen
  Dem        VARCHAR(30)  NULL,
  Ten        VARCHAR(30)  NOT NULL,
  NgaySinh   DATE         NOT NULL,
  GioiTinh   CHAR(1)      NOT NULL,
  SoNha      VARCHAR(50)  NULL,                   -- thuộc tính kép DiaChi
  Phuong     VARCHAR(50)  NULL,
  Quan       VARCHAR(50)  NULL,
  TinhTP     VARCHAR(50)  NOT NULL,
  Email      VARCHAR(100) NULL,
  LoaiNguoi  CHAR(2)      NOT NULL,               -- thuộc tính phân biệt ISA
  CONSTRAINT PK_NGUOI PRIMARY KEY (MaNguoi),
  CONSTRAINT UQ_NGUOI_Email UNIQUE (Email),
  CONSTRAINT CK_NGUOI_Loai CHECK (LoaiNguoi IN ('DG','TT')),
  CONSTRAINT CK_NGUOI_Ma CHECK ((LoaiNguoi = 'DG' AND MaNguoi REGEXP '^DG[0-9]{4}$')
                             OR (LoaiNguoi = 'TT' AND MaNguoi REGEXP '^TT[0-9]{3}$')),
  CONSTRAINT CK_NGUOI_GioiTinh CHECK (GioiTinh IN ('M','F')),
  CONSTRAINT CK_NGUOI_NgaySinh CHECK (NgaySinh >= '1920-01-01'),
  CONSTRAINT CK_NGUOI_Email CHECK (Email IS NULL OR Email LIKE '%_@_%._%')
);

CREATE TABLE SDT_NGUOI (                           -- thuộc tính đa trị
  MaNguoi      VARCHAR(10) NOT NULL,
  SoDienThoai  VARCHAR(10) NOT NULL,
  CONSTRAINT PK_SDT_NGUOI PRIMARY KEY (MaNguoi, SoDienThoai),
  CONSTRAINT FK_SDT_NGUOI FOREIGN KEY (MaNguoi) REFERENCES NGUOI(MaNguoi)
      ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT CK_SDT_Dang CHECK (SoDienThoai REGEXP '^0[0-9]{9}$')
);

CREATE TABLE DOC_GIA (                             -- lớp con ISA
  MaNguoi     VARCHAR(10) NOT NULL,
  MaChiNhanh  CHAR(4)     NOT NULL,
  NgayDangKy  DATE        NOT NULL,
  TrangThai   VARCHAR(10) NOT NULL DEFAULT 'HoatDong',
  CONSTRAINT PK_DOC_GIA PRIMARY KEY (MaNguoi),
  CONSTRAINT FK_DOCGIA_NGUOI FOREIGN KEY (MaNguoi) REFERENCES NGUOI(MaNguoi),
  CONSTRAINT FK_DOCGIA_CHINHANH FOREIGN KEY (MaChiNhanh) REFERENCES CHI_NHANH(MaChiNhanh),
  CONSTRAINT CK_DOCGIA_Ma CHECK (MaNguoi LIKE 'DG%'),
  CONSTRAINT CK_DOCGIA_TrangThai CHECK (TrangThai IN ('HoatDong','Khoa'))
);

CREATE TABLE THE_DOC_GIA (
  SoThe       VARCHAR(12) NOT NULL,
  MaDocGia    VARCHAR(10) NOT NULL,
  NgayCap     DATE        NOT NULL,
  NgayHetHan  DATE        NOT NULL,
  CONSTRAINT PK_THE_DOC_GIA PRIMARY KEY (SoThe),
  CONSTRAINT UQ_THE_DocGia UNIQUE (MaDocGia),                   -- liên kết 1:1
  CONSTRAINT FK_THE_DOCGIA FOREIGN KEY (MaDocGia) REFERENCES DOC_GIA(MaNguoi)
      ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT CK_THE_Han CHECK (NgayHetHan > NgayCap)
);

CREATE TABLE THU_THU (                             -- lớp con ISA
  MaNguoi     VARCHAR(10) NOT NULL,
  MaChiNhanh  CHAR(4)     NOT NULL,
  NgayVaoLam  DATE        NOT NULL,
  MaQuanLy    VARCHAR(10) NULL,                    -- liên kết đệ quy
  CONSTRAINT PK_THU_THU PRIMARY KEY (MaNguoi),
  CONSTRAINT FK_THUTHU_NGUOI FOREIGN KEY (MaNguoi) REFERENCES NGUOI(MaNguoi),
  CONSTRAINT FK_THUTHU_CHINHANH FOREIGN KEY (MaChiNhanh) REFERENCES CHI_NHANH(MaChiNhanh),
  CONSTRAINT FK_THUTHU_QUANLY FOREIGN KEY (MaQuanLy) REFERENCES THU_THU(MaNguoi),
  CONSTRAINT CK_THUTHU_Ma CHECK (MaNguoi LIKE 'TT%'),
  CONSTRAINT CK_THUTHU_QuanLy CHECK (MaQuanLy IS NULL OR MaQuanLy <> MaNguoi)
);

ALTER TABLE CHI_NHANH
  ADD CONSTRAINT FK_CHINHANH_TRUONG FOREIGN KEY (MaThuThuTruong) REFERENCES THU_THU(MaNguoi)
      ON DELETE SET NULL;

-- ---------------------------------------------------------------------
-- 2. Kho sách
-- ---------------------------------------------------------------------
CREATE TABLE THE_LOAI (
  MaTheLoai   CHAR(2)     NOT NULL,
  TenTheLoai  VARCHAR(50) NOT NULL,
  SoNgayMuon  SMALLINT    NOT NULL,
  TuoiThoNam  TINYINT     NOT NULL,
  CONSTRAINT PK_THE_LOAI PRIMARY KEY (MaTheLoai),
  CONSTRAINT UQ_THE_LOAI_Ten UNIQUE (TenTheLoai),
  CONSTRAINT CK_THELOAI_Ma CHECK (MaTheLoai REGEXP '^[A-Z]{2}$'),
  CONSTRAINT CK_THELOAI_SoNgay CHECK (SoNgayMuon BETWEEN 1 AND 90),
  CONSTRAINT CK_THELOAI_TuoiTho CHECK (TuoiThoNam BETWEEN 1 AND 50)
);

CREATE TABLE BANG_PHI_PHAT (                       -- thực thể yếu của THE_LOAI
  MaTheLoai    CHAR(2)       NOT NULL,
  NgayApDung   DATE          NOT NULL,             -- khóa bán phần
  PhatCoBan    DECIMAL(12,0) NOT NULL,
  PhatMoiNgay  DECIMAL(12,0) NOT NULL,
  CONSTRAINT PK_BANG_PHI_PHAT PRIMARY KEY (MaTheLoai, NgayApDung),
  CONSTRAINT FK_PHIPHAT_THELOAI FOREIGN KEY (MaTheLoai) REFERENCES THE_LOAI(MaTheLoai)
      ON DELETE CASCADE,
  CONSTRAINT CK_PHIPHAT_Tien CHECK (PhatCoBan >= 0 AND PhatMoiNgay >= 0)
);

CREATE TABLE TAC_GIA (
  MaTacGia   INT          NOT NULL AUTO_INCREMENT,
  TenTacGia  VARCHAR(100) NOT NULL,
  QuocTich   VARCHAR(50)  NULL,
  CONSTRAINT PK_TAC_GIA PRIMARY KEY (MaTacGia)
);

CREATE TABLE DAU_SACH (
  MaDauSach        CHAR(6)      NOT NULL,          -- vd TR0012
  MaTheLoai        CHAR(2)      NOT NULL,
  TenSach          VARCHAR(200) NOT NULL,
  NhaXuatBan       VARCHAR(100) NULL,
  NamXuatBan       SMALLINT     NULL,
  SoNgayMuonRieng  SMALLINT     NULL,              -- hạn mượn riêng theo nội dung
  CONSTRAINT PK_DAU_SACH PRIMARY KEY (MaDauSach),
  CONSTRAINT FK_DAUSACH_THELOAI FOREIGN KEY (MaTheLoai) REFERENCES THE_LOAI(MaTheLoai),
  CONSTRAINT CK_DAUSACH_Ma CHECK (MaDauSach REGEXP '^[A-Z]{2}[0-9]{4}$'),
  CONSTRAINT CK_DAUSACH_TheLoai CHECK (MaTheLoai = LEFT(MaDauSach, 2)),
  CONSTRAINT CK_DAUSACH_Nam CHECK (NamXuatBan IS NULL OR NamXuatBan BETWEEN 1900 AND 2100),
  CONSTRAINT CK_DAUSACH_SoNgay CHECK (SoNgayMuonRieng IS NULL OR SoNgayMuonRieng BETWEEN 1 AND 90)
);

CREATE TABLE DAU_SACH_TAC_GIA (                    -- liên kết N:N viet
  MaDauSach  CHAR(6) NOT NULL,
  MaTacGia   INT     NOT NULL,
  CONSTRAINT PK_DAU_SACH_TAC_GIA PRIMARY KEY (MaDauSach, MaTacGia),
  CONSTRAINT FK_DSTG_DAUSACH FOREIGN KEY (MaDauSach) REFERENCES DAU_SACH(MaDauSach)
      ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT FK_DSTG_TACGIA FOREIGN KEY (MaTacGia) REFERENCES TAC_GIA(MaTacGia)
      ON DELETE CASCADE
);

CREATE TABLE PHONG_KHO (
  MaPhongKho  VARCHAR(8)  NOT NULL,                -- vd CN01-K1
  MaChiNhanh  CHAR(4)     NOT NULL,
  TenPhong    VARCHAR(50) NOT NULL,
  Tang        TINYINT     NOT NULL DEFAULT 1,
  CONSTRAINT PK_PHONG_KHO PRIMARY KEY (MaPhongKho),
  CONSTRAINT UQ_PHONGKHO_Ten UNIQUE (MaChiNhanh, TenPhong),
  CONSTRAINT FK_PHONGKHO_CHINHANH FOREIGN KEY (MaChiNhanh) REFERENCES CHI_NHANH(MaChiNhanh),
  CONSTRAINT CK_PHONGKHO_Tang CHECK (Tang BETWEEN 0 AND 20)
);

CREATE TABLE GIA_SACH (
  MaGia          VARCHAR(12) NOT NULL,             -- vd CN01-K1-TR1
  MaPhongKho     VARCHAR(8)  NOT NULL,
  MaTheLoai      CHAR(2)     NOT NULL,             -- mỗi giá chỉ 1 thể loại
  SucChua        SMALLINT    NOT NULL DEFAULT 100,
  SoLuongHienCo  SMALLINT    NOT NULL DEFAULT 0,
  CONSTRAINT PK_GIA_SACH PRIMARY KEY (MaGia),
  CONSTRAINT FK_GIASACH_PHONGKHO FOREIGN KEY (MaPhongKho) REFERENCES PHONG_KHO(MaPhongKho),
  CONSTRAINT FK_GIASACH_THELOAI FOREIGN KEY (MaTheLoai) REFERENCES THE_LOAI(MaTheLoai),
  CONSTRAINT CK_GIASACH_SucChua CHECK (SucChua BETWEEN 1 AND 100),
  CONSTRAINT CK_GIASACH_SoLuong CHECK (SoLuongHienCo BETWEEN 0 AND SucChua)
);

CREATE TABLE CUON_SACH (                           -- thực thể yếu của DAU_SACH
  MaCuonSach          VARCHAR(10) NOT NULL,        -- vd TR0012-003
  MaDauSach           CHAR(6)     NOT NULL,
  STT                 SMALLINT    NOT NULL,        -- khóa bán phần
  MaGia               VARCHAR(12) NOT NULL,
  NgayNhap            DATE        NOT NULL,
  TuoiThoConLaiThang  SMALLINT    NOT NULL,
  TrangThai           VARCHAR(12) NOT NULL DEFAULT 'TrenGia',
  CONSTRAINT PK_CUON_SACH PRIMARY KEY (MaCuonSach),
  CONSTRAINT UQ_CUONSACH_DauSach_STT UNIQUE (MaDauSach, STT),
  CONSTRAINT FK_CUONSACH_DAUSACH FOREIGN KEY (MaDauSach) REFERENCES DAU_SACH(MaDauSach),
  CONSTRAINT FK_CUONSACH_GIASACH FOREIGN KEY (MaGia) REFERENCES GIA_SACH(MaGia),
  CONSTRAINT CK_CUONSACH_Ma CHECK (MaCuonSach = CONCAT(MaDauSach, '-', LPAD(STT, 3, '0'))),
  CONSTRAINT CK_CUONSACH_STT CHECK (STT BETWEEN 1 AND 999),
  CONSTRAINT CK_CUONSACH_TuoiTho CHECK (TuoiThoConLaiThang >= 0),
  CONSTRAINT CK_CUONSACH_TrangThai CHECK (TrangThai IN ('TrenGia','DangMuon','ChoThanhLy'))
);

CREATE TABLE SACH_THANH_LY (                       -- danh mục riêng, tách khỏi kho
  MaCuonSach   VARCHAR(10)  NOT NULL,
  MaDauSach    CHAR(6)      NOT NULL,
  STT          SMALLINT     NOT NULL,
  NgayNhap     DATE         NOT NULL,
  NgayThanhLy  DATE         NOT NULL,
  LyDo         VARCHAR(200) NOT NULL DEFAULT 'Hết niên hạn sử dụng',
  CONSTRAINT PK_SACH_THANH_LY PRIMARY KEY (MaCuonSach),
  CONSTRAINT UQ_THANHLY_DauSach_STT UNIQUE (MaDauSach, STT),
  CONSTRAINT FK_THANHLY_DAUSACH FOREIGN KEY (MaDauSach) REFERENCES DAU_SACH(MaDauSach),
  CONSTRAINT CK_THANHLY_Ngay CHECK (NgayThanhLy >= NgayNhap)
);

-- ---------------------------------------------------------------------
-- 3. Mượn – trả – phạt
-- ---------------------------------------------------------------------
CREATE TABLE PHIEU_MUON (
  MaPhieuMuon  INT         NOT NULL AUTO_INCREMENT,
  MaDocGia     VARCHAR(10) NOT NULL,
  MaThuThu     VARCHAR(10) NOT NULL,
  NgayMuon     DATE        NOT NULL,
  CONSTRAINT PK_PHIEU_MUON PRIMARY KEY (MaPhieuMuon),
  CONSTRAINT FK_PHIEUMUON_DOCGIA FOREIGN KEY (MaDocGia) REFERENCES DOC_GIA(MaNguoi),
  CONSTRAINT FK_PHIEUMUON_THUTHU FOREIGN KEY (MaThuThu) REFERENCES THU_THU(MaNguoi)
);

CREATE TABLE PHIEU_TRA (
  MaPhieuTra  INT         NOT NULL AUTO_INCREMENT,
  MaDocGia    VARCHAR(10) NOT NULL,
  MaThuThu    VARCHAR(10) NOT NULL,
  NgayTra     DATE        NOT NULL,
  CONSTRAINT PK_PHIEU_TRA PRIMARY KEY (MaPhieuTra),
  CONSTRAINT FK_PHIEUTRA_DOCGIA FOREIGN KEY (MaDocGia) REFERENCES DOC_GIA(MaNguoi),
  CONSTRAINT FK_PHIEUTRA_THUTHU FOREIGN KEY (MaThuThu) REFERENCES THU_THU(MaNguoi)
);

CREATE TABLE CT_MUON (                             -- liên kết N:N gom_sach (+ kết hợp)
  MaPhieuMuon  INT         NOT NULL,
  MaCuonSach   VARCHAR(10) NOT NULL,
  HanTra       DATE        NOT NULL,
  MaPhieuTra   INT         NULL,                   -- NULL = chưa trả
  CONSTRAINT PK_CT_MUON PRIMARY KEY (MaPhieuMuon, MaCuonSach),
  CONSTRAINT FK_CTMUON_PHIEUMUON FOREIGN KEY (MaPhieuMuon) REFERENCES PHIEU_MUON(MaPhieuMuon)
      ON DELETE CASCADE,
  CONSTRAINT FK_CTMUON_CUONSACH FOREIGN KEY (MaCuonSach) REFERENCES CUON_SACH(MaCuonSach),
  CONSTRAINT FK_CTMUON_PHIEUTRA FOREIGN KEY (MaPhieuTra) REFERENCES PHIEU_TRA(MaPhieuTra)
);

CREATE TABLE PHIEU_PHAT (                          -- kết hợp bi_phat (1:1 với CT_MUON)
  MaPhieuPhat    INT           NOT NULL AUTO_INCREMENT,
  MaPhieuMuon    INT           NOT NULL,
  MaCuonSach     VARCHAR(10)   NOT NULL,
  SoNgayTre      SMALLINT      NOT NULL,
  SoTien         DECIMAL(12,0) NOT NULL,
  DaThanhToan    TINYINT(1)    NOT NULL DEFAULT 0,
  NgayThanhToan  DATE          NULL,
  CONSTRAINT PK_PHIEU_PHAT PRIMARY KEY (MaPhieuPhat),
  CONSTRAINT UQ_PHIEUPHAT_CTMuon UNIQUE (MaPhieuMuon, MaCuonSach),
  CONSTRAINT FK_PHIEUPHAT_CTMUON FOREIGN KEY (MaPhieuMuon, MaCuonSach)
      REFERENCES CT_MUON(MaPhieuMuon, MaCuonSach) ON DELETE CASCADE,
  CONSTRAINT CK_PHIEUPHAT_Tre CHECK (SoNgayTre > 0),
  CONSTRAINT CK_PHIEUPHAT_Tien CHECK (SoTien >= 0),
  CONSTRAINT CK_PHIEUPHAT_ThanhToan CHECK ((DaThanhToan = 0 AND NgayThanhToan IS NULL)
                                        OR (DaThanhToan = 1 AND NgayThanhToan IS NOT NULL))
);

-- Lưu trữ lịch sử mượn của các cuốn đã thanh lý (cuốn bị xóa khỏi CUON_SACH nên
-- dòng CT_MUON không thể giữ khóa ngoại tới nó nữa)
CREATE TABLE CT_MUON_LUU_TRU (
  MaPhieuMuon  INT           NOT NULL,
  MaCuonSach   VARCHAR(10)   NOT NULL,
  HanTra       DATE          NOT NULL,
  MaPhieuTra   INT           NOT NULL,
  TienPhat     DECIMAL(12,0) NOT NULL DEFAULT 0,  -- phạt đã thanh toán của dòng này
  CONSTRAINT PK_CT_MUON_LUU_TRU PRIMARY KEY (MaPhieuMuon, MaCuonSach),
  CONSTRAINT FK_LUUTRU_PHIEUMUON FOREIGN KEY (MaPhieuMuon) REFERENCES PHIEU_MUON(MaPhieuMuon),
  CONSTRAINT FK_LUUTRU_PHIEUTRA FOREIGN KEY (MaPhieuTra) REFERENCES PHIEU_TRA(MaPhieuTra),
  CONSTRAINT FK_LUUTRU_THANHLY FOREIGN KEY (MaCuonSach) REFERENCES SACH_THANH_LY(MaCuonSach),
  CONSTRAINT CK_LUUTRU_Tien CHECK (TienPhat >= 0)
);

-- ---------------------------------------------------------------------
-- 4. Phòng đọc
-- ---------------------------------------------------------------------
CREATE TABLE LOAI_PHONG (
  MaLoaiPhong    VARCHAR(8)    NOT NULL,
  TenLoai        VARCHAR(50)   NOT NULL,
  GiaMoiGio      DECIMAL(12,0) NOT NULL,
  SoGioToiThieu  TINYINT       NOT NULL,
  SoGioToiDa     TINYINT       NOT NULL,
  CONSTRAINT PK_LOAI_PHONG PRIMARY KEY (MaLoaiPhong),
  CONSTRAINT UQ_LOAIPHONG_Ten UNIQUE (TenLoai),
  CONSTRAINT CK_LOAIPHONG_Gia CHECK (GiaMoiGio > 0),
  CONSTRAINT CK_LOAIPHONG_Gio CHECK (SoGioToiThieu >= 1 AND SoGioToiThieu <= SoGioToiDa)
);

CREATE TABLE PHONG_DOC (
  MaPhongDoc   VARCHAR(8)  NOT NULL,               -- vd CN01-N1, CN01-H1
  MaChiNhanh   CHAR(4)     NOT NULL,
  MaLoaiPhong  VARCHAR(8)  NOT NULL,
  TenPhong     VARCHAR(50) NOT NULL,
  SucChua      SMALLINT    NOT NULL,
  CONSTRAINT PK_PHONG_DOC PRIMARY KEY (MaPhongDoc),
  CONSTRAINT UQ_PHONGDOC_Ten UNIQUE (MaChiNhanh, TenPhong),
  CONSTRAINT FK_PHONGDOC_CHINHANH FOREIGN KEY (MaChiNhanh) REFERENCES CHI_NHANH(MaChiNhanh),
  CONSTRAINT FK_PHONGDOC_LOAI FOREIGN KEY (MaLoaiPhong) REFERENCES LOAI_PHONG(MaLoaiPhong),
  CONSTRAINT CK_PHONGDOC_SucChua CHECK (SucChua BETWEEN 1 AND 200)
);

CREATE TABLE PHIEU_THUE_PHONG (
  MaPhieuThue    INT           NOT NULL AUTO_INCREMENT,
  MaDocGia       VARCHAR(10)   NOT NULL,
  MaPhongDoc     VARCHAR(8)    NOT NULL,
  MaThuThuDuyet  VARCHAR(10)   NOT NULL,
  NgayDat        DATE          NOT NULL,
  BatDau         DATETIME      NOT NULL,
  KetThuc        DATETIME      NOT NULL,
  SoNguoi        SMALLINT      NOT NULL,
  MucDich        VARCHAR(20)   NOT NULL,
  TongTien       DECIMAL(12,0) NOT NULL,
  TrangThai      VARCHAR(10)   NOT NULL DEFAULT 'DaDuyet',
  CONSTRAINT PK_PHIEU_THUE_PHONG PRIMARY KEY (MaPhieuThue),
  CONSTRAINT FK_THUE_DOCGIA FOREIGN KEY (MaDocGia) REFERENCES DOC_GIA(MaNguoi),
  CONSTRAINT FK_THUE_PHONGDOC FOREIGN KEY (MaPhongDoc) REFERENCES PHONG_DOC(MaPhongDoc),
  CONSTRAINT FK_THUE_THUTHU FOREIGN KEY (MaThuThuDuyet) REFERENCES THU_THU(MaNguoi),
  CONSTRAINT CK_THUE_ThoiGian CHECK (KetThuc > BatDau AND DATE(KetThuc) = DATE(BatDau)),
  CONSTRAINT CK_THUE_GioMoCua CHECK (TIME(BatDau) >= '07:00:00' AND TIME(KetThuc) <= '21:00:00'),
  CONSTRAINT CK_THUE_GioTron CHECK (MINUTE(BatDau) = 0 AND SECOND(BatDau) = 0
                                AND MINUTE(KetThuc) = 0 AND SECOND(KetThuc) = 0),
  CONSTRAINT CK_THUE_DatTruoc CHECK (DATE(BatDau) >= NgayDat AND DATEDIFF(BatDau, NgayDat) <= 14),
  CONSTRAINT CK_THUE_SoNguoi CHECK (SoNguoi > 0),
  CONSTRAINT CK_THUE_MucDich CHECK (MucDich IN ('HocNhom','HoiThao')),
  CONSTRAINT CK_THUE_Tien CHECK (TongTien >= 0),
  CONSTRAINT CK_THUE_TrangThai CHECK (TrangThai IN ('DaDuyet','DaHuy'))
);
```

## A.2 Function và procedure thêm/xóa/sửa/tìm kiếm (02_function_procedure.sql)

```sql
-- =====================================================================
-- 02_function_procedure.sql – Function nghiệp vụ và procedure CRUD
-- Quy ước: tham số p_, biến v_; procedure tìm kiếm nhận NULL = bỏ qua điều kiện
-- Lỗi nghiệp vụ: SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Exxx: ...'
-- =====================================================================
SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;
USE QLTV;
DELIMITER //

-- ---------------------------------------------------------------------
-- A. FUNCTION
-- ---------------------------------------------------------------------
-- Thuộc tính dẫn xuất Tuoi
CREATE OR REPLACE FUNCTION fn_Tuoi(p_NgaySinh DATE, p_Ngay DATE) RETURNS INT DETERMINISTIC
  RETURN TIMESTAMPDIFF(YEAR, p_NgaySinh, p_Ngay) //

-- Thuộc tính dẫn xuất ConHan của thẻ: 1 nếu thẻ còn hiệu lực tại ngày p_Ngay
CREATE OR REPLACE FUNCTION fn_TheConHan(p_MaDocGia VARCHAR(10), p_Ngay DATE) RETURNS TINYINT
READS SQL DATA
  RETURN EXISTS (SELECT 1 FROM THE_DOC_GIA
                 WHERE MaDocGia = p_MaDocGia AND p_Ngay BETWEEN NgayCap AND NgayHetHan) //

-- Số cuốn độc giả đang giữ (chưa trả)
CREATE OR REPLACE FUNCTION fn_SoSachDangMuon(p_MaDocGia VARCHAR(10)) RETURNS INT
READS SQL DATA
  RETURN (SELECT COUNT(*) FROM CT_MUON ct JOIN PHIEU_MUON pm ON pm.MaPhieuMuon = ct.MaPhieuMuon
          WHERE pm.MaDocGia = p_MaDocGia AND ct.MaPhieuTra IS NULL) //

-- Tổng tiền phạt chưa thanh toán
CREATE OR REPLACE FUNCTION fn_NoPhat(p_MaDocGia VARCHAR(10)) RETURNS DECIMAL(12,0)
READS SQL DATA
  RETURN (SELECT COALESCE(SUM(pp.SoTien), 0)
          FROM PHIEU_PHAT pp JOIN PHIEU_MUON pm ON pm.MaPhieuMuon = pp.MaPhieuMuon
          WHERE pm.MaDocGia = p_MaDocGia AND pp.DaThanhToan = 0) //

-- Hạn trả = ngày mượn + số ngày riêng của đầu sách, nếu không có thì của thể loại
CREATE OR REPLACE FUNCTION fn_HanTra(p_MaCuonSach VARCHAR(10), p_NgayMuon DATE) RETURNS DATE
READS SQL DATA
BEGIN
  DECLARE v_SoNgay SMALLINT;
  SELECT COALESCE(ds.SoNgayMuonRieng, tl.SoNgayMuon) INTO v_SoNgay
  FROM CUON_SACH cs JOIN DAU_SACH ds ON ds.MaDauSach = cs.MaDauSach
                    JOIN THE_LOAI tl ON tl.MaTheLoai = ds.MaTheLoai
  WHERE cs.MaCuonSach = p_MaCuonSach;
  RETURN DATE_ADD(p_NgayMuon, INTERVAL v_SoNgay DAY);
END //

-- Tiền phạt 1 cuốn = phạt cơ bản + phạt/ngày × số ngày trễ, theo biểu phí có hiệu lực tại ngày trả
CREATE OR REPLACE FUNCTION fn_TinhTienPhat(p_MaCuonSach VARCHAR(10), p_HanTra DATE, p_NgayTra DATE)
RETURNS DECIMAL(12,0) READS SQL DATA
BEGIN
  DECLARE v_Tre INT DEFAULT DATEDIFF(p_NgayTra, p_HanTra);
  DECLARE v_CoBan, v_MoiNgay DECIMAL(12,0);
  IF v_Tre <= 0 THEN RETURN 0; END IF;
  SELECT bp.PhatCoBan, bp.PhatMoiNgay INTO v_CoBan, v_MoiNgay
  FROM BANG_PHI_PHAT bp
  WHERE bp.MaTheLoai = LEFT(p_MaCuonSach, 2) AND bp.NgayApDung <= p_NgayTra
  ORDER BY bp.NgayApDung DESC LIMIT 1;
  RETURN v_CoBan + v_MoiNgay * v_Tre;
END //

-- Thuộc tính dẫn xuất TongTien của lượt thuê phòng = số giờ × giá/giờ của loại phòng
CREATE OR REPLACE FUNCTION fn_TienThuePhong(p_MaPhongDoc VARCHAR(8), p_BatDau DATETIME, p_KetThuc DATETIME)
RETURNS DECIMAL(12,0) READS SQL DATA
  RETURN TIMESTAMPDIFF(HOUR, p_BatDau, p_KetThuc) *
         (SELECT l.GiaMoiGio FROM PHONG_DOC p JOIN LOAI_PHONG l ON l.MaLoaiPhong = p.MaLoaiPhong
          WHERE p.MaPhongDoc = p_MaPhongDoc) //

-- Sinh mã kế tiếp dạng <tiền tố><số> (vd DG0201, TT016)
CREATE OR REPLACE FUNCTION fn_MaNguoiMoi(p_Loai CHAR(2)) RETURNS VARCHAR(10)
READS SQL DATA
BEGIN
  DECLARE v_Max INT;
  SELECT COALESCE(MAX(CAST(SUBSTRING(MaNguoi, 3) AS UNSIGNED)), 0) INTO v_Max
  FROM NGUOI WHERE LoaiNguoi = p_Loai;
  RETURN CONCAT(p_Loai, LPAD(v_Max + 1, IF(p_Loai = 'DG', 4, 3), '0'));
END //

-- ---------------------------------------------------------------------
-- B. CHI NHÁNH
-- ---------------------------------------------------------------------
CREATE OR REPLACE PROCEDURE sp_ChiNhanh_Them(IN p_Ma CHAR(4), IN p_Ten VARCHAR(100),
       IN p_DiaChi VARCHAR(200), IN p_GioMo TIME, IN p_GioDong TIME)
  INSERT INTO CHI_NHANH(MaChiNhanh, TenChiNhanh, DiaChi, GioMo, GioDong)
  VALUES (p_Ma, p_Ten, p_DiaChi, COALESCE(p_GioMo, '07:00'), COALESCE(p_GioDong, '21:00')) //

CREATE OR REPLACE PROCEDURE sp_ChiNhanh_Sua(IN p_Ma CHAR(4), IN p_Ten VARCHAR(100),
       IN p_DiaChi VARCHAR(200), IN p_MaThuThuTruong VARCHAR(10))
BEGIN
  IF p_MaThuThuTruong IS NOT NULL AND NOT EXISTS
     (SELECT 1 FROM THU_THU WHERE MaNguoi = p_MaThuThuTruong AND MaChiNhanh = p_Ma) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'E401: Thủ thư trưởng phải làm việc tại chính chi nhánh này';
  END IF;
  UPDATE CHI_NHANH SET TenChiNhanh = COALESCE(p_Ten, TenChiNhanh),
                       DiaChi = COALESCE(p_DiaChi, DiaChi),
                       MaThuThuTruong = COALESCE(p_MaThuThuTruong, MaThuThuTruong)
  WHERE MaChiNhanh = p_Ma;
END //

CREATE OR REPLACE PROCEDURE sp_ChiNhanh_Xoa(IN p_Ma CHAR(4))
  DELETE FROM CHI_NHANH WHERE MaChiNhanh = p_Ma //   -- FK RESTRICT chặn nếu còn dữ liệu liên quan

CREATE OR REPLACE PROCEDURE sp_ChiNhanh_TimKiem(IN p_TuKhoa VARCHAR(100))
  SELECT cn.*, CONCAT_WS(' ', n.Ho, n.Dem, n.Ten) AS ThuThuTruong,
         (SELECT COUNT(*) FROM DOC_GIA d WHERE d.MaChiNhanh = cn.MaChiNhanh) AS SoDocGia
  FROM CHI_NHANH cn LEFT JOIN NGUOI n ON n.MaNguoi = cn.MaThuThuTruong
  WHERE p_TuKhoa IS NULL OR cn.MaChiNhanh = p_TuKhoa OR cn.TenChiNhanh LIKE CONCAT('%', p_TuKhoa, '%') //

-- ---------------------------------------------------------------------
-- C. ĐỘC GIẢ  (thêm mới = sp_DangKyDocGia ở 04_transaction.sql)
-- ---------------------------------------------------------------------
CREATE OR REPLACE PROCEDURE sp_DocGia_Sua(IN p_Ma VARCHAR(10), IN p_Ho VARCHAR(30), IN p_Dem VARCHAR(30),
       IN p_Ten VARCHAR(30), IN p_SoNha VARCHAR(50), IN p_Phuong VARCHAR(50), IN p_Quan VARCHAR(50),
       IN p_TinhTP VARCHAR(50), IN p_Email VARCHAR(100), IN p_TrangThai VARCHAR(10))
BEGIN
  IF NOT EXISTS (SELECT 1 FROM DOC_GIA WHERE MaNguoi = p_Ma) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'E402: Không tìm thấy độc giả';
  END IF;
  UPDATE NGUOI SET Ho = COALESCE(p_Ho, Ho), Dem = COALESCE(p_Dem, Dem), Ten = COALESCE(p_Ten, Ten),
         SoNha = COALESCE(p_SoNha, SoNha), Phuong = COALESCE(p_Phuong, Phuong),
         Quan = COALESCE(p_Quan, Quan), TinhTP = COALESCE(p_TinhTP, TinhTP), Email = COALESCE(p_Email, Email)
  WHERE MaNguoi = p_Ma;
  UPDATE DOC_GIA SET TrangThai = COALESCE(p_TrangThai, TrangThai) WHERE MaNguoi = p_Ma;
END //

CREATE OR REPLACE PROCEDURE sp_DocGia_Xoa(IN p_Ma VARCHAR(10))
BEGIN
  DECLARE EXIT HANDLER FOR SQLEXCEPTION BEGIN ROLLBACK; RESIGNAL; END;
  START TRANSACTION;
    DELETE FROM DOC_GIA WHERE MaNguoi = p_Ma;     -- TRG8 chặn nếu còn giữ sách / nợ phạt; THE_DOC_GIA xóa theo CASCADE
    DELETE FROM NGUOI WHERE MaNguoi = p_Ma;       -- SDT_NGUOI xóa theo CASCADE
  COMMIT;
END //

CREATE OR REPLACE PROCEDURE sp_DocGia_TimKiem(IN p_TuKhoa VARCHAR(100), IN p_MaChiNhanh CHAR(4))
  SELECT d.MaNguoi AS MaDocGia, CONCAT_WS(' ', n.Ho, n.Dem, n.Ten) AS HoTen,
         fn_Tuoi(n.NgaySinh, CURDATE()) AS Tuoi, n.Email,
         (SELECT GROUP_CONCAT(s.SoDienThoai) FROM SDT_NGUOI s WHERE s.MaNguoi = d.MaNguoi) AS SoDienThoai,
         d.MaChiNhanh, t.SoThe, t.NgayHetHan, d.TrangThai,
         fn_SoSachDangMuon(d.MaNguoi) AS DangMuon, fn_NoPhat(d.MaNguoi) AS NoPhat
  FROM DOC_GIA d JOIN NGUOI n ON n.MaNguoi = d.MaNguoi
                 LEFT JOIN THE_DOC_GIA t ON t.MaDocGia = d.MaNguoi
  WHERE (p_MaChiNhanh IS NULL OR d.MaChiNhanh = p_MaChiNhanh)
    AND (p_TuKhoa IS NULL OR d.MaNguoi = p_TuKhoa OR t.SoThe = p_TuKhoa
         OR CONCAT_WS(' ', n.Ho, n.Dem, n.Ten) LIKE CONCAT('%', p_TuKhoa, '%')
         OR EXISTS (SELECT 1 FROM SDT_NGUOI s WHERE s.MaNguoi = d.MaNguoi AND s.SoDienThoai = p_TuKhoa))
  ORDER BY d.MaNguoi //

CREATE OR REPLACE PROCEDURE sp_DocGia_GiaHanThe(IN p_MaDocGia VARCHAR(10), IN p_Ngay DATE)
BEGIN
  UPDATE THE_DOC_GIA
  SET NgayHetHan = DATE_ADD(GREATEST(NgayHetHan, p_Ngay), INTERVAL 1 YEAR)
  WHERE MaDocGia = p_MaDocGia;
  IF ROW_COUNT() = 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'E402: Không tìm thấy thẻ của độc giả';
  END IF;
END //

-- ---------------------------------------------------------------------
-- D. THỦ THƯ
-- ---------------------------------------------------------------------
CREATE OR REPLACE PROCEDURE sp_ThuThu_Them(IN p_Ho VARCHAR(30), IN p_Dem VARCHAR(30), IN p_Ten VARCHAR(30),
       IN p_NgaySinh DATE, IN p_GioiTinh CHAR(1), IN p_TinhTP VARCHAR(50), IN p_Email VARCHAR(100),
       IN p_SDT VARCHAR(10), IN p_MaChiNhanh CHAR(4), IN p_NgayVaoLam DATE, IN p_MaQuanLy VARCHAR(10),
       OUT p_MaMoi VARCHAR(10))
BEGIN
  DECLARE EXIT HANDLER FOR SQLEXCEPTION BEGIN ROLLBACK; RESIGNAL; END;
  START TRANSACTION;
    SET p_MaMoi = fn_MaNguoiMoi('TT');
    INSERT INTO NGUOI(MaNguoi, Ho, Dem, Ten, NgaySinh, GioiTinh, TinhTP, Email, LoaiNguoi)
    VALUES (p_MaMoi, p_Ho, p_Dem, p_Ten, p_NgaySinh, p_GioiTinh, p_TinhTP, p_Email, 'TT');
    INSERT INTO SDT_NGUOI VALUES (p_MaMoi, p_SDT);
    INSERT INTO THU_THU(MaNguoi, MaChiNhanh, NgayVaoLam, MaQuanLy)
    VALUES (p_MaMoi, p_MaChiNhanh, p_NgayVaoLam, p_MaQuanLy);
  COMMIT;
END //

CREATE OR REPLACE PROCEDURE sp_ThuThu_Sua(IN p_Ma VARCHAR(10), IN p_MaChiNhanh CHAR(4),
       IN p_MaQuanLy VARCHAR(10), IN p_Email VARCHAR(100))
BEGIN
  UPDATE THU_THU SET MaChiNhanh = COALESCE(p_MaChiNhanh, MaChiNhanh),
                     MaQuanLy = COALESCE(p_MaQuanLy, MaQuanLy) WHERE MaNguoi = p_Ma;
  UPDATE NGUOI SET Email = COALESCE(p_Email, Email) WHERE MaNguoi = p_Ma;
END //

CREATE OR REPLACE PROCEDURE sp_ThuThu_Xoa(IN p_Ma VARCHAR(10))
BEGIN
  DECLARE EXIT HANDLER FOR SQLEXCEPTION BEGIN ROLLBACK; RESIGNAL; END;
  IF EXISTS (SELECT 1 FROM CHI_NHANH WHERE MaThuThuTruong = p_Ma) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'E403: Thủ thư đang là trưởng chi nhánh, đổi trưởng trước khi xóa';
  END IF;
  START TRANSACTION;
    UPDATE THU_THU SET MaQuanLy = NULL WHERE MaQuanLy = p_Ma;
    DELETE FROM THU_THU WHERE MaNguoi = p_Ma;    -- FK chặn nếu thủ thư đã lập phiếu
    DELETE FROM NGUOI WHERE MaNguoi = p_Ma;
  COMMIT;
END //

CREATE OR REPLACE PROCEDURE sp_ThuThu_TimKiem(IN p_TuKhoa VARCHAR(100), IN p_MaChiNhanh CHAR(4))
  SELECT t.MaNguoi AS MaThuThu, CONCAT_WS(' ', n.Ho, n.Dem, n.Ten) AS HoTen, t.MaChiNhanh, t.NgayVaoLam,
         t.MaQuanLy, CONCAT_WS(' ', q.Ho, q.Dem, q.Ten) AS NguoiQuanLy,
         (cn.MaThuThuTruong = t.MaNguoi) AS LaTruongChiNhanh
  FROM THU_THU t JOIN NGUOI n ON n.MaNguoi = t.MaNguoi
                 JOIN CHI_NHANH cn ON cn.MaChiNhanh = t.MaChiNhanh
                 LEFT JOIN NGUOI q ON q.MaNguoi = t.MaQuanLy
  WHERE (p_MaChiNhanh IS NULL OR t.MaChiNhanh = p_MaChiNhanh)
    AND (p_TuKhoa IS NULL OR t.MaNguoi = p_TuKhoa
         OR CONCAT_WS(' ', n.Ho, n.Dem, n.Ten) LIKE CONCAT('%', p_TuKhoa, '%'))
  ORDER BY t.MaNguoi //

-- ---------------------------------------------------------------------
-- E. PHÒNG KHO, GIÁ SÁCH
-- ---------------------------------------------------------------------
CREATE OR REPLACE PROCEDURE sp_PhongKho_Them(IN p_Ma VARCHAR(8), IN p_MaChiNhanh CHAR(4),
       IN p_Ten VARCHAR(50), IN p_Tang TINYINT)
  INSERT INTO PHONG_KHO VALUES (p_Ma, p_MaChiNhanh, p_Ten, COALESCE(p_Tang, 1)) //

CREATE OR REPLACE PROCEDURE sp_PhongKho_Sua(IN p_Ma VARCHAR(8), IN p_Ten VARCHAR(50), IN p_Tang TINYINT)
  UPDATE PHONG_KHO SET TenPhong = COALESCE(p_Ten, TenPhong), Tang = COALESCE(p_Tang, Tang)
  WHERE MaPhongKho = p_Ma //

CREATE OR REPLACE PROCEDURE sp_PhongKho_Xoa(IN p_Ma VARCHAR(8))
  DELETE FROM PHONG_KHO WHERE MaPhongKho = p_Ma //

CREATE OR REPLACE PROCEDURE sp_PhongKho_TimKiem(IN p_MaChiNhanh CHAR(4))
  SELECT pk.*, (SELECT COUNT(*) FROM GIA_SACH g WHERE g.MaPhongKho = pk.MaPhongKho) AS SoGia,
         (SELECT COALESCE(SUM(g.SoLuongHienCo), 0) FROM GIA_SACH g WHERE g.MaPhongKho = pk.MaPhongKho) AS SoCuonTrenGia
  FROM PHONG_KHO pk
  WHERE p_MaChiNhanh IS NULL OR pk.MaChiNhanh = p_MaChiNhanh
  ORDER BY pk.MaPhongKho //

CREATE OR REPLACE PROCEDURE sp_GiaSach_Them(IN p_Ma VARCHAR(12), IN p_MaPhongKho VARCHAR(8),
       IN p_MaTheLoai CHAR(2), IN p_SucChua SMALLINT)
  INSERT INTO GIA_SACH(MaGia, MaPhongKho, MaTheLoai, SucChua)
  VALUES (p_Ma, p_MaPhongKho, p_MaTheLoai, COALESCE(p_SucChua, 100)) //

CREATE OR REPLACE PROCEDURE sp_GiaSach_Sua(IN p_Ma VARCHAR(12), IN p_SucChua SMALLINT)
  UPDATE GIA_SACH SET SucChua = p_SucChua WHERE MaGia = p_Ma //   -- CHECK chặn nếu nhỏ hơn số đang có

CREATE OR REPLACE PROCEDURE sp_GiaSach_Xoa(IN p_Ma VARCHAR(12))
  DELETE FROM GIA_SACH WHERE MaGia = p_Ma //

CREATE OR REPLACE PROCEDURE sp_GiaSach_TimKiem(IN p_MaChiNhanh CHAR(4), IN p_MaTheLoai CHAR(2))
  SELECT g.*, pk.MaChiNhanh, pk.TenPhong, tl.TenTheLoai, g.SucChua - g.SoLuongHienCo AS ConTrong
  FROM GIA_SACH g JOIN PHONG_KHO pk ON pk.MaPhongKho = g.MaPhongKho
                  JOIN THE_LOAI tl ON tl.MaTheLoai = g.MaTheLoai
  WHERE (p_MaChiNhanh IS NULL OR pk.MaChiNhanh = p_MaChiNhanh)
    AND (p_MaTheLoai IS NULL OR g.MaTheLoai = p_MaTheLoai)
  ORDER BY g.MaGia //

-- ---------------------------------------------------------------------
-- F. ĐẦU SÁCH, CUỐN SÁCH  (nhập lô nhiều cuốn = sp_NhapLoSach ở 04_transaction.sql)
-- ---------------------------------------------------------------------
CREATE OR REPLACE PROCEDURE sp_DauSach_Them(IN p_Ma CHAR(6), IN p_Ten VARCHAR(200), IN p_NXB VARCHAR(100),
       IN p_Nam SMALLINT, IN p_SoNgayRieng SMALLINT)
  INSERT INTO DAU_SACH VALUES (p_Ma, LEFT(p_Ma, 2), p_Ten, p_NXB, p_Nam, p_SoNgayRieng) //

CREATE OR REPLACE PROCEDURE sp_DauSach_Sua(IN p_Ma CHAR(6), IN p_Ten VARCHAR(200), IN p_NXB VARCHAR(100),
       IN p_Nam SMALLINT, IN p_SoNgayRieng SMALLINT)
  UPDATE DAU_SACH SET TenSach = COALESCE(p_Ten, TenSach), NhaXuatBan = COALESCE(p_NXB, NhaXuatBan),
         NamXuatBan = COALESCE(p_Nam, NamXuatBan), SoNgayMuonRieng = p_SoNgayRieng
  WHERE MaDauSach = p_Ma //

CREATE OR REPLACE PROCEDURE sp_DauSach_Xoa(IN p_Ma CHAR(6))
BEGIN
  IF EXISTS (SELECT 1 FROM CUON_SACH WHERE MaDauSach = p_Ma) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'E302: Đầu sách còn cuốn trong kho, không xóa được';
  END IF;
  DELETE FROM DAU_SACH WHERE MaDauSach = p_Ma;
END //

CREATE OR REPLACE PROCEDURE sp_DauSach_TimKiem(IN p_TuKhoa VARCHAR(200), IN p_MaTheLoai CHAR(2))
  SELECT ds.MaDauSach, ds.TenSach, tl.TenTheLoai, ds.NhaXuatBan, ds.NamXuatBan,
         (SELECT GROUP_CONCAT(tg.TenTacGia SEPARATOR ', ') FROM DAU_SACH_TAC_GIA x
            JOIN TAC_GIA tg ON tg.MaTacGia = x.MaTacGia WHERE x.MaDauSach = ds.MaDauSach) AS TacGia,
         (SELECT COUNT(*) FROM CUON_SACH c WHERE c.MaDauSach = ds.MaDauSach) AS TongCuon,
         (SELECT COUNT(*) FROM CUON_SACH c WHERE c.MaDauSach = ds.MaDauSach AND c.TrangThai = 'TrenGia') AS ConTrenGia
  FROM DAU_SACH ds JOIN THE_LOAI tl ON tl.MaTheLoai = ds.MaTheLoai
  WHERE (p_MaTheLoai IS NULL OR ds.MaTheLoai = p_MaTheLoai)
    AND (p_TuKhoa IS NULL OR ds.MaDauSach = p_TuKhoa OR ds.TenSach LIKE CONCAT('%', p_TuKhoa, '%')
         OR EXISTS (SELECT 1 FROM DAU_SACH_TAC_GIA x JOIN TAC_GIA tg ON tg.MaTacGia = x.MaTacGia
                    WHERE x.MaDauSach = ds.MaDauSach AND tg.TenTacGia LIKE CONCAT('%', p_TuKhoa, '%')))
  ORDER BY ds.MaDauSach //

CREATE OR REPLACE PROCEDURE sp_CuonSach_ChuyenGia(IN p_MaCuonSach VARCHAR(10), IN p_MaGiaMoi VARCHAR(12))
BEGIN
  DECLARE EXIT HANDLER FOR SQLEXCEPTION BEGIN ROLLBACK; RESIGNAL; END;
  START TRANSACTION;
    UPDATE CUON_SACH SET MaGia = p_MaGiaMoi WHERE MaCuonSach = p_MaCuonSach;   -- TRG6 kiểm tra giá mới
  COMMIT;
END //

CREATE OR REPLACE PROCEDURE sp_CuonSach_Xoa(IN p_MaCuonSach VARCHAR(10))
BEGIN
  IF EXISTS (SELECT 1 FROM CT_MUON WHERE MaCuonSach = p_MaCuonSach) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'E303: Cuốn sách đã có lịch sử mượn, hãy dùng thanh lý thay vì xóa';
  END IF;
  DELETE FROM CUON_SACH WHERE MaCuonSach = p_MaCuonSach;      -- TRG4 giảm số lượng trên giá
END //

CREATE OR REPLACE PROCEDURE sp_CuonSach_TimKiem(IN p_TuKhoa VARCHAR(200), IN p_MaChiNhanh CHAR(4),
       IN p_TrangThai VARCHAR(12))
  SELECT cs.MaCuonSach, ds.TenSach, ds.MaTheLoai, cs.MaGia, pk.MaChiNhanh, cs.TrangThai,
         cs.TuoiThoConLaiThang, cs.NgayNhap
  FROM CUON_SACH cs JOIN DAU_SACH ds ON ds.MaDauSach = cs.MaDauSach
                    JOIN GIA_SACH g ON g.MaGia = cs.MaGia
                    JOIN PHONG_KHO pk ON pk.MaPhongKho = g.MaPhongKho
  WHERE (p_MaChiNhanh IS NULL OR pk.MaChiNhanh = p_MaChiNhanh)
    AND (p_TrangThai IS NULL OR cs.TrangThai = p_TrangThai)
    AND (p_TuKhoa IS NULL OR cs.MaCuonSach = p_TuKhoa OR cs.MaDauSach = p_TuKhoa
         OR ds.TenSach LIKE CONCAT('%', p_TuKhoa, '%'))
  ORDER BY cs.MaCuonSach //

-- ---------------------------------------------------------------------
-- G. PHÒNG ĐỌC
-- ---------------------------------------------------------------------
CREATE OR REPLACE PROCEDURE sp_PhongDoc_Them(IN p_Ma VARCHAR(8), IN p_MaChiNhanh CHAR(4),
       IN p_MaLoai VARCHAR(8), IN p_Ten VARCHAR(50), IN p_SucChua SMALLINT)
  INSERT INTO PHONG_DOC VALUES (p_Ma, p_MaChiNhanh, p_MaLoai, p_Ten, p_SucChua) //

CREATE OR REPLACE PROCEDURE sp_PhongDoc_Sua(IN p_Ma VARCHAR(8), IN p_Ten VARCHAR(50), IN p_SucChua SMALLINT)
  UPDATE PHONG_DOC SET TenPhong = COALESCE(p_Ten, TenPhong), SucChua = COALESCE(p_SucChua, SucChua)
  WHERE MaPhongDoc = p_Ma //

CREATE OR REPLACE PROCEDURE sp_PhongDoc_Xoa(IN p_Ma VARCHAR(8))
  DELETE FROM PHONG_DOC WHERE MaPhongDoc = p_Ma //

CREATE OR REPLACE PROCEDURE sp_PhongDoc_TimKiem(IN p_MaChiNhanh CHAR(4), IN p_MaLoai VARCHAR(8),
       IN p_SoNguoi SMALLINT)
  SELECT p.MaPhongDoc, p.TenPhong, p.MaChiNhanh, l.TenLoai, p.SucChua, l.GiaMoiGio
  FROM PHONG_DOC p JOIN LOAI_PHONG l ON l.MaLoaiPhong = p.MaLoaiPhong
  WHERE (p_MaChiNhanh IS NULL OR p.MaChiNhanh = p_MaChiNhanh)
    AND (p_MaLoai IS NULL OR p.MaLoaiPhong = p_MaLoai)
    AND (p_SoNguoi IS NULL OR p.SucChua >= p_SoNguoi)
  ORDER BY p.MaPhongDoc //

-- Báo giá trước khi đặt phòng: giao diện gọi lại mỗi khi đổi phòng / khung giờ / số người
CREATE OR REPLACE PROCEDURE sp_ThuePhong_BaoGia(IN p_MaPhongDoc VARCHAR(8), IN p_BatDau DATETIME,
       IN p_KetThuc DATETIME, IN p_SoNguoi SMALLINT)
  SELECT l.TenLoai, l.GiaMoiGio, TIMESTAMPDIFF(HOUR, p_BatDau, p_KetThuc) AS SoGio,
         fn_TienThuePhong(p_MaPhongDoc, p_BatDau, p_KetThuc) AS TongTien,
         CASE WHEN TIMESTAMPDIFF(HOUR, p_BatDau, p_KetThuc) NOT BETWEEN l.SoGioToiThieu AND l.SoGioToiDa
                THEN CONCAT('E203: Số giờ thuê không đúng quy định của loại phòng (',
                            l.SoGioToiThieu, '–', l.SoGioToiDa, ' giờ)')
              WHEN p_SoNguoi > p.SucChua
                THEN CONCAT('E202: Số người vượt sức chứa của phòng (tối đa ', p.SucChua, ' người)')
         END AS CanhBao
  FROM PHONG_DOC p JOIN LOAI_PHONG l ON l.MaLoaiPhong = p.MaLoaiPhong
  WHERE p.MaPhongDoc = p_MaPhongDoc //

DELIMITER ;
```

## A.3 Trigger (03_trigger.sql)

```sql
-- =====================================================================
-- 03_trigger.sql – 8 trigger nghiệp vụ (MariaDB, FOR EACH ROW)
-- Một số trigger gồm 2–3 trigger con cùng mục đích (khác sự kiện).
-- MariaDB: trigger không được sửa chính bảng đã kích hoạt nó (lỗi 1442),
-- nên đổi dữ liệu dòng đang ghi dùng BEFORE + SET NEW.cot, đổi bảng khác dùng AFTER.
-- =====================================================================
SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;
USE QLTV;
DELIMITER //

-- ---------------------------------------------------------------------
-- TRG1. Mỗi lần (phiếu) mượn tối đa 10 cuốn                          [đề]
-- ---------------------------------------------------------------------
CREATE OR REPLACE TRIGGER trg_CTMuon_ToiDa10
BEFORE INSERT ON CT_MUON FOR EACH ROW
BEGIN
  IF (SELECT COUNT(*) FROM CT_MUON WHERE MaPhieuMuon = NEW.MaPhieuMuon) >= 10 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'E101: Mỗi lần mượn tối đa 10 cuốn sách';
  END IF;
END //

-- ---------------------------------------------------------------------
-- TRG2. Một độc giả giữ tối đa 50 cuốn chưa trả; chỉ mượn được cuốn đang trên giá   [đề]
-- ---------------------------------------------------------------------
CREATE OR REPLACE TRIGGER trg_CTMuon_ToiDa50
BEFORE INSERT ON CT_MUON FOR EACH ROW FOLLOWS trg_CTMuon_ToiDa10
BEGIN
  DECLARE v_DocGia VARCHAR(10);
  DECLARE v_TrangThai VARCHAR(12);
  SELECT MaDocGia INTO v_DocGia FROM PHIEU_MUON WHERE MaPhieuMuon = NEW.MaPhieuMuon;
  IF fn_SoSachDangMuon(v_DocGia) >= 50 THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'E102: Độc giả đang giữ 50 cuốn, phải trả bớt trước khi mượn thêm';
  END IF;
  SELECT TrangThai INTO v_TrangThai FROM CUON_SACH WHERE MaCuonSach = NEW.MaCuonSach;
  IF v_TrangThai IS NULL OR v_TrangThai <> 'TrenGia' THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'E104: Cuốn sách không có trên giá (đang được mượn hoặc chờ thanh lý)';
  END IF;
END //

-- ---------------------------------------------------------------------
-- TRG3. Khi trả sách: kiểm tra hợp lệ và tự lập phiếu phạt nếu trả muộn       [đề]
--       Tiền phạt theo thể loại: phạt cơ bản + phạt/ngày × số ngày trễ
-- ---------------------------------------------------------------------
CREATE OR REPLACE TRIGGER trg_CTMuon_KiemTraTra
BEFORE UPDATE ON CT_MUON FOR EACH ROW
BEGIN
  DECLARE v_NgayTra, v_NgayMuon DATE;
  DECLARE v_DgTra, v_DgMuon VARCHAR(10);
  IF OLD.MaPhieuTra IS NOT NULL AND NOT (NEW.MaPhieuTra <=> OLD.MaPhieuTra) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'E106: Cuốn sách này đã được trả, không sửa được phiếu trả';
  END IF;
  IF OLD.MaPhieuTra IS NULL AND NEW.MaPhieuTra IS NOT NULL THEN
    SELECT NgayTra, MaDocGia INTO v_NgayTra, v_DgTra FROM PHIEU_TRA WHERE MaPhieuTra = NEW.MaPhieuTra;
    SELECT NgayMuon, MaDocGia INTO v_NgayMuon, v_DgMuon FROM PHIEU_MUON WHERE MaPhieuMuon = NEW.MaPhieuMuon;
    IF v_DgTra <> v_DgMuon THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'E107: Phiếu trả và phiếu mượn không cùng độc giả';
    END IF;
    IF v_NgayTra < v_NgayMuon THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'E105: Ngày trả không được trước ngày mượn';
    END IF;
  END IF;
END //

CREATE OR REPLACE TRIGGER trg_CTMuon_LapPhieuPhat
AFTER UPDATE ON CT_MUON FOR EACH ROW
BEGIN
  DECLARE v_NgayTra DATE;
  IF OLD.MaPhieuTra IS NULL AND NEW.MaPhieuTra IS NOT NULL THEN
    SELECT NgayTra INTO v_NgayTra FROM PHIEU_TRA WHERE MaPhieuTra = NEW.MaPhieuTra;
    IF v_NgayTra > NEW.HanTra THEN
      INSERT INTO PHIEU_PHAT(MaPhieuMuon, MaCuonSach, SoNgayTre, SoTien)
      VALUES (NEW.MaPhieuMuon, NEW.MaCuonSach, DATEDIFF(v_NgayTra, NEW.HanTra),
              fn_TinhTienPhat(NEW.MaCuonSach, NEW.HanTra, v_NgayTra));
    END IF;
  END IF;
END //

-- ---------------------------------------------------------------------
-- TRG4. Mượn thì số sách trên giá giảm, trả thì tăng                 [đề]
--   (a) mượn/trả đổi trạng thái cuốn sách;
--   (b) mọi thay đổi trạng thái/vị trí/thêm/xóa cuốn cập nhật GIA_SACH.SoLuongHienCo.
--   Cuốn được tính "trên giá" khi TrangThai <> 'DangMuon'.
-- ---------------------------------------------------------------------
CREATE OR REPLACE TRIGGER trg_CTMuon_Muon
AFTER INSERT ON CT_MUON FOR EACH ROW
  UPDATE CUON_SACH SET TrangThai = 'DangMuon' WHERE MaCuonSach = NEW.MaCuonSach //

CREATE OR REPLACE TRIGGER trg_CTMuon_Tra
AFTER UPDATE ON CT_MUON FOR EACH ROW FOLLOWS trg_CTMuon_LapPhieuPhat
BEGIN
  IF OLD.MaPhieuTra IS NULL AND NEW.MaPhieuTra IS NOT NULL THEN
    UPDATE CUON_SACH SET TrangThai = 'TrenGia' WHERE MaCuonSach = NEW.MaCuonSach;   -- TRG6 đổi sang ChoThanhLy nếu hết tuổi thọ
  END IF;
END //

CREATE OR REPLACE TRIGGER trg_CuonSach_DemGia_Them
AFTER INSERT ON CUON_SACH FOR EACH ROW
BEGIN
  IF NEW.TrangThai <> 'DangMuon' THEN
    UPDATE GIA_SACH SET SoLuongHienCo = SoLuongHienCo + 1 WHERE MaGia = NEW.MaGia;
  END IF;
END //

CREATE OR REPLACE TRIGGER trg_CuonSach_DemGia_Sua
AFTER UPDATE ON CUON_SACH FOR EACH ROW
BEGIN
  DECLARE v_Cu  TINYINT DEFAULT (OLD.TrangThai <> 'DangMuon');
  DECLARE v_Moi TINYINT DEFAULT (NEW.TrangThai <> 'DangMuon');
  IF OLD.MaGia = NEW.MaGia THEN
    IF v_Cu <> v_Moi THEN
      UPDATE GIA_SACH SET SoLuongHienCo = SoLuongHienCo + v_Moi - v_Cu WHERE MaGia = NEW.MaGia;
    END IF;
  ELSE
    IF v_Cu = 1 THEN UPDATE GIA_SACH SET SoLuongHienCo = SoLuongHienCo - 1 WHERE MaGia = OLD.MaGia; END IF;
    IF v_Moi = 1 THEN UPDATE GIA_SACH SET SoLuongHienCo = SoLuongHienCo + 1 WHERE MaGia = NEW.MaGia; END IF;
  END IF;
END //

CREATE OR REPLACE TRIGGER trg_CuonSach_DemGia_Xoa
AFTER DELETE ON CUON_SACH FOR EACH ROW
BEGIN
  IF OLD.TrangThai <> 'DangMuon' THEN
    UPDATE GIA_SACH SET SoLuongHienCo = SoLuongHienCo - 1 WHERE MaGia = OLD.MaGia;
  END IF;
END //

-- ---------------------------------------------------------------------
-- TRG5. Sau mỗi lần được mượn, tuổi thọ cuốn sách giảm 1 tháng        [đề]
-- ---------------------------------------------------------------------
CREATE OR REPLACE TRIGGER trg_CTMuon_GiamTuoiTho
AFTER INSERT ON CT_MUON FOR EACH ROW FOLLOWS trg_CTMuon_Muon
  UPDATE CUON_SACH SET TuoiThoConLaiThang = GREATEST(TuoiThoConLaiThang - 1, 0)
  WHERE MaCuonSach = NEW.MaCuonSach //

-- ---------------------------------------------------------------------
-- TRG6. Mỗi giá chỉ chứa sách cùng thể loại và không vượt sức chứa;
--       sách hết tuổi thọ đang nằm trên giá tự chuyển 'ChoThanhLy'   [đề]
-- ---------------------------------------------------------------------
CREATE OR REPLACE TRIGGER trg_CuonSach_DungGia_Them
BEFORE INSERT ON CUON_SACH FOR EACH ROW
BEGIN
  DECLARE v_TheLoai CHAR(2);
  DECLARE v_Co, v_Chua SMALLINT;
  SELECT MaTheLoai, SucChua INTO v_TheLoai, v_Chua FROM GIA_SACH WHERE MaGia = NEW.MaGia;
  -- đếm cả cuốn đang được mượn: chỗ của chúng trên giá vẫn phải được giữ
  SELECT COUNT(*) INTO v_Co FROM CUON_SACH WHERE MaGia = NEW.MaGia;
  IF v_TheLoai <> LEFT(NEW.MaDauSach, 2) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'E301: Giá sách chỉ chứa sách cùng thể loại';
  END IF;
  IF v_Co >= v_Chua THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'E304: Giá sách đã đầy';
  END IF;
END //

CREATE OR REPLACE TRIGGER trg_CuonSach_DungGia_Sua
BEFORE UPDATE ON CUON_SACH FOR EACH ROW
BEGIN
  DECLARE v_TheLoai CHAR(2);
  DECLARE v_Co, v_Chua SMALLINT;
  IF NEW.MaCuonSach <> OLD.MaCuonSach OR NEW.MaDauSach <> OLD.MaDauSach THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'E305: Không được sửa mã cuốn sách';
  END IF;
  IF NEW.MaGia <> OLD.MaGia THEN
    SELECT MaTheLoai, SucChua INTO v_TheLoai, v_Chua FROM GIA_SACH WHERE MaGia = NEW.MaGia;
    SELECT COUNT(*) INTO v_Co FROM CUON_SACH WHERE MaGia = NEW.MaGia;
    IF v_TheLoai <> LEFT(NEW.MaDauSach, 2) THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'E301: Giá sách chỉ chứa sách cùng thể loại';
    END IF;
    IF v_Co >= v_Chua THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'E304: Giá sách đã đầy';
    END IF;
  END IF;
  IF NEW.TuoiThoConLaiThang = 0 AND NEW.TrangThai = 'TrenGia' THEN
    SET NEW.TrangThai = 'ChoThanhLy';
  END IF;
END //

-- ---------------------------------------------------------------------
-- TRG7. Một phòng đọc không có 2 lượt thuê (đã duyệt) trùng giờ
-- ---------------------------------------------------------------------
CREATE OR REPLACE TRIGGER trg_ThuePhong_KhongTrung_Them
BEFORE INSERT ON PHIEU_THUE_PHONG FOR EACH ROW
BEGIN
  IF NEW.TrangThai = 'DaDuyet' AND EXISTS (
       SELECT 1 FROM PHIEU_THUE_PHONG
       WHERE MaPhongDoc = NEW.MaPhongDoc AND TrangThai = 'DaDuyet'
         AND BatDau < NEW.KetThuc AND KetThuc > NEW.BatDau) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'E201: Phòng đã có người thuê trong khung giờ này';
  END IF;
END //

CREATE OR REPLACE TRIGGER trg_ThuePhong_KhongTrung_Sua
BEFORE UPDATE ON PHIEU_THUE_PHONG FOR EACH ROW
BEGIN
  IF NEW.TrangThai = 'DaDuyet' AND EXISTS (
       SELECT 1 FROM PHIEU_THUE_PHONG
       WHERE MaPhongDoc = NEW.MaPhongDoc AND TrangThai = 'DaDuyet' AND MaPhieuThue <> NEW.MaPhieuThue
         AND BatDau < NEW.KetThuc AND KetThuc > NEW.BatDau) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'E201: Phòng đã có người thuê trong khung giờ này';
  END IF;
END //

-- ---------------------------------------------------------------------
-- TRG8. Toàn vẹn độc giả:
--   không xóa độc giả còn giữ sách hoặc còn nợ phạt; không sửa mã;
--   bảng con ISA phải khớp thuộc tính phân biệt LoaiNguoi
-- ---------------------------------------------------------------------
CREATE OR REPLACE TRIGGER trg_DocGia_ChanXoa
BEFORE DELETE ON DOC_GIA FOR EACH ROW
BEGIN
  IF fn_SoSachDangMuon(OLD.MaNguoi) > 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'E404: Độc giả còn giữ sách, không xóa được';
  END IF;
  IF fn_NoPhat(OLD.MaNguoi) > 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'E405: Độc giả còn nợ tiền phạt, không xóa được';
  END IF;
END //

CREATE OR REPLACE TRIGGER trg_DocGia_ChanSuaMa
BEFORE UPDATE ON DOC_GIA FOR EACH ROW
BEGIN
  IF NEW.MaNguoi <> OLD.MaNguoi THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'E406: Không được sửa mã độc giả';
  END IF;
END //

CREATE OR REPLACE TRIGGER trg_DocGia_DungLoai
BEFORE INSERT ON DOC_GIA FOR EACH ROW
BEGIN
  IF (SELECT LoaiNguoi FROM NGUOI WHERE MaNguoi = NEW.MaNguoi) <> 'DG' THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'E407: Người này không thuộc loại độc giả (LoaiNguoi phải là DG)';
  END IF;
END //

CREATE OR REPLACE TRIGGER trg_ThuThu_DungLoai
BEFORE INSERT ON THU_THU FOR EACH ROW
BEGIN
  IF (SELECT LoaiNguoi FROM NGUOI WHERE MaNguoi = NEW.MaNguoi) <> 'TT' THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'E407: Người này không thuộc loại thủ thư (LoaiNguoi phải là TT)';
  END IF;
END //

DELIMITER ;
```

## A.4 Transaction (04_transaction.sql)

```sql
-- =====================================================================
-- 04_transaction.sql – 7 transaction nghiệp vụ, viết dưới dạng procedure
-- Mẫu chung:
--   DECLARE EXIT HANDLER FOR SQLEXCEPTION BEGIN ROLLBACK; RESIGNAL; END;
--   START TRANSACTION; ... kiểm tra, khóa bản ghi (SELECT ... FOR UPDATE) ... COMMIT;
-- Lỗi ở bất kỳ câu lệnh nào (kể cả SIGNAL từ trigger) làm ROLLBACK toàn bộ giao dịch.
-- Danh sách nhiều phần tử (cuốn sách, SĐT, tác giả) truyền dạng mảng JSON, đọc bằng JSON_TABLE.
-- =====================================================================
SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;
USE QLTV;
DELIMITER //

-- ---------------------------------------------------------------------
-- TX1. Mượn sách: 1–10 cuốn trong một phiếu
--   CALL sp_MuonSach('DG0001','TT001','["TR0001-001","TK0003-002"]','2026-07-05', @pm);
-- ---------------------------------------------------------------------
CREATE OR REPLACE PROCEDURE sp_MuonSach(IN p_MaDocGia VARCHAR(10), IN p_MaThuThu VARCHAR(10),
       IN p_DsCuon JSON, IN p_NgayMuon DATE, OUT p_MaPhieuMuon INT)
BEGIN
  DECLARE v_SoCuon INT DEFAULT JSON_LENGTH(p_DsCuon);
  DECLARE v_SoKhoa INT;
  DECLARE EXIT HANDLER FOR SQLEXCEPTION BEGIN ROLLBACK; RESIGNAL; END;
  SET p_NgayMuon = COALESCE(p_NgayMuon, CURDATE());

  START TRANSACTION;
    IF v_SoCuon IS NULL OR v_SoCuon = 0 THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'E100: Phiếu mượn phải có ít nhất 1 cuốn';
    END IF;
    IF v_SoCuon > 10 THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'E101: Mỗi lần mượn tối đa 10 cuốn sách';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM DOC_GIA WHERE MaNguoi = p_MaDocGia AND TrangThai = 'HoatDong') THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'E402: Độc giả không tồn tại hoặc đang bị khóa';
    END IF;
    IF fn_TheConHan(p_MaDocGia, p_NgayMuon) = 0 THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'E103: Thẻ độc giả đã hết hạn';
    END IF;
    -- Khóa dòng độc giả (tuần tự hóa các giao dịch mượn của cùng độc giả → đếm 50 cuốn chính xác)
    -- và khóa các cuốn sách (hai thủ thư không cho mượn trùng một cuốn)
    SELECT MaNguoi INTO @v_khoa FROM DOC_GIA WHERE MaNguoi = p_MaDocGia FOR UPDATE;
    SELECT COUNT(*) INTO v_SoKhoa
    FROM CUON_SACH cs JOIN JSON_TABLE(p_DsCuon, '$[*]' COLUMNS (Ma VARCHAR(10) CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci PATH '$')) j
         ON j.Ma = cs.MaCuonSach
    WHERE cs.TrangThai = 'TrenGia'
    FOR UPDATE;
    IF v_SoKhoa <> v_SoCuon THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'E104: Có cuốn không tồn tại, bị trùng hoặc không có trên giá';
    END IF;

    INSERT INTO PHIEU_MUON(MaDocGia, MaThuThu, NgayMuon) VALUES (p_MaDocGia, p_MaThuThu, p_NgayMuon);
    SET p_MaPhieuMuon = LAST_INSERT_ID();
    -- TRG1, TRG2 kiểm tra; TRG4, TRG5 đổi trạng thái, số lượng trên giá, tuổi thọ
    INSERT INTO CT_MUON(MaPhieuMuon, MaCuonSach, HanTra)
    SELECT p_MaPhieuMuon, j.Ma, fn_HanTra(j.Ma, p_NgayMuon)
    FROM JSON_TABLE(p_DsCuon, '$[*]' COLUMNS (Ma VARCHAR(10) CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci PATH '$')) j;
  COMMIT;
END //

-- ---------------------------------------------------------------------
-- TX2. Trả sách: 1 đến nhiều cuốn (có thể thuộc nhiều phiếu mượn), tự lập phiếu phạt
--   CALL sp_TraSach('DG0001','TT002','["TR0001-001"]','2026-07-25', @pt, @phat);
-- ---------------------------------------------------------------------
CREATE OR REPLACE PROCEDURE sp_TraSach(IN p_MaDocGia VARCHAR(10), IN p_MaThuThu VARCHAR(10),
       IN p_DsCuon JSON, IN p_NgayTra DATE, OUT p_MaPhieuTra INT, OUT p_TongPhat DECIMAL(12,0))
BEGIN
  DECLARE v_SoCuon INT DEFAULT JSON_LENGTH(p_DsCuon);
  DECLARE v_SoDong INT;
  DECLARE EXIT HANDLER FOR SQLEXCEPTION BEGIN ROLLBACK; RESIGNAL; END;
  SET p_NgayTra = COALESCE(p_NgayTra, CURDATE());

  START TRANSACTION;
    IF v_SoCuon IS NULL OR v_SoCuon = 0 THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'E100: Phiếu trả phải có ít nhất 1 cuốn';
    END IF;
    INSERT INTO PHIEU_TRA(MaDocGia, MaThuThu, NgayTra) VALUES (p_MaDocGia, p_MaThuThu, p_NgayTra);
    SET p_MaPhieuTra = LAST_INSERT_ID();
    -- TRG3 kiểm tra & lập phiếu phạt; TRG4 đưa sách về giá
    UPDATE CT_MUON ct
      JOIN PHIEU_MUON pm ON pm.MaPhieuMuon = ct.MaPhieuMuon
      JOIN JSON_TABLE(p_DsCuon, '$[*]' COLUMNS (Ma VARCHAR(10) CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci PATH '$')) j ON j.Ma = ct.MaCuonSach
    SET ct.MaPhieuTra = p_MaPhieuTra
    WHERE pm.MaDocGia = p_MaDocGia AND ct.MaPhieuTra IS NULL;
    SET v_SoDong = ROW_COUNT();
    IF v_SoDong <> v_SoCuon THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'E108: Có cuốn không do độc giả này mượn hoặc đã được trả';
    END IF;
    SELECT COALESCE(SUM(pp.SoTien), 0) INTO p_TongPhat
    FROM PHIEU_PHAT pp JOIN CT_MUON ct ON ct.MaPhieuMuon = pp.MaPhieuMuon AND ct.MaCuonSach = pp.MaCuonSach
    WHERE ct.MaPhieuTra = p_MaPhieuTra;
  COMMIT;
END //

-- ---------------------------------------------------------------------
-- TX3. Thanh toán toàn bộ tiền phạt chưa trả của một độc giả
-- ---------------------------------------------------------------------
CREATE OR REPLACE PROCEDURE sp_ThanhToanPhat(IN p_MaDocGia VARCHAR(10), IN p_Ngay DATE,
       OUT p_TongTien DECIMAL(12,0))
BEGIN
  DECLARE EXIT HANDLER FOR SQLEXCEPTION BEGIN ROLLBACK; RESIGNAL; END;
  SET p_Ngay = COALESCE(p_Ngay, CURDATE());
  START TRANSACTION;
    SELECT COALESCE(SUM(pp.SoTien), 0) INTO p_TongTien
    FROM PHIEU_PHAT pp JOIN PHIEU_MUON pm ON pm.MaPhieuMuon = pp.MaPhieuMuon
    WHERE pm.MaDocGia = p_MaDocGia AND pp.DaThanhToan = 0
    FOR UPDATE;
    IF p_TongTien = 0 THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'E109: Độc giả không có khoản phạt nào chưa thanh toán';
    END IF;
    UPDATE PHIEU_PHAT pp JOIN PHIEU_MUON pm ON pm.MaPhieuMuon = pp.MaPhieuMuon
    SET pp.DaThanhToan = 1, pp.NgayThanhToan = p_Ngay
    WHERE pm.MaDocGia = p_MaDocGia AND pp.DaThanhToan = 0;
  COMMIT;
END //

-- ---------------------------------------------------------------------
-- TX4. Nhập lô sách: tạo đầu sách (nếu mới) + tác giả + n cuốn, xếp lên giá
--   CALL sp_NhapLoSach('TR0301','Dế Mèn phiêu lưu ký','Kim Đồng',2020,NULL,'["Tô Hoài"]',5,'CN01-K1-TR1','2026-07-01',@sl);
-- ---------------------------------------------------------------------
CREATE OR REPLACE PROCEDURE sp_NhapLoSach(IN p_MaDauSach CHAR(6), IN p_TenSach VARCHAR(200),
       IN p_NXB VARCHAR(100), IN p_Nam SMALLINT, IN p_SoNgayRieng SMALLINT, IN p_DsTacGia JSON,
       IN p_SoLuong INT, IN p_MaGia VARCHAR(12), IN p_NgayNhap DATE, OUT p_SoCuonDaNhap INT)
BEGIN
  DECLARE v_STT, v_TuoiTho, i INT;
  DECLARE EXIT HANDLER FOR SQLEXCEPTION BEGIN ROLLBACK; RESIGNAL; END;
  SET p_NgayNhap = COALESCE(p_NgayNhap, CURDATE());
  START TRANSACTION;
    IF p_SoLuong IS NULL OR p_SoLuong < 1 THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'E306: Số lượng nhập phải từ 1 cuốn';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM DAU_SACH WHERE MaDauSach = p_MaDauSach) THEN
      INSERT INTO DAU_SACH VALUES (p_MaDauSach, LEFT(p_MaDauSach, 2), p_TenSach, p_NXB, p_Nam, p_SoNgayRieng);
      -- tác giả: thêm người chưa có, rồi gắn với đầu sách
      INSERT INTO TAC_GIA(TenTacGia)
      SELECT DISTINCT j.Ten FROM JSON_TABLE(COALESCE(p_DsTacGia, '[]'), '$[*]' COLUMNS (Ten VARCHAR(100) CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci PATH '$')) j
      WHERE NOT EXISTS (SELECT 1 FROM TAC_GIA t WHERE t.TenTacGia = j.Ten);
      INSERT INTO DAU_SACH_TAC_GIA(MaDauSach, MaTacGia)
      SELECT DISTINCT p_MaDauSach, t.MaTacGia
      FROM JSON_TABLE(COALESCE(p_DsTacGia, '[]'), '$[*]' COLUMNS (Ten VARCHAR(100) CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci PATH '$')) j
      JOIN TAC_GIA t ON t.TenTacGia = j.Ten;
    END IF;
    -- STT tiếp theo, tính cả các cuốn đã thanh lý để không tái sử dụng mã
    SELECT GREATEST(COALESCE((SELECT MAX(STT) FROM CUON_SACH WHERE MaDauSach = p_MaDauSach), 0),
                    COALESCE((SELECT MAX(STT) FROM SACH_THANH_LY WHERE MaDauSach = p_MaDauSach), 0))
      INTO v_STT;
    SELECT TuoiThoNam * 12 INTO v_TuoiTho FROM THE_LOAI WHERE MaTheLoai = LEFT(p_MaDauSach, 2);
    SELECT MaGia INTO @v_khoa FROM GIA_SACH WHERE MaGia = p_MaGia FOR UPDATE;
    SET i = 1;
    WHILE i <= p_SoLuong DO                         -- TRG6 kiểm tra thể loại & sức chứa từng cuốn
      INSERT INTO CUON_SACH(MaCuonSach, MaDauSach, STT, MaGia, NgayNhap, TuoiThoConLaiThang)
      VALUES (CONCAT(p_MaDauSach, '-', LPAD(v_STT + i, 3, '0')), p_MaDauSach, v_STT + i,
              p_MaGia, p_NgayNhap, v_TuoiTho);
      SET i = i + 1;
    END WHILE;
    SET p_SoCuonDaNhap = p_SoLuong;
  COMMIT;
END //

-- ---------------------------------------------------------------------
-- TX5. Thanh lý sách hết niên hạn: chuyển sang SACH_THANH_LY (danh mục riêng),
--      chuyển lịch sử mượn sang CT_MUON_LUU_TRU, rồi xóa khỏi CSDL đang quản lý
--      Chỉ thanh lý cuốn 'ChoThanhLy' không còn khoản phạt chưa thanh toán.
-- ---------------------------------------------------------------------
CREATE OR REPLACE PROCEDURE sp_ThanhLySach(IN p_Ngay DATE, OUT p_SoCuon INT)
BEGIN
  DECLARE EXIT HANDLER FOR SQLEXCEPTION BEGIN ROLLBACK; DROP TEMPORARY TABLE IF EXISTS tmp_TL; RESIGNAL; END;
  SET p_Ngay = COALESCE(p_Ngay, CURDATE());
  START TRANSACTION;
    DROP TEMPORARY TABLE IF EXISTS tmp_TL;
    CREATE TEMPORARY TABLE tmp_TL AS
      SELECT cs.MaCuonSach FROM CUON_SACH cs
      WHERE cs.TrangThai = 'ChoThanhLy'
        AND NOT EXISTS (SELECT 1 FROM PHIEU_PHAT pp WHERE pp.MaCuonSach = cs.MaCuonSach AND pp.DaThanhToan = 0)
      FOR UPDATE;
    SELECT COUNT(*) INTO p_SoCuon FROM tmp_TL;

    INSERT INTO SACH_THANH_LY(MaCuonSach, MaDauSach, STT, NgayNhap, NgayThanhLy, LyDo)
    SELECT cs.MaCuonSach, cs.MaDauSach, cs.STT, cs.NgayNhap, p_Ngay, 'Hết niên hạn sử dụng'
    FROM CUON_SACH cs JOIN tmp_TL t ON t.MaCuonSach = cs.MaCuonSach;

    INSERT INTO CT_MUON_LUU_TRU(MaPhieuMuon, MaCuonSach, HanTra, MaPhieuTra, TienPhat)
    SELECT ct.MaPhieuMuon, ct.MaCuonSach, ct.HanTra, ct.MaPhieuTra, COALESCE(pp.SoTien, 0)
    FROM CT_MUON ct JOIN tmp_TL t ON t.MaCuonSach = ct.MaCuonSach
         LEFT JOIN PHIEU_PHAT pp ON pp.MaPhieuMuon = ct.MaPhieuMuon AND pp.MaCuonSach = ct.MaCuonSach;

    DELETE ct FROM CT_MUON ct JOIN tmp_TL t ON t.MaCuonSach = ct.MaCuonSach;   -- PHIEU_PHAT xóa theo CASCADE
    DELETE cs FROM CUON_SACH cs JOIN tmp_TL t ON t.MaCuonSach = cs.MaCuonSach; -- TRG4 giảm số lượng trên giá
    DROP TEMPORARY TABLE tmp_TL;
  COMMIT;
END //

-- ---------------------------------------------------------------------
-- TX6. Đăng ký độc giả: NGUOI + DOC_GIA + ≥1 SĐT + thẻ 1 năm, trong một giao dịch
--   CALL sp_DangKyDocGia('Nguyễn','Văn','An','2000-05-01','M','12','Dịch Vọng','Cầu Giấy','Hà Nội',
--                        'an@gmail.com','["0912345678"]','CN01','2026-07-01',@ma,@the);
-- ---------------------------------------------------------------------
CREATE OR REPLACE PROCEDURE sp_DangKyDocGia(IN p_Ho VARCHAR(30), IN p_Dem VARCHAR(30), IN p_Ten VARCHAR(30),
       IN p_NgaySinh DATE, IN p_GioiTinh CHAR(1), IN p_SoNha VARCHAR(50), IN p_Phuong VARCHAR(50),
       IN p_Quan VARCHAR(50), IN p_TinhTP VARCHAR(50), IN p_Email VARCHAR(100), IN p_DsSDT JSON,
       IN p_MaChiNhanh CHAR(4), IN p_NgayDangKy DATE, OUT p_MaDocGia VARCHAR(10), OUT p_SoThe VARCHAR(12))
BEGIN
  DECLARE EXIT HANDLER FOR SQLEXCEPTION BEGIN ROLLBACK; RESIGNAL; END;
  SET p_NgayDangKy = COALESCE(p_NgayDangKy, CURDATE());
  START TRANSACTION;
    IF COALESCE(JSON_LENGTH(p_DsSDT), 0) = 0 THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'E408: Độc giả phải có ít nhất 1 số điện thoại';
    END IF;
    SELECT MaNguoi INTO @v_khoa FROM NGUOI WHERE LoaiNguoi = 'DG' ORDER BY MaNguoi DESC LIMIT 1 FOR UPDATE;
    SET p_MaDocGia = fn_MaNguoiMoi('DG');
    SET p_SoThe = CONCAT('THE', SUBSTRING(p_MaDocGia, 3));
    INSERT INTO NGUOI(MaNguoi, Ho, Dem, Ten, NgaySinh, GioiTinh, SoNha, Phuong, Quan, TinhTP, Email, LoaiNguoi)
    VALUES (p_MaDocGia, p_Ho, p_Dem, p_Ten, p_NgaySinh, p_GioiTinh, p_SoNha, p_Phuong, p_Quan, p_TinhTP, p_Email, 'DG');
    INSERT INTO SDT_NGUOI(MaNguoi, SoDienThoai)
    SELECT DISTINCT p_MaDocGia, j.So FROM JSON_TABLE(p_DsSDT, '$[*]' COLUMNS (So VARCHAR(10) CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci PATH '$')) j;
    INSERT INTO DOC_GIA(MaNguoi, MaChiNhanh, NgayDangKy) VALUES (p_MaDocGia, p_MaChiNhanh, p_NgayDangKy);
    INSERT INTO THE_DOC_GIA(SoThe, MaDocGia, NgayCap, NgayHetHan)
    VALUES (p_SoThe, p_MaDocGia, p_NgayDangKy, DATE_ADD(p_NgayDangKy, INTERVAL 1 YEAR));
  COMMIT;
END //

-- ---------------------------------------------------------------------
-- TX7. Thuê phòng đọc: kiểm tra thẻ, nợ phạt, sức chứa, số giờ theo loại phòng,
--      giờ mở cửa của chi nhánh; tính tiền; TRG7 chặn trùng giờ
--   CALL sp_ThuePhong('DG0001','CN01-N1','TT001','2026-07-10 09:00','2026-07-10 11:00',6,'2026-07-05',@pt,@tien);
-- ---------------------------------------------------------------------
CREATE OR REPLACE PROCEDURE sp_ThuePhong(IN p_MaDocGia VARCHAR(10), IN p_MaPhongDoc VARCHAR(8),
       IN p_MaThuThu VARCHAR(10), IN p_BatDau DATETIME, IN p_KetThuc DATETIME, IN p_SoNguoi SMALLINT,
       IN p_NgayDat DATE, OUT p_MaPhieuThue INT, OUT p_TongTien DECIMAL(12,0))
BEGIN
  DECLARE v_SucChua SMALLINT;
  DECLARE v_Min, v_Max TINYINT;
  DECLARE v_Loai VARCHAR(8);
  DECLARE v_Mo, v_Dong TIME;
  DECLARE v_SoGio INT DEFAULT TIMESTAMPDIFF(HOUR, p_BatDau, p_KetThuc);
  DECLARE EXIT HANDLER FOR SQLEXCEPTION BEGIN ROLLBACK; RESIGNAL; END;
  SET p_NgayDat = COALESCE(p_NgayDat, CURDATE());
  START TRANSACTION;
    -- khóa phòng: các giao dịch đặt cùng phòng chạy tuần tự, TRG7 kiểm tra trùng giờ chính xác
    SELECT p.SucChua, l.SoGioToiThieu, l.SoGioToiDa, l.MaLoaiPhong, cn.GioMo, cn.GioDong
      INTO v_SucChua, v_Min, v_Max, v_Loai, v_Mo, v_Dong
    FROM PHONG_DOC p JOIN LOAI_PHONG l ON l.MaLoaiPhong = p.MaLoaiPhong
                     JOIN CHI_NHANH cn ON cn.MaChiNhanh = p.MaChiNhanh
    WHERE p.MaPhongDoc = p_MaPhongDoc FOR UPDATE;
    IF v_SucChua IS NULL THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'E205: Không tìm thấy phòng đọc';
    END IF;
    IF fn_TheConHan(p_MaDocGia, DATE(p_BatDau)) = 0 THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'E103: Thẻ độc giả hết hạn vào ngày thuê';
    END IF;
    IF fn_NoPhat(p_MaDocGia) > 0 THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'E110: Độc giả còn nợ tiền phạt, không được thuê phòng';
    END IF;
    IF p_SoNguoi > v_SucChua THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'E202: Số người vượt sức chứa của phòng';
    END IF;
    IF v_SoGio < v_Min OR v_SoGio > v_Max THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'E203: Số giờ thuê không đúng quy định của loại phòng';
    END IF;
    IF TIME(p_BatDau) < v_Mo OR TIME(p_KetThuc) > v_Dong THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'E204: Ngoài giờ mở cửa của chi nhánh';
    END IF;
    SET p_TongTien = fn_TienThuePhong(p_MaPhongDoc, p_BatDau, p_KetThuc);   -- cùng công thức với báo giá
    INSERT INTO PHIEU_THUE_PHONG(MaDocGia, MaPhongDoc, MaThuThuDuyet, NgayDat, BatDau, KetThuc,
                                 SoNguoi, MucDich, TongTien)
    VALUES (p_MaDocGia, p_MaPhongDoc, p_MaThuThu, p_NgayDat, p_BatDau, p_KetThuc, p_SoNguoi,
            IF(v_Loai = 'HOITHAO', 'HoiThao', 'HocNhom'), p_TongTien);
    SET p_MaPhieuThue = LAST_INSERT_ID();
  COMMIT;
END //

DELIMITER ;
```

## A.5 Truy vấn báo cáo (06_view_baocao.sql)

```sql
-- =====================================================================
-- 06_view_baocao.sql – 6 truy vấn hiển thị bắt buộc của đề
-- Mỗi yêu cầu có một VIEW (dùng lại được, không sắp xếp) và một procedure
-- sp_BC_* lọc theo chi nhánh (NULL = tất cả) và sắp xếp đúng yêu cầu.
-- Tham số p_Ngay / p_ThoiDiem cho phép xem báo cáo tại một ngày bất kỳ (demo với dữ liệu quá khứ).
-- =====================================================================
SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;
USE QLTV;

-- Thông tin chung của một dòng mượn (dùng cho báo cáo 1, 2)
CREATE OR REPLACE VIEW v_ChiTietMuon AS
SELECT ct.MaPhieuMuon, ct.MaCuonSach, ds.MaDauSach, ds.TenSach, tl.TenTheLoai,
       pm.MaDocGia, CONCAT_WS(' ', n.Ho, n.Dem, n.Ten) AS HoTenDocGia, dg.MaChiNhanh,
       pm.NgayMuon, ct.HanTra, ct.MaPhieuTra
FROM CT_MUON ct
JOIN PHIEU_MUON pm ON pm.MaPhieuMuon = ct.MaPhieuMuon
JOIN CUON_SACH cs  ON cs.MaCuonSach  = ct.MaCuonSach
JOIN DAU_SACH ds   ON ds.MaDauSach   = cs.MaDauSach
JOIN THE_LOAI tl   ON tl.MaTheLoai   = ds.MaTheLoai
JOIN DOC_GIA dg    ON dg.MaNguoi     = pm.MaDocGia
JOIN NGUOI n       ON n.MaNguoi      = pm.MaDocGia;

-- 1. Sách đang được mượn (chưa trả) – sắp theo hạn trả
CREATE OR REPLACE VIEW v_SachDangMuon AS
SELECT MaCuonSach, TenSach, TenTheLoai, MaDocGia, HoTenDocGia, MaChiNhanh, NgayMuon, HanTra
FROM v_ChiTietMuon WHERE MaPhieuTra IS NULL;

-- 3. Đầu sách theo lượt mượn (tính cả lịch sử của cuốn đã thanh lý; chi nhánh = nơi lập phiếu)
CREATE OR REPLACE VIEW v_LuotMuonDauSach AS
SELECT x.MaDauSach, tt.MaChiNhanh, COUNT(*) AS LuotMuon
FROM (SELECT ct.MaPhieuMuon, cs.MaDauSach FROM CT_MUON ct JOIN CUON_SACH cs ON cs.MaCuonSach = ct.MaCuonSach
      UNION ALL
      SELECT lt.MaPhieuMuon, tl.MaDauSach FROM CT_MUON_LUU_TRU lt JOIN SACH_THANH_LY tl ON tl.MaCuonSach = lt.MaCuonSach) x
JOIN PHIEU_MUON pm ON pm.MaPhieuMuon = x.MaPhieuMuon
JOIN THU_THU tt    ON tt.MaNguoi     = pm.MaThuThu
GROUP BY x.MaDauSach, tt.MaChiNhanh;

-- 4. Các khoản phạt trả muộn của độc giả (phiếu phạt hiện hành + phạt của cuốn đã thanh lý)
CREATE OR REPLACE VIEW v_PhatTraMuon AS
SELECT pm.MaDocGia, pp.SoTien, pp.DaThanhToan FROM PHIEU_PHAT pp JOIN PHIEU_MUON pm ON pm.MaPhieuMuon = pp.MaPhieuMuon
UNION ALL
SELECT pm.MaDocGia, lt.TienPhat, 1 FROM CT_MUON_LUU_TRU lt JOIN PHIEU_MUON pm ON pm.MaPhieuMuon = lt.MaPhieuMuon
WHERE lt.TienPhat > 0;

-- 5. Sách sắp hết hạn sử dụng (tuổi thọ còn dưới 2 năm = 24 tháng)
CREATE OR REPLACE VIEW v_SachSapHetHan AS
SELECT cs.MaCuonSach, ds.TenSach, tl.TenTheLoai, pk.MaChiNhanh, cs.MaGia, cs.NgayNhap,
       cs.TuoiThoConLaiThang, cs.TrangThai
FROM CUON_SACH cs
JOIN DAU_SACH ds  ON ds.MaDauSach  = cs.MaDauSach
JOIN THE_LOAI tl  ON tl.MaTheLoai  = ds.MaTheLoai
JOIN GIA_SACH g   ON g.MaGia       = cs.MaGia
JOIN PHONG_KHO pk ON pk.MaPhongKho = g.MaPhongKho
WHERE cs.TuoiThoConLaiThang < 24;

DELIMITER //

-- 1. Sách đang được mượn, sắp theo thời hạn trả
CREATE OR REPLACE PROCEDURE sp_BC_SachDangMuon(IN p_MaChiNhanh CHAR(4))
  SELECT * FROM v_SachDangMuon
  WHERE p_MaChiNhanh IS NULL OR MaChiNhanh = p_MaChiNhanh
  ORDER BY HanTra, MaCuonSach //

-- 1b. Cách hiểu rộng của yêu cầu 1: mọi lượt sách đã được mượn trong khoảng ngày (kể cả đã trả),
--     sắp theo thời hạn trả; cột TinhTrang cho biết đã trả hay chưa
CREATE OR REPLACE PROCEDURE sp_BC_SachDaMuon(IN p_MaChiNhanh CHAR(4), IN p_TuNgay DATE, IN p_DenNgay DATE)
  SELECT v.MaCuonSach, v.TenSach, v.TenTheLoai, v.MaDocGia, v.HoTenDocGia, v.MaChiNhanh, v.NgayMuon, v.HanTra,
         pt.NgayTra, CASE WHEN v.MaPhieuTra IS NULL THEN 'Chưa trả' ELSE 'Đã trả' END AS TinhTrang
  FROM v_ChiTietMuon v LEFT JOIN PHIEU_TRA pt ON pt.MaPhieuTra = v.MaPhieuTra
  WHERE (p_MaChiNhanh IS NULL OR v.MaChiNhanh = p_MaChiNhanh)
    AND v.NgayMuon BETWEEN COALESCE(p_TuNgay, '1900-01-01') AND COALESCE(p_DenNgay, '2999-12-31')
  ORDER BY v.HanTra, v.MaCuonSach //

-- 2. Sách đã quá hạn trả tại ngày p_Ngay, sắp theo số ngày quá hạn (giảm dần)
CREATE OR REPLACE PROCEDURE sp_BC_SachQuaHan(IN p_MaChiNhanh CHAR(4), IN p_Ngay DATE)
BEGIN
  SET p_Ngay = COALESCE(p_Ngay, CURDATE());
  SELECT MaCuonSach, TenSach, TenTheLoai, MaDocGia, HoTenDocGia, MaChiNhanh, NgayMuon, HanTra,
         DATEDIFF(p_Ngay, HanTra) AS SoNgayQuaHan,
         fn_TinhTienPhat(MaCuonSach, HanTra, p_Ngay) AS PhatDuKien
  FROM v_ChiTietMuon
  WHERE MaPhieuTra IS NULL AND NgayMuon <= p_Ngay AND HanTra < p_Ngay
    AND (p_MaChiNhanh IS NULL OR MaChiNhanh = p_MaChiNhanh)
  ORDER BY SoNgayQuaHan DESC, MaCuonSach;
END //

-- 3. Đầu sách sắp theo lượt mượn nhiều nhất (đầu sách chưa ai mượn có lượt = 0)
CREATE OR REPLACE PROCEDURE sp_BC_DauSachLuotMuon(IN p_MaChiNhanh CHAR(4))
  SELECT ds.MaDauSach, ds.TenSach, tl.TenTheLoai,
         COALESCE(SUM(l.LuotMuon), 0) AS LuotMuon,
         RANK() OVER (ORDER BY COALESCE(SUM(l.LuotMuon), 0) DESC) AS XepHang
  FROM DAU_SACH ds
  JOIN THE_LOAI tl ON tl.MaTheLoai = ds.MaTheLoai
  LEFT JOIN v_LuotMuonDauSach l ON l.MaDauSach = ds.MaDauSach
                               AND (p_MaChiNhanh IS NULL OR l.MaChiNhanh = p_MaChiNhanh)
  GROUP BY ds.MaDauSach, ds.TenSach, tl.TenTheLoai
  ORDER BY LuotMuon DESC, ds.MaDauSach //

-- 4. Độc giả có sách trả muộn, sắp theo tổng tiền phạt rồi số sách trả muộn (giảm dần)
CREATE OR REPLACE PROCEDURE sp_BC_DocGiaTraMuon(IN p_MaChiNhanh CHAR(4))
  SELECT p.MaDocGia, CONCAT_WS(' ', n.Ho, n.Dem, n.Ten) AS HoTen, dg.MaChiNhanh,
         COUNT(*) AS SoSachTraMuon, SUM(p.SoTien) AS TongTienPhat,
         SUM(CASE WHEN p.DaThanhToan = 0 THEN p.SoTien ELSE 0 END) AS ConNo
  FROM v_PhatTraMuon p
  JOIN DOC_GIA dg ON dg.MaNguoi = p.MaDocGia
  JOIN NGUOI n    ON n.MaNguoi  = p.MaDocGia
  WHERE p_MaChiNhanh IS NULL OR dg.MaChiNhanh = p_MaChiNhanh
  GROUP BY p.MaDocGia, HoTen, dg.MaChiNhanh
  ORDER BY TongTienPhat DESC, SoSachTraMuon DESC //

-- 5. Sách sắp hết hạn sử dụng (dưới 2 năm), sắp theo tuổi thọ còn lại
CREATE OR REPLACE PROCEDURE sp_BC_SachSapHetHan(IN p_MaChiNhanh CHAR(4))
  SELECT *, CONCAT(TuoiThoConLaiThang DIV 12, ' năm ', TuoiThoConLaiThang MOD 12, ' tháng') AS ConLai
  FROM v_SachSapHetHan
  WHERE p_MaChiNhanh IS NULL OR MaChiNhanh = p_MaChiNhanh
  ORDER BY TuoiThoConLaiThang, MaCuonSach //

-- 6. Phòng đọc đang có / chưa có người sử dụng tại thời điểm p_ThoiDiem
CREATE OR REPLACE PROCEDURE sp_BC_PhongTaiThoiDiem(IN p_MaChiNhanh CHAR(4), IN p_ThoiDiem DATETIME)
BEGIN
  SET p_ThoiDiem = COALESCE(p_ThoiDiem, NOW());
  SELECT p.MaPhongDoc, p.TenPhong, p.MaChiNhanh, l.TenLoai, p.SucChua,
         CASE WHEN t.MaPhieuThue IS NULL THEN 'Trống' ELSE 'Đang sử dụng' END AS TinhTrang,
         t.MaDocGia, t.SoNguoi, t.BatDau, t.KetThuc
  FROM PHONG_DOC p
  JOIN LOAI_PHONG l ON l.MaLoaiPhong = p.MaLoaiPhong
  LEFT JOIN PHIEU_THUE_PHONG t ON t.MaPhongDoc = p.MaPhongDoc AND t.TrangThai = 'DaDuyet'
                              AND t.BatDau <= p_ThoiDiem AND p_ThoiDiem < t.KetThuc
  WHERE p_MaChiNhanh IS NULL OR p.MaChiNhanh = p_MaChiNhanh
  ORDER BY p.MaChiNhanh, TinhTrang DESC, p.MaPhongDoc;
END //

DELIMITER ;
```

## A.6 Chỉ mục và phân quyền (07_index_baomat.sql)

```sql
-- =====================================================================
-- 07_index_baomat.sql – Tối ưu truy vấn (INDEX) và an toàn bảo mật (ROLE, GRANT)
-- InnoDB đã tự tạo index cho PK, UNIQUE và mọi FK; dưới đây là index bổ sung
-- cho các điều kiện lọc/sắp xếp của báo cáo và trigger.
-- =====================================================================
SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;
USE QLTV;

-- Sách chưa trả (MaPhieuTra IS NULL) sắp theo hạn trả: báo cáo 1, 2; fn_SoSachDangMuon
CREATE INDEX IX_CTMUON_ChuaTra_HanTra ON CT_MUON (MaPhieuTra, HanTra);
-- Sách sắp hết hạn: báo cáo 5
CREATE INDEX IX_CUONSACH_TuoiTho ON CUON_SACH (TuoiThoConLaiThang);
-- Kiểm tra trùng giờ thuê phòng (TRG7) và báo cáo 6
CREATE INDEX IX_THUE_Phong_ThoiGian ON PHIEU_THUE_PHONG (MaPhongDoc, TrangThai, BatDau, KetThuc);
-- Phạt chưa thanh toán (fn_NoPhat, TX3)
CREATE INDEX IX_PHIEUPHAT_ChuaTT ON PHIEU_PHAT (DaThanhToan);
-- Tìm kiếm độc giả theo tên, sách theo tên
CREATE INDEX IX_NGUOI_Ten ON NGUOI (Ten, Ho);
CREATE INDEX IX_DAUSACH_TenSach ON DAU_SACH (TenSach);
ANALYZE TABLE CT_MUON, CUON_SACH, PHIEU_THUE_PHONG, PHIEU_PHAT, NGUOI, DAU_SACH;

-- ---------------------------------------------------------------------
-- Phân quyền theo vai trò. Người dùng không được truy cập bảng trực tiếp:
-- mọi thao tác qua procedure (SQL SECURITY DEFINER mặc định) → luật nghiệp vụ
-- không thể bị vượt qua bằng INSERT/UPDATE tay. MariaDB không có DENY nên
-- nguyên tắc là chỉ GRANT quyền tối thiểu.
-- ---------------------------------------------------------------------
DROP ROLE IF EXISTS r_ThuThu;
DROP ROLE IF EXISTS r_QuanLy;
CREATE ROLE r_ThuThu;
CREATE ROLE r_QuanLy;

-- Thủ thư: nghiệp vụ hằng ngày + tra cứu + báo cáo
GRANT EXECUTE ON PROCEDURE QLTV.sp_MuonSach           TO r_ThuThu;
GRANT EXECUTE ON PROCEDURE QLTV.sp_TraSach            TO r_ThuThu;
GRANT EXECUTE ON PROCEDURE QLTV.sp_ThanhToanPhat      TO r_ThuThu;
GRANT EXECUTE ON PROCEDURE QLTV.sp_DangKyDocGia       TO r_ThuThu;
GRANT EXECUTE ON PROCEDURE QLTV.sp_DocGia_Sua         TO r_ThuThu;
GRANT EXECUTE ON PROCEDURE QLTV.sp_DocGia_GiaHanThe   TO r_ThuThu;
GRANT EXECUTE ON PROCEDURE QLTV.sp_DocGia_TimKiem     TO r_ThuThu;
GRANT EXECUTE ON PROCEDURE QLTV.sp_DauSach_TimKiem    TO r_ThuThu;
GRANT EXECUTE ON PROCEDURE QLTV.sp_CuonSach_TimKiem   TO r_ThuThu;
GRANT EXECUTE ON PROCEDURE QLTV.sp_PhongDoc_TimKiem   TO r_ThuThu;
GRANT EXECUTE ON PROCEDURE QLTV.sp_ThuePhong          TO r_ThuThu;
GRANT EXECUTE ON PROCEDURE QLTV.sp_ThuePhong_BaoGia   TO r_ThuThu;
GRANT EXECUTE ON PROCEDURE QLTV.sp_BC_SachDangMuon    TO r_ThuThu;
GRANT EXECUTE ON PROCEDURE QLTV.sp_BC_SachDaMuon      TO r_ThuThu;
GRANT EXECUTE ON PROCEDURE QLTV.sp_BC_SachQuaHan      TO r_ThuThu;
GRANT EXECUTE ON PROCEDURE QLTV.sp_BC_DauSachLuotMuon TO r_ThuThu;
GRANT EXECUTE ON PROCEDURE QLTV.sp_BC_DocGiaTraMuon   TO r_ThuThu;
GRANT EXECUTE ON PROCEDURE QLTV.sp_BC_SachSapHetHan   TO r_ThuThu;
GRANT EXECUTE ON PROCEDURE QLTV.sp_BC_PhongTaiThoiDiem TO r_ThuThu;
GRANT SELECT ON QLTV.v_SachDangMuon  TO r_ThuThu;
GRANT SELECT ON QLTV.v_SachSapHetHan TO r_ThuThu;

-- Quản lý: toàn quyền thực thi procedure/function (thêm/xóa/sửa danh mục, nhập lô, thanh lý)
-- và đọc mọi bảng; vẫn không ghi trực tiếp vào bảng.
GRANT r_ThuThu TO r_QuanLy;
GRANT EXECUTE ON QLTV.* TO r_QuanLy;
GRANT SELECT  ON QLTV.* TO r_QuanLy;

-- Tài khoản mẫu
DROP USER IF EXISTS 'tt_cn01'@'%';
DROP USER IF EXISTS 'ql_thuvien'@'%';
CREATE USER 'tt_cn01'@'%'    IDENTIFIED BY 'ThuThu@2026';
CREATE USER 'ql_thuvien'@'%' IDENTIFIED BY 'QuanLy@2026';
GRANT r_ThuThu TO 'tt_cn01'@'%';
GRANT r_QuanLy TO 'ql_thuvien'@'%';
SET DEFAULT ROLE r_ThuThu FOR 'tt_cn01'@'%';
SET DEFAULT ROLE r_QuanLy FOR 'ql_thuvien'@'%';
```
