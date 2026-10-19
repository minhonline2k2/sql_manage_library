"""Kiểm thử giao diện bằng Playwright: mở từng chức năng, thực hiện các thao tác thêm/sửa/xóa/mượn/trả,
ghi lại thông báo của hệ thống và chụp màn hình cho báo cáo.
Chạy trên CSDL vừa dựng: python3 chup_man_hinh.py <thư mục ảnh>   (Streamlit đang chạy ở cổng 8501)"""
import sys, re, time, json, datetime
import pymysql
from playwright.sync_api import sync_playwright

URL, OUT = "http://localhost:8501", sys.argv[1]
HOM_NAY = datetime.date.today().isoformat()
cn = pymysql.connect(unix_socket="/run/mysqld/mysqld.sock", user="root", database="QLTV", charset="utf8mb4", autocommit=True)
def q1(sql):
    with cn.cursor() as c: c.execute(sql); return c.fetchone()
def vi_tri(sql, ma):
    """Thứ tự hàng của `ma` trong kết quả procedure (giống thứ tự bảng trên giao diện)."""
    with cn.cursor() as c: c.execute(sql); return [r[0] for r in c.fetchall()].index(ma)
# dữ liệu cho các thao tác (CN01)
dg_sach = q1(f"""SELECT d.MaNguoi FROM DOC_GIA d JOIN THE_DOC_GIA t ON t.MaDocGia=d.MaNguoi WHERE d.MaChiNhanh='CN01'
  AND t.NgayHetHan > '{HOM_NAY}' AND fn_NoPhat(d.MaNguoi)=0 AND fn_SoSachDangMuon(d.MaNguoi)=0 ORDER BY d.MaNguoi LIMIT 1""")[0]
tren_gia = [r[0] for r in [q1(f"""SELECT cs.MaCuonSach FROM CUON_SACH cs JOIN GIA_SACH g USING(MaGia) WHERE g.MaPhongKho LIKE 'CN01%'
  AND cs.TrangThai='TrenGia' AND cs.TuoiThoConLaiThang>2 ORDER BY cs.MaCuonSach LIMIT {i},1""") for i in range(14)]]
cuon_muon, cuon_qua_10 = tren_gia[:3], tren_gia[3:14]
dg_tre, cuon_tre = q1("""SELECT pm.MaDocGia, ct.MaCuonSach FROM CT_MUON ct JOIN PHIEU_MUON pm USING(MaPhieuMuon) JOIN DOC_GIA d ON d.MaNguoi=pm.MaDocGia
  WHERE ct.MaPhieuTra IS NULL AND d.MaChiNhanh='CN01' AND pm.MaDocGia<>'DG0001' ORDER BY ct.HanTra LIMIT 1""")
cuon_xoa = q1("""SELECT cs.MaCuonSach FROM CUON_SACH cs JOIN GIA_SACH g USING(MaGia) WHERE g.MaPhongKho LIKE 'CN01%'
  AND NOT EXISTS (SELECT 1 FROM CT_MUON c WHERE c.MaCuonSach=cs.MaCuonSach) ORDER BY 1 LIMIT 1""")[0]
ket_qua = []

def doi(p, s=2.5):
    time.sleep(s)
    for _ in range(60):
        if not p.locator('[data-testid="stStatusWidget"]').is_visible(): break
        time.sleep(0.25)

with sync_playwright() as pw:
    b = pw.chromium.launch()
    p = b.new_page(viewport={"width": 1500, "height": 950})
    def mo(trang): p.goto(f"{URL}/?trang={trang}"); doi(p, 4)
    def tab(ten): p.get_by_role("tab", name=ten).click(); doi(p, 1)
    def o(nhan): return p.locator('[data-testid="stMain"]').get_by_label(nhan, exact=True).filter(visible=True).first   # bỏ qua menu thanh bên
    def go(nhan, gia_tri): x = o(nhan); x.fill(str(gia_tri)); x.press("Tab"); p.keyboard.press("Escape"); doi(p, 1)
    def chon(nhan, ma):   # danh sách chọn: gõ mã để lọc rồi bấm lựa chọn bắt đầu bằng mã
        o(nhan).click(); p.keyboard.type(ma); time.sleep(0.5)
        p.get_by_role("option", name=re.compile("^" + re.escape(ma))).first.click(); doi(p, 1)
    def chon_nhieu(nhan, ds):
        for ma in ds: chon(nhan, ma)
        p.keyboard.press("Escape"); doi(p, 1)
    def chon_hang(i, bang=0):   # bấm vào ô chữ của hàng thứ i (0-based) → chọn cả hàng
        bb = p.locator('[data-testid="stDataFrame"]').filter(visible=True).nth(bang).bounding_box()
        p.mouse.click(bb["x"] + 250, bb["y"] + 35 * (i + 1) + 17); doi(p, 1.5)
    def bam(ten, mong_doi="success"):
        p.get_by_role("button", name=ten, exact=True).click(); doi(p)
        al = p.locator('[data-testid="stAlert"]').filter(
            has=p.locator('[data-testid="stAlertContentSuccess"], [data-testid="stAlertContentError"]')).last
        txt = al.inner_text() if al.count() else "(không có thông báo)"
        loai = "success" if al.count() and al.locator('[data-testid="stAlertContentSuccess"]').count() else "error"
        ket_qua.append((ten, mong_doi, loai, txt.strip().replace("\n", " ")))
        print(f"[{'PASS' if loai == mong_doi else 'FAIL'}] {ten}: {txt.strip()[:90]}")
    def chup(ten): p.screenshot(path=f"{OUT}/{ten}.png", full_page=True)

    # 1. Mượn sách: chọn độc giả và các cuốn từ danh sách; thành công, rồi bị chặn khi quá 10 cuốn
    mo(0); chup("01_muon_sach")
    chon("Độc giả", dg_sach); chon_nhieu("Cuốn sách (tối đa 10)", cuon_muon)
    bam("Lập phiếu mượn"); chup("02a_muon_thanh_cong")
    chon_nhieu("Cuốn sách (tối đa 10)", cuon_qua_10)
    bam("Lập phiếu mượn", "error"); chup("02_muon_qua_10_cuon")
    # 2. Trả sách quá hạn → phát sinh phạt, rồi thanh toán
    mo(1); chon("Độc giả", dg_tre); chup("03_tra_sach")
    chon_nhieu("Cuốn trả (1 hoặc nhiều)", [cuon_tre]); bam("Lập phiếu trả"); chup("03a_tra_co_phat")
    bam("Thanh toán toàn bộ phạt"); chup("03b_thanh_toan_phat")
    # 3. Phòng đọc: báo giá khi chọn phòng; quản lý phòng (thêm, chọn hàng để sửa, xóa)
    mo(2); chon("Độc giả", dg_sach); chon("Phòng", "CN01-N1"); chup("04_thue_phong")
    tab("Quản lý phòng đọc"); go("Mã phòng (vd CN01-N6)", "CN01-N6"); go("Tên phòng mới", "Phòng nhóm 6"); go("Sức chứa phòng mới", 8)
    bam("Thêm phòng"); chup("04a_them_phong_doc")
    i = vi_tri("CALL sp_PhongDoc_TimKiem('CN01', NULL, NULL)", "CN01-N6")
    chon_hang(i); go("Sức chứa", 10); bam("Sửa tên / sức chứa")
    chon_hang(i); bam("Xóa phòng")
    # 4. Độc giả: đăng ký, chọn hàng để sửa / gia hạn / xóa
    mo(3); chup("05_doc_gia")
    tab("Đăng ký mới")
    for k, v in [("Họ", "Trần"), ("Đệm", "Bảo"), ("Tên", "Ngọc"), ("Email", "baongoc.demo@gmail.com"), ("Số nhà", "12"), ("Phường", "Dịch Vọng"), ("Quận", "Cầu Giấy"),
                 ("Số điện thoại (nhiều số cách bởi dấu phẩy)", "0987654321, 0912345670")]: go(k, v)
    bam("Đăng ký"); chup("05a_dang_ky_doc_gia")
    ma_moi = q1("SELECT MAX(MaNguoi) FROM DOC_GIA")[0]
    tab("Danh sách / sửa / xóa"); go("Lọc theo mã, số thẻ, tên hoặc SĐT", ma_moi)
    chon_hang(0); go("Email", "ngoc.moi@gmail.com"); bam("Lưu sửa")
    chon_hang(0); bam("Gia hạn thẻ 1 năm")
    chon_hang(0); bam("Xóa độc giả")
    go("Lọc theo mã, số thẻ, tên hoặc SĐT", "DG0001"); chon_hang(0); bam("Xóa độc giả", "error"); chup("05b_xoa_doc_gia_bi_chan")
    # 5. Sách & kho: phòng kho, giá sách, xóa cuốn (chọn hàng trong bảng)
    mo(4); chup("06_sach_kho")
    tab("Phòng kho"); go("Mã phòng kho (vd CN01-K3)", "CN01-K3"); go("Tên phòng kho mới", "Kho tầng 3"); go("Tầng của phòng mới", 3)
    bam("Thêm phòng kho"); chup("06a_them_phong_kho")
    mo(4); tab("Giá sách"); go("Mã giá (vd CN01-K1-TR9)", "CN01-K1-TR9"); bam("Thêm giá"); chup("06b_them_gia_sach")
    i = vi_tri("CALL sp_GiaSach_TimKiem('CN01', NULL)", "CN01-K1-TR9")
    chon_hang(i); go("Sức chứa (≤ 100)", 80); bam("Sửa sức chứa")
    chon_hang(i); bam("Xóa giá")
    mo(4); tab("Phòng kho"); chon_hang(vi_tri("CALL sp_PhongKho_TimKiem('CN01')", "CN01-K3")); bam("Xóa phòng kho")
    mo(4); tab("Cuốn sách"); go("Lọc theo mã cuốn / tên sách", cuon_xoa); chon_hang(0); bam("Xóa cuốn sách")
    go("Lọc theo mã cuốn / tên sách", cuon_muon[0]); chon_hang(0); bam("Xóa cuốn sách", "error"); chup("06c_xoa_cuon_bi_chan")
    # 6. Thủ thư: thêm, chọn hàng để sửa, xóa
    mo(5); chup("07_thu_thu")
    tab("Thêm thủ thư")
    for k, v in [("Họ", "Lê"), ("Đệm", "Minh"), ("Tên", "Châu"), ("Email", "chau.tt@gmail.com"), ("Số điện thoại", "0977111222")]: go(k, v)
    bam("Thêm thủ thư"); chup("07a_them_thu_thu")
    ma_tt = q1("SELECT MAX(MaNguoi) FROM THU_THU")[0]
    tab("Danh sách / sửa / xóa"); go("Lọc theo mã hoặc tên thủ thư", ma_tt)
    chon_hang(0); go("Email mới", "chau.moi@gmail.com"); bam("Lưu sửa thủ thư")
    chon_hang(0); bam("Xóa thủ thư")
    go("Lọc theo mã hoặc tên thủ thư", "TT001"); chon_hang(0); bam("Xóa thủ thư", "error"); chup("07b_xoa_truong_bi_chan")
    # 7. Báo cáo 1–6
    for i in range(1, 7):
        p.goto(f"{URL}/?trang=6&bc={i}"); doi(p, 4)
        p.screenshot(path=f"{OUT}/1{i}_bao_cao_{i}.png")
    p.goto(f"{URL}/?trang=6&bc=1"); doi(p, 4); p.get_by_text("Chỉ sách đang được mượn (chưa trả)").click(); doi(p, 3)
    p.screenshot(path=f"{OUT}/11b_bao_cao_1_ca_da_tra.png")
    b.close()
json.dump(ket_qua, open(f"{OUT}/ket_qua_giao_dien.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("PASS", sum(1 for r in ket_qua if r[1] == r[2]), "/", len(ket_qua))
