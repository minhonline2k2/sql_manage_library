"""Ghép các phần P1, P2, mục 4 (tự động + P7), P8 thành BaoCao.md (nguồn để build_docx.js chuyển sang Word).
Chạy trong thư mục ma_nguon/baocao sau khi có muc4_tudong.md và ảnh trong ../anh, ../erd/erd.png, ../phan_tan/so_do_tong_the.png"""
import re, json
R = lambda p: open(p, encoding="utf-8").read()

def doan(text, bat_dau, ket_thuc=None):
    i = text.index(bat_dau)
    j = text.index(ket_thuc, i) if ket_thuc else len(text)
    return text[i:j].strip() + "\n"

def ha_cap(text, n=1):  # ### -> ## khi n=1
    return re.sub(r"^(#{2,6}) ", lambda m: "#" * max(2, len(m.group(1)) - n) + " ", text, flags=re.M)

def muc(text, cu, moi):  # đổi tiêu đề "## cu" → "## moi"
    assert cu in text, cu
    return text.replace(cu, moi, 1)

TL = "../../tai_lieu/"   # nội dung các chương nằm ở thư mục tài liệu
P1, P2, P7, P8, A = R(TL + "P1_phan_tich_ERD.md"), R(TL + "P2_chuan_hoa.md"), R(TL + "P7_truy_van_toi_uu_bao_mat.md"), R(TL + "P8_phan_tan.md"), R("muc4_tudong.md")
o = []

o.append("""# LỜI MỞ ĐẦU

Trong học phần Các hệ thống cơ sở dữ liệu, nhóm chúng em được giao đề tài "Xây dựng hệ thống quản lý thư viện". Đây là bài toán quen thuộc nhưng có khá nhiều ràng buộc cần xử lý cẩn thận: mỗi giá chỉ chứa sách của một thể loại, mỗi lần mượn không quá 10 cuốn, mỗi độc giả không giữ quá 50 cuốn, tiền phạt và tuổi thọ của sách phụ thuộc vào thể loại, phòng đọc không được cho thuê trùng giờ. Vì vậy nhóm quyết định đặt toàn bộ các luật này ngay trong cơ sở dữ liệu (ràng buộc, trigger, thủ tục lưu trữ) thay vì để giao diện tự kiểm tra. Nhờ đó, dù thao tác qua giao diện hay gõ lệnh SQL trực tiếp, dữ liệu vẫn luôn hợp lệ.

Báo cáo gồm năm chương. Chương 1 phân tích các yêu cầu của đề. Chương 2 trình bày lược đồ thực thể – liên kết. Chương 3 chuyển lược đồ E-R sang lược đồ quan hệ và chuẩn hóa về dạng BCNF. Chương 4 trình bày quá trình cài đặt trên MariaDB, dữ liệu ba tháng vận hành, các truy vấn theo yêu cầu, kết quả kiểm thử và giao diện ứng dụng. Chương 5 phân tích và thiết kế cơ sở dữ liệu phân tán cho ba chi nhánh. Mã nguồn SQL chính được đưa vào phần phụ lục.

Nhóm chúng em xin chân thành cảm ơn cô Phan Thị Hà đã tận tình giảng dạy và hướng dẫn trong suốt học phần. Do thời gian và hiểu biết còn hạn chế, báo cáo khó tránh khỏi thiếu sót; nhóm rất mong nhận được góp ý của cô để bài làm được hoàn thiện hơn.
""")

o.append("# CHƯƠNG 1. PHÂN TÍCH YÊU CẦU\n")
o.append(ha_cap(doan(P1, "### 1.1", "## 2.")))

c2 = ha_cap(doan(P1, "### 2.1"))
c2 = re.sub(r"## 2\.4 Sơ đồ\n\n.*", """## 2.4 Sơ đồ E-R

Lược đồ E-R ở Hình 2.1 được vẽ theo ký hiệu Chen trong bài giảng:

- Tập thực thể là hình chữ nhật, thực thể yếu là hình chữ nhật viền kép; liên kết là hình thoi, liên kết xác định là hình thoi viền kép.
- Thuộc tính là hình ellipse: thuộc tính khóa được gạch chân, khóa bán phần của thực thể yếu có viền xám, thuộc tính dẫn xuất vẽ nét đứt, thuộc tính đa trị có viền kép.
- Tam giác ISA có chữ d thể hiện cụ thể hóa phân tách (disjoint); đường đôi từ NGUOI lên tam giác nghĩa là mọi người đều phải là độc giả hoặc thủ thư.
- Hình thoi nét đứt gom_sach là kết hợp (aggregation). Hình thoi màu cam thue_phong là liên kết 3 ngôi giữa DOC_GIA, PHONG_DOC và THU_THU (thủ thư duyệt), mang các thuộc tính của một lượt thuê.
- Trên mỗi đường nối, nhãn 1, N hoặc M ghi sát thực thể cho biết lực lượng liên kết; đầu thực thể ở phía "nhiều" có thêm ký hiệu chân chim. Đường đôi giữa thực thể và hình thoi nghĩa là thực thể đó tham gia toàn bộ, đường đơn là tham gia một phần.
- Hai giới hạn cụ thể của đề được ghi bằng cặp (min,max): (1,10) cạnh PHIEU_MUON trên gom_sach, tức mỗi phiếu mượn có từ 1 đến 10 cuốn; (0,50) trên nhánh DOC_GIA của giu_sach, tức mỗi độc giả giữ nhiều nhất 50 cuốn.
- Liên kết đệ quy quan_ly ghi tên vai trò "quản lý" và "nhân viên" trên hai nhánh.

![Hình 2.1. Lược đồ E-R của hệ thống quản lý thư viện](../erd/erd_doc.png)
""", c2, flags=re.S)
o.append("# CHƯƠNG 2. LƯỢC ĐỒ THỰC THỂ – LIÊN KẾT\n")
o.append(c2)

o.append("# CHƯƠNG 3. LƯỢC ĐỒ QUAN HỆ VÀ CHUẨN HÓA\n")
o.append(doan(P2, "Ký hiệu:"))
o.append("""## 3.7 Sơ đồ lược đồ quan hệ

Hình 3.1 được vẽ tự động từ `information_schema` của CSDL đã cài đặt (chương trình `gen_tudien.py`), nên luôn khớp với các bảng thật. Mỗi khung là một quan hệ; khóa chính in đậm và gạch chân, khóa ngoại in nghiêng. Mỗi đường nối đi từ cột khóa ngoại tới khóa chính mà nó tham chiếu, hai đầu đường dùng ký hiệu chân chim: phía bảng chứa khóa ngoại là "không hoặc nhiều" (hoặc "không hoặc một" nếu cột khóa ngoại là UNIQUE), phía bảng được tham chiếu là "một và chỉ một" (hoặc "không hoặc một" nếu khóa ngoại được phép NULL). Màu nền dòng tiêu đề chia các bảng thành bốn nhóm: con người (xanh dương), sách và kho (xanh lá), mượn trả (cam), phòng đọc (vàng).

![Hình 3.1. Sơ đồ lược đồ quan hệ với các liên kết khóa chính – khóa ngoại](../erd/luoc_do_quan_he.png)
""")
o.append(R("tu_dien_du_lieu.md"))

c4 = ["# CHƯƠNG 4. CÀI ĐẶT CƠ SỞ DỮ LIỆU VÀ ỨNG DỤNG\n", """## 4.1 Môi trường và quy trình cài đặt

- Hệ quản trị: MariaDB (kiểm thử trên 10.11 LTS, tương thích 11.4 LTS), engine InnoDB, bảng mã `utf8mb4`, collation `utf8mb4_unicode_ci`.
- Giao diện: Python 3 + Streamlit + PyMySQL (chỉ gọi stored procedure / view).
- Mã nguồn chia thành các script chạy theo thứ tự, dựng lại toàn bộ CSDL bằng một lệnh `sh build_all.sh -uroot -p`:

| File | Nội dung |
| --- | --- |
| 01_schema.sql | Tạo database QLTV, 23 bảng và toàn bộ ràng buộc PK, FK, UNIQUE, CHECK, DEFAULT |
| 02_function_procedure.sql | 8 function nghiệp vụ, các procedure thêm/xóa/sửa/tìm kiếm, báo giá thuê phòng, thủ tục và event cập nhật tuổi thọ sách |
| 03_trigger.sql | 8 trigger nghiệp vụ (18 trigger con) |
| 04_transaction.sql | 7 transaction nghiệp vụ dạng procedure |
| 05_seed.sql | Dữ liệu 3 tháng, sinh bởi gen_seed.py bằng cách gọi chính các transaction |
| 06_view_baocao.sql | 6 truy vấn hiển thị theo yêu cầu đề (view + procedure) |
| 07_index_baomat.sql | Chỉ mục tối ưu, vai trò và phân quyền |
| 08_test.sql | 52 ca kiểm thử tự động |
| 09_phan_tan.sql | Minh họa phân mảnh, cấp phát, nhân bản trên 3 site |

Dữ liệu mẫu không nhập tay mà được sinh bằng một chương trình mô phỏng thư viện chạy từng ngày từ 01/07 đến 30/09/2026. Mỗi ngày chương trình phát sinh các lời gọi đăng ký độc giả, mượn sách (TX1), trả sách (TX2), nộp phạt (TX3), gia hạn thẻ, thuê phòng (TX7); giữa kỳ có một đợt thanh lý sách (TX5). Như vậy mọi bản ghi đều đi qua trigger và các bước kiểm tra nghiệp vụ, dữ liệu luôn hợp lệ; hạt giống ngẫu nhiên được cố định nên lần dựng nào cũng cho ra cùng một bộ dữ liệu. Cuối file, thủ tục sp_CapNhatTuoiTho đưa tuổi thọ sách về đúng ngày dựng CSDL; sau đó event ev_CapNhatTuoiTho của MariaDB tự cập nhật mỗi ngày (cần bật event_scheduler).

## 4.2 Một số lưu ý khi cài đặt trên MariaDB

Bài giảng chương 6 minh họa trigger bằng SQL Server; nhóm cài đặt trên MariaDB nên có các điểm tương ứng sau:

| Slide (SQL Server) | Cài đặt trên MariaDB |
| --- | --- |
| Bảng logic `inserted` / `deleted` | Bản ghi `NEW` / `OLD` trong trigger `FOR EACH ROW` |
| `INSTEAD OF`, `ROLLBACK TRANSACTION` trong trigger | Trigger `BEFORE` + `SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Exxx: …'` (hủy câu lệnh, transaction gọi nó sẽ ROLLBACK) |
| `IF UPDATE(cot)` | `IF NEW.cot <> OLD.cot THEN … END IF` |
| `BEGIN TRAN … COMMIT` | `START TRANSACTION … COMMIT` + `DECLARE EXIT HANDLER FOR SQLEXCEPTION BEGIN ROLLBACK; RESIGNAL; END` |
| Tham số bảng (table-valued parameter) | Chuỗi JSON đọc bằng `JSON_TABLE` |
| `WITH (UPDLOCK, HOLDLOCK)` | `SELECT … FOR UPDATE` |
| `DENY` | Không có; chỉ `GRANT` quyền tối thiểu |

Ba giới hạn của MariaDB ảnh hưởng đến thiết kế:
- Ràng buộc CHECK không được dùng cột thuộc khóa ngoại có `ON UPDATE/DELETE CASCADE` hoặc `SET NULL` (lỗi 1901). Các khóa ngoại có CHECK đi kèm vì vậy để mặc định RESTRICT; việc xóa dây chuyền (độc giả, thủ thư) được làm trong procedure.
- Trigger không được sửa chính bảng đã kích hoạt nó (lỗi 1442): thay đổi dòng đang ghi dùng trigger `BEFORE` + `SET NEW.cot`, thay đổi bảng khác dùng trigger `AFTER`; nhiều trigger cùng sự kiện được sắp thứ tự bằng `FOLLOWS`.
- Cột của `JSON_TABLE` mặc định theo collation của kết nối; nhóm khai báo `CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci` cho cột và `SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci` ở đầu mọi script để tránh lỗi trộn collation (1267).
"""]
c4.append(ha_cap(A.split("### 4.9")[0]).replace("## 4.3", "## 4.3").rstrip() + "\n")
c4.append("""## 4.7 Đặc tả trigger và transaction nghiệp vụ

| Mã | Đối tượng | Luật nghiệp vụ | Cách xử lý |
| --- | --- | --- | --- |
| TRG1 | trg_CTMuon_ToiDa10 (CT_MUON, BEFORE INSERT) | Mỗi lần mượn tối đa 10 cuốn | Đếm số cuốn của phiếu, ≥ 10 thì SIGNAL E101 |
| TRG2 | trg_CTMuon_ToiDa50 (CT_MUON, BEFORE INSERT) | Mỗi độc giả giữ tối đa 50 cuốn; chỉ mượn cuốn đang trên giá | fn_SoSachDangMuon ≥ 50 → E102; trạng thái khác TrenGia → E104 |
| TRG3 | trg_CTMuon_KiemTraTra (BEFORE UPDATE), trg_CTMuon_LapPhieuPhat (AFTER UPDATE) | Trả muộn bị phạt theo thể loại | Kiểm tra cùng độc giả (E107), ngày trả ≥ ngày mượn (E105), không sửa dòng đã trả (E106); trả muộn → INSERT PHIEU_PHAT với fn_TinhTienPhat theo biểu phí có hiệu lực |
| TRG4 | trg_CTMuon_Muon, trg_CTMuon_Tra, trg_CuonSach_DemGia_Them/Sua/Xoa | Mượn thì số sách trên giá giảm, trả thì tăng | Mượn/trả đổi trạng thái cuốn; mọi thay đổi trạng thái, vị trí, thêm/xóa cuốn cập nhật GIA_SACH.SoLuongHienCo |
| TRG5 | trg_CTMuon_GiamTuoiTho (AFTER INSERT, FOLLOWS trg_CTMuon_Muon) | Mỗi lần mượn tuổi thọ giảm 1 tháng | TuoiThoConLaiThang − 1 (không âm) |
| TRG6 | trg_CuonSach_DungGia_Them/Sua (CUON_SACH, BEFORE) | Giá chỉ chứa sách cùng thể loại, không vượt sức chứa; sách hết tuổi thọ tách khỏi lưu thông | Sai thể loại → E301; giá đầy (tính cả cuốn đang mượn) → E304; không sửa mã → E305; tuổi thọ = 0 và đang trên giá → SET NEW.TrangThai = 'ChoThanhLy' |
| TRG7 | trg_ThuePhong_KhongTrung_Them/Sua (BEFORE) | Một phòng không có 2 lượt thuê trùng giờ | Tồn tại lượt đã duyệt giao khoảng [BatDau, KetThuc) → E201 |
| TRG8 | trg_DocGia_ChanXoa, trg_DocGia_ChanSuaMa, trg_DocGia_DungLoai, trg_ThuThu_DungLoai | Toàn vẹn độc giả và ISA | Còn giữ sách → E404; còn nợ phạt → E405; sửa mã → E406; bảng con không khớp LoaiNguoi → E407 |
| Tuổi thọ | sp_CapNhatTuoiTho, event ev_CapNhatTuoiTho (chạy mỗi ngày) | Tuổi thọ sách giảm theo thời gian | Tuổi thọ còn lại = tuổi thọ thể loại (tháng) − số tháng kể từ ngày nhập − số lần đã mượn; chỉ cho giảm, không bao giờ tăng; cuốn trên giá về 0 được TRG6 chuyển sang ChoThanhLy |
| TX1 | sp_MuonSach | Lập phiếu mượn 1–10 cuốn | Kiểm tra thẻ (E103), khóa dòng độc giả và các cuốn bằng FOR UPDATE, cuốn không trên giá hoặc bị lặp trong danh sách → E104, lập phiếu, chèn chi tiết với hạn trả fn_HanTra; mọi lỗi → ROLLBACK cả phiếu |
| TX2 | sp_TraSach | Trả 1 đến nhiều cuốn | Lập phiếu trả, cập nhật chi tiết mượn; số dòng cập nhật khác số cuốn → E108 và ROLLBACK; trả về tổng phạt |
| TX3 | sp_ThanhToanPhat | Thu toàn bộ phạt chưa thanh toán | Khóa các phiếu phạt, đánh dấu đã thanh toán; không có nợ → E109 |
| TX4 | sp_NhapLoSach | Nhập đầu sách mới, tác giả, n cuốn | Tạo đầu sách + tác giả (nếu mới), sinh mã cuốn liên tiếp, xếp lên giá; giá sai thể loại hoặc đầy → ROLLBACK toàn bộ lô |
| TX5 | sp_ThanhLySach | Sách hết niên hạn tách khỏi CSDL đang quản lý | Chuyển cuốn sang SACH_THANH_LY, lịch sử mượn sang CT_MUON_LUU_TRU, rồi xóa khỏi CUON_SACH |
| TX6 | sp_DangKyDocGia | Đăng ký độc giả | Chèn NGUOI, SDT_NGUOI (≥ 1 số, E408), DOC_GIA, THE_DOC_GIA trong một giao dịch |
| TX7 | sp_ThuePhong | Thuê phòng đọc | Khóa phòng, kiểm tra thẻ, nợ phạt (E110), sức chứa (E202), số giờ theo loại phòng (E203), giờ mở cửa (E204); tính tiền và lập phiếu |

Đoạn mã minh họa (TRG1 và khung transaction TX1):

```sql
CREATE OR REPLACE TRIGGER trg_CTMuon_ToiDa10
BEFORE INSERT ON CT_MUON FOR EACH ROW
BEGIN
  IF (SELECT COUNT(*) FROM CT_MUON WHERE MaPhieuMuon = NEW.MaPhieuMuon) >= 10 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'E101: Mỗi lần mượn tối đa 10 cuốn sách';
  END IF;
END //

CREATE OR REPLACE PROCEDURE sp_MuonSach(IN p_MaDocGia VARCHAR(10), IN p_MaThuThu VARCHAR(10),
       IN p_DsCuon JSON, IN p_NgayMuon DATE, OUT p_MaPhieuMuon INT)
BEGIN
  DECLARE EXIT HANDLER FOR SQLEXCEPTION BEGIN ROLLBACK; RESIGNAL; END;
  START TRANSACTION;
    -- kiểm tra số cuốn, thẻ; khóa độc giả và các cuốn bằng SELECT ... FOR UPDATE
    INSERT INTO PHIEU_MUON(MaDocGia, MaThuThu, NgayMuon) VALUES (p_MaDocGia, p_MaThuThu, p_NgayMuon);
    SET p_MaPhieuMuon = LAST_INSERT_ID();
    INSERT INTO CT_MUON(MaPhieuMuon, MaCuonSach, HanTra)        -- TRG1, 2, 4, 5 chạy tại đây
    SELECT p_MaPhieuMuon, j.Ma, fn_HanTra(j.Ma, p_NgayMuon)
    FROM JSON_TABLE(p_DsCuon, '$[*]' COLUMNS (Ma VARCHAR(10) PATH '$')) j;
  COMMIT;
END //
```
""")
q = ha_cap(doan(P7, "## 4.x", "## 4.y"), 0).replace("## 4.x Truy vấn hiển thị theo yêu cầu đề", "## 4.8 Truy vấn hiển thị theo yêu cầu đề")
anh_bc = ["Sách đang được mượn, sắp theo hạn trả", "Sách quá hạn, sắp theo số ngày quá hạn", "Đầu sách theo lượt mượn", "Độc giả trả muộn theo tổng tiền phạt và số sách", "Sách sắp hết hạn sử dụng", "Tình trạng phòng đọc tại một thời điểm"]
q += "\n" + "\n".join(f"![Hình 4.{i}. Báo cáo {i}: {t}](../anh/1{i}_bao_cao_{i}.png)\n" for i, t in enumerate(anh_bc, 1))
q = q.replace("(../anh/11_bao_cao_1.png)\n", "(../anh/11_bao_cao_1.png)\n\n![Hình 4.1b. Báo cáo 1 theo nghĩa rộng: mọi sách đã được mượn trong khoảng ngày (cả đã trả), gọi sp_BC_SachDaMuon](../anh/11b_bao_cao_1_ca_da_tra.png)\n")
c4.append(q)
c4.append(doan(P7, "## 4.y", "## 4.z").replace("## 4.y Tối ưu truy vấn bằng chỉ mục", "## 4.9 Tối ưu truy vấn bằng chỉ mục"))
c4.append(doan(P7, "## 4.z", "## 4.t").replace("## 4.z An toàn bảo mật", "## 4.10 An toàn bảo mật"))
kt = doan(P7, "## 4.t", "## Bảng mã lỗi").replace("## 4.t Kiểm thử ràng buộc, trigger và transaction", "## 4.11 Kiểm thử ràng buộc, trigger và transaction")
c4.append(kt + "\nChi tiết từng ca:\n\n" + A.split("### 4.9 Kết quả kiểm thử tự động (08_test.sql)")[1].strip() + "\n")
c4.append(doan(P7, "## Bảng mã lỗi").replace("## Bảng mã lỗi nghiệp vụ", "## 4.12 Bảng mã lỗi nghiệp vụ"))
ui = [("01_muon_sach", "Màn hình mượn sách"), ("02a_muon_thanh_cong", "Lập phiếu mượn 3 cuốn thành công"),
      ("02_muon_qua_10_cuon", "Mượn 11 cuốn bị CSDL chặn, hiển thị nguyên văn lỗi E101"),
      ("03_tra_sach", "Màn hình trả sách: danh sách sách đang giữ và nợ phạt của độc giả"), ("03a_tra_co_phat", "Trả sách quá hạn, trigger tự lập phiếu phạt"),
      ("03b_thanh_toan_phat", "Thanh toán toàn bộ phạt (TX3)"),
      ("04_thue_phong", "Màn hình thuê phòng đọc: tiền thuê dự kiến cập nhật theo phòng, khung giờ và tình trạng phòng"), ("04a_them_phong_doc", "Quản lý phòng đọc: thêm phòng mới thành công"),
      ("05_doc_gia", "Quản lý độc giả: danh sách, bấm chọn hàng để sửa, gia hạn, xóa"), ("05a_dang_ky_doc_gia", "Đăng ký độc giả mới (TX6) thành công"),
      ("05b_xoa_doc_gia_bi_chan", "Xóa độc giả còn giữ sách bị trigger chặn (E404)"),
      ("06_sach_kho", "Quản lý sách và kho: danh sách đầu sách"), ("06a_them_phong_kho", "Thêm phòng kho thành công"),
      ("06b_them_gia_sach", "Thêm giá sách thành công"), ("06c_xoa_cuon_bi_chan", "Xóa cuốn sách đã có lịch sử mượn bị chặn (E303)"),
      ("07_thu_thu", "Danh sách thủ thư của chi nhánh"), ("07a_them_thu_thu", "Thêm thủ thư mới thành công"),
      ("07b_xoa_truong_bi_chan", "Xóa thủ thư đang là trưởng chi nhánh bị chặn (E403)")]
kq = json.load(open("../anh/ket_qua_giao_dien.json", encoding="utf-8"))
dat = sum(1 for r in kq if r[1] == r[2])
bang_kq = "| # | Thao tác (nút bấm) | Kỳ vọng | Thông báo của hệ thống | Kết quả |\n| --- | --- | --- | --- | --- |\n" + "\n".join(
    f"| {i} | {r[0]} | {'Thành công' if r[1] == 'success' else 'Bị chặn'} | {r[3].replace('|', '/')} | {'Đạt' if r[1] == r[2] else 'Không đạt'} |" for i, r in enumerate(kq, 1))
c4.append("""## 4.13 Giao diện ứng dụng

Ứng dụng có bảy chức năng ở thanh bên trái: mượn sách, trả sách và phạt, phòng đọc, độc giả, sách và kho, thủ thư và chi nhánh, báo cáo. Trước khi thao tác, thủ thư chọn chi nhánh làm việc và tên của mình. Các đối tượng chính (độc giả, thủ thư, chi nhánh, đầu sách, cuốn sách, giá sách, phòng kho, phòng đọc) đều có thể thêm, sửa, xóa và tìm kiếm ngay trên giao diện.

Để thủ thư ít phải gõ, các bảng dữ liệu cho phép bấm vào một hàng để chọn; ô sửa sẽ hiện sẵn giá trị của hàng đó, và sau mỗi thao tác bảng được nạp lại. Những mã đã có trong CSDL như độc giả, cuốn sách, phòng, giá, đầu sách được chọn từ danh sách, có ô gõ để lọc nhanh. Ở trang mượn và trả, thủ thư có thể bấm thẳng nhiều hàng trong bảng sách để đưa các cuốn đó vào phiếu. Trang phòng đọc hiện tiền thuê dự kiến ngay khi đổi phòng, khung giờ hoặc số người; số tiền này lấy từ procedure `sp_ThuePhong_BaoGia`, dùng chung công thức `fn_TienThuePhong` với TX7 nên luôn khớp với tiền thực thu, kèm cảnh báo E202, E203 nếu thuê sai quy định.

Mỗi nút bấm gọi đúng một stored procedure. Khi CSDL từ chối một thao tác (do SIGNAL, CHECK hoặc khóa ngoại), giao diện hiện nguyên văn thông báo lỗi của CSDL; bản thân giao diện không tự kiểm tra luật nghiệp vụ nào. Ứng dụng kết nối bằng tài khoản `ql_thuvien` (vai trò r_QuanLy), tài khoản này không có quyền ghi trực tiếp vào bảng.

Giao diện được kiểm thử tự động bằng Playwright (chương trình `app/chup_man_hinh.py`): trình duyệt lần lượt mở từng màn hình, chọn dữ liệu, bấm nút và đọc thông báo trả về. Kết quả {{dat}}/{{len(kq)}} thao tác cho đúng kết quả mong đợi.

{{bang_kq}}

""".replace("{{dat}}", str(dat)).replace("{{len(kq)}}", str(len(kq))).replace("{{bang_kq}}", bang_kq) + "\n".join(f"![Hình 4.{6 + i}. {t}](../anh/{f}.png)\n" for i, (f, t) in enumerate(ui, 1)))
o += c4

c5 = doan(P8, "## 5.1")
c5 = c5.replace("## 5.8 Sơ đồ tổng thể hệ thống\n", "## 5.8 Sơ đồ tổng thể hệ thống\n\n![Hình 5.1. Sơ đồ tổng thể hệ CSDL phân tán của thư viện](../phan_tan/so_do_tong_the.png)\n")
o.append("# CHƯƠNG 5. PHÂN TÍCH VÀ THIẾT KẾ CƠ SỞ DỮ LIỆU PHÂN TÁN\n")
o.append(c5)

o.append("""# KẾT LUẬN

Qua bài tập lớn này, nhóm đã đi qua đủ các bước thiết kế một hệ cơ sở dữ liệu, từ phân tích yêu cầu đến cài đặt và kiểm thử. Những kết quả chính nhóm đạt được:

- Lược đồ E-R có đủ các loại tập thực thể, thuộc tính và liên kết mà đề yêu cầu, gồm cả thực thể yếu, cụ thể hóa ISA, liên kết đệ quy, liên kết 3 ngôi và kết hợp.
- 23 lược đồ quan hệ đều ở dạng chuẩn BCNF, kèm phụ thuộc hàm, khóa, ví dụ chuẩn hóa từng bước, sơ đồ khóa chính – khóa ngoại và từ điển dữ liệu.
- CSDL cài trên MariaDB với 23 khóa chính, 34 khóa ngoại, 11 ràng buộc UNIQUE, 44 ràng buộc CHECK, 8 trigger, 7 transaction và 8 function; tuổi thọ sách được cập nhật hằng ngày bằng event của MariaDB.
- Dữ liệu mô phỏng ba tháng hoạt động ở ba chi nhánh (300 đầu sách, 1.623 cuốn, 200 độc giả, 831 phiếu mượn, 2.217 lượt mượn); sáu truy vấn hiển thị sắp xếp đúng như đề yêu cầu.
- 52 ca kiểm thử nghiệp vụ và 23 thao tác trên giao diện đều cho kết quả đúng như mong đợi.
- Thiết kế phân tán cho ba site gồm phân mảnh ngang nguyên thủy (COM_MIN, PHORIZONTAL), phân mảnh dẫn xuất, phân mảnh dọc (BEA), phân mảnh lai, cấp phát và nhân bản; ba quy tắc phân mảnh được kiểm chứng trên dữ liệu (36/36 ca đạt).

Bên cạnh đó, bài làm vẫn còn một số hạn chế. Phần phân tán mới được minh họa bằng ba database trên cùng một máy chủ, chưa chạy trên ba máy riêng. Nghiệp vụ hiện cho phép mượn sách ở chi nhánh khác nhưng chưa có giao tác phân tán cho trường hợp này. Giao diện còn đơn giản, chủ yếu phục vụ công việc của thủ thư.

Thời gian tới, nhóm dự định triển khai ba site trên ba máy chủ thật, dùng cơ chế nhân bản (replication) của MariaDB cho các bảng danh mục, đồng thời bổ sung chức năng đặt trước sách và gửi email nhắc hạn trả cho độc giả.
""")

phu_luc = ["# PHỤ LỤC A. MÃ NGUỒN SQL\n", "Mã nguồn đầy đủ của các script chính (các file 05_seed.sql, 08_test.sql, 09_phan_tan.sql dài và được sinh tự động, nộp kèm theo).\n"]
for f, t in [("01_schema.sql", "A.1 Tạo bảng và ràng buộc"), ("02_function_procedure.sql", "A.2 Function và procedure thêm/xóa/sửa/tìm kiếm"),
             ("03_trigger.sql", "A.3 Trigger"), ("04_transaction.sql", "A.4 Transaction"), ("06_view_baocao.sql", "A.5 Truy vấn báo cáo"), ("07_index_baomat.sql", "A.6 Chỉ mục và phân quyền")]:
    phu_luc.append(f"## {t} ({f})\n\n```sql\n{R('../sql/' + f).strip()}\n```\n")
o += phu_luc
open("BaoCao.md", "w", encoding="utf-8").write("\n".join(o))
print("ok", sum(len(x) for x in o))
