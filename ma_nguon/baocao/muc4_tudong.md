### 4.3 Minh chứng dữ liệu đã nạp

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

### 4.4 Toàn bộ ràng buộc toàn vẹn cài đặt bằng SQL

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

### 4.5 Danh sách trigger

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

### 4.6 Danh sách function và stored procedure

7 function: `fn_HanTra`, `fn_MaNguoiMoi`, `fn_NoPhat`, `fn_SoSachDangMuon`, `fn_TheConHan`, `fn_TinhTienPhat`, `fn_Tuoi`.

- **Transaction nghiệp vụ (TX1–TX7)** (7): `sp_DangKyDocGia`, `sp_MuonSach`, `sp_NhapLoSach`, `sp_ThanhLySach`, `sp_ThanhToanPhat`, `sp_ThuePhong`, `sp_TraSach`
- **Báo cáo** (7): `sp_BC_DauSachLuotMuon`, `sp_BC_DocGiaTraMuon`, `sp_BC_PhongTaiThoiDiem`, `sp_BC_SachDaMuon`, `sp_BC_SachDangMuon`, `sp_BC_SachQuaHan`, `sp_BC_SachSapHetHan`
- **Thêm / xóa / sửa / tìm kiếm** (31): `sp_ChiNhanh_Sua`, `sp_ChiNhanh_Them`, `sp_ChiNhanh_TimKiem`, `sp_ChiNhanh_Xoa`, `sp_CuonSach_ChuyenGia`, `sp_CuonSach_TimKiem`, `sp_CuonSach_Xoa`, `sp_DauSach_Sua`, `sp_DauSach_Them`, `sp_DauSach_TimKiem`, `sp_DauSach_Xoa`, `sp_DocGia_GiaHanThe`, `sp_DocGia_Sua`, `sp_DocGia_TimKiem`, `sp_DocGia_Xoa`, `sp_GiaSach_Sua`, `sp_GiaSach_Them`, `sp_GiaSach_TimKiem`, `sp_GiaSach_Xoa`, `sp_PhongDoc_Sua`, `sp_PhongDoc_Them`, `sp_PhongDoc_TimKiem`, `sp_PhongDoc_Xoa`, `sp_PhongKho_Sua`, `sp_PhongKho_Them`, `sp_PhongKho_TimKiem`, `sp_PhongKho_Xoa`, `sp_ThuThu_Sua`, `sp_ThuThu_Them`, `sp_ThuThu_TimKiem`, `sp_ThuThu_Xoa`

### 4.9 Kết quả kiểm thử tự động (08_test.sql)

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

