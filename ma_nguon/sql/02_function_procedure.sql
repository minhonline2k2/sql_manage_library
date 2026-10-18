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

DELIMITER ;
