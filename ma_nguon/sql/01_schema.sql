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
