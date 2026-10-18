"""Sinh 05_seed.sql: dữ liệu thư viện vận hành 01/07/2026 – 30/09/2026.

Phần A: dữ liệu danh mục (INSERT trực tiếp).
Phần B: nhập sách bằng TX4, đăng ký độc giả bằng TX6.
Phần C: mô phỏng từng ngày, sinh lời gọi TX1 (mượn), TX2 (trả), TX3 (nộp phạt),
        gia hạn thẻ, TX7 (thuê phòng), TX5 (thanh lý) theo đúng thứ tự thời gian,
        để mọi trigger chạy thật và dữ liệu luôn hợp lệ.
Bộ sinh giữ một bản sao trạng thái (sách trên giá, sách độc giả đang giữ, nợ phạt, lịch phòng)
để chỉ phát sinh những lời gọi hợp lệ. Hạt giống ngẫu nhiên cố định → mọi máy sinh dữ liệu giống nhau.
Chạy: python3 gen_seed.py > 05_seed.sql
"""
import random, json, sys
from datetime import date, datetime, timedelta

random.seed(2026)
D0, D1 = date(2026, 7, 1), date(2026, 9, 30)
out = []
w = out.append
q = lambda s: "NULL" if s is None else "'" + str(s).replace("'", "''") + "'"
J = lambda xs: q(json.dumps(xs, ensure_ascii=False))

def months_between(a, b):            # = TIMESTAMPDIFF(MONTH, a, b)
    m = (b.year - a.year) * 12 + (b.month - a.month)
    if b.day < a.day: m -= 1
    return m

w("-- 05_seed.sql – sinh tự động bởi gen_seed.py (random.seed(2026)). Không sửa tay.")
w("USE QLTV;\nSET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;\n")

# ------------------------------------------------------------------ A. danh mục
TL = {  # mã: (tên, số ngày mượn, tuổi thọ năm, phạt cơ bản, phạt/ngày, số đầu sách)
 "TR": ("Truyện", 14, 15, 100000, 10000, 70),
 "TK": ("Tài liệu tham khảo", 7, 10, 200000, 30000, 60),
 "GT": ("Giáo trình", 30, 8, 150000, 20000, 50),
 "KH": ("Khoa học phổ thông", 14, 12, 120000, 15000, 50),
 "NV": ("Sách ngoại văn", 21, 12, 200000, 30000, 40),
 "TC": ("Tạp chí", 7, 3, 50000, 5000, 30),
}
w("-- A. Danh mục")
for m, (ten, ngay, tt, cb, mn, _) in TL.items():
    w(f"INSERT INTO THE_LOAI VALUES ({q(m)},{q(ten)},{ngay},{tt});")
for m, (_, _, _, cb, mn, _) in TL.items():
    w(f"INSERT INTO BANG_PHI_PHAT VALUES ({q(m)},'2026-01-01',{cb},{mn});")
# biểu phí mới cho tạp chí từ 01/09/2026 (minh họa thực thể yếu có lịch sử)
w("INSERT INTO BANG_PHI_PHAT VALUES ('TC','2026-09-01',60000,6000);")
w("INSERT INTO LOAI_PHONG VALUES ('NHOM','Học nhóm',50000,1,4),('HOITHAO','Hội thảo',300000,2,8);")

CN = [("CN01", "Chi nhánh Cầu Giấy", "144 Xuân Thủy, Cầu Giấy, Hà Nội"),
      ("CN02", "Chi nhánh Hà Đông", "96A Trần Phú, Hà Đông, Hà Nội"),
      ("CN03", "Chi nhánh Hoàn Kiếm", "35 Tràng Tiền, Hoàn Kiếm, Hà Nội")]
for m, t, d in CN:
    w(f"INSERT INTO CHI_NHANH(MaChiNhanh,TenChiNhanh,DiaChi) VALUES ({q(m)},{q(t)},{q(d)});")

HO = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ", "Đặng", "Bùi", "Đỗ", "Hồ", "Ngô", "Dương", "Lý"]
DEM_M = ["Văn", "Đức", "Minh", "Quang", "Hữu", "Thành", "Công", "Tuấn", "Gia", "Anh"]
DEM_F = ["Thị", "Ngọc", "Thu", "Thanh", "Minh", "Phương", "Hồng", "Mai", "Khánh", "Bảo"]
TEN_M = ["An", "Bình", "Cường", "Dũng", "Đạt", "Hải", "Hiếu", "Hoàng", "Hùng", "Khánh", "Long", "Minh", "Nam", "Phong", "Quân", "Sơn", "Thắng", "Trung", "Tùng", "Việt"]
TEN_F = ["Anh", "Chi", "Dung", "Giang", "Hà", "Hạnh", "Hoa", "Hương", "Lan", "Linh", "Mai", "My", "Ngân", "Nhung", "Phương", "Quỳnh", "Thảo", "Trang", "Uyên", "Yến"]
QUAN = {"CN01": [("Dịch Vọng", "Cầu Giấy"), ("Quan Hoa", "Cầu Giấy"), ("Mai Dịch", "Cầu Giấy"), ("Nghĩa Đô", "Cầu Giấy"), ("Mỹ Đình 1", "Nam Từ Liêm")],
        "CN02": [("Mộ Lao", "Hà Đông"), ("Văn Quán", "Hà Đông"), ("Hà Cầu", "Hà Đông"), ("Kiến Hưng", "Hà Đông"), ("Thanh Xuân Bắc", "Thanh Xuân")],
        "CN03": [("Tràng Tiền", "Hoàn Kiếm"), ("Hàng Bài", "Hoàn Kiếm"), ("Lý Thái Tổ", "Hoàn Kiếm"), ("Phan Chu Trinh", "Hoàn Kiếm"), ("Bách Khoa", "Hai Bà Trưng")]}
used_email, used_sdt = set(), set()

def nguoi_ngau_nhien(tuoi_min, tuoi_max):
    gt = random.choice("MF")
    ho = random.choice(HO); dem = random.choice(DEM_M if gt == "M" else DEM_F); ten = random.choice(TEN_M if gt == "M" else TEN_F)
    ns = date(2026 - random.randint(tuoi_min, tuoi_max), random.randint(1, 12), random.randint(1, 28))
    base = "".join(c for c in (ten + ho).lower() if c.isascii() and c.isalpha()) or "user"
    k = 1
    while f"{base}{k}@gmail.com" in used_email: k += 1
    used_email.add(f"{base}{k}@gmail.com")
    def sdt():
        while True:
            s = "0" + random.choice("389") + "".join(random.choice("0123456789") for _ in range(8))
            if s not in used_sdt: used_sdt.add(s); return s
    return gt, ho, dem, ten, ns, f"{base}{k}@gmail.com", sdt

# thủ thư: 5 người mỗi chi nhánh, người đầu là trưởng, quản lý 4 người còn lại
TT = {c[0]: [] for c in CN}
n = 0
for cn, _, _ in CN:
    for i in range(5):
        n += 1; ma = f"TT{n:03d}"
        gt, ho, dem, ten, ns, email, sdt = nguoi_ngau_nhien(24, 55)
        ph, qu = random.choice(QUAN[cn])
        w(f"INSERT INTO NGUOI VALUES ({q(ma)},{q(ho)},{q(dem)},{q(ten)},{q(ns)},{q(gt)},'{random.randint(1,200)}',{q(ph)},{q(qu)},'Hà Nội',{q(email)},'TT');")
        w(f"INSERT INTO SDT_NGUOI VALUES ({q(ma)},{q(sdt())});")
        ql = TT[cn][0] if i > 0 else None
        w(f"INSERT INTO THU_THU VALUES ({q(ma)},{q(cn)},'{2015 + i}-0{random.randint(1,9)}-01',{q(ql)});")
        TT[cn].append(ma)
    w(f"UPDATE CHI_NHANH SET MaThuThuTruong = {q(TT[cn][0])} WHERE MaChiNhanh = {q(cn)};")

KHO_CUA = {"TR": "K1", "TK": "K1", "GT": "K1", "KH": "K2", "NV": "K2", "TC": "K2"}
for cn, _, _ in CN:
    w(f"INSERT INTO PHONG_KHO VALUES ('{cn}-K1','{cn}','Kho tầng 1',1),('{cn}-K2','{cn}','Kho tầng 2',2);")

# phòng đọc: 5 phòng nhóm, 2 hội thảo mỗi chi nhánh
PHONG = []
for cn, _, _ in CN:
    for i in range(1, 6):
        sc = random.choice([6, 8, 10]); PHONG.append((f"{cn}-N{i}", cn, "NHOM", sc))
        w(f"INSERT INTO PHONG_DOC VALUES ('{cn}-N{i}','{cn}','NHOM','Phòng nhóm {i}',{sc});")
    for i in range(1, 3):
        sc = random.choice([30, 60]); PHONG.append((f"{cn}-H{i}", cn, "HOITHAO", sc))
        w(f"INSERT INTO PHONG_DOC VALUES ('{cn}-H{i}','{cn}','HOITHAO','Hội trường {i}',{sc});")

# ------------------------------------------------------------------ B. sách (TX4)
CHU = {"TR": (["Bí mật", "Hành trình", "Ký ức", "Giấc mơ", "Chuyện", "Mùa hè", "Dòng sông", "Ngọn đèn", "Cánh đồng", "Thành phố"],
              ["của biển", "phương Nam", "tuổi thơ", "không ngủ", "bên kia núi", "xanh", "cuối cùng", "lặng im", "mùa thu", "đầy sao"]),
       "TK": (["Cẩm nang", "Từ điển", "Sổ tay", "Tra cứu", "Hướng dẫn", "Bách khoa", "Tổng quan", "Chuyên khảo"],
              ["luật doanh nghiệp", "kế toán", "y học gia đình", "tiếng Anh thương mại", "lịch sử Việt Nam", "địa lý", "kỹ thuật điện", "pháp luật đất đai", "thuế", "kinh tế học"]),
       "GT": (["Giáo trình", "Bài giảng", "Nhập môn"], ["Cơ sở dữ liệu", "Toán cao cấp", "Kinh tế vi mô", "Mạng máy tính", "Lập trình C", "Xác suất thống kê", "Hệ điều hành", "Triết học", "Vật lý đại cương", "Kế toán tài chính", "An toàn thông tin", "Trí tuệ nhân tạo"]),
       "KH": (["Khám phá", "Thế giới", "Bí ẩn", "Câu chuyện", "Vì sao"], ["vũ trụ", "đại dương", "cơ thể người", "khủng long", "khí hậu", "côn trùng", "ánh sáng", "trí não", "rừng mưa", "núi lửa"]),
       "NV": (["The", "A", "Modern", "Essential", "Advanced"], ["Database Systems", "History of Asia", "English Grammar", "Data Science", "Economics", "Network Security", "Software Design", "Marketing", "Statistics", "Philosophy"]),
       "TC": (["Tạp chí"], ["Tia Sáng", "Khoa học & Đời sống", "Kiến trúc", "Văn nghệ quân đội", "Tri thức trẻ", "Kinh tế & Dự báo", "Tin học & Đời sống", "Du lịch"])}
NXB = ["NXB Trẻ", "NXB Kim Đồng", "NXB Giáo dục Việt Nam", "NXB Khoa học và Kỹ thuật", "NXB Thông tin và Truyền thông", "NXB Tổng hợp TP.HCM", "Pearson", "O'Reilly", "NXB Lao động"]
TACGIA = ["Nguyễn Nhật Ánh", "Tô Hoài", "Nam Cao", "Nguyễn Huy Thiệp", "Bảo Ninh", "Phan Thị Hà", "Hà Hải Nam", "Trần Đình Quế", "Lê Văn Phùng",
          "Ngô Bảo Châu", "Đặng Thái Sơn", "Hector Garcia-Molina", "Jeffrey D. Ullman", "Jennifer Widom", "M. Tamer Özsu", "Patrick Valduriez",
          "Andrew Tanenbaum", "Ross Anderson", "Nguyễn Văn Tuấn", "Vũ Trọng Phụng", "Xuân Diệu", "Nguyễn Tuân", "Phạm Văn Ất", "Trịnh Minh Hà",
          "Lê Thị Mai", "Hoàng Văn Bình", "Đỗ Thu Hằng", "Ban biên tập"]

DAU = {}      # mã -> dict(theloai, ngay_rieng)
CUON = {}     # mã cuốn -> dict(dau, cn, tuoitho, trangthai)
w("\n-- B. Nhập sách bằng TX4 (sp_NhapLoSach)")
gia_cn = {}   # (cn, tl) -> list[[ma, count]]
lenh_tx4 = []
for tl, (_, _, ttn, _, _, so_dau) in TL.items():
    names = set()
    for k in range(1, so_dau + 1):
        ma = f"{tl}{k:04d}"
        a, b = CHU[tl]
        while True:
            ten = f"{random.choice(a)} {random.choice(b)}" + (f" (tập {random.randint(1,3)})" if tl in ("TR", "GT") and random.random() < .2 else "")
            if tl == "TC": ten += f" số {random.randint(1, 12)}/{random.choice([2024, 2025, 2026])}"
            if ten not in names: names.add(ten); break
        nam = random.randint(2008, 2026)
        rieng = random.choice([3, 5, 7]) if random.random() < .1 else None
        DAU[ma] = dict(tl=tl, rieng=rieng, ten=ten)
        tg = random.sample(TACGIA, 1 if random.random() < .7 else 2) if tl != "TC" else ["Ban biên tập"]
        tong = random.randint(3, 8)
        phan = [0, 0, 0]
        for _ in range(tong): phan[random.randrange(3)] += 1
        dau_tien = True
        for ci, (cn, _, _) in enumerate(CN):
            if phan[ci] == 0: continue
            lst = gia_cn.setdefault((cn, tl), [])
            if not lst or lst[-1][1] + phan[ci] > 90:
                lst.append([f"{cn}-{KHO_CUA[tl]}-{tl}{len(lst)+1}", 0])
            g = lst[-1]; g[1] += phan[ci]
            nhap = date(max(nam, 2014), 1, 1) + timedelta(days=random.randint(0, 3000))
            if nhap > date(2026, 6, 25): nhap = date(2026, 6, random.randint(1, 25))
            lenh_tx4.append((nhap, f"CALL sp_NhapLoSach({q(ma)},{q(ten)},{q(random.choice(NXB))},{nam},{rieng if rieng else 'NULL'},{J(tg) if dau_tien else 'NULL'},{phan[ci]},{q(g[0])},{q(nhap)},@sl);",
                              ma, cn, phan[ci], ttn))
            dau_tien = False
for (cn, tl), lst in gia_cn.items():
    for g, _ in lst:
        w(f"INSERT INTO GIA_SACH(MaGia,MaPhongKho,MaTheLoai,SucChua) VALUES ({q(g)},'{cn}-{KHO_CUA[tl]}',{q(tl)},100);")
stt = {}
for nhap, sql, ma, cn, sl, ttn in lenh_tx4:     # thứ tự giữ nguyên để lần nhập đầu tạo đầu sách
    w(sql)
    for _ in range(sl):
        stt[ma] = stt.get(ma, 0) + 1
        con = max(ttn * 12 - months_between(nhap, D0), 0)
        CUON[f"{ma}-{stt[ma]:03d}"] = dict(dau=ma, cn=cn, tt=con, st="TrenGia" if con > 0 else "ChoThanhLy")
# số dư tuổi thọ đầu kỳ: phần tuổi thọ đã dùng trước 01/07/2026
w("-- Tuổi thọ tồn đầu kỳ (01/07/2026) = tuổi thọ thể loại − số tháng đã sử dụng kể từ ngày nhập")
w("UPDATE CUON_SACH cs JOIN THE_LOAI tl ON tl.MaTheLoai = LEFT(cs.MaDauSach,2) "
  "SET cs.TuoiThoConLaiThang = GREATEST(tl.TuoiThoNam*12 - TIMESTAMPDIFF(MONTH, cs.NgayNhap, '2026-07-01'), 0);")

# ------------------------------------------------------------------ độc giả (TX6)
w("\n-- Độc giả đăng ký bằng TX6 (sp_DangKyDocGia); một phần đăng ký trong kỳ")
DG = {}   # ma -> dict(cn, het_han, giu: set, no: float)
dk_trong_ky = []
ngay_trong_ky = sorted(D0 + timedelta(days=random.randint(0, 80)) for _ in range(30))   # mã DB sinh theo thứ tự đăng ký
for k in range(1, 201):
    ma = f"DG{k:04d}"
    cn = CN[(k - 1) % 3][0] if k > 1 else "CN01"
    gt, ho, dem, ten, ns, email, sdt = nguoi_ngau_nhien(16, 65)
    ph, qu = random.choice(QUAN[cn])
    dsdt = [sdt()] + ([sdt()] if random.random() < .3 else [])
    if k == 1: ngay = date(2026, 6, 1)
    elif k <= 170: ngay = date(2025, 6, 1) + timedelta(days=random.randint(0, 390))
    else: ngay = ngay_trong_ky[k - 171]
    rec = dict(cn=cn, het=date(ngay.year + 1, ngay.month, ngay.day), giu={}, no=0, dk=ngay,
               sql=f"CALL sp_DangKyDocGia({q(ho)},{q(dem)},{q(ten)},{q(ns)},{q(gt)},'{random.randint(1,300)}',{q(ph)},{q(qu)},'Hà Nội',{q(email)},{J(dsdt)},{q(cn)},{q(ngay)},@ma,@the);")
    DG[ma] = rec
    if ngay < D0: w(rec["sql"])
    else: dk_trong_ky.append(ma)

# ------------------------------------------------------------------ C. mô phỏng
w("\n-- C. Mô phỏng vận hành từng ngày 01/07/2026 – 30/09/2026")
def han_tra(cuon, ngay):
    d = DAU[CUON[cuon]["dau"]]
    return ngay + timedelta(days=d["rieng"] or TL[d["tl"]][1])

lich_tra = {}     # ngày -> {dg: [cuon]}
lich_nop = {}     # ngày -> set(dg)
lich_phong = {p[0]: [] for p in PHONG}
DAC_BIET = "DG0001"
dem = dict(muon=0, cuon=0, tra=0, phat=0, nop=0, thue=0, giahan=0)

for i in range((D1 - D0).days + 1):
    day = D0 + timedelta(days=i)
    w(f"-- {day}")
    for ma in dk_trong_ky:
        if DG[ma]["dk"] == day: w(DG[ma]["sql"])
    # 1. trả sách
    for dg, ds in sorted(lich_tra.pop(day, {}).items()):
        ds = [c for c in ds if c in DG[dg]["giu"]]
        if not ds: continue
        tt = random.choice(TT[DG[dg]["cn"]])
        w(f"CALL sp_TraSach({q(dg)},{q(tt)},{J(ds)},{q(day)},@pt,@phat);")
        dem["tra"] += 1
        tre = False
        for c in ds:
            han = DG[dg]["giu"].pop(c)
            if day > han:
                tre = True; dem["phat"] += 1
            if CUON[c]["tt"] == 0: CUON[c]["st"] = "ChoThanhLy"
            else: CUON[c]["st"] = "TrenGia"
        if tre:
            DG[dg]["no"] = 1
            if random.random() < .75:
                lich_nop.setdefault(day + timedelta(days=random.randint(0, 10)), set()).add(dg)
    # 2. nộp phạt
    for dg in sorted(lich_nop.pop(day, set())):
        if DG[dg]["no"]:
            w(f"CALL sp_ThanhToanPhat({q(dg)},{q(day)},@tien);"); DG[dg]["no"] = 0; dem["nop"] += 1
    # 3. thanh lý giữa kỳ
    if day == date(2026, 9, 15):
        w("CALL sp_ThanhLySach('2026-09-15',@sotl);")
        # chỉ cuốn không còn nợ phạt bị thanh lý; trong mô phỏng phạt gắn với độc giả,
        # nên cuốn ChoThanhLy có độc giả cuối còn nợ được giữ lại → dùng cờ no_cuon
        for c in [c for c, v in CUON.items() if v["st"] == "ChoThanhLy" and not v.get("no")]:
            CUON[c]["st"] = "DaThanhLy"
    # 4. mượn sách
    if day == date(2026, 9, 3):        # độc giả đặc biệt mượn đủ 50 cuốn (5 phiếu × 10)
        for _ in range(5):
            cs = [c for c, v in CUON.items() if v["cn"] == "CN01" and v["st"] == "TrenGia" and v["tt"] > 1][:10]
            w(f"CALL sp_MuonSach({q(DAC_BIET)},{q(TT['CN01'][1])},{J(cs)},{q(day)},@pm);")
            for c in cs:
                CUON[c]["st"] = "DangMuon"; CUON[c]["tt"] -= 1; DG[DAC_BIET]["giu"][c] = han_tra(c, day)
            dem["muon"] += 1; dem["cuon"] += 10
    so_phieu = random.randint(7, 14) if day.weekday() < 5 else random.randint(4, 7)
    ung_vien = [m for m, v in DG.items() if m != DAC_BIET and v["dk"] <= day]
    for _ in range(so_phieu):
        dg = random.choice(ung_vien); v = DG[dg]
        if v["het"] < day:
            if random.random() < .85:
                v["het"] = date(max(v["het"], day).year + 1, max(v["het"], day).month, min(max(v["het"], day).day, 28))
                w(f"CALL sp_DocGia_GiaHanThe({q(dg)},{q(day)});"); dem["giahan"] += 1
            else:
                continue
        con = 50 - len(v["giu"])
        sl = min(random.choices([1, 2, 3, 4, 5, 10], [30, 28, 20, 10, 8, 4])[0], con)
        san = [c for c, x in CUON.items() if x["cn"] == v["cn"] and x["st"] == "TrenGia"]
        if sl <= 0 or len(san) < sl: continue
        # ưu tiên đầu sách "nổi": 40% đầu sách đầu mỗi thể loại được mượn nhiều hơn
        san.sort(key=lambda c: (int(c[2:6]) > 25) + random.random() * 1.5)
        cs = random.sample(san[:max(sl * 4, 20)], sl)
        tt = random.choice(TT[v["cn"]])
        w(f"CALL sp_MuonSach({q(dg)},{q(tt)},{J(cs)},{q(day)},@pm);")
        dem["muon"] += 1; dem["cuon"] += sl
        for c in cs:
            CUON[c]["st"] = "DangMuon"; CUON[c]["tt"] = max(CUON[c]["tt"] - 1, 0)
            han = han_tra(c, day); v["giu"][c] = han
            r = random.random()
            if r < .72: tra = day + timedelta(days=random.randint(1, (han - day).days))
            elif r < .92: tra = han + timedelta(days=random.randint(1, 20))
            else: tra = None                       # chưa trả đến hết kỳ
            if tra and tra <= D1:
                lich_tra.setdefault(tra, {}).setdefault(dg, []).append(c)
                if tra > han and CUON[c]["tt"] == 0: CUON[c]["no"] = True
    # 5. thuê phòng
    for _ in range(random.randint(0, 4)):
        dg = random.choice(ung_vien); v = DG[dg]
        if v["no"]: continue
        ph, cn, loai, sc = random.choice([p for p in PHONG if p[1] == v["cn"]])
        bd_ngay = day + timedelta(days=random.randint(0, 14))
        if bd_ngay > v["het"]: continue
        gio = random.randint(1, 4) if loai == "NHOM" else random.randint(2, 6)
        h0 = random.randint(7, 21 - gio)
        bd = datetime(bd_ngay.year, bd_ngay.month, bd_ngay.day, h0); kt = bd + timedelta(hours=gio)
        if any(b < kt and e > bd for b, e in lich_phong[ph]): continue
        so_nguoi = random.randint(3, sc) if loai == "NHOM" else random.randint(15, sc)
        lich_phong[ph].append((bd, kt))
        w(f"CALL sp_ThuePhong({q(dg)},{q(ph)},{q(random.choice(TT[cn]))},{q(bd)},{q(kt)},{so_nguoi},{q(day)},@pt,@tien);")
        dem["thue"] += 1

w(f"\n-- Thống kê mô phỏng: {json.dumps(dem)}")
sys.stdout.write("\n".join(out) + "\n")
print(json.dumps(dem), file=sys.stderr)
