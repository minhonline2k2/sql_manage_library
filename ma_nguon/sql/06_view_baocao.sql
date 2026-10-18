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
