"""Sinh từ điển dữ liệu (tu_dien_du_lieu.md) và sơ đồ lược đồ quan hệ PK–FK (../erd/luoc_do_quan_he.dot → .png)
trực tiếp từ information_schema của CSDL QLTV. Chạy trong btl/baocao: python3 gen_tudien.py"""
import pymysql, subprocess
cn = pymysql.connect(unix_socket="/run/mysqld/mysqld.sock", user="root", database="QLTV", charset="utf8mb4")
cur = cn.cursor()
def q(sql, *a):
    cur.execute(sql, a); return cur.fetchall()

BANG = ["CHI_NHANH", "NGUOI", "SDT_NGUOI", "DOC_GIA", "THE_DOC_GIA", "THU_THU", "THE_LOAI", "BANG_PHI_PHAT", "TAC_GIA", "DAU_SACH",
        "DAU_SACH_TAC_GIA", "PHONG_KHO", "GIA_SACH", "CUON_SACH", "SACH_THANH_LY", "PHIEU_MUON", "PHIEU_TRA", "CT_MUON", "PHIEU_PHAT",
        "CT_MUON_LUU_TRU", "LOAI_PHONG", "PHONG_DOC", "PHIEU_THUE_PHONG"]
TEN_BANG = {"CHI_NHANH": "Chi nhánh thư viện", "NGUOI": "Người – lớp cha của độc giả và thủ thư (ISA)", "SDT_NGUOI": "Số điện thoại của người (thuộc tính đa trị)",
 "DOC_GIA": "Độc giả (lớp con)", "THE_DOC_GIA": "Thẻ độc giả", "THU_THU": "Thủ thư (lớp con)", "THE_LOAI": "Thể loại sách",
 "BANG_PHI_PHAT": "Biểu phí phạt theo thể loại (thực thể yếu)", "TAC_GIA": "Tác giả", "DAU_SACH": "Đầu sách",
 "DAU_SACH_TAC_GIA": "Liên kết N:N đầu sách – tác giả", "PHONG_KHO": "Phòng đựng sách", "GIA_SACH": "Giá sách",
 "CUON_SACH": "Cuốn sách (thực thể yếu của đầu sách)", "SACH_THANH_LY": "Sách đã thanh lý", "PHIEU_MUON": "Phiếu mượn",
 "PHIEU_TRA": "Phiếu trả", "CT_MUON": "Chi tiết mượn – liên kết N:N phiếu mượn – cuốn sách", "PHIEU_PHAT": "Phiếu phạt trả muộn",
 "CT_MUON_LUU_TRU": "Lịch sử mượn của sách đã thanh lý", "LOAI_PHONG": "Loại phòng đọc", "PHONG_DOC": "Phòng đọc",
 "PHIEU_THUE_PHONG": "Phiếu thuê phòng (liên kết 3 ngôi thue_phong)"}
MO_TA = {
 "MaChiNhanh": "Mã chi nhánh, dạng CN01", "TenChiNhanh": "Tên chi nhánh", "DiaChi": "Địa chỉ chi nhánh", "GioMo": "Giờ mở cửa", "GioDong": "Giờ đóng cửa",
 "MaThuThuTruong": "Thủ thư trưởng chi nhánh (1:1)", "MaNguoi": "Mã người: DGxxxx (độc giả) hoặc TTxxx (thủ thư)", "Ho": "Họ", "Dem": "Tên đệm", "Ten": "Tên",
 "NgaySinh": "Ngày sinh", "GioiTinh": "Giới tính M/F", "SoNha": "Số nhà", "Phuong": "Phường", "Quan": "Quận", "TinhTP": "Tỉnh/thành phố",
 "Email": "Thư điện tử", "LoaiNguoi": "Thuộc tính phân biệt ISA: DG / TT", "SoDienThoai": "Một số điện thoại",
 "NgayDangKy": "Ngày đăng ký độc giả", "SoThe": "Số thẻ, dạng THExxxx", "MaDocGia": "Độc giả", "NgayCap": "Ngày cấp thẻ", "NgayHetHan": "Ngày hết hạn thẻ",
 "NgayVaoLam": "Ngày vào làm", "MaQuanLy": "Thủ thư quản lý trực tiếp (đệ quy)", "MaTheLoai": "Mã thể loại", "TenTheLoai": "Tên thể loại",
 "SoNgayMuon": "Số ngày được mượn mặc định", "TuoiThoNam": "Tuổi thọ (năm) của sách thuộc thể loại", "NgayApDung": "Ngày biểu phí bắt đầu có hiệu lực (khóa bán phần)",
 "PhatCoBan": "Tiền phạt cơ bản mỗi lần trả muộn (đ)", "PhatMoiNgay": "Tiền phạt mỗi ngày trễ (đ)", "MaTacGia": "Mã tác giả", "TenTacGia": "Tên tác giả",
 "QuocTich": "Quốc tịch", "MaDauSach": "Mã đầu sách, dạng TR0012", "TenSach": "Tên sách", "NhaXuatBan": "Nhà xuất bản", "NamXuatBan": "Năm xuất bản",
 "SoNgayMuonRieng": "Số ngày mượn riêng của đầu sách (NULL = theo thể loại)", "MaPhongKho": "Mã phòng kho, dạng CN01-K1", "Tang": "Tầng",
 "MaGia": "Mã giá sách, dạng CN01-K1-TR1", "SoLuongHienCo": "Số cuốn đang nằm trên giá (trigger TRG4 duy trì)",
 "MaCuonSach": "Mã cuốn, dạng TR0012-003", "STT": "Số thứ tự cuốn trong đầu sách (khóa bán phần)", "NgayNhap": "Ngày nhập sách",
 "TuoiThoConLaiThang": "Tuổi thọ còn lại (tháng), giảm 1 mỗi lần mượn", "NgayThanhLy": "Ngày thanh lý", "LyDo": "Lý do thanh lý",
 "MaPhieuMuon": "Số phiếu mượn", "MaThuThu": "Thủ thư lập phiếu", "NgayMuon": "Ngày mượn", "MaPhieuTra": "Số phiếu trả (NULL khi chưa trả)",
 "NgayTra": "Ngày trả", "HanTra": "Hạn trả của cuốn trong phiếu", "MaPhieuPhat": "Số phiếu phạt", "SoNgayTre": "Số ngày trả trễ",
 "SoTien": "Tiền phạt (đ), tính theo biểu phí có hiệu lực", "TienPhat": "Tiền phạt (đ) đã phát sinh", "DaThanhToan": "Đã thanh toán (0/1)", "NgayThanhToan": "Ngày thanh toán phạt",
 "MaLoaiPhong": "Mã loại phòng", "TenLoai": "Tên loại phòng", "GiaMoiGio": "Giá thuê mỗi giờ (đ)", "SoGioToiThieu": "Số giờ thuê tối thiểu",
 "SoGioToiDa": "Số giờ thuê tối đa", "MaPhongDoc": "Mã phòng đọc, dạng CN01-N1", "SucChua": "Sức chứa", "TenPhong": "Tên phòng",
 "MaPhieuThue": "Số phiếu thuê (khóa thay thế)", "MaThuThuDuyet": "Thủ thư duyệt phiếu thuê", "NgayDat": "Ngày đặt", "BatDau": "Thời điểm bắt đầu thuê",
 "KetThuc": "Thời điểm kết thúc thuê", "SoNguoi": "Số người sử dụng", "MucDich": "Mục đích thuê", "TongTien": "Tổng tiền thuê (đ), lưu tại thời điểm đặt",
}
RIENG = {("DOC_GIA", "TrangThai"): "Trạng thái độc giả", ("CUON_SACH", "TrangThai"): "TrenGia / DangMuon / ChoThanhLy",
         ("PHIEU_THUE_PHONG", "TrangThai"): "DaDuyet / DaHuy", ("DOC_GIA", "MaChiNhanh"): "Chi nhánh đăng ký",
         ("THU_THU", "MaChiNhanh"): "Chi nhánh làm việc", ("GIA_SACH", "SucChua"): "Số cuốn tối đa (≤ 100)", ("GIA_SACH", "MaTheLoai"): "Thể loại duy nhất của giá",
         ("PHONG_DOC", "SucChua"): "Số người tối đa", ("PHIEU_TRA", "MaThuThu"): "Thủ thư nhận trả", ("PHIEU_TRA", "MaDocGia"): "Độc giả trả sách",
         ("PHIEU_MUON", "MaDocGia"): "Độc giả mượn", ("CUON_SACH", "MaGia"): "Giá đang đặt cuốn sách", ("SACH_THANH_LY", "MaCuonSach"): "Mã cuốn đã thanh lý"}

def fk_cua(t):
    return {r[0]: (r[1], r[2]) for r in q("""SELECT COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME FROM information_schema.KEY_COLUMN_USAGE
        WHERE TABLE_SCHEMA='QLTV' AND TABLE_NAME=%s AND REFERENCED_TABLE_NAME IS NOT NULL""", t)}

o = []; w = o.append
w("## 3.8 Từ điển dữ liệu\n")
w("Từ điển dữ liệu được trích tự động từ `information_schema` của CSDL đã cài đặt (kiểu dữ liệu, cho phép NULL, khóa, giá trị mặc định). "
  "Ký hiệu cột Khóa: **PK** khóa chính, **FK → Bảng** khóa ngoại, **UQ** thuộc ràng buộc UNIQUE. Các ràng buộc CHECK của từng bảng liệt kê ở mục 4.4.\n")
for i, t in enumerate(BANG, 1):
    fk = fk_cua(t)
    uq = {r[0] for r in q("""SELECT k.COLUMN_NAME FROM information_schema.KEY_COLUMN_USAGE k JOIN information_schema.TABLE_CONSTRAINTS c
        ON c.CONSTRAINT_SCHEMA=k.CONSTRAINT_SCHEMA AND c.TABLE_NAME=k.TABLE_NAME AND c.CONSTRAINT_NAME=k.CONSTRAINT_NAME
        WHERE k.TABLE_SCHEMA='QLTV' AND k.TABLE_NAME=%s AND c.CONSTRAINT_TYPE='UNIQUE'""", t)}
    w(f"**{i}. {t}** – {TEN_BANG[t]}\n")
    w("| Cột | Kiểu dữ liệu | NULL | Khóa | Mặc định | Mô tả |"); w("| --- | --- | --- | --- | --- | --- |")
    for col, typ, nul, key, dft, extra in q("""SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_KEY, COLUMN_DEFAULT, EXTRA FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA='QLTV' AND TABLE_NAME=%s ORDER BY ORDINAL_POSITION""", t):
        k = []
        if key == "PRI": k.append("PK")
        if col in fk: k.append(f"FK → {fk[col][0]}")
        if col in uq: k.append("UQ")
        d = "" if dft in (None, "NULL") else str(dft).strip("'")
        if "auto_increment" in extra: d = "tự tăng"
        w(f"| {col} | {typ} | {'Có' if nul == 'YES' else 'Không'} | {', '.join(k)} | {d} | {RIENG.get((t, col), MO_TA.get(col, ''))} |")
    w("")
open("tu_dien_du_lieu.md", "w", encoding="utf-8").write("\n".join(o))

# ---- sơ đồ lược đồ quan hệ: mỗi bảng một bảng HTML, PK gạch chân, FK in nghiêng, cạnh FK → PK
NHOM = {"Con người": ["NGUOI", "SDT_NGUOI", "DOC_GIA", "THE_DOC_GIA", "THU_THU", "CHI_NHANH"],
        "Sách và kho": ["THE_LOAI", "BANG_PHI_PHAT", "TAC_GIA", "DAU_SACH", "DAU_SACH_TAC_GIA", "PHONG_KHO", "GIA_SACH", "CUON_SACH", "SACH_THANH_LY"],
        "Mượn trả": ["PHIEU_MUON", "PHIEU_TRA", "CT_MUON", "PHIEU_PHAT", "CT_MUON_LUU_TRU"], "Phòng đọc": ["LOAI_PHONG", "PHONG_DOC", "PHIEU_THUE_PHONG"]}
MAU = {"Con người": "#DDEBF7", "Sách và kho": "#E2EFDA", "Mượn trả": "#FCE4D6", "Phòng đọc": "#FFF2CC"}
d = ['digraph LDQH {', 'graph [rankdir=LR, nodesep=0.35, ranksep=0.9, fontname="Arial", splines=true, concentrate=false];',
     'node [shape=plaintext, fontname="Arial", fontsize=10]; edge [arrowsize=0.9, color="#555555"];']
for g, ds in NHOM.items():
    for t in ds:
        fk = fk_cua(t)
        hang = []
        for col, key in q("SELECT COLUMN_NAME, COLUMN_KEY FROM information_schema.COLUMNS WHERE TABLE_SCHEMA='QLTV' AND TABLE_NAME=%s ORDER BY ORDINAL_POSITION", t):
            txt = col
            if col in fk: txt = f"<I>{txt}</I>"
            if key == "PRI": txt = f"<U><B>{txt}</B></U>"
            hang.append(f'<TR><TD ALIGN="LEFT" PORT="{col}">{txt}</TD></TR>')
        d.append(f'{t} [label=<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="2" BGCOLOR="white"><TR><TD BGCOLOR="{MAU[g]}"><B>{t}</B></TD></TR>{"".join(hang)}</TABLE>>];')
# Cạnh FK → PK dùng ký hiệu chân gà, suy ra từ ràng buộc thật: đầu bảng FK là 0..N (0..1 nếu cột FK là UNIQUE/PK riêng),
# đầu bảng PK là "một và chỉ một" (0..1 nếu cột FK cho phép NULL)
DUY_NHAT = {(t, c) for t, c in q("""SELECT TABLE_NAME, MAX(COLUMN_NAME) FROM information_schema.STATISTICS
    WHERE TABLE_SCHEMA='QLTV' AND NON_UNIQUE=0 GROUP BY TABLE_NAME, INDEX_NAME HAVING COUNT(*) = 1""")}
CO_NULL = {(t, c) for t, c in q("SELECT TABLE_NAME, COLUMN_NAME FROM information_schema.COLUMNS WHERE TABLE_SCHEMA='QLTV' AND IS_NULLABLE='YES'")}
for t in BANG:
    seen = set()
    for col, (rt, rc) in fk_cua(t).items():
        if (rt, col) in seen: continue
        seen.add((rt, col))
        duoi = "teeodot" if (t, col) in DUY_NHAT else "crowodot"
        dau = "teeodot" if (t, col) in CO_NULL else "teetee"
        d.append(f'{t}:{col} -> {rt}:{rc} [dir=both, arrowtail={duoi}, arrowhead={dau}];')
d.append("}")
open("../erd/luoc_do_quan_he.dot", "w", encoding="utf-8").write("\n".join(d))
subprocess.run("dot -Tpng -Gdpi=130 ../erd/luoc_do_quan_he.dot -o ../erd/luoc_do_quan_he.png", shell=True, check=True)
print("ok", len(o), "dòng từ điển")
