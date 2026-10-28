"""Giao diện tối giản Hệ thống quản lý thư viện.  Chạy: streamlit run app.py
Mọi thao tác gọi stored procedure; thông báo lỗi hiển thị nguyên văn từ CSDL (SIGNAL Exxx).
Bảng bấm chọn hàng để sửa/xóa; mã có sẵn trong CSDL được chọn từ danh sách, không gõ tay."""
import json
from datetime import date, datetime, time
import streamlit as st
from db import goi, bang, doc, LoiNghiepVu

st.set_page_config(page_title="Quản lý thư viện", layout="wide")
CN = ["CN01", "CN02", "CN03"]
# Streamlit chỉ chọn hàng khi bấm ô vuông đầu hàng; script này cho bấm vào bất kỳ ô nào cũng chọn (bôi) cả hàng
st.html("""<script>
if (!window.__chonCaHang) {
  window.__chonCaHang = true;
  document.addEventListener("pointerdown", (e) => {
    if (!e.isTrusted || e.button !== 0) return;
    const sc = e.target.closest && e.target.closest("[data-testid=stDataFrame] .dvn-scroller");
    if (!sc) return;
    const r = sc.getBoundingClientRect();
    if (e.clientX < r.left + 40 || e.clientY < r.top + 36) return;   // ô vuông đầu hàng, dòng tiêu đề: giữ nguyên
    const o = {clientX: r.left + 18, clientY: e.clientY, bubbles: true, cancelable: true,
               pointerId: 1, isPrimary: true, button: 0, pointerType: "mouse"};
    setTimeout(() => {
      sc.dispatchEvent(new PointerEvent("pointerdown", {...o, buttons: 1}));
      sc.dispatchEvent(new PointerEvent("pointerup", o));
      sc.dispatchEvent(new MouseEvent("click", o));
    }, 30);
  }, true);
}
</script>""", unsafe_allow_javascript=True)


def chay(ham, thanh_cong="Thành công", noi="chung"):
    """Gọi CSDL; thành công thì nạp lại trang (bỏ chọn bảng, làm trống ô chọn) và báo tại `noi`, lỗi thì báo ngay."""
    try:
        kq = ham()
    except LoiNghiepVu as e:
        st.error(str(e))
        return
    st.session_state.thong_bao = (noi, thanh_cong if kq is None else f"{thanh_cong}: {kq}")
    st.session_state.lam_moi = st.session_state.get("lam_moi", 0) + 1
    st.rerun()


def bao(noi="chung"):
    tb = st.session_state.get("thong_bao")
    if tb and tb[0] == noi:
        st.success(tb[1])
        del st.session_state["thong_bao"]


def tien(x):
    """Số tiền kiểu Việt Nam: 3200000 → '3.200.000 đ'."""
    return f"{x:,.0f}".replace(",", ".") + " đ"


def ds_ma(text):
    return json.dumps([x.strip() for x in text.replace("\n", ",").split(",") if x.strip()])


def chon_hang(df, key, height=None):
    """Bảng bấm chọn một hàng (bôi cả hàng); trả về hàng đang chọn hoặc None."""
    ev = st.dataframe(df, key=f"{key}_{st.session_state.get('lam_moi', 0)}", on_select="rerun",
                      selection_mode="single-row", hide_index=True, use_container_width=True,
                      **({"height": height} if height else {}))
    hang = [i for i in ev.selection.rows if i < len(df)]
    return df.iloc[hang[0]] if hang else None


def bang_chon_nhieu(df, key, o_nhap, cot_ma="MaCuonSach", height=None):
    """Bảng bấm chọn nhiều hàng; hàng vừa bấm chọn thì thêm mã vào ô `o_nhap` (key của st.multiselect),
    bấm lại để bỏ chọn thì bỏ mã đó. Mã người dùng tự thêm/bớt ở ô nhập được giữ nguyên."""
    k = f"{key}_{st.session_state.get('lam_moi', 0)}"
    ma = df[cot_ma].tolist()
    tt = st.session_state.get(k)
    hang = tt["selection"]["rows"] if tt else []
    st.session_state[f"_ma_{k}"] = ma
    st.session_state[f"_truoc_{k}"] = {ma[i] for i in hang if i < len(ma)}     # lựa chọn trước lần bấm kế tiếp

    def khi_chon():
        ma_, truoc = st.session_state[f"_ma_{k}"], st.session_state[f"_truoc_{k}"]
        nay = {ma_[i] for i in st.session_state[k]["selection"]["rows"] if i < len(ma_)}
        hien = st.session_state.get(o_nhap, [])
        st.session_state[o_nhap] = ([m for m in hien if m not in truoc - nay]
                                    + [m for m in ma_ if m in nay - truoc and m not in hien])

    st.dataframe(df, key=k, on_select=khi_chon, selection_mode="multi-row", hide_index=True,
                 use_container_width=True, **({"height": height} if height else {}))


def chon(nhan, df, cot_ma, cot_ten=None, key=None, nhieu=False):
    """Danh sách chọn (gõ để lọc) lấy từ kết quả procedure; hiển thị 'mã – tên'."""
    ten = dict(zip(df[cot_ma], df[cot_ten])) if cot_ten else {}
    hien = lambda m: f"{m} – {ten[m]}" if m in ten else str(m)
    ma = df[cot_ma].tolist()
    if nhieu:
        return st.multiselect(nhan, ma, format_func=hien, key=key, placeholder="Chọn hoặc gõ để tìm")
    return st.selectbox(nhan, ma, format_func=hien, key=key, index=None, placeholder="Chọn hoặc gõ để tìm")


def goi_y(r):
    """Hiện hàng đang chọn hoặc lời nhắc chọn."""
    if r is None:
        st.info("Bấm vào một hàng trong bảng để chọn.")
    else:
        st.markdown(f"Đang chọn: **{r.iloc[0]}** – {r.iloc[1]}")


with st.sidebar:
    st.title("Thư viện")
    chi_nhanh = st.selectbox("Chi nhánh làm việc", CN)
    DS_TRANG = ["Mượn sách", "Trả sách & phạt", "Phòng đọc", "Độc giả", "Sách & kho", "Thủ thư & chi nhánh", "Báo cáo"]
    trang = st.radio("Chức năng", DS_TRANG, index=int(st.query_params.get("trang", 0)))   # ?trang=6&bc=3 để mở thẳng
    thu_thu = doc("SELECT MaNguoi FROM THU_THU WHERE MaChiNhanh = %s ORDER BY MaNguoi", (chi_nhanh,))["MaNguoi"].tolist()
    ma_thu_thu = st.selectbox("Thủ thư thao tác", thu_thu)

st.header(trang)
doc_gia_cn = bang("sp_DocGia_TimKiem", None, chi_nhanh) if trang in ("Mượn sách", "Trả sách & phạt", "Phòng đọc") else None

# ------------------------------------------------------------------ MƯỢN
if trang == "Mượn sách":
    tren_gia = bang("sp_CuonSach_TimKiem", None, chi_nhanh, "TrenGia")
    c1, c2 = st.columns([1, 2])
    with c1:
        dg = chon("Độc giả", doc_gia_cn, "MaDocGia", "HoTen", key="muon_dg")
        ngay = st.date_input("Ngày mượn", date.today())
        cuon = chon("Cuốn sách (tối đa 10)", tren_gia, "MaCuonSach", "TenSach", key=f"muon_cuon_{st.session_state.get('lam_moi', 0)}", nhieu=True)
        if st.button("Lập phiếu mượn", type="primary", disabled=not (dg and cuon)):
            chay(lambda: goi("sp_MuonSach", dg, ma_thu_thu, json.dumps(cuon), ngay, so_out=1)[1][0], "Đã lập phiếu mượn số", "muon")
        bao("muon")
    with c2:
        st.caption("Sách đang trên giá tại chi nhánh – bấm vào hàng để thêm mã vào ô \"Cuốn sách\" (bấm lại để bỏ)")
        bang_chon_nhieu(tren_gia, "muon_bang", f"muon_cuon_{st.session_state.get('lam_moi', 0)}", height=420)

# ------------------------------------------------------------------ TRẢ
elif trang == "Trả sách & phạt":
    dg = chon("Độc giả", doc_gia_cn, "MaDocGia", "HoTen", key="tra_dg")
    dang_giu = bang("sp_BC_SachDangMuon", None).query("MaDocGia == @dg") if dg else None
    if dg:
        st.caption("Sách độc giả đang giữ – bấm vào hàng để thêm mã vào ô \"Cuốn trả\" (bấm lại để bỏ)")
        bang_chon_nhieu(dang_giu, f"tra_bang_{dg}", f"tra_cuon_{st.session_state.get('lam_moi', 0)}")
        c1, c2 = st.columns(2)
        with c1:
            ngay = st.date_input("Ngày trả", date.today())
            cuon = chon("Cuốn trả (1 hoặc nhiều)", dang_giu, "MaCuonSach", "TenSach", key=f"tra_cuon_{st.session_state.get('lam_moi', 0)}", nhieu=True)
            if st.button("Lập phiếu trả", type="primary", disabled=not cuon):
                chay(lambda: (lambda pt, phat: f"phiếu {pt}, tiền phạt {tien(phat)}")(*goi("sp_TraSach", dg, ma_thu_thu, json.dumps(cuon), ngay, so_out=2)[1]),
                     "Đã trả", "tra")
            bao("tra")
        with c2:
            if st.button("Thanh toán toàn bộ phạt"):
                chay(lambda: tien(goi('sp_ThanhToanPhat', dg, date.today(), so_out=1)[1][0]), "Đã thu", "phat")
            bao("phat")

# ------------------------------------------------------------------ PHÒNG ĐỌC
elif trang == "Phòng đọc":
    tab1, tab2 = st.tabs(["Đặt phòng / tình trạng", "Quản lý phòng đọc"])
    ds_phong = bang("sp_PhongDoc_TimKiem", chi_nhanh, None, None)
    with tab1:
        c1, c2 = st.columns([1, 2])
        with c1:
            dg = chon("Độc giả", doc_gia_cn, "MaDocGia", "HoTen", key="pd_dg")
            phong = chon("Phòng", ds_phong, "MaPhongDoc", "TenPhong", key="pd_phong")
            ngay = st.date_input("Ngày sử dụng", date.today())
            gio = st.slider("Khung giờ", 7, 21, (9, 11))
            so_nguoi = st.number_input("Số người", 1, 200, 4)
            bd, kt = datetime.combine(ngay, time(gio[0])), datetime.combine(ngay, time(gio[1]))
            bg = bang("sp_ThuePhong_BaoGia", phong, bd, kt, so_nguoi) if phong else None
            if bg is not None and not bg.empty:   # Streamlit chạy lại mỗi lần đổi giá trị → giá cập nhật ngay
                r = bg.iloc[0]
                st.metric("Tiền thuê dự kiến", tien(r.TongTien))
                st.caption(f"{r.TenLoai}: {tien(r.GiaMoiGio)}/giờ × {r.SoGio} giờ")
                if r.CanhBao:
                    st.warning(r.CanhBao)
            if st.button("Đặt phòng", type="primary", disabled=not (dg and phong)):
                chay(lambda: (lambda pt, so_tien: f"phiếu {pt}, {tien(so_tien)}")(*goi("sp_ThuePhong", dg, phong, ma_thu_thu,
                     bd, kt, so_nguoi, date.today(), so_out=2)[1]), "Đã đặt", "dat_phong")
            bao("dat_phong")
        with c2:
            a, b = st.columns(2)
            ngay_xem = a.date_input("Xem tình trạng phòng ngày", date.today())
            gio_xem = b.selectbox("Lúc", list(range(7, 22)), index=min(max(datetime.now().hour, 7), 21) - 7, format_func=lambda h: f"{h:02d}:00")
            st.dataframe(bang("sp_BC_PhongTaiThoiDiem", chi_nhanh, datetime.combine(ngay_xem, time(gio_xem))),
                         hide_index=True, use_container_width=True)
    with tab2:
        loai = st.selectbox("Lọc theo loại phòng", [None, "NHOM", "HOITHAO"])
        toi_thieu = st.number_input("Sức chứa tối thiểu", 0, 200, 0)
        r = chon_hang(bang("sp_PhongDoc_TimKiem", chi_nhanh, loai, toi_thieu or None), "pd_bang")
        st.subheader("Sửa / xóa phòng đang chọn")
        goi_y(r)
        if r is not None:
            a, b = st.columns(2)
            ten_moi = a.text_input("Tên phòng", r.TenPhong, key=f"pd_ten_{r.MaPhongDoc}")
            sc_moi = b.number_input("Sức chứa", 1, 200, int(r.SucChua), key=f"pd_sc_{r.MaPhongDoc}")
            k1, k2 = st.columns(2)
            if k1.button("Sửa tên / sức chứa"):
                chay(lambda: goi("sp_PhongDoc_Sua", r.MaPhongDoc, ten_moi or None, sc_moi) and None, f"Đã sửa phòng {r.MaPhongDoc}", "pd_sua")
            if k2.button("Xóa phòng"):
                chay(lambda: goi("sp_PhongDoc_Xoa", r.MaPhongDoc) and None, f"Đã xóa phòng {r.MaPhongDoc}", "pd_sua")
        bao("pd_sua")
        st.subheader("Thêm phòng mới")
        a, b, c, d = st.columns(4)
        ma = a.text_input("Mã phòng (vd CN01-N6)", key="pd_ma"); ten = b.text_input("Tên phòng mới", key="pd_ten")
        lp = c.selectbox("Loại", ["NHOM", "HOITHAO"], key="pd_loai"); sc = d.number_input("Sức chứa phòng mới", 1, 200, 8, key="pd_sc")
        if st.button("Thêm phòng"):
            chay(lambda: goi("sp_PhongDoc_Them", ma, chi_nhanh, lp, ten, sc) and None, f"Đã thêm phòng {ma}", "pd_them")
        bao("pd_them")

# ------------------------------------------------------------------ ĐỘC GIẢ
elif trang == "Độc giả":
    tab1, tab2 = st.tabs(["Danh sách / sửa / xóa", "Đăng ký mới"])
    with tab1:
        tu = st.text_input("Lọc theo mã, số thẻ, tên hoặc SĐT", "")
        r = chon_hang(bang("sp_DocGia_TimKiem", tu or None, chi_nhanh), "dg_bang", height=380)
        goi_y(r)
        if r is not None:
            email_moi = st.text_input("Email", r.Email or "", key=f"dg_email_{r.MaDocGia}")
            k1, k2, k3, k4 = st.columns(4)
            if k1.button("Lưu sửa"):
                chay(lambda: goi("sp_DocGia_Sua", r.MaDocGia, None, None, None, None, None, None, None, email_moi or None, None) and None,
                     f"Đã sửa {r.MaDocGia}", "dg")
            if k2.button("Gia hạn thẻ 1 năm"):
                chay(lambda: goi("sp_DocGia_GiaHanThe", r.MaDocGia, date.today()) and None, f"Đã gia hạn thẻ {r.MaDocGia}", "dg")
            if k3.button("Khóa độc giả"):
                chay(lambda: goi("sp_DocGia_Sua", r.MaDocGia, None, None, None, None, None, None, None, None, "Khoa") and None,
                     f"Đã khóa {r.MaDocGia}", "dg")
            if k4.button("Xóa độc giả"):
                chay(lambda: goi("sp_DocGia_Xoa", r.MaDocGia) and None, f"Đã xóa {r.MaDocGia}", "dg")
        bao("dg")
    with tab2:
        a, b, c = st.columns(3)
        ho, dem, ten = a.text_input("Họ"), b.text_input("Đệm"), c.text_input("Tên")
        ns = a.date_input("Ngày sinh", date(2000, 1, 1)); gt = b.selectbox("Giới tính", ["M", "F"]); email = c.text_input("Email")
        so_nha, phuong, quan = a.text_input("Số nhà"), b.text_input("Phường"), c.text_input("Quận")
        sdt = a.text_input("Số điện thoại (nhiều số cách bởi dấu phẩy)")
        if st.button("Đăng ký", type="primary"):
            chay(lambda: "mã %s, thẻ %s" % tuple(goi("sp_DangKyDocGia", ho, dem or None, ten, ns, gt, so_nha or None, phuong or None,
                 quan or None, "Hà Nội", email or None, ds_ma(sdt), chi_nhanh, date.today(), so_out=2)[1]), "Đã đăng ký", "dg_moi")
        bao("dg_moi")

# ------------------------------------------------------------------ SÁCH
elif trang == "Sách & kho":
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Đầu sách", "Cuốn sách", "Nhập lô / thanh lý", "Giá sách", "Phòng kho"])
    the_loai = doc("SELECT MaTheLoai, TenTheLoai FROM THE_LOAI ORDER BY MaTheLoai")
    with tab1:
        a, b = st.columns([3, 1])
        tu = a.text_input("Lọc theo tên sách, tác giả hoặc mã", "")
        tl = b.selectbox("Thể loại", [None] + the_loai["MaTheLoai"].tolist())
        r = chon_hang(bang("sp_DauSach_TimKiem", tu or None, tl), "ds_bang", height=380)
        goi_y(r)
        if r is not None:
            ten = st.text_input("Tên sách", r.TenSach, key=f"ds_ten_{r.MaDauSach}")
            x1, x2 = st.columns(2)
            if x1.button("Sửa tên"):
                chay(lambda: goi("sp_DauSach_Sua", r.MaDauSach, ten, None, None, None) and None, f"Đã sửa {r.MaDauSach}", "ds")
            if x2.button("Xóa đầu sách"):
                chay(lambda: goi("sp_DauSach_Xoa", r.MaDauSach) and None, f"Đã xóa {r.MaDauSach}", "ds")
        bao("ds")
    with tab2:
        a, b = st.columns([3, 1])
        tu = a.text_input("Lọc theo mã cuốn / tên sách", "", key="cs")
        tt = b.selectbox("Trạng thái", [None, "TrenGia", "DangMuon", "ChoThanhLy"])
        r = chon_hang(bang("sp_CuonSach_TimKiem", tu or None, chi_nhanh, tt), "cs_bang", height=380)
        goi_y(r)
        if r is not None:
            gia = chon("Chuyển sang giá (cùng thể loại)", bang("sp_GiaSach_TimKiem", chi_nhanh, r.MaTheLoai), "MaGia", "TenPhong",
                       key=f"cs_gia_{r.MaCuonSach}")
            x1, x2 = st.columns(2)
            if x1.button("Chuyển giá", disabled=not gia):
                chay(lambda: goi("sp_CuonSach_ChuyenGia", r.MaCuonSach, gia) and None, f"Đã chuyển {r.MaCuonSach} sang {gia}", "cs")
            if x2.button("Xóa cuốn sách"):
                chay(lambda: goi("sp_CuonSach_Xoa", r.MaCuonSach) and None, f"Đã xóa {r.MaCuonSach}", "cs")
        bao("cs")
    with tab3:
        moi = st.radio("Đầu sách", ["Đã có trong thư viện", "Đầu sách mới"], horizontal=True)
        a, b = st.columns(2)
        if moi.startswith("Đã có"):
            ma = chon("Chọn đầu sách", bang("sp_DauSach_TimKiem", None, None), "MaDauSach", "TenSach", key="nl_ds")
            ten = nxb = tg = None; nam = None
        else:
            tl_moi = a.selectbox("Thể loại", the_loai["MaTheLoai"].tolist(), format_func=lambda m: f"{m} – {dict(the_loai.values)[m]}")
            ma = tl_moi + b.text_input("Số hiệu đầu sách (4 chữ số, vd 0301)", max_chars=4)
            ten = a.text_input("Tên sách"); nxb = b.text_input("Nhà xuất bản") or None
            nam = a.number_input("Năm xuất bản", 1900, 2100, 2025); tg = ds_ma(b.text_input("Tác giả (cách bởi dấu phẩy)"))
        a, b = st.columns(2)
        sl = a.number_input("Số cuốn", 1, 100, 5)
        gia = chon("Xếp lên giá", bang("sp_GiaSach_TimKiem", chi_nhanh, ma[:2] if ma else None), "MaGia", "TenPhong", key="nl_gia")
        if st.button("Nhập lô sách", type="primary", disabled=not (ma and len(ma) == 6 and gia)):
            chay(lambda: goi("sp_NhapLoSach", ma, ten, nxb, nam, None, tg, sl, gia, date.today(), so_out=1)[1][0], "Số cuốn đã nhập", "nl")
        bao("nl")
        st.divider()
        if st.button("Thanh lý toàn bộ sách hết niên hạn"):
            chay(lambda: goi("sp_ThanhLySach", date.today(), so_out=1)[1][0], "Số cuốn đã thanh lý", "tl")
        bao("tl")
    with tab4:
        ds_kho = bang("sp_PhongKho_TimKiem", chi_nhanh)
        r = chon_hang(bang("sp_GiaSach_TimKiem", chi_nhanh, None), "gs_bang")
        st.subheader("Sửa / xóa giá đang chọn")
        goi_y(r)
        if r is not None:
            sc_moi = st.number_input("Sức chứa (≤ 100)", 1, 100, int(r.SucChua), key=f"gs_sc_{r.MaGia}")
            k1, k2 = st.columns(2)
            if k1.button("Sửa sức chứa"):
                chay(lambda: goi("sp_GiaSach_Sua", r.MaGia, sc_moi) and None, f"Đã sửa giá {r.MaGia}", "gs_sua")
            if k2.button("Xóa giá"):
                chay(lambda: goi("sp_GiaSach_Xoa", r.MaGia) and None, f"Đã xóa giá {r.MaGia}", "gs_sua")
        bao("gs_sua")
        st.subheader("Thêm giá mới")
        a, b, c, d = st.columns(4)
        mg = a.text_input("Mã giá (vd CN01-K1-TR9)"); kho = b.selectbox("Phòng kho", ds_kho["MaPhongKho"])
        tl2 = c.selectbox("Thể loại của giá", the_loai["MaTheLoai"].tolist()); sc = d.number_input("Sức chứa", 1, 100, 100)
        if st.button("Thêm giá"):
            chay(lambda: goi("sp_GiaSach_Them", mg, kho, tl2, sc) and None, f"Đã thêm giá {mg}", "gs_them")
        bao("gs_them")
    with tab5:
        r = chon_hang(bang("sp_PhongKho_TimKiem", chi_nhanh), "pk_bang")
        st.subheader("Sửa / xóa phòng kho đang chọn")
        goi_y(r)
        if r is not None:
            a, b = st.columns(2)
            tk_moi = a.text_input("Tên phòng kho", r.TenPhong, key=f"pk_ten_{r.MaPhongKho}")
            tang_moi = b.number_input("Tầng", 0, 20, int(r.Tang), key=f"pk_tang_{r.MaPhongKho}")
            k1, k2 = st.columns(2)
            if k1.button("Sửa phòng kho"):
                chay(lambda: goi("sp_PhongKho_Sua", r.MaPhongKho, tk_moi or None, tang_moi) and None, f"Đã sửa {r.MaPhongKho}", "pk_sua")
            if k2.button("Xóa phòng kho"):
                chay(lambda: goi("sp_PhongKho_Xoa", r.MaPhongKho) and None, f"Đã xóa {r.MaPhongKho}", "pk_sua")
        bao("pk_sua")
        st.subheader("Thêm phòng kho mới")
        a, b, c = st.columns(3)
        mk = a.text_input("Mã phòng kho (vd CN01-K3)"); tk = b.text_input("Tên phòng kho mới"); tang = c.number_input("Tầng của phòng mới", 0, 20, 1)
        if st.button("Thêm phòng kho"):
            chay(lambda: goi("sp_PhongKho_Them", mk, chi_nhanh, tk, tang) and None, f"Đã thêm {mk}", "pk_them")
        bao("pk_them")

# ------------------------------------------------------------------ THỦ THƯ
elif trang == "Thủ thư & chi nhánh":
    tab1, tab2, tab3 = st.tabs(["Danh sách / sửa / xóa", "Thêm thủ thư", "Chi nhánh"])
    with tab1:
        tu = st.text_input("Lọc theo mã hoặc tên thủ thư", "", key="tt_tu")
        r = chon_hang(bang("sp_ThuThu_TimKiem", tu or None, chi_nhanh), "tt_bang")
        goi_y(r)
        if r is not None:
            a, b = st.columns(2)
            cn_moi = a.selectbox("Chuyển chi nhánh", [None] + [c for c in CN if c != r.MaChiNhanh], key=f"tt_cn_{r.MaThuThu}")
            email_moi = b.text_input("Email mới", key=f"tt_email2_{r.MaThuThu}")
            k1, k2 = st.columns(2)
            if k1.button("Lưu sửa thủ thư"):
                chay(lambda: goi("sp_ThuThu_Sua", r.MaThuThu, cn_moi, None, email_moi or None) and None, f"Đã sửa {r.MaThuThu}", "tt")
            if k2.button("Xóa thủ thư"):
                chay(lambda: goi("sp_ThuThu_Xoa", r.MaThuThu) and None, f"Đã xóa {r.MaThuThu}", "tt")
        bao("tt")
    with tab2:
        a, b, c = st.columns(3)
        ho, dem, ten = a.text_input("Họ", key="tt_ho"), b.text_input("Đệm", key="tt_dem"), c.text_input("Tên", key="tt_ten")
        ns = a.date_input("Ngày sinh", date(1995, 1, 1), key="tt_ns"); gt = b.selectbox("Giới tính", ["M", "F"], key="tt_gt")
        email = c.text_input("Email", key="tt_email"); sdt = a.text_input("Số điện thoại", key="tt_sdt")
        ql = b.selectbox("Người quản lý", [None] + thu_thu, key="tt_ql")
        if st.button("Thêm thủ thư", type="primary"):
            chay(lambda: goi("sp_ThuThu_Them", ho, dem or None, ten, ns, gt, "Hà Nội", email or None, sdt, chi_nhanh,
                 date.today(), ql, so_out=1)[1][0], "Đã thêm thủ thư mã", "tt_them")
        bao("tt_them")
    with tab3:
        st.dataframe(bang("sp_ChiNhanh_TimKiem", None), hide_index=True, use_container_width=True)
        truong = st.selectbox("Đổi thủ thư trưởng của chi nhánh đang chọn", thu_thu)
        if st.button("Cập nhật thủ thư trưởng"):
            chay(lambda: goi("sp_ChiNhanh_Sua", chi_nhanh, None, None, truong) and None, f"{chi_nhanh} có trưởng mới {truong}", "cn")
        bao("cn")

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
    else:
        a, b = st.columns(2)
        ngay_xem = a.date_input("Ngày", date(2026, 7, 16))
        gio_xem = b.selectbox("Giờ", list(range(7, 22)), index=12, format_func=lambda h: f"{h:02d}:00")
        df = bang("sp_BC_PhongTaiThoiDiem", cn, datetime.combine(ngay_xem, time(gio_xem)))
    st.caption(f"{len(df)} dòng")
    st.dataframe(df, use_container_width=True, height=520, hide_index=True)
