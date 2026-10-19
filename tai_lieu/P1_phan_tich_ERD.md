# P1. Phân tích yêu cầu và lược đồ E-R

## 1. Phân tích yêu cầu

### 1.1 Mô tả nghiệp vụ

Thư viện có 3 chi nhánh (CN01 Cầu Giấy, CN02 Hà Đông, CN03 Hoàn Kiếm), mở cửa 07:00–21:00. Mỗi chi nhánh có các phòng đựng sách (phòng kho), trong đó đặt các giá sách; mỗi giá chỉ chứa sách của **một thể loại**, tối đa 100 cuốn. Sách được quản lý theo **đầu sách** (một tựa sách); mỗi đầu sách có nhiều **cuốn sách** vật lý. Mã đầu sách có dạng `TR0012`, trong đó 2 ký tự đầu là mã thể loại; mã cuốn có dạng `TR0012-003` (đầu sách + số thứ tự), nên mã cuốn luôn chứa thông tin đầu sách và thể loại như đề yêu cầu.

Thủ thư làm việc tại một chi nhánh, có thể có thủ thư quản lý trực tiếp; mỗi chi nhánh có đúng một thủ thư trưởng. Độc giả đăng ký tại một chi nhánh và được cấp thẻ có hiệu lực 1 năm (gia hạn mỗi lần 1 năm).

**Mượn sách:** thủ thư lập phiếu mượn cho độc giả; mỗi phiếu tối đa **10 cuốn**; tại mọi thời điểm một độc giả giữ tối đa **50 cuốn** chưa trả. Mỗi cuốn trong phiếu có hạn trả riêng = ngày mượn + số ngày mượn của thể loại, hoặc số ngày riêng của đầu sách nếu có (sách quý, ít bản). Thẻ hết hạn thì không được mượn. Khi mượn, số lượng sách trên giá giảm và tuổi thọ cuốn sách giảm 1 tháng.

**Trả sách:** mỗi lần trả, độc giả trả 1 đến nhiều cuốn (có thể thuộc nhiều phiếu mượn khác nhau); số lượng trên giá tăng lại. Trả muộn bị phạt theo thể loại: tiền phạt = phạt cơ bản/cuốn + phạt mỗi ngày × số ngày trễ (Truyện 100.000đ + 10.000đ/ngày; Tham khảo 200.000đ + 30.000đ/ngày; các thể loại khác do nhóm quy định). Bảng phí phạt có ngày áp dụng để thư viện thay đổi chính sách mà không làm sai các phiếu phạt cũ.

**Tuổi thọ sách:** mỗi thể loại có tuổi thọ (Truyện 15 năm, Tham khảo 10 năm, …), lưu theo tháng; mỗi lần mượn giảm 1 tháng. Cuốn về 0 chuyển trạng thái chờ thanh lý; khi thanh lý được chuyển sang bảng **SACH_THANH_LY** và xóa khỏi kho đang quản lý.

**Phòng đọc:** độc giả thuê phòng học nhóm (4–10 người, 50.000đ/giờ, 1–4 giờ) hoặc phòng hội thảo (20–60 người, 300.000đ/giờ, 2–8 giờ); thuê theo giờ tròn trong giờ mở cửa, đặt trước tối đa 14 ngày, không trùng giờ, số người không vượt sức chứa; thủ thư duyệt phiếu thuê. Độc giả còn nợ phạt hoặc thẻ hết hạn không được thuê.

### 1.2 Thông tin cần lưu trữ

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

### 1.3 Các ứng dụng triển khai trên CSDL

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

### 1.4 Ràng buộc về số lượng bản ghi

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

## 2. Lược đồ E-R

### 2.1 Tập thực thể

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

### 2.2 Liên kết

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

### 2.3 Đối chiếu yêu cầu "đầy đủ các loại" của đề

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

### 2.4 Sơ đồ

Sơ đồ ERD ký hiệu Chen được vẽ bằng Graphviz (`btl/erd/erd.dot`), xuất ảnh ở phần P10 để đưa vào báo cáo: chữ nhật = tập thực thể, chữ nhật kép = thực thể yếu, thoi = liên kết, thoi kép = liên kết xác định, ellipse = thuộc tính (gạch chân = khóa, nét đứt = dẫn xuất, viền kép = đa trị), tam giác ISA, hộp nét đứt bao quanh gom_sach = kết hợp. Ký hiệu đường nối theo chuẩn chân gà (crow's foot), đặt ở đầu sát thực thể và đọc ngang qua liên kết (số thực thể phía đó ứng với một thực thể phía bên kia): vạch + vòng tròn = không hoặc một (0..1); hai vạch = một và chỉ một (1); chân gà + vòng tròn = không hoặc nhiều (0..N); chân gà + vạch = một hoặc nhiều (1..N). Vạch (min = 1) ở đầu bên kia thể hiện thực thể tham gia toàn bộ, vòng tròn (min = 0) là tham gia một phần. Giới hạn cụ thể ghi kèm: tối đa 10 cuốn mỗi phiếu (gom_sach), tối đa 50 cuốn mỗi độc giả (giu_sach). Riêng tổng quát hóa ISA dùng đường đôi = tổng quát hóa đầy đủ.
