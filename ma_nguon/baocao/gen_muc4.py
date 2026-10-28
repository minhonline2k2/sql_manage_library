"""Sinh phần dữ liệu tự động cho mục 4 báo cáo, đọc trực tiếp từ CSDL QLTV vừa dựng (chưa chạy 08_test).
Chạy: python3 gen_muc4.py > muc4_tudong.md   (cần pymysql, MariaDB đang chạy, user root qua socket)"""
import pymysql, subprocess, sys
cn = pymysql.connect(unix_socket="/run/mysqld/mysqld.sock", user="root", database="QLTV", charset="utf8mb4")
cur = cn.cursor()
def q(sql, *a):
    cur.execute(sql, a); return cur.fetchall()
o = []; w = o.append
def bang(hdr, rows):
    w("| " + " | ".join(hdr) + " |"); w("| " + " | ".join("---" for _ in hdr) + " |")
    for r in rows: w("| " + " | ".join("" if v is None else str(v).replace("|", "\\|").replace("\n", " ") for v in r) + " |")
    w("")

MO_TA = {"CHI_NHANH": "Chi nhánh thư viện", "NGUOI": "Người (lớp cha ISA)", "SDT_NGUOI": "Số điện thoại (đa trị)", "DOC_GIA": "Độc giả (lớp con)",
 "THE_DOC_GIA": "Thẻ độc giả", "THU_THU": "Thủ thư (lớp con)", "THE_LOAI": "Thể loại sách", "BANG_PHI_PHAT": "Biểu phí phạt (thực thể yếu)",
 "TAC_GIA": "Tác giả", "DAU_SACH": "Đầu sách", "DAU_SACH_TAC_GIA": "Đầu sách – tác giả (N:N)", "PHONG_KHO": "Phòng đựng sách",
 "GIA_SACH": "Giá sách", "CUON_SACH": "Cuốn sách (thực thể yếu)", "SACH_THANH_LY": "Sách đã thanh lý", "PHIEU_MUON": "Phiếu mượn",
 "PHIEU_TRA": "Phiếu trả", "CT_MUON": "Chi tiết mượn (N:N, kết hợp)", "PHIEU_PHAT": "Phiếu phạt", "CT_MUON_LUU_TRU": "Lịch sử mượn của sách đã thanh lý",
 "LOAI_PHONG": "Loại phòng đọc", "PHONG_DOC": "Phòng đọc", "PHIEU_THUE_PHONG": "Phiếu thuê phòng"}

BANG = [t for t in MO_TA if q("SELECT COUNT(*) FROM information_schema.TABLES WHERE TABLE_SCHEMA='QLTV' AND TABLE_NAME=%s", t)[0][0]]
w("### 4.3 Minh chứng dữ liệu đã nạp\n")
w("Số bản ghi của từng bảng sau khi chạy `05_seed.sql` (thư viện vận hành 01/07/2026 – 30/09/2026), đếm bằng `SELECT COUNT(*)`:\n")
rows = []
for t in BANG:
    rows.append((t, MO_TA.get(t, ""), q(f"SELECT COUNT(*) FROM `{t}`")[0][0]))
bang(["Bảng", "Nội dung", "Số bản ghi"], rows)
w("Một số chỉ số vận hành trong 3 tháng:\n")
chi_so = [
 ("Số lượt mượn (cuốn)", q("SELECT (SELECT COUNT(*) FROM CT_MUON)+(SELECT COUNT(*) FROM CT_MUON_LUU_TRU)")[0][0]),
 ("Số cuốn đang được mượn ngày 30/09/2026", q("SELECT COUNT(*) FROM CT_MUON WHERE MaPhieuTra IS NULL")[0][0]),
 ("Số cuốn quá hạn ngày 30/09/2026", q("SELECT COUNT(*) FROM CT_MUON WHERE MaPhieuTra IS NULL AND HanTra < '2026-09-30'")[0][0]),
 ("Số phiếu phạt / tổng tiền phạt (đ)", "%s / %s" % q("SELECT COUNT(*), FORMAT(SUM(SoTien),0,'de_DE') FROM PHIEU_PHAT")[0]),
 ("Số cuốn sắp hết hạn sử dụng (còn dưới 24 tháng, tính đến ngày dựng CSDL)", q("SELECT COUNT(*) FROM CUON_SACH WHERE TuoiThoConLaiThang < 24")[0][0]),
 ("Số cuốn đã thanh lý", q("SELECT COUNT(*) FROM SACH_THANH_LY")[0][0]),
 ("Độc giả giữ nhiều sách nhất", "%s (%s cuốn)" % q("SELECT MaNguoi, fn_SoSachDangMuon(MaNguoi) s FROM DOC_GIA ORDER BY s DESC LIMIT 1")[0]),
 ("Lượt thuê phòng / doanh thu (đ)", "%s / %s" % q("SELECT COUNT(*), FORMAT(SUM(TongTien),0,'de_DE') FROM PHIEU_THUE_PHONG")[0]),
]
bang(["Chỉ số", "Giá trị"], chi_so)
w("Dữ liệu mẫu (5 dòng đầu) của một số bảng chính:\n")
for t, sql in [("DAU_SACH", "SELECT MaDauSach, MaTheLoai, TenSach, NhaXuatBan, NamXuatBan FROM DAU_SACH ORDER BY MaDauSach LIMIT 5"),
               ("CUON_SACH", "SELECT MaCuonSach, STT, MaGia, NgayNhap, TuoiThoConLaiThang, TrangThai FROM CUON_SACH ORDER BY MaCuonSach LIMIT 5"),
               ("NGUOI / DOC_GIA", "SELECT d.MaNguoi, CONCAT_WS(' ',n.Ho,n.Dem,n.Ten) AS HoTen, n.NgaySinh, n.Quan, d.MaChiNhanh, t.SoThe, t.NgayHetHan FROM DOC_GIA d JOIN NGUOI n ON n.MaNguoi=d.MaNguoi JOIN THE_DOC_GIA t ON t.MaDocGia=d.MaNguoi ORDER BY d.MaNguoi LIMIT 5"),
               ("PHIEU_MUON + CT_MUON", "SELECT pm.MaPhieuMuon, pm.MaDocGia, pm.MaThuThu, pm.NgayMuon, ct.MaCuonSach, ct.HanTra, ct.MaPhieuTra FROM PHIEU_MUON pm JOIN CT_MUON ct ON ct.MaPhieuMuon=pm.MaPhieuMuon ORDER BY pm.MaPhieuMuon LIMIT 5"),
               ("PHIEU_PHAT", "SELECT MaPhieuPhat, MaPhieuMuon, MaCuonSach, SoNgayTre, SoTien, DaThanhToan, NgayThanhToan FROM PHIEU_PHAT ORDER BY MaPhieuPhat LIMIT 5"),
               ("PHIEU_THUE_PHONG", "SELECT MaPhieuThue, MaDocGia, MaPhongDoc, BatDau, KetThuc, SoNguoi, TongTien FROM PHIEU_THUE_PHONG ORDER BY MaPhieuThue LIMIT 5")]:
    cur.execute(sql); hdr = [d[0] for d in cur.description]
    w(f"**{t}**\n"); bang(hdr, cur.fetchall())

w("### 4.4 Toàn bộ ràng buộc toàn vẹn cài đặt bằng SQL\n")
n_ck = q("SELECT COUNT(*) FROM information_schema.CHECK_CONSTRAINTS WHERE CONSTRAINT_SCHEMA='QLTV' AND TABLE_NAME IN (%s)" % ",".join(f"'{t}'" for t in BANG))[0][0]
dem = dict(q("SELECT CONSTRAINT_TYPE, COUNT(*) FROM information_schema.TABLE_CONSTRAINTS WHERE TABLE_SCHEMA='QLTV' AND TABLE_NAME IN (%s) GROUP BY CONSTRAINT_TYPE" % ",".join(f"'{t}'" for t in BANG)))
w(f"Tổng cộng: {dem.get('PRIMARY KEY',0)} khóa chính, {dem.get('FOREIGN KEY',0)} khóa ngoại, {dem.get('UNIQUE',0)} ràng buộc UNIQUE, {n_ck} ràng buộc CHECK, cùng các ràng buộc NOT NULL và DEFAULT (xem mã DDL ở Phụ lục A). Bảng dưới được trích tự động từ `information_schema`.\n")
rows = []
for t in BANG:
    for name, typ in q("SELECT CONSTRAINT_NAME, CONSTRAINT_TYPE FROM information_schema.TABLE_CONSTRAINTS WHERE TABLE_SCHEMA='QLTV' AND TABLE_NAME=%s ORDER BY FIELD(CONSTRAINT_TYPE,'PRIMARY KEY','UNIQUE','FOREIGN KEY','CHECK'), CONSTRAINT_NAME", t):
        if typ in ("PRIMARY KEY", "UNIQUE"):
            cols = ", ".join(r[0] for r in q("SELECT COLUMN_NAME FROM information_schema.KEY_COLUMN_USAGE WHERE TABLE_SCHEMA='QLTV' AND TABLE_NAME=%s AND CONSTRAINT_NAME=%s ORDER BY ORDINAL_POSITION", t, name))
            nd = f"{typ} ({cols})"
        elif typ == "FOREIGN KEY":
            kc = q("SELECT COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME FROM information_schema.KEY_COLUMN_USAGE WHERE TABLE_SCHEMA='QLTV' AND TABLE_NAME=%s AND CONSTRAINT_NAME=%s ORDER BY ORDINAL_POSITION", t, name)
            rc = q("SELECT DELETE_RULE, UPDATE_RULE FROM information_schema.REFERENTIAL_CONSTRAINTS WHERE CONSTRAINT_SCHEMA='QLTV' AND CONSTRAINT_NAME=%s AND TABLE_NAME=%s", name, t)[0]
            nd = f"({', '.join(k[0] for k in kc)}) → {kc[0][1]}({', '.join(k[2] for k in kc)})" + (f" ON DELETE {rc[0]}" if rc[0] != "RESTRICT" else "") + (f" ON UPDATE {rc[1]}" if rc[1] != "RESTRICT" else "")
            typ = "FK"
        else:
            nd = q("SELECT CHECK_CLAUSE FROM information_schema.CHECK_CONSTRAINTS WHERE CONSTRAINT_SCHEMA='QLTV' AND TABLE_NAME=%s AND CONSTRAINT_NAME=%s", t, name)[0][0]
            nd = nd.replace("`", "")
        rows.append((t, name, typ.replace("PRIMARY KEY", "PK"), nd))
bang(["Bảng", "Tên ràng buộc", "Loại", "Nội dung"], rows)

w("### 4.5 Danh sách trigger\n")
cur.execute("SELECT TRIGGER_NAME, ACTION_TIMING, EVENT_MANIPULATION, EVENT_OBJECT_TABLE FROM information_schema.TRIGGERS WHERE TRIGGER_SCHEMA='QLTV' ORDER BY EVENT_OBJECT_TABLE, ACTION_ORDER")
NHOM = {"trg_CTMuon_ToiDa10": "TRG1", "trg_CTMuon_ToiDa50": "TRG2", "trg_CTMuon_KiemTraTra": "TRG3", "trg_CTMuon_LapPhieuPhat": "TRG3",
        "trg_CTMuon_Muon": "TRG4", "trg_CTMuon_Tra": "TRG4", "trg_CuonSach_DemGia_Them": "TRG4", "trg_CuonSach_DemGia_Sua": "TRG4", "trg_CuonSach_DemGia_Xoa": "TRG4",
        "trg_CTMuon_GiamTuoiTho": "TRG5", "trg_CuonSach_DungGia_Them": "TRG6", "trg_CuonSach_DungGia_Sua": "TRG6",
        "trg_ThuePhong_KhongTrung_Them": "TRG7", "trg_ThuePhong_KhongTrung_Sua": "TRG7",
        "trg_DocGia_ChanXoa": "TRG8", "trg_DocGia_ChanSuaMa": "TRG8", "trg_DocGia_DungLoai": "TRG8", "trg_ThuThu_DungLoai": "TRG8"}
rows = sorted(((NHOM.get(r[0], "?"), r[0], f"{r[1]} {r[2]}", r[3]) for r in cur.fetchall()), key=lambda x: (x[0], x[1]))
bang(["Nhóm", "Trigger", "Thời điểm, sự kiện", "Bảng"], rows)

w("### 4.6 Danh sách function và stored procedure\n")
cur.execute("SELECT ROUTINE_TYPE, ROUTINE_NAME FROM information_schema.ROUTINES WHERE ROUTINE_SCHEMA='QLTV' AND ROUTINE_NAME NOT LIKE 'sp\\_KT\\_%' ORDER BY ROUTINE_TYPE, ROUTINE_NAME")
r = cur.fetchall()
fn = [x[1] for x in r if x[0] == "FUNCTION"]; sp = [x[1] for x in r if x[0] == "PROCEDURE"]
nhom = {"Transaction nghiệp vụ (TX1–TX7)": [p for p in sp if p in ("sp_MuonSach", "sp_TraSach", "sp_ThanhToanPhat", "sp_NhapLoSach", "sp_ThanhLySach", "sp_DangKyDocGia", "sp_ThuePhong")],
        "Báo cáo": [p for p in sp if p.startswith("sp_BC_")]}
nhom["Cập nhật định kỳ"] = [p for p in sp if p == "sp_CapNhatTuoiTho"]
nhom["Thêm / xóa / sửa / tìm kiếm, báo giá"] = [p for p in sp if p not in sum(nhom.values(), [])]
w(f"{len(fn)} function: " + ", ".join(f"`{x}`" for x in fn) + ".\n")
for k, v in nhom.items():
    w(f"- **{k}** ({len(v)}): " + ", ".join(f"`{x}`" for x in v))
ev = q("SELECT EVENT_NAME, INTERVAL_VALUE, INTERVAL_FIELD FROM information_schema.EVENTS WHERE EVENT_SCHEMA='QLTV' ORDER BY 1")
chu_ky = lambda gt, don_vi: ("mỗi ngày" if str(gt) == "1" else f"mỗi {gt} ngày") if don_vi == "DAY" else f"mỗi {gt} {don_vi.lower()}"
w(f"- **Event** ({len(ev)}): " + ", ".join(f"`{e[0]}` (chạy {chu_ky(e[1], e[2])}, gọi sp_CapNhatTuoiTho)" for e in ev))
w("")

# Kết quả kiểm thử: chạy 08_test.sql (làm thay đổi dữ liệu, nên để cuối)
cn.close()
out = subprocess.run("mariadb --default-character-set=utf8mb4 -uroot QLTV < ../sql/08_test.sql", shell=True, capture_output=True, text=True).stdout
cn = pymysql.connect(unix_socket="/run/mysqld/mysqld.sock", user="root", database="QLTV", charset="utf8mb4"); cur = cn.cursor()
w("### 4.9 Kết quả kiểm thử tự động (08_test.sql)\n")
rows = q("SELECT MaCa, MoTa, KyVong, ThucTe, IF(KetQua='PASS', 'Đạt', 'Không đạt') FROM KET_QUA_KIEM_THU ORDER BY STT")
tong = q("SELECT SUM(KetQua='PASS'), COUNT(*) FROM KET_QUA_KIEM_THU")[0]
w(f"Kết quả: {tong[0]}/{tong[1]} ca đạt.\n")
bang(["Mã ca", "Mô tả", "Kỳ vọng", "Thực tế", "Kết quả"], rows)
sys.stdout.write("\n".join(o) + "\n")
