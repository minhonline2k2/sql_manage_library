"""Giao diện tối giản Hệ thống quản lý thư viện.  Chạy: streamlit run app.py
Mọi thao tác gọi stored procedure; thông báo lỗi hiển thị nguyên văn từ CSDL (SIGNAL Exxx)."""
import json
from datetime import date, datetime, time
import streamlit as st
from db import goi, bang, doc, LoiNghiepVu

st.set_page_config(page_title="Quản lý thư viện", layout="wide")
CN = ["CN01", "CN02", "CN03"]


def chay(ham, thanh_cong="Thành công"):
    try:
        kq = ham()
        st.success(thanh_cong if kq is None else f"{thanh_cong}: {kq}")
    except LoiNghiepVu as e:
        st.error(str(e))


def ds_ma(text):
    return json.dumps([x.strip() for x in text.replace("\n", ",").split(",") if x.strip()])


with st.sidebar:
    st.title("Thư viện")
    chi_nhanh = st.selectbox("Chi nhánh làm việc", CN)
    DS_TRANG = ["Mượn sách", "Trả sách & phạt", "Phòng đọc", "Độc giả", "Sách & kho", "Thủ thư & chi nhánh", "Báo cáo"]
    trang = st.radio("Chức năng", DS_TRANG, index=int(st.query_params.get("trang", 0)))   # ?trang=6&bc=3 để mở thẳng
    thu_thu = doc("SELECT MaNguoi FROM THU_THU WHERE MaChiNhanh = %s ORDER BY MaNguoi", (chi_nhanh,))["MaNguoi"].tolist()
    ma_thu_thu = st.selectbox("Thủ thư thao tác", thu_thu)

st.header(trang)

# ------------------------------------------------------------------ MƯỢN
if trang == "Mượn sách":
    c1, c2 = st.columns([1, 2])
    with c1:
        dg = st.text_input("Mã độc giả", "DG0002")
        ngay = st.date_input("Ngày mượn", date.today())
        cuon = st.text_area("Mã cuốn sách (tối đa 10, cách nhau bởi dấu phẩy)", height=120)
        if st.button("Lập phiếu mượn", type="primary"):
            chay(lambda: goi("sp_MuonSach", dg, ma_thu_thu, ds_ma(cuon), ngay, so_out=1)[1][0], "Đã lập phiếu mượn số")
    with c2:
        st.caption("Sách đang trên giá tại chi nhánh")
        tu = st.text_input("Tìm theo tên / mã", "")
        st.dataframe(bang("sp_CuonSach_TimKiem", tu or None, chi_nhanh, "TrenGia"), height=380, use_container_width=True)

# ------------------------------------------------------------------ TRẢ
elif trang == "Trả sách & phạt":
    dg = st.text_input("Mã độc giả", "DG0002")
    if dg:
        st.caption("Sách độc giả đang giữ")
        st.dataframe(bang("sp_BC_SachDangMuon", None).query("MaDocGia == @dg"), use_container_width=True)
    c1, c2 = st.columns(2)
    with c1:
        ngay = st.date_input("Ngày trả", date.today())
        cuon = st.text_area("Mã cuốn trả (1 hoặc nhiều)")
        if st.button("Lập phiếu trả", type="primary"):
            chay(lambda: "phiếu %s, tiền phạt %s đ" % tuple(goi("sp_TraSach", dg, ma_thu_thu, ds_ma(cuon), ngay, so_out=2)[1]), "Đã trả")
    with c2:
        if st.button("Thanh toán toàn bộ phạt"):
            chay(lambda: f"{goi('sp_ThanhToanPhat', dg, date.today(), so_out=1)[1][0]:,} đ", "Đã thu")

# ------------------------------------------------------------------ PHÒNG ĐỌC
elif trang == "Phòng đọc":
    tab1, tab2 = st.tabs(["Đặt phòng / tình trạng", "Quản lý phòng đọc"])
    with tab1:
        c1, c2 = st.columns([1, 2])
        with c1:
            dg = st.text_input("Mã độc giả", "DG0002", key="pd_dg")
            phong = st.selectbox("Phòng", bang("sp_PhongDoc_TimKiem", chi_nhanh, None, None)["MaPhongDoc"])
            ngay = st.date_input("Ngày sử dụng", date.today())
            gio = st.slider("Khung giờ", 7, 21, (9, 11))
            so_nguoi = st.number_input("Số người", 1, 200, 4)
            bd, kt = datetime.combine(ngay, time(gio[0])), datetime.combine(ngay, time(gio[1]))
            bg = bang("sp_ThuePhong_BaoGia", phong, bd, kt, so_nguoi) if phong else None
            if bg is not None and not bg.empty:   # Streamlit chạy lại mỗi lần đổi giá trị → giá cập nhật ngay
                r = bg.iloc[0]
                st.metric("Tiền thuê dự kiến", f"{r.TongTien:,.0f} đ".replace(",", "."))
                st.caption(f"{r.TenLoai}: {r.GiaMoiGio:,.0f} đ/giờ × {r.SoGio} giờ".replace(",", "."))
                if r.CanhBao:
                    st.warning(r.CanhBao)
            if st.button("Đặt phòng", type="primary"):
                chay(lambda: "phiếu %s, %s đ" % tuple(goi("sp_ThuePhong", dg, phong, ma_thu_thu,
                     bd, kt, so_nguoi, date.today(), so_out=2)[1]), "Đã đặt")
        with c2:
            thoi_diem = st.text_input("Xem tình trạng phòng tại thời điểm", datetime.now().strftime("%Y-%m-%d %H:00"))
            st.dataframe(bang("sp_BC_PhongTaiThoiDiem", chi_nhanh, thoi_diem), use_container_width=True)
    with tab2:
        loai = st.selectbox("Lọc theo loại phòng", [None, "NHOM", "HOITHAO"])
        toi_thieu = st.number_input("Sức chứa tối thiểu", 0, 200, 0)
        st.dataframe(bang("sp_PhongDoc_TimKiem", chi_nhanh, loai, toi_thieu or None), use_container_width=True)
        a, b, c, d = st.columns(4)
        ma = a.text_input("Mã phòng (vd CN01-N6)", key="pd_ma"); ten = b.text_input("Tên phòng", key="pd_ten")
        lp = c.selectbox("Loại", ["NHOM", "HOITHAO"], key="pd_loai"); sc = d.number_input("Sức chứa", 1, 200, 8, key="pd_sc")
        k1, k2, k3 = st.columns(3)
        if k1.button("Thêm phòng"):
            chay(lambda: goi("sp_PhongDoc_Them", ma, chi_nhanh, lp, ten, sc) and None, f"Đã thêm phòng {ma}")
        if k2.button("Sửa tên / sức chứa"):
            chay(lambda: goi("sp_PhongDoc_Sua", ma, ten or None, sc) and None, f"Đã sửa phòng {ma}")
        if k3.button("Xóa phòng"):
            chay(lambda: goi("sp_PhongDoc_Xoa", ma) and None, f"Đã xóa phòng {ma}")

# ------------------------------------------------------------------ ĐỘC GIẢ
elif trang == "Độc giả":
    tab1, tab2, tab3 = st.tabs(["Tìm kiếm", "Đăng ký mới", "Sửa / gia hạn / xóa"])
    with tab1:
        tu = st.text_input("Mã, số thẻ, tên hoặc SĐT", "")
        st.dataframe(bang("sp_DocGia_TimKiem", tu or None, chi_nhanh), use_container_width=True)
    with tab2:
        a, b, c = st.columns(3)
        ho, dem, ten = a.text_input("Họ"), b.text_input("Đệm"), c.text_input("Tên")
        ns = a.date_input("Ngày sinh", date(2000, 1, 1)); gt = b.selectbox("Giới tính", ["M", "F"]); email = c.text_input("Email")
        so_nha, phuong, quan = a.text_input("Số nhà"), b.text_input("Phường"), c.text_input("Quận")
        sdt = a.text_input("Số điện thoại (nhiều số cách bởi dấu phẩy)")
        if st.button("Đăng ký", type="primary"):
            chay(lambda: "mã %s, thẻ %s" % tuple(goi("sp_DangKyDocGia", ho, dem or None, ten, ns, gt, so_nha or None, phuong or None,
                 quan or None, "Hà Nội", email or None, ds_ma(sdt), chi_nhanh, date.today(), so_out=2)[1]), "Đã đăng ký")
    with tab3:
        ma = st.text_input("Mã độc giả cần thao tác")
        email_moi = st.text_input("Email mới (để trống nếu giữ nguyên)")
        k1, k2, k3, k4 = st.columns(4)
        if k1.button("Lưu sửa"):
            chay(lambda: goi("sp_DocGia_Sua", ma, None, None, None, None, None, None, None, email_moi or None, None) and None)
        if k2.button("Gia hạn thẻ 1 năm"):
            chay(lambda: goi("sp_DocGia_GiaHanThe", ma, date.today()) and None)
        if k3.button("Khóa độc giả"):
            chay(lambda: goi("sp_DocGia_Sua", ma, None, None, None, None, None, None, None, None, "Khoa") and None)
        if k4.button("Xóa độc giả"):
            chay(lambda: goi("sp_DocGia_Xoa", ma) and None)

# ------------------------------------------------------------------ SÁCH
elif trang == "Sách & kho":
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Đầu sách", "Cuốn sách", "Nhập lô / thanh lý", "Giá sách", "Phòng kho"])
    with tab1:
        tu = st.text_input("Tên sách, tác giả hoặc mã", "")
        tl = st.selectbox("Thể loại", [None] + doc("SELECT MaTheLoai FROM THE_LOAI")["MaTheLoai"].tolist())
        st.dataframe(bang("sp_DauSach_TimKiem", tu or None, tl), use_container_width=True)
        ma = st.text_input("Mã đầu sách cần sửa/xóa"); ten = st.text_input("Tên mới")
        x1, x2 = st.columns(2)
        if x1.button("Sửa tên"):
            chay(lambda: goi("sp_DauSach_Sua", ma, ten, None, None, None) and None)
        if x2.button("Xóa đầu sách"):
            chay(lambda: goi("sp_DauSach_Xoa", ma) and None)
    with tab2:
        tu = st.text_input("Mã cuốn / tên sách", "", key="cs")
        tt = st.selectbox("Trạng thái", [None, "TrenGia", "DangMuon", "ChoThanhLy"])
        st.dataframe(bang("sp_CuonSach_TimKiem", tu or None, chi_nhanh, tt), use_container_width=True)
        cuon, gia = st.text_input("Mã cuốn chuyển giá"), st.text_input("Giá mới")
        x1, x2 = st.columns(2)
        if x1.button("Chuyển giá"):
            chay(lambda: goi("sp_CuonSach_ChuyenGia", cuon, gia) and None, f"Đã chuyển {cuon} sang {gia}")
        if x2.button("Xóa cuốn sách"):
            chay(lambda: goi("sp_CuonSach_Xoa", cuon) and None, f"Đã xóa {cuon}")
    with tab3:
        a, b = st.columns(2)
        ma = a.text_input("Mã đầu sách (vd TR0301)"); ten = b.text_input("Tên sách")
        nxb = a.text_input("Nhà xuất bản"); nam = b.number_input("Năm xuất bản", 1900, 2100, 2025)
        tg = a.text_input("Tác giả (cách bởi dấu phẩy)"); sl = b.number_input("Số cuốn", 1, 100, 5)
        gia = a.selectbox("Xếp lên giá", bang("sp_GiaSach_TimKiem", chi_nhanh, ma[:2] if len(ma) >= 2 else None)["MaGia"])
        if st.button("Nhập lô sách", type="primary"):
            chay(lambda: goi("sp_NhapLoSach", ma, ten, nxb or None, nam, None, ds_ma(tg), sl, gia, date.today(), so_out=1)[1][0], "Số cuốn đã nhập")
        st.divider()
        if st.button("Thanh lý toàn bộ sách hết niên hạn"):
            chay(lambda: goi("sp_ThanhLySach", date.today(), so_out=1)[1][0], "Số cuốn đã thanh lý")
    with tab4:
        st.dataframe(bang("sp_GiaSach_TimKiem", chi_nhanh, None), use_container_width=True)
        a, b, c, d = st.columns(4)
        mg = a.text_input("Mã giá (vd CN01-K1-TR9)"); kho = b.selectbox("Phòng kho", bang("sp_PhongKho_TimKiem", chi_nhanh)["MaPhongKho"])
        tl2 = c.selectbox("Thể loại của giá", doc("SELECT MaTheLoai FROM THE_LOAI")["MaTheLoai"].tolist()); sc = d.number_input("Sức chứa (≤ 100)", 1, 100, 100)
        k1, k2, k3 = st.columns(3)
        if k1.button("Thêm giá"):
            chay(lambda: goi("sp_GiaSach_Them", mg, kho, tl2, sc) and None, f"Đã thêm giá {mg}")
        if k2.button("Sửa sức chứa"):
            chay(lambda: goi("sp_GiaSach_Sua", mg, sc) and None, f"Đã sửa giá {mg}")
        if k3.button("Xóa giá"):
            chay(lambda: goi("sp_GiaSach_Xoa", mg) and None, f"Đã xóa giá {mg}")
    with tab5:
        st.dataframe(bang("sp_PhongKho_TimKiem", chi_nhanh), use_container_width=True)
        a, b, c = st.columns(3)
        mk = a.text_input("Mã phòng kho (vd CN01-K3)"); tk = b.text_input("Tên phòng kho"); tang = c.number_input("Tầng", 0, 20, 1)
        k1, k2, k3 = st.columns(3)
        if k1.button("Thêm phòng kho"):
            chay(lambda: goi("sp_PhongKho_Them", mk, chi_nhanh, tk, tang) and None, f"Đã thêm {mk}")
        if k2.button("Sửa phòng kho"):
            chay(lambda: goi("sp_PhongKho_Sua", mk, tk or None, tang) and None, f"Đã sửa {mk}")
        if k3.button("Xóa phòng kho"):
            chay(lambda: goi("sp_PhongKho_Xoa", mk) and None, f"Đã xóa {mk}")

# ------------------------------------------------------------------ THỦ THƯ
elif trang == "Thủ thư & chi nhánh":
    tab1, tab2, tab3 = st.tabs(["Tìm kiếm thủ thư", "Thêm / sửa / xóa thủ thư", "Chi nhánh"])
    with tab1:
        tu = st.text_input("Mã hoặc tên thủ thư", "", key="tt_tu")
        st.dataframe(bang("sp_ThuThu_TimKiem", tu or None, chi_nhanh), use_container_width=True)
    with tab2:
        st.subheader("Thêm thủ thư")
        a, b, c = st.columns(3)
        ho, dem, ten = a.text_input("Họ", key="tt_ho"), b.text_input("Đệm", key="tt_dem"), c.text_input("Tên", key="tt_ten")
        ns = a.date_input("Ngày sinh", date(1995, 1, 1), key="tt_ns"); gt = b.selectbox("Giới tính", ["M", "F"], key="tt_gt")
        email = c.text_input("Email", key="tt_email"); sdt = a.text_input("Số điện thoại", key="tt_sdt")
        ql = b.selectbox("Người quản lý", [None] + thu_thu, key="tt_ql")
        if st.button("Thêm thủ thư", type="primary"):
            chay(lambda: goi("sp_ThuThu_Them", ho, dem or None, ten, ns, gt, "Hà Nội", email or None, sdt, chi_nhanh,
                 date.today(), ql, so_out=1)[1][0], "Đã thêm thủ thư mã")
        st.subheader("Sửa / xóa thủ thư")
        a, b, c = st.columns(3)
        ma = a.text_input("Mã thủ thư", key="tt_ma"); cn_moi = b.selectbox("Chuyển chi nhánh", [None] + CN, key="tt_cn")
        email_moi = c.text_input("Email mới", key="tt_email2")
        k1, k2 = st.columns(2)
        if k1.button("Lưu sửa thủ thư"):
            chay(lambda: goi("sp_ThuThu_Sua", ma, cn_moi, None, email_moi or None) and None, f"Đã sửa {ma}")
        if k2.button("Xóa thủ thư"):
            chay(lambda: goi("sp_ThuThu_Xoa", ma) and None, f"Đã xóa {ma}")
    with tab3:
        st.dataframe(bang("sp_ChiNhanh_TimKiem", None), use_container_width=True)
        truong = st.selectbox("Đổi thủ thư trưởng của chi nhánh đang chọn", thu_thu)
        if st.button("Cập nhật thủ thư trưởng"):
            chay(lambda: goi("sp_ChiNhanh_Sua", chi_nhanh, None, None, truong) and None, f"{chi_nhanh} có trưởng mới {truong}")

# ------------------------------------------------------------------ BÁO CÁO
elif trang == "Báo cáo":
    loai = st.selectbox("Báo cáo", [
        "1. Sách đã được mượn (theo hạn trả)",
        "2. Sách quá hạn (theo số ngày quá hạn)",
        "3. Đầu sách theo lượt mượn",
        "4. Độc giả trả muộn (theo tổng phạt, số sách)",
        "5. Sách sắp hết hạn sử dụng (< 2 năm)",
        "6. Phòng đọc tại một thời điểm"], index=int(st.query_params.get("bc", 1)) - 1)
    pham_vi = st.radio("Phạm vi", ["Chi nhánh đang chọn", "Toàn hệ thống"], horizontal=True)
    cn = chi_nhanh if pham_vi.startswith("Chi") else None
    so = loai[0]
    if so == "1":
        chi_chua_tra = st.checkbox("Chỉ sách đang được mượn (chưa trả)", value=True)
        if chi_chua_tra:
            df = bang("sp_BC_SachDangMuon", cn)
        else:
            k = st.date_input("Mượn trong khoảng", (date(2026, 7, 1), date(2026, 9, 30)))
            df = bang("sp_BC_SachDaMuon", cn, k[0], k[-1])
    elif so == "2": df = bang("sp_BC_SachQuaHan", cn, st.date_input("Tính đến ngày", date.today()))
    elif so == "3": df = bang("sp_BC_DauSachLuotMuon", cn)
    elif so == "4": df = bang("sp_BC_DocGiaTraMuon", cn)
    elif so == "5": df = bang("sp_BC_SachSapHetHan", cn)
    else: df = bang("sp_BC_PhongTaiThoiDiem", cn, st.text_input("Thời điểm", "2026-07-16 19:00"))
    st.caption(f"{len(df)} dòng")
    st.dataframe(df, use_container_width=True, height=520)
