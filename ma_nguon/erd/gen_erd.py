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

# Ký hiệu chân gà (min..max) đặt ở đầu đường nối sát thực thể, đọc ngang qua liên kết:
# số thực thể phía này ứng với MỘT thực thể phía bên kia. Graphviz: hình đầu tiên nằm sát node.
CHAN_GA = {"0..1": "teeodot", "1": "teetee", "0..N": "crowodot", "1..N": "crowtee"}

def link(a, b, card="", total=False, dau=None, cuoi=None, nhan_dau="", nhan_cuoi=""):
    """Nối a -- b; dau/cuoi = ký hiệu chân gà ở đầu a / đầu b; total = đường đôi (tham gia toàn bộ)."""
    opt = [f'label="{card}"'] if card else []
    if dau or cuoi:
        opt.append("dir=" + ("both" if dau and cuoi else "back" if dau else "forward"))
        if dau: opt.append(f"arrowtail={CHAN_GA[dau]}")
        if cuoi: opt.append(f"arrowhead={CHAN_GA[cuoi]}")
    if nhan_dau: opt.append(f'taillabel="{nhan_dau}"')
    if nhan_cuoi: opt.append(f'headlabel="{nhan_cuoi}"')
    if total: opt.append('color="black:white:black"')
    L.append(f"{a} -- {b}" + (f" [{', '.join(opt)}]" if opt else "") + ";")

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

# ---- liên kết hai ngôi: (thực thể, ký hiệu ở đầu thực thể đó, nhãn vai trò)
# Tham gia toàn bộ của A thể hiện bằng min = 1 ở ký hiệu đầu bên kia (vạch thay vì vòng tròn), không vẽ đường đôi.
R = [
 ("r_truong", "truong_chi_nhanh", False, ("THU_THU", "1"), ("CHI_NHANH", "0..1")),
 ("r_lamviec", "lam_viec_tai", False, ("THU_THU", "1..N"), ("CHI_NHANH", "1")),
 ("r_quanly", "quan_ly", False, ("THU_THU", "0..1"), ("THU_THU", "0..N")),   # vai trò ghi ở giữa hai nhánh, xem dưới
 ("r_dangky", "dang_ky_tai", False, ("DOC_GIA", "0..N"), ("CHI_NHANH", "1")),
 ("r_the", "so_huu_the", False, ("DOC_GIA", "1"), ("THE_DOC_GIA", "1")),
 ("r_theloai", "thuoc_the_loai", False, ("DAU_SACH", "0..N"), ("THE_LOAI", "1")),
 ("r_phi", "ap_dung_phi", True, ("THE_LOAI", "1"), ("BANG_PHI_PHAT", "1..N")),
 ("r_viet", "viet", False, ("DAU_SACH", "1..N"), ("TAC_GIA", "0..N")),
 ("r_gomcuon", "gom_cuon", True, ("DAU_SACH", "1"), ("CUON_SACH", "0..N")),
 ("r_dattai", "dat_tai", False, ("CUON_SACH", "0..N"), ("GIA_SACH", "1")),
 ("r_chuatl", "chua_the_loai", False, ("GIA_SACH", "0..N"), ("THE_LOAI", "1")),
 ("r_namtrong", "nam_trong", False, ("GIA_SACH", "0..N"), ("PHONG_KHO", "1")),
 ("r_khocn", "thuoc_chi_nhanh", False, ("PHONG_KHO", "0..N"), ("CHI_NHANH", "1")),
 ("r_lapmuon", "lap_phieu_muon", False, ("THU_THU", "1"), ("PHIEU_MUON", "0..N")),
 ("r_muonboi", "muon_boi", False, ("DOC_GIA", "1"), ("PHIEU_MUON", "0..N")),
 ("r_lap_tra", "lap_phieu_tra", False, ("THU_THU", "1"), ("PHIEU_TRA", "0..N")),
 ("r_traboi", "tra_boi", False, ("DOC_GIA", "1"), ("PHIEU_TRA", "0..N")),
 ("r_loaiphong", "thuoc_loai", False, ("PHONG_DOC", "0..N"), ("LOAI_PHONG", "1")),
 ("r_phongcn", "phong_cua", False, ("PHONG_DOC", "0..N"), ("CHI_NHANH", "1")),
 ("r_tl", "thanh_ly_tu", False, ("SACH_THANH_LY", "0..N"), ("DAU_SACH", "1")),
]
VAI_TRO = {"r_quanly": ("quản lý", "nhân viên")}   # liên kết đệ quy: tên vai trò trên từng nhánh
for rid, lab, ident, (a, ka), (b, kb) in R:
    rel(rid, lab, ident)
    va, vb = VAI_TRO.get(rid, ("", ""))
    link(a, rid, va, dau=ka)
    link(rid, b, vb, cuoi=kb)

# ---- kết hợp gom_sach (PHIEU_MUON – CUON_SACH, thuộc tính HanTra): mỗi phiếu 1..10 cuốn
E.append('r_gomsach [shape=diamond, style="filled,dashed", fillcolor="#FFE699", penwidth=2, label="gom_sach\\n[kết hợp]"];')
link("PHIEU_MUON", "r_gomsach", dau="0..N"); link("r_gomsach", "CUON_SACH", cuoi="1..N", nhan_cuoi="tối đa 10")
attr("r_gomsach", "HanTra")
rel("r_tralai", "tra_lai"); link("PHIEU_TRA", "r_tralai", dau="0..1"); link("r_tralai", "r_gomsach", cuoi="1..N")
rel("r_biphat", "bi_phat"); link("PHIEU_PHAT", "r_biphat", dau="0..1"); link("r_biphat", "r_gomsach", cuoi="1")
rel("r_giu", "giu_sach\\n(suy ra, ≤ 50)"); link("DOC_GIA", "r_giu", dau="0..1"); link("r_giu", "CUON_SACH", cuoi="0..N")

# ---- liên kết 3 ngôi thue_phong (DOC_GIA – PHONG_DOC – THU_THU duyệt), thuộc tính đặt trên liên kết
E.append('r_thue [shape=diamond, style=filled, fillcolor="#F4B183", penwidth=2, label="thue_phong\\n(3 ngôi)"];')
link("DOC_GIA", "r_thue", dau="0..N"); link("PHONG_DOC", "r_thue", dau="0..N"); link("THU_THU", "r_thue", dau="1", nhan_dau="duyệt")
for x in ["NgayDat", "BatDau", "KetThuc", "SoNguoi", "MucDich", "TrangThai"]: attr("r_thue", x)
attr("r_thue", "TongTien", derived=True)

out = ["graph ERD {", 'graph [layout=neato, overlap=false, sep="+6", splines=true, fontname="Arial", outputorder=edgesfirst];',
       'node [fontname="Arial", fontsize=10]; edge [fontname="Arial", fontsize=9, arrowsize=1.1, labelfontsize=9, labeldistance=2.8];'] + E + L + ["}"]
open(sys.argv[1], "w").write("\n".join(out))
