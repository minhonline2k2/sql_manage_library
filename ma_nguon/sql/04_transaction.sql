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
  DECLARE v_Gia DECIMAL(12,0);
  DECLARE v_Min, v_Max TINYINT;
  DECLARE v_Loai VARCHAR(8);
  DECLARE v_Mo, v_Dong TIME;
  DECLARE v_SoGio INT DEFAULT TIMESTAMPDIFF(HOUR, p_BatDau, p_KetThuc);
  DECLARE EXIT HANDLER FOR SQLEXCEPTION BEGIN ROLLBACK; RESIGNAL; END;
  SET p_NgayDat = COALESCE(p_NgayDat, CURDATE());
  START TRANSACTION;
    -- khóa phòng: các giao dịch đặt cùng phòng chạy tuần tự, TRG7 kiểm tra trùng giờ chính xác
    SELECT p.SucChua, l.GiaMoiGio, l.SoGioToiThieu, l.SoGioToiDa, l.MaLoaiPhong, cn.GioMo, cn.GioDong
      INTO v_SucChua, v_Gia, v_Min, v_Max, v_Loai, v_Mo, v_Dong
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
    SET p_TongTien = v_SoGio * v_Gia;
    INSERT INTO PHIEU_THUE_PHONG(MaDocGia, MaPhongDoc, MaThuThuDuyet, NgayDat, BatDau, KetThuc,
                                 SoNguoi, MucDich, TongTien)
    VALUES (p_MaDocGia, p_MaPhongDoc, p_MaThuThu, p_NgayDat, p_BatDau, p_KetThuc, p_SoNguoi,
            IF(v_Loai = 'HOITHAO', 'HoiThao', 'HocNhom'), p_TongTien);
    SET p_MaPhieuThue = LAST_INSERT_ID();
  COMMIT;
END //

DELIMITER ;
