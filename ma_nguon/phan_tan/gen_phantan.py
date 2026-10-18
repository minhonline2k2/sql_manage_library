"""Sinh 09_phan_tan.sql: minh họa thiết kế phân tán trên 3 database QLTV_CN01..03 (3 site)."""
CN = ["CN01", "CN02", "CN03"]
TT = [("HD", "HoatDong"), ("KHOA", "Khoa")]
o = []
w = o.append
w("""-- =====================================================================
-- 09_phan_tan.sql – Minh họa phân mảnh, định vị, nhân bản trên 3 site (sinh bởi gen_phantan.py)
-- Site k = database QLTV_CN0k. Quan hệ toàn cục = database QLTV.
-- Chạy sau build_all.sh. Cuối file kiểm tra 3 quy tắc: đầy đủ, tái thiết, tách biệt.
-- =====================================================================
SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;""")
NHAN_BAN = ["CHI_NHANH", "THE_LOAI", "BANG_PHI_PHAT", "LOAI_PHONG", "DAU_SACH", "TAC_GIA", "DAU_SACH_TAC_GIA"]
for k, cn in enumerate(CN, 1):
    db = f"QLTV_{cn}"
    w(f"\n-- ================= Site S{k} = {db} =================")
    w(f"DROP DATABASE IF EXISTS {db};\nCREATE DATABASE {db} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    w("-- Nhân bản toàn phần các bảng danh mục (ít cập nhật, đọc ở mọi site)")
    for t in NHAN_BAN:
        w(f"CREATE TABLE {db}.{t} AS SELECT * FROM QLTV.{t};")
    w("-- Phân mảnh ngang nguyên thủy DOC_GIA theo minterm (MaChiNhanh, TrangThai)")
    for code, tt in TT:
        w(f"CREATE TABLE {db}.DOC_GIA_{code} AS SELECT * FROM QLTV.DOC_GIA WHERE MaChiNhanh = '{cn}' AND TrangThai = '{tt}';")
    dg = f"(SELECT MaNguoi FROM {db}.DOC_GIA_HD UNION ALL SELECT MaNguoi FROM {db}.DOC_GIA_KHOA)"
    w("-- Phân mảnh lai NGUOI (phần độc giả): ngang dẫn xuất theo DOC_GIA_k, rồi dọc theo kết quả BEA")
    w(f"CREATE TABLE {db}.NGUOI_DG_A AS SELECT MaNguoi, Ho, Dem, Ten, Email, LoaiNguoi FROM QLTV.NGUOI WHERE MaNguoi IN {dg};")
    w(f"CREATE TABLE {db}.NGUOI_DG_B AS SELECT MaNguoi, NgaySinh, GioiTinh, SoNha, Phuong, Quan, TinhTP FROM QLTV.NGUOI WHERE MaNguoi IN {dg};")
    w("-- Phân mảnh ngang dẫn xuất (bán kết nối) theo DOC_GIA_k")
    w(f"CREATE TABLE {db}.SDT_NGUOI_DG AS SELECT * FROM QLTV.SDT_NGUOI WHERE MaNguoi IN {dg};")
    w(f"CREATE TABLE {db}.THE_DOC_GIA AS SELECT * FROM QLTV.THE_DOC_GIA WHERE MaDocGia IN {dg};")
    w(f"CREATE TABLE {db}.PHIEU_MUON AS SELECT * FROM QLTV.PHIEU_MUON WHERE MaDocGia IN {dg};")
    w(f"CREATE TABLE {db}.PHIEU_TRA AS SELECT * FROM QLTV.PHIEU_TRA WHERE MaDocGia IN {dg};")
    w(f"CREATE TABLE {db}.CT_MUON AS SELECT * FROM QLTV.CT_MUON WHERE MaPhieuMuon IN (SELECT MaPhieuMuon FROM {db}.PHIEU_MUON);")
    w(f"CREATE TABLE {db}.PHIEU_PHAT AS SELECT * FROM QLTV.PHIEU_PHAT WHERE (MaPhieuMuon, MaCuonSach) IN (SELECT MaPhieuMuon, MaCuonSach FROM {db}.CT_MUON);")
    w("-- Phân mảnh ngang nguyên thủy theo MaChiNhanh và dây chuyền dẫn xuất PHONG_KHO → GIA_SACH → CUON_SACH")
    w(f"CREATE TABLE {db}.THU_THU AS SELECT * FROM QLTV.THU_THU WHERE MaChiNhanh = '{cn}';")
    w(f"CREATE TABLE {db}.NGUOI_TT AS SELECT * FROM QLTV.NGUOI WHERE MaNguoi IN (SELECT MaNguoi FROM {db}.THU_THU);")
    w(f"CREATE TABLE {db}.SDT_NGUOI_TT AS SELECT * FROM QLTV.SDT_NGUOI WHERE MaNguoi IN (SELECT MaNguoi FROM {db}.THU_THU);")
    w(f"CREATE TABLE {db}.PHONG_KHO AS SELECT * FROM QLTV.PHONG_KHO WHERE MaChiNhanh = '{cn}';")
    w(f"CREATE TABLE {db}.GIA_SACH AS SELECT * FROM QLTV.GIA_SACH WHERE MaPhongKho IN (SELECT MaPhongKho FROM {db}.PHONG_KHO);")
    w(f"CREATE TABLE {db}.CUON_SACH AS SELECT * FROM QLTV.CUON_SACH WHERE MaGia IN (SELECT MaGia FROM {db}.GIA_SACH);")
    w(f"CREATE TABLE {db}.PHONG_DOC AS SELECT * FROM QLTV.PHONG_DOC WHERE MaChiNhanh = '{cn}';")
    w(f"CREATE TABLE {db}.PHIEU_THUE_PHONG AS SELECT * FROM QLTV.PHIEU_THUE_PHONG WHERE MaPhongDoc IN (SELECT MaPhongDoc FROM {db}.PHONG_DOC);")
    if k == 1:
        w("-- Bảng lưu trữ (ít truy cập) chỉ đặt tại trụ sở S1, không phân mảnh")
        w(f"CREATE TABLE {db}.SACH_THANH_LY AS SELECT * FROM QLTV.SACH_THANH_LY;")
        w(f"CREATE TABLE {db}.CT_MUON_LUU_TRU AS SELECT * FROM QLTV.CT_MUON_LUU_TRU;")
    w(f"ALTER TABLE {db}.DOC_GIA_HD ADD PRIMARY KEY (MaNguoi); ALTER TABLE {db}.CUON_SACH ADD PRIMARY KEY (MaCuonSach); ALTER TABLE {db}.CT_MUON ADD PRIMARY KEY (MaPhieuMuon, MaCuonSach);")

U = lambda t: " UNION ALL ".join(f"SELECT * FROM QLTV_{c}.{t}" for c in CN)
w("\n-- ================= Tái thiết quan hệ toàn cục từ các mảnh (lược đồ ánh xạ) =================")
w("USE QLTV;")
w("CREATE OR REPLACE VIEW pt_DOC_GIA AS " + " UNION ALL ".join(f"SELECT * FROM QLTV_{c}.DOC_GIA_{x}" for c in CN for x, _ in TT) + ";")
w("CREATE OR REPLACE VIEW pt_NGUOI_DG AS " + " UNION ALL ".join(
    f"SELECT a.MaNguoi, a.Ho, a.Dem, a.Ten, b.NgaySinh, b.GioiTinh, b.SoNha, b.Phuong, b.Quan, b.TinhTP, a.Email, a.LoaiNguoi "
    f"FROM QLTV_{c}.NGUOI_DG_A a JOIN QLTV_{c}.NGUOI_DG_B b ON b.MaNguoi = a.MaNguoi" for c in CN) + ";")
for t in ["PHIEU_MUON", "CT_MUON", "PHIEU_TRA", "PHIEU_PHAT", "CUON_SACH", "GIA_SACH", "THU_THU", "PHONG_DOC", "PHIEU_THUE_PHONG", "THE_DOC_GIA"]:
    w(f"CREATE OR REPLACE VIEW pt_{t} AS {U(t)};")

w("""
-- ================= Kiểm tra 3 quy tắc phân mảnh =================
DROP TABLE IF EXISTS KIEM_TRA_PHAN_TAN;
CREATE TABLE KIEM_TRA_PHAN_TAN (QuanHe VARCHAR(30), QuyTac VARCHAR(20), GiaTri BIGINT, KyVong BIGINT, KetQua CHAR(4));""")
def ck(rel, rule, expr, exp):
    w(f"INSERT INTO KIEM_TRA_PHAN_TAN SELECT '{rel}', '{rule}', v, {exp}, IF(v = {exp}, 'PASS', 'FAIL') FROM (SELECT ({expr}) AS v) x;")
for t, pk in [("DOC_GIA", "MaNguoi"), ("PHIEU_MUON", "MaPhieuMuon"), ("CT_MUON", "MaPhieuMuon, MaCuonSach"), ("PHIEU_TRA", "MaPhieuTra"),
              ("PHIEU_PHAT", "MaPhieuPhat"), ("CUON_SACH", "MaCuonSach"), ("GIA_SACH", "MaGia"), ("THU_THU", "MaNguoi"),
              ("PHONG_DOC", "MaPhongDoc"), ("PHIEU_THUE_PHONG", "MaPhieuThue"), ("THE_DOC_GIA", "SoThe")]:
    ck(t, "Day du", f"SELECT COUNT(*) FROM (SELECT * FROM QLTV.{t} EXCEPT SELECT * FROM pt_{t}) d", 0)
    ck(t, "Tai thiet", f"SELECT (SELECT COUNT(*) FROM pt_{t}) - (SELECT COUNT(*) FROM QLTV.{t})", 0)
    ck(t, "Tach biet", f"SELECT COUNT(*) FROM (SELECT {pk} FROM pt_{t} GROUP BY {pk} HAVING COUNT(*) > 1) d", 0)
ck("NGUOI (doc gia)", "Day du", "SELECT COUNT(*) FROM (SELECT * FROM QLTV.NGUOI WHERE LoaiNguoi='DG' EXCEPT SELECT * FROM pt_NGUOI_DG) d", 0)
ck("NGUOI (doc gia)", "Tai thiet", "SELECT (SELECT COUNT(*) FROM pt_NGUOI_DG) - (SELECT COUNT(*) FROM QLTV.NGUOI WHERE LoaiNguoi='DG')", 0)
ck("NGUOI (doc)", "Tach biet", "SELECT COUNT(*) FROM information_schema.COLUMNS a JOIN information_schema.COLUMNS b ON a.COLUMN_NAME = b.COLUMN_NAME WHERE a.TABLE_SCHEMA='QLTV_CN01' AND a.TABLE_NAME='NGUOI_DG_A' AND b.TABLE_SCHEMA='QLTV_CN01' AND b.TABLE_NAME='NGUOI_DG_B' AND a.COLUMN_NAME <> 'MaNguoi'", 0)
w("SELECT * FROM KIEM_TRA_PHAN_TAN;")
w("SELECT KetQua, COUNT(*) FROM KIEM_TRA_PHAN_TAN GROUP BY KetQua;")
w("""
-- ================= Số bộ của từng mảnh tại từng site (lược đồ cấp phát) =================
SELECT TABLE_SCHEMA AS Site, TABLE_NAME AS Manh, TABLE_ROWS AS SoBo_UocLuong
FROM information_schema.TABLES WHERE TABLE_SCHEMA LIKE 'QLTV\\_CN0%' ORDER BY TABLE_SCHEMA, TABLE_NAME;""")
print("\n".join(o))
