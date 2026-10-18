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
