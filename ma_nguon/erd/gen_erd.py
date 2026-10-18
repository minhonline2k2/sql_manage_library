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

def link(a, b, card="", total=False):
    L.append(f'{a} -- {b} [label="{card}"' + (', color="black:white:black"' if total else "") + "];")

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

# ---- relationships
R = [
 ("r_truong", "truong_chi_nhanh", False, ("THU_THU", "1", False), ("CHI_NHANH", "1", True)),
 ("r_lamviec", "lam_viec_tai", False, ("THU_THU", "N", True), ("CHI_NHANH", "1", False)),
 ("r_quanly", "quan_ly", False, ("THU_THU", "1\\nquản lý", False), ("THU_THU", "N\\nnhân viên", False)),
 ("r_dangky", "dang_ky_tai", False, ("DOC_GIA", "N", True), ("CHI_NHANH", "1", False)),
 ("r_the", "so_huu_the", False, ("DOC_GIA", "1", True), ("THE_DOC_GIA", "1", True)),
 ("r_theloai", "thuoc_the_loai", False, ("DAU_SACH", "N", True), ("THE_LOAI", "1", False)),
 ("r_phi", "ap_dung_phi", True, ("THE_LOAI", "1", False), ("BANG_PHI_PHAT", "N", True)),
 ("r_viet", "viet", False, ("DAU_SACH", "N", False), ("TAC_GIA", "M", False)),
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
for rid, lab, ident, (a, ca, ta), (b, cb, tb) in R:
    rel(rid, lab, ident); link(a, rid, ca, ta); link(rid, b, cb, tb)

# ---- aggregation: gom_sach (PHIEU_MUON – CUON_SACH) with HanTra
E.append('r_gomsach [shape=diamond, style="filled,dashed", fillcolor="#FFE699", penwidth=2, label="gom_sach\\n[kết hợp]"];')
link("PHIEU_MUON", "r_gomsach", "(1,10)", True); link("r_gomsach", "CUON_SACH", "M")
attr("r_gomsach", "HanTra")
rel("r_tralai", "tra_lai"); link("PHIEU_TRA", "r_tralai", "1", True); link("r_tralai", "r_gomsach", "N  (vào kết hợp)")
rel("r_biphat", "bi_phat"); link("PHIEU_PHAT", "r_biphat", "1", True); link("r_biphat", "r_gomsach", "1  (vào kết hợp)")
rel("r_giu", "giu_sach\\n(suy ra)"); link("DOC_GIA", "r_giu", "(0,50)"); link("r_giu", "CUON_SACH", "")

# ---- liên kết 3 ngôi thue_phong (DOC_GIA – PHONG_DOC – THU_THU duyệt), thuộc tính đặt trên liên kết
E.append('r_thue [shape=diamond, style=filled, fillcolor="#F4B183", penwidth=2, label="thue_phong\\n(3 ngôi)"];')
link("DOC_GIA", "r_thue", "M"); link("PHONG_DOC", "r_thue", "N"); link("THU_THU", "r_thue", "1\\n(duyệt)")
for x in ["NgayDat", "BatDau", "KetThuc", "SoNguoi", "MucDich", "TrangThai"]: attr("r_thue", x)
attr("r_thue", "TongTien", derived=True)

out = ["graph ERD {", 'graph [layout=neato, overlap=false, sep="+6", splines=true, fontname="Arial", outputorder=edgesfirst];',
       'node [fontname="Arial", fontsize=10]; edge [fontname="Arial", fontsize=9];'] + E + L + ["}"]
open(sys.argv[1], "w").write("\n".join(out))
