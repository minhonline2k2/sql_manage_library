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
