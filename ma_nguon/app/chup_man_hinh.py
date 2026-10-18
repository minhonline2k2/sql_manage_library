"""Kiểm thử giao diện bằng Playwright: mở từng chức năng, thực hiện các thao tác thêm/sửa/xóa/mượn/trả,
ghi lại thông báo của hệ thống và chụp màn hình cho báo cáo.
Chạy trên CSDL vừa dựng: python3 chup_man_hinh.py <thư mục ảnh>   (Streamlit đang chạy ở cổng 8501)"""
import sys, time, json, datetime
import pymysql
from playwright.sync_api import sync_playwright

URL, OUT = "http://localhost:8501", sys.argv[1]
HOM_NAY = datetime.date.today().isoformat()
cn = pymysql.connect(unix_socket="/run/mysqld/mysqld.sock", user="root", database="QLTV", charset="utf8mb4", autocommit=True)
def q1(sql):
    with cn.cursor() as c: c.execute(sql); return c.fetchone()
# dữ liệu cho các thao tác (CN01)
dg_sach = q1(f"""SELECT d.MaNguoi FROM DOC_GIA d JOIN THE_DOC_GIA t ON t.MaDocGia=d.MaNguoi WHERE d.MaChiNhanh='CN01'
  AND t.NgayHetHan > '{HOM_NAY}' AND fn_NoPhat(d.MaNguoi)=0 AND fn_SoSachDangMuon(d.MaNguoi)=0 ORDER BY d.MaNguoi LIMIT 1""")[0]
cuon_muon = [r[0] for r in [q1(f"""SELECT cs.MaCuonSach FROM CUON_SACH cs JOIN GIA_SACH g USING(MaGia) WHERE g.MaPhongKho LIKE 'CN01%'
  AND cs.TrangThai='TrenGia' AND cs.TuoiThoConLaiThang>2 ORDER BY cs.MaCuonSach LIMIT {i},1""") for i in range(3)]]
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
    def go(nhan, gia_tri, i=0): o = p.get_by_label(nhan, exact=True).nth(i); o.fill(str(gia_tri)); o.press("Tab"); p.keyboard.press("Escape"); time.sleep(0.4)   # Escape: đóng lịch của date_input tự mở khi nhận focus (Streamlit ≥ 1.5x)
    def bam(ten, mong_doi="success"):
        p.get_by_role("button", name=ten, exact=True).click(); doi(p)
        al = p.locator('[data-testid="stAlert"]').last
        txt = al.inner_text() if al.count() else "(không có thông báo)"
        loai = "success" if al.count() and al.locator('[data-testid="stAlertContentSuccess"]').count() else "error"
        ket_qua.append((ten, mong_doi, loai, txt.strip().replace("\n", " ")))
        print(f"[{'PASS' if loai == mong_doi else 'FAIL'}] {ten}: {txt.strip()[:90]}")
    def chup(ten): p.screenshot(path=f"{OUT}/{ten}.png", full_page=True)

    # 1. Mượn sách: thành công, rồi bị chặn khi quá 10 cuốn
    mo(0); chup("01_muon_sach")
    go("Mã độc giả", dg_sach); go("Mã cuốn sách (tối đa 10, cách nhau bởi dấu phẩy)", ",".join(cuon_muon))
    bam("Lập phiếu mượn"); chup("02a_muon_thanh_cong")
    go("Mã cuốn sách (tối đa 10, cách nhau bởi dấu phẩy)", ",".join(f"TR0001-00{i}" for i in range(1, 10)) + ",TR0002-001,TR0002-002")
    bam("Lập phiếu mượn", "error"); chup("02_muon_qua_10_cuon")
    # 2. Trả sách quá hạn → phát sinh phạt, rồi thanh toán
    mo(1); go("Mã độc giả", dg_tre); doi(p, 1.5); chup("03_tra_sach")
    go("Mã cuốn trả (1 hoặc nhiều)", cuon_tre); bam("Lập phiếu trả"); chup("03a_tra_co_phat")
    bam("Thanh toán toàn bộ phạt"); chup("03b_thanh_toan_phat")
    # 3. Phòng đọc: đặt phòng, quản lý phòng (thêm, sửa, xóa)
    mo(2); chup("04_thue_phong")
    tab("Quản lý phòng đọc"); go("Mã phòng (vd CN01-N6)", "CN01-N6"); go("Tên phòng", "Phòng nhóm 6"); go("Sức chứa", 8)
    bam("Thêm phòng"); chup("04a_them_phong_doc"); go("Sức chứa", 10); bam("Sửa tên / sức chứa"); bam("Xóa phòng")
    # 4. Độc giả: đăng ký, sửa, xóa
    mo(3); chup("05_doc_gia")
    tab("Đăng ký mới")
    for k, v in [("Họ", "Trần"), ("Đệm", "Bảo"), ("Tên", "Ngọc"), ("Email", "baongoc.demo@gmail.com"), ("Số nhà", "12"), ("Phường", "Dịch Vọng"), ("Quận", "Cầu Giấy"),
                 ("Số điện thoại (nhiều số cách bởi dấu phẩy)", "0987654321, 0912345670")]: go(k, v)
    bam("Đăng ký"); chup("05a_dang_ky_doc_gia")
    ma_moi = q1("SELECT MAX(MaNguoi) FROM DOC_GIA")[0]
    tab("Sửa / gia hạn / xóa"); go("Mã độc giả cần thao tác", ma_moi); go("Email mới (để trống nếu giữ nguyên)", "ngoc.moi@gmail.com")
    bam("Lưu sửa"); bam("Gia hạn thẻ 1 năm"); bam("Xóa độc giả"); go("Mã độc giả cần thao tác", "DG0001"); bam("Xóa độc giả", "error"); chup("05b_xoa_doc_gia_bi_chan")
    # 5. Sách & kho: phòng kho, giá sách, xóa cuốn
    mo(4); chup("06_sach_kho")
    tab("Phòng kho"); go("Mã phòng kho (vd CN01-K3)", "CN01-K3"); go("Tên phòng kho", "Kho tầng 3"); go("Tầng", 3)
    bam("Thêm phòng kho"); chup("06a_them_phong_kho")
    mo(4); tab("Giá sách"); go("Mã giá (vd CN01-K1-TR9)", "CN01-K1-TR9"); bam("Thêm giá"); chup("06b_them_gia_sach")
    go("Sức chứa (≤ 100)", 80); bam("Sửa sức chứa"); bam("Xóa giá")
    mo(4); tab("Phòng kho"); go("Mã phòng kho (vd CN01-K3)", "CN01-K3"); bam("Xóa phòng kho")
    mo(4); tab("Cuốn sách"); go("Mã cuốn chuyển giá", cuon_xoa); bam("Xóa cuốn sách")
    go("Mã cuốn chuyển giá", cuon_muon[0]); bam("Xóa cuốn sách", "error"); chup("06c_xoa_cuon_bi_chan")
    # 6. Thủ thư: thêm, sửa, xóa
    mo(5); chup("07_thu_thu")
    tab("Thêm / sửa / xóa thủ thư")
    for k, v in [("Họ", "Lê"), ("Đệm", "Minh"), ("Tên", "Châu"), ("Email", "chau.tt@gmail.com"), ("Số điện thoại", "0977111222")]: go(k, v)
    bam("Thêm thủ thư"); chup("07a_them_thu_thu")
    ma_tt = q1("SELECT MAX(MaNguoi) FROM THU_THU")[0]
    go("Mã thủ thư", ma_tt); go("Email mới", "chau.moi@gmail.com"); bam("Lưu sửa thủ thư"); bam("Xóa thủ thư")
    go("Mã thủ thư", "TT001"); bam("Xóa thủ thư", "error"); chup("07b_xoa_truong_bi_chan")
    # 7. Báo cáo 1–6
    for i in range(1, 7):
        p.goto(f"{URL}/?trang=6&bc={i}"); doi(p, 4)
        p.screenshot(path=f"{OUT}/1{i}_bao_cao_{i}.png")
    p.goto(f"{URL}/?trang=6&bc=1"); doi(p, 4); p.get_by_text("Chỉ sách đang được mượn (chưa trả)").click(); doi(p, 3)
    p.screenshot(path=f"{OUT}/11b_bao_cao_1_ca_da_tra.png")
    b.close()
json.dump(ket_qua, open(f"{OUT}/ket_qua_giao_dien.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("PASS", sum(1 for r in ket_qua if r[1] == r[2]), "/", len(ket_qua))
