"""Sinh file erd.dot (ký hiệu Chen) cho hệ thống quản lý thư viện."""
import sys

E = []      # entity lines
L = []      # edges
n = 0

def attr(owner, name, key=False, derived=False, multi=False, parts=None, partial=False):
    global n
    n += 1
    a = f"a{n}"
    lab = f"<<U>{name}</U>>" if key else f'"{name}"'
    if partial:
        lab = f"<<U>{name}</U>>"
    style = []
    if derived: style.append("dashed")
    E.append(f'{a} [shape=ellipse, label={lab}, style="{",".join(style) or "solid"}"'
             + (", peripheries=2" if multi else "") + (", color=gray30" if partial else "") + "];")
    L.append(f"{owner} -- {a};")
    for p in parts or []:
        attr(a, p)

def ent(name, weak=False):
    E.append(f'{name} [shape=box, style=filled, fillcolor="#C6E0B4", label="{name}"'
             + (", peripheries=2" if weak else "") + "];")

def rel(name, label, ident=False):
    E.append(f'{name} [shape=diamond, style=filled, fillcolor="#FFE699", label="{label}"'
             + (", peripheries=2" if ident else "") + "];")

# Ký hiệu liên kết theo bài giảng (Chen): nhãn lực lượng 1 / N / M ghi sát thực thể; chân gà ở đầu thực thể
# phía "nhiều"; đường đôi = thực thể tham gia toàn bộ; (min,max) ghi kèm khi có giới hạn cụ thể.
def link(a, b, total=False):
    """Nối a -- b không ký hiệu (ISA); total = đường đôi."""
    L.append(f"{a} -- {b}" + (' [color="black:white:black"]' if total else "") + ";")

def noi(rid, e, the, toan_bo=False, kem="", cong=None, giua=""):
    """Nối hình thoi rid với thực thể e: nhãn lực lượng `the` (1/N/M, kèm `kem` = (min,max) hoặc vai trò) sát e,
    chân gà sát e nếu e ở phía nhiều, đường đôi nếu e tham gia toàn bộ; cong = góc của e để gắn (vd "sw");
    giua = nhãn đặt giữa đường (vai trò, (min,max)) cho chỗ đông."""
    cong = cong or GOC.get((rid, e))
    opt = [f'headlabel="{the}' + (f"\\n{kem}" if kem else "") + '"']
    if the in ("N", "M"): opt += ["dir=forward", "arrowhead=crow"]    # đầu mũi tên luôn ở phía thực thể
    if toan_bo: opt.append('color="black:white:black"')
    if cong: opt.append(f"headport={cong}")
    if giua: opt.append(f'label="{giua}"')
    L.append(f"{rid} -- {e} [{', '.join(opt)}];")

# ---- entities + attributes
ent("CHI_NHANH"); attr("CHI_NHANH", "MaChiNhanh", key=True)
for x in ["TenChiNhanh", "DiaChi", "GioMo", "GioDong"]: attr("CHI_NHANH", x)
ent("NGUOI"); attr("NGUOI", "MaNguoi", key=True)
attr("NGUOI", "HoTen", parts=["Ho", "Dem", "Ten"]); attr("NGUOI", "NgaySinh"); attr("NGUOI", "Tuoi", derived=True)
attr("NGUOI", "GioiTinh"); attr("NGUOI", "DiaChi", parts=["SoNha", "Phuong", "Quan", "TinhTP"])
attr("NGUOI", "Email"); attr("NGUOI", "SoDienThoai", multi=True)
ent("DOC_GIA"); attr("DOC_GIA", "NgayDangKy"); attr("DOC_GIA", "TrangThai")
ent("THU_THU"); attr("THU_THU", "NgayVaoLam")
ent("THE_DOC_GIA"); attr("THE_DOC_GIA", "SoThe", key=True); attr("THE_DOC_GIA", "NgayCap"); attr("THE_DOC_GIA", "NgayHetHan"); attr("THE_DOC_GIA", "ConHan", derived=True)
ent("THE_LOAI"); attr("THE_LOAI", "MaTheLoai", key=True)
for x in ["TenTheLoai", "SoNgayMuon", "TuoiThoNam"]: attr("THE_LOAI", x)
ent("BANG_PHI_PHAT", weak=True); attr("BANG_PHI_PHAT", "NgayApDung", partial=True); attr("BANG_PHI_PHAT", "PhatCoBan"); attr("BANG_PHI_PHAT", "PhatMoiNgay")
ent("TAC_GIA"); attr("TAC_GIA", "MaTacGia", key=True); attr("TAC_GIA", "TenTacGia"); attr("TAC_GIA", "QuocTich")
ent("DAU_SACH"); attr("DAU_SACH", "MaDauSach", key=True)
for x in ["TenSach", "NhaXuatBan", "NamXuatBan", "SoNgayMuonRieng"]: attr("DAU_SACH", x)
attr("DAU_SACH", "SoLuotMuon", derived=True)
ent("CUON_SACH", weak=True); attr("CUON_SACH", "STT", partial=True)
for x in ["NgayNhap", "TuoiThoConLaiThang", "TrangThai"]: attr("CUON_SACH", x)
ent("PHONG_KHO"); attr("PHONG_KHO", "MaPhongKho", key=True); attr("PHONG_KHO", "TenPhong"); attr("PHONG_KHO", "Tang")
ent("GIA_SACH"); attr("GIA_SACH", "MaGia", key=True); attr("GIA_SACH", "SucChua"); attr("GIA_SACH", "SoLuongHienCo", derived=True)
ent("SACH_THANH_LY"); attr("SACH_THANH_LY", "MaCuonSach", key=True)
for x in ["NgayNhap", "NgayThanhLy", "LyDo"]: attr("SACH_THANH_LY", x)
ent("PHIEU_MUON"); attr("PHIEU_MUON", "MaPhieuMuon", key=True); attr("PHIEU_MUON", "NgayMuon")
ent("PHIEU_TRA"); attr("PHIEU_TRA", "MaPhieuTra", key=True); attr("PHIEU_TRA", "NgayTra")
ent("PHIEU_PHAT"); attr("PHIEU_PHAT", "MaPhieuPhat", key=True); attr("PHIEU_PHAT", "SoNgayTre")
attr("PHIEU_PHAT", "SoTien", derived=True); attr("PHIEU_PHAT", "DaThanhToan"); attr("PHIEU_PHAT", "NgayThanhToan")
ent("LOAI_PHONG"); attr("LOAI_PHONG", "MaLoaiPhong", key=True)
for x in ["TenLoai", "GiaMoiGio", "SoGioToiThieu", "SoGioToiDa"]: attr("LOAI_PHONG", x)
ent("PHONG_DOC"); attr("PHONG_DOC", "MaPhongDoc", key=True); attr("PHONG_DOC", "TenPhong"); attr("PHONG_DOC", "SucChua")

# ---- ISA
E.append('ISA [shape=invtriangle, style=filled, fillcolor="#FFFF00", label="ISA\\nd"];')
link("NGUOI", "ISA", total=True); link("ISA", "DOC_GIA"); link("ISA", "THU_THU")

# ---- liên kết hai ngôi: (thực thể, lực lượng 1/N/M ghi sát thực thể đó, thực thể đó tham gia toàn bộ?)
R = [
 ("r_truong", "truong_chi_nhanh", False, ("THU_THU", "1", False), ("CHI_NHANH", "1", True)),
 ("r_lamviec", "lam_viec_tai", False, ("THU_THU", "N", True), ("CHI_NHANH", "1", True)),
 ("r_quanly", "quan_ly", False, ("THU_THU", "1", False), ("THU_THU", "N", False)),   # đệ quy, xem KEM
 ("r_dangky", "dang_ky_tai", False, ("DOC_GIA", "N", True), ("CHI_NHANH", "1", False)),
 ("r_the", "so_huu_the", False, ("DOC_GIA", "1", True), ("THE_DOC_GIA", "1", True)),
 ("r_theloai", "thuoc_the_loai", False, ("DAU_SACH", "N", True), ("THE_LOAI", "1", False)),
 ("r_phi", "ap_dung_phi", True, ("THE_LOAI", "1", True), ("BANG_PHI_PHAT", "N", True)),
 ("r_viet", "viet", False, ("DAU_SACH", "M", False), ("TAC_GIA", "N", True)),
 ("r_gomcuon", "gom_cuon", True, ("DAU_SACH", "1", False), ("CUON_SACH", "N", True)),
 ("r_dattai", "dat_tai", False, ("CUON_SACH", "N", True), ("GIA_SACH", "1", False)),
 ("r_chuatl", "chua_the_loai", False, ("GIA_SACH", "N", True), ("THE_LOAI", "1", False)),
 ("r_namtrong", "nam_trong", False, ("GIA_SACH", "N", True), ("PHONG_KHO", "1", False)),
 ("r_khocn", "thuoc_chi_nhanh", False, ("PHONG_KHO", "N", True), ("CHI_NHANH", "1", False)),
 ("r_lapmuon", "lap_phieu_muon", False, ("THU_THU", "1", False), ("PHIEU_MUON", "N", True)),
 ("r_muonboi", "muon_boi", False, ("DOC_GIA", "1", False), ("PHIEU_MUON", "N", True)),
 ("r_lap_tra", "lap_phieu_tra", False, ("THU_THU", "1", False), ("PHIEU_TRA", "N", True)),
 ("r_traboi", "tra_boi", False, ("DOC_GIA", "1", False), ("PHIEU_TRA", "N", True)),
 ("r_loaiphong", "thuoc_loai", False, ("PHONG_DOC", "N", True), ("LOAI_PHONG", "1", False)),
 ("r_phongcn", "phong_cua", False, ("PHONG_DOC", "N", True), ("CHI_NHANH", "1", False)),
 ("r_tl", "thanh_ly_tu", False, ("SACH_THANH_LY", "N", True), ("DAU_SACH", "1", False)),
]
# Góc gắn cố định cho các chỗ nhiều đường cùng đi vào một điểm (Graphviz: n, ne, e, se, s, sw, w, nw)
GOC = {("r_dangky", "DOC_GIA"): "nw"}
# Liên kết đệ quy quan_ly: vai trò ghi cạnh nhãn 1/N; nhánh "nhân viên" vào cạnh trái, nhánh "quản lý" vào góc dưới trái
# của THU_THU (góc dưới phải bị so_huu_the chắn)
KEM = {"r_quanly": (("quản lý", "sw"), ("nhân viên", "w"))}
for rid, lab, ident, (a, ca, ta), (b, cb, tb) in R:
    rel(rid, lab, ident)
    (ka, pa), (kb, pb) = KEM.get(rid, (("", None), ("", None)))
    noi(rid, a, ca, ta, kem=ka, cong=pa); noi(rid, b, cb, tb, kem=kb, cong=pb)

# ---- kết hợp gom_sach (PHIEU_MUON – CUON_SACH, M:N, thuộc tính HanTra); (1,10): mỗi phiếu tham gia 1..10 lần
E.append('r_gomsach [shape=diamond, style="filled,dashed", fillcolor="#FFE699", penwidth=2, label="gom_sach\\n[kết hợp]"];')
noi("r_gomsach", "PHIEU_MUON", "M", True, kem="(1,10)"); noi("r_gomsach", "CUON_SACH", "N")
attr("r_gomsach", "HanTra")
rel("r_tralai", "tra_lai"); noi("r_tralai", "PHIEU_TRA", "1", True); noi("r_tralai", "r_gomsach", "N")
rel("r_biphat", "bi_phat"); noi("r_biphat", "PHIEU_PHAT", "1", True); noi("r_biphat", "r_gomsach", "1")
rel("r_giu", "giu_sach\\n(suy ra)"); noi("r_giu", "DOC_GIA", "1", giua="(0,50)"); noi("r_giu", "CUON_SACH", "N")

# ---- liên kết 3 ngôi thue_phong M:N:1 (DOC_GIA – PHONG_DOC – THU_THU duyệt), thuộc tính đặt trên liên kết
E.append('r_thue [shape=diamond, style=filled, fillcolor="#F4B183", penwidth=2, label="thue_phong\\n(3 ngôi)"];')
noi("r_thue", "DOC_GIA", "M"); noi("r_thue", "PHONG_DOC", "N"); noi("r_thue", "THU_THU", "1", kem="duyệt")
for x in ["NgayDat", "BatDau", "KetThuc", "SoNguoi", "MucDich", "TrangThai"]: attr("r_thue", x)
attr("r_thue", "TongTien", derived=True)

out = ["graph ERD {", 'graph [layout=neato, overlap=false, sep="+6", splines=true, fontname="Arial", outputorder=edgesfirst];',
       'node [fontname="Arial", fontsize=10]; edge [fontname="Arial", fontsize=9, arrowsize=1.1, labelfontsize=9, labeldistance=2.8];'] + E + L + ["}"]
open(sys.argv[1], "w").write("\n".join(out))
