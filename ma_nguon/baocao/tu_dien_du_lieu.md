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
