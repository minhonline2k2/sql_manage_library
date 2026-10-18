# P8. Phân tích và thiết kế CSDL phân tán (mục 5 báo cáo)

## 5.1 Bối cảnh và kiến trúc

Thư viện có 3 chi nhánh, mỗi chi nhánh là một **site** có máy chủ CSDL riêng, nối với nhau qua mạng WAN: S1 = CN01 Cầu Giấy (trụ sở), S2 = CN02 Hà Đông, S3 = CN03 Hoàn Kiếm. Phần lớn nghiệp vụ (mượn, trả, thuê phòng, tra cứu kho) diễn ra tại chi nhánh nơi độc giả đăng ký, nên dữ liệu được đặt tại chỗ để giảm truyền thông và cho phép mỗi chi nhánh vẫn hoạt động khi đường mạng tới chi nhánh khác gặp sự cố.

Kiến trúc: **hệ CSDL phân tán thuần nhất** (cùng MariaDB ở mọi site), mô hình tham chiếu nhiều mức của chương 7a:

| Mức | Nội dung trong thiết kế |
| --- | --- |
| Lược đồ toàn cục | 23 quan hệ của mục 3 (database `QLTV`) |
| Lược đồ phân mảnh | Mục 5.3–5.5: ngang nguyên thủy, ngang dẫn xuất, dọc, lai |
| Lược đồ cấp phát | Mục 5.6: mảnh nào đặt ở site nào, mảnh nào nhân bản |
| Lược đồ ánh xạ cục bộ | Mỗi site là một database MariaDB `QLTV_CN0k`; view `pt_*` ánh xạ ngược về quan hệ toàn cục |

Mức trong suốt hướng tới: **trong suốt phân mảnh** – ứng dụng chỉ làm việc với quan hệ toàn cục, thông qua các view tái thiết `pt_*`.

## 5.2 Số liệu giả định dùng cho thiết kế

| Thông số | S1 CN01 | S2 CN02 | S3 CN03 | Ghi chú |
| --- | --- | --- | --- | --- |
| Độc giả | 2.400 | 1.800 | 1.800 | Tổng 6.000 khi hệ thống đầy đủ (dữ liệu demo: 200) |
| Tỷ lệ độc giả bị khóa | 5% | 5% | 5% | Thẻ vi phạm, nợ lâu |
| Cuốn sách | 6.000 | 4.500 | 4.500 | |
| Phiếu mượn mỗi ngày | 120 | 90 | 90 | |
| Đầu sách (danh mục) | 3.000, dùng chung | | | Cập nhật ~5 đầu sách mới/ngày tại S1 |
| Băng thông giữa các site | 20 Mbps, chi phí 1 đơn vị/thông điệp | | | |

## 5.3 Phân mảnh ngang nguyên thủy DOC_GIA

**Ứng dụng:**
- UD1 (chạy tại cả 3 site, ~300 lượt/ngày mỗi site): thủ thư tra cứu, mượn/trả cho độc giả đăng ký tại chi nhánh mình → `WHERE MaChiNhanh = 'CN0k'`.
- UD2 (chạy tại S1, ~4 lượt/tháng): bộ phận quản lý rà soát độc giả bị khóa để mở khóa hoặc xóa → `WHERE TrangThai = 'Khoa'`.

**Tập vị từ đơn giản:** Pr = { p1: MaChiNhanh = 'CN01'; p2: MaChiNhanh = 'CN02'; p3: MaChiNhanh = 'CN03'; p4: TrangThai = 'Khoa' }.

**Thuật toán COM_MIN:**
1. Chọn p1: p1 phân hoạch DOC_GIA thành {CN01} và {còn lại}, hai phần được UD1 truy nhập khác nhau (S1 chỉ truy nhập phần CN01) → p1 liên đới. Pr' = {p1}, F = {f1}.
2. Thêm p2: tách phần "còn lại" thành CN02 và CN03, S2 chỉ truy nhập phần CN02 → liên đới. Pr' = {p1, p2}.
3. Thêm p3: tương tự, S3 chỉ truy nhập phần CN03 → liên đới. Pr' = {p1, p2, p3}.
4. Thêm p4: tách mỗi mảnh theo trạng thái. Xét mi = p1 ∧ p4 (CN01, khóa, 120 bộ) và mj = p1 ∧ ¬p4 (CN01, hoạt động, 2.280 bộ). UD1 truy nhập đều các bộ CN01 (9.000 lượt/tháng) nên phân cho mi 9.000 × 120/2.400 = 450 lượt và mj 8.550 lượt; UD2 thêm 4 lượt/tháng chỉ vào mi. acc(mi)/card(fi) = 454/120 ≈ 3,78 ≠ acc(mj)/card(fj) = 8.550/2.280 = 3,75 → có ứng dụng (UD2) truy nhập hai mảnh khác nhau → p4 liên đới. Pr' = {p1, p2, p3, p4}.
5. Không còn vị từ; kiểm tra lại không vị từ nào trong Pr' mất tính liên đới → **Pr' đầy đủ và cực tiểu**.

*Ví dụ không cực tiểu:* nếu thêm p5: GioiTinh = 'M', p5 chia mỗi mảnh thành 2 phần nhưng không ứng dụng nào truy nhập hai phần này khác nhau (acc/card bằng nhau) → p5 không liên đới, Pr' ∪ {p5} không cực tiểu, nên loại p5.

**Thuật toán PHORIZONTAL:**
- Số vị từ hội sơ cấp lý thuyết: 2⁴ = 16 (mỗi pi ở dạng khẳng định hoặc phủ định).
- Tập phép kéo theo I: p1 ⇒ ¬p2 ∧ ¬p3; p2 ⇒ ¬p1 ∧ ¬p3; p3 ⇒ ¬p1 ∧ ¬p2; ¬p1 ∧ ¬p2 ⇒ p3 (miền MaChiNhanh chỉ có 3 giá trị).
- Loại các minterm mâu thuẫn với I (hai chi nhánh cùng lúc, hoặc không chi nhánh nào) → còn **6 minterm**:

| Mảnh | Vị từ hội sơ cấp | Biểu thức | Số bộ giả định | Số bộ dữ liệu demo |
| --- | --- | --- | --- | --- |
| DOC_GIA_1 | p1 ∧ ¬p4 | σ MaChiNhanh='CN01' ∧ TrangThai='HoatDong' (DOC_GIA) | 2.280 | 67 |
| DOC_GIA_2 | p1 ∧ p4 | σ MaChiNhanh='CN01' ∧ TrangThai='Khoa' (DOC_GIA) | 120 | 0 |
| DOC_GIA_3 | p2 ∧ ¬p4 | σ MaChiNhanh='CN02' ∧ TrangThai='HoatDong' (DOC_GIA) | 1.710 | 67 |
| DOC_GIA_4 | p2 ∧ p4 | σ MaChiNhanh='CN02' ∧ TrangThai='Khoa' (DOC_GIA) | 90 | 0 |
| DOC_GIA_5 | p3 ∧ ¬p4 | σ MaChiNhanh='CN03' ∧ TrangThai='HoatDong' (DOC_GIA) | 1.710 | 66 |
| DOC_GIA_6 | p3 ∧ p4 | σ MaChiNhanh='CN03' ∧ TrangThai='Khoa' (DOC_GIA) | 90 | 0 |

Các mảnh "Khoa" rỗng trong dữ liệu demo (chưa có độc giả bị khóa), tương tự PROJ2, PROJ5 trong ví dụ của slide; chúng vẫn được giữ trong lược đồ vì ràng buộc nghiệp vụ cho phép phát sinh.

Tương tự, **THU_THU, PHONG_KHO, PHONG_DOC** được phân mảnh ngang nguyên thủy theo vị từ MaChiNhanh = 'CN0k' (ứng dụng duy nhất là truy nhập theo chi nhánh) → mỗi quan hệ 3 mảnh.

## 5.4 Phân mảnh ngang dẫn xuất

Đường liên kết (owner → member) và các mảnh dẫn xuất bằng phép bán kết nối ⋉:

| Quan hệ member | Owner | Mảnh dẫn xuất (k = 1..3 theo chi nhánh) |
| --- | --- | --- |
| SDT_NGUOI (độc giả), THE_DOC_GIA | DOC_GIA | SDT_k = SDT_NGUOI ⋉ (DOC_GIA_{2k-1} ∪ DOC_GIA_{2k}); THE_k tương tự |
| PHIEU_MUON | DOC_GIA | PHIEU_MUON_k = PHIEU_MUON ⋉_{MaDocGia = MaNguoi} DOC_GIA_k |
| PHIEU_TRA | DOC_GIA | PHIEU_TRA_k = PHIEU_TRA ⋉ DOC_GIA_k |
| CT_MUON | PHIEU_MUON | CT_MUON_k = CT_MUON ⋉ PHIEU_MUON_k |
| PHIEU_PHAT | CT_MUON | PHIEU_PHAT_k = PHIEU_PHAT ⋉ CT_MUON_k |
| GIA_SACH | PHONG_KHO | GIA_SACH_k = GIA_SACH ⋉ PHONG_KHO_k |
| CUON_SACH | GIA_SACH | CUON_SACH_k = CUON_SACH ⋉ GIA_SACH_k |
| PHIEU_THUE_PHONG | PHONG_DOC | THUE_k = PHIEU_THUE_PHONG ⋉ PHONG_DOC_k |
| NGUOI (thủ thư) | THU_THU | NGUOI_TT_k = NGUOI ⋉ THU_THU_k |

Nhận xét:
- Xảy ra **phân mảnh dây chuyền** giống ví dụ PAY → EMP → ASG trong slide: DOC_GIA → PHIEU_MUON → CT_MUON → PHIEU_PHAT và PHONG_KHO → GIA_SACH → CUON_SACH.
- CT_MUON có hai owner có thể chọn (PHIEU_MUON và CUON_SACH). Nhóm chọn PHIEU_MUON vì (1) đặc tính kết nối tốt hơn: các truy vấn mượn/trả và báo cáo luôn kết nối CT_MUON với PHIEU_MUON và độc giả; (2) phục vụ nhiều ứng dụng hơn (mượn, trả, phạt, báo cáo 1, 2, 4). Do độc giả chỉ mượn sách tại chi nhánh mình, CT_MUON_k ⋈ CUON_SACH_k vẫn hoàn toàn cục bộ.

## 5.5 Phân mảnh dọc và phân mảnh lai NGUOI (phần độc giả)

Quan hệ NGUOI chứa thông tin cá nhân độc giả, nhưng các ứng dụng chỉ dùng từng nhóm thuộc tính. Khóa MaNguoi có mặt ở mọi mảnh nên không đưa vào ma trận lực hút (theo Özsu & Valduriez). Gom thuộc tính kép thành một thuộc tính khi phân tích: A1 = HoTen (Ho, Dem, Ten), A2 = NgaySinh (+ GioiTinh), A3 = DiaChi (SoNha, Phuong, Quan, TinhTP), A4 = Email.

**Ứng dụng và tần suất (lượt/ngày, ref = 1):**

| Ứng dụng | Câu truy vấn | S1 | S2 | S3 |
| --- | --- | --- | --- | --- |
| q1 | Tra cứu tên độc giả khi mượn/trả: SELECT HoTen WHERE MaNguoi = ? | 45 | 30 | 25 |
| q2 | Gửi email nhắc hạn trả: SELECT HoTen, Email WHERE MaNguoi IN (…) | 25 | 20 | 15 |
| q3 | Thống kê độ tuổi theo khu vực: SELECT NgaySinh, DiaChi | 40 | 30 | 30 |
| q4 | In/cấp lại thẻ: SELECT HoTen, NgaySinh, DiaChi WHERE MaNguoi = ? | 5 | 3 | 2 |

**Ma trận sử dụng A** (hàng q1..q4, cột A1..A4): q1 = [1,0,0,0]; q2 = [1,0,0,1]; q3 = [0,1,1,0]; q4 = [1,1,1,0].

**Ma trận lực hút AA**, aff(Ai, Aj) = Σ_{qk dùng cả Ai, Aj} Σ_sites acc:

|  | A1 | A2 | A3 | A4 |
| --- | --- | --- | --- | --- |
| A1 | 170 | 10 | 10 | 60 |
| A2 | 10 | 110 | 110 | 0 |
| A3 | 10 | 110 | 110 | 0 |
| A4 | 60 | 0 | 0 | 60 |

Ví dụ: aff(A1, A1) = q1 + q2 + q4 = 100 + 60 + 10 = 170; aff(A2, A3) = q3 + q4 = 100 + 10 = 110.

**Thuật toán BEA** (bond(Ax, Ay) = Σz aff(Az, Ax)·aff(Az, Ay); cont(Ai, Ak, Aj) = 2·bond(Ai, Ak) + 2·bond(Ak, Aj) − 2·bond(Ai, Aj); A0, A5 là cột biên bằng 0):

1. Khởi tạo CA với cột A1, A2.
2. Đặt A3: cont(A0, A3, A1) = 7.800; cont(A1, A3, A2) = 48.600; cont(A2, A3, A5) = 48.600 → chọn vị trí đầu tiên đạt max: giữa A1 và A2 → thứ tự A1, A3, A2.
3. Đặt A4: cont(A0, A4, A1) = 27.600; cont(A1, A4, A3) = 21.000; cont(A3, A4, A2) = −46.200; cont(A2, A4, A5) = 1.200 → đặt A4 bên trái A1 → thứ tự **A4, A1, A3, A2**.
4. Sắp hàng theo thứ tự cột, được ma trận CA hai khối rõ rệt:

|  | A4 | A1 | A3 | A2 |
| --- | --- | --- | --- | --- |
| A4 | 60 | 60 | 0 | 0 |
| A1 | 60 | 170 | 10 | 10 |
| A3 | 0 | 10 | 110 | 110 |
| A2 | 0 | 10 | 110 | 110 |

**Chọn điểm chia** (z = CTQ·CBQ − COQ², lấy max):

| x | TA | BA | TQ | BQ | OQ | CTQ | CBQ | COQ | z |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | {A4} | {A1, A3, A2} | — | q1, q3, q4 | q2 | 0 | 210 | 60 | −3.600 |
| **2** | **{A4, A1}** | **{A3, A2}** | q1, q2 | q3 | q4 | 160 | 100 | 10 | **15.900** |
| 3 | {A4, A1, A3} | {A2} | q1, q2 | — | q3, q4 | 160 | 0 | 110 | −12.100 |

**Kết quả:** NGUOI_DG_A(MaNguoi, Ho, Dem, Ten, Email, LoaiNguoi) và NGUOI_DG_B(MaNguoi, NgaySinh, GioiTinh, SoNha, Phuong, Quan, TinhTP). Chỉ q4 (10 lượt/ngày) phải kết nối hai mảnh.

**Phân mảnh lai:** NGUOI (độc giả) trước hết được phân mảnh ngang dẫn xuất theo DOC_GIA của từng chi nhánh, rồi mỗi mảnh ngang được phân mảnh dọc như trên → 6 mảnh: NGUOI_DG_A_k, NGUOI_DG_B_k (k = 1..3). Tái thiết: NGUOI_DG = ∪_k (NGUOI_DG_A_k ⋈ NGUOI_DG_B_k).

## 5.6 Kiểm tra tính đúng đắn của phân mảnh

| Quy tắc | Phân mảnh ngang (DOC_GIA và các mảnh dẫn xuất) | Phân mảnh dọc (NGUOI_DG_A, NGUOI_DG_B) |
| --- | --- | --- |
| Đầy đủ | Mỗi bộ có MaChiNhanh ∈ {CN01, CN02, CN03} và TrangThai ∈ {HoatDong, Khoa} (CHECK) nên thuộc đúng một minterm; mảnh dẫn xuất đầy đủ nhờ ràng buộc khóa ngoại | A ∪ B = toàn bộ thuộc tính của NGUOI |
| Tái thiết | DOC_GIA = ∪ DOC_GIA_i | NGUOI_DG = A ⋈_MaNguoi B |
| Tách biệt | Các minterm loại trừ nhau; mỗi phiếu thuộc đúng một độc giả nên mảnh dẫn xuất cũng rời nhau | A ∩ B = {MaNguoi} (chỉ chung khóa) |

Kiểm chứng trên dữ liệu bằng `09_phan_tan.sql`: dùng EXCEPT (đầy đủ), so sánh số bộ của hợp các mảnh với quan hệ gốc (tái thiết), đếm khóa trùng giữa các mảnh (tách biệt) cho 12 quan hệ → **36/36 PASS**.

## 5.7 Cấp phát và nhân bản

**Phân tích chi phí cho quyết định nhân bản** (chi phí truyền thông, 1 đơn vị/thông điệp, theo ngày):

| Quan hệ | Đọc/ngày | Ghi/ngày | Phương án 1 bản tại S1 | Nhân bản tại 3 site | Quyết định |
| --- | --- | --- | --- | --- | --- |
| DAU_SACH, TAC_GIA, DAU_SACH_TAC_GIA | 1.500 mỗi site (tra cứu, tính hạn trả) | 5 (S1) | Đọc từ xa của S2, S3: 3.000 | Đồng bộ ghi tới 2 site: 5 × 2 = 10 | Nhân bản toàn phần |
| THE_LOAI, BANG_PHI_PHAT, LOAI_PHONG, CHI_NHANH | ~800 mỗi site (TRG3, TX1, TX7) | ~0 | 1.600 | ≈ 0 | Nhân bản toàn phần |
| CUON_SACH_k | 1.200 tại site k, 60 từ site khác (tìm sách liên chi nhánh) | 250 tại site k | 60 | 250 × 2 = 500 | Không nhân bản, đặt tại site k |
| SACH_THANH_LY, CT_MUON_LUU_TRU | Vài lượt/tháng | Vài lần/năm | Gần 0 | — | Một bản tại S1 |

**Lược đồ cấp phát** (Rij = mảnh i đặt tại site j; số bộ theo dữ liệu demo):

| Site | Mảnh cấp phát (không nhân bản) | Số bộ demo |
| --- | --- | --- |
| S1 (CN01) | DOC_GIA_1, DOC_GIA_2; NGUOI_DG_A_1, NGUOI_DG_B_1; THE_1; PHIEU_MUON_1; CT_MUON_1; PHIEU_TRA_1; PHIEU_PHAT_1; THU_THU_1, NGUOI_TT_1; PHONG_KHO_1; GIA_SACH_1; CUON_SACH_1; PHONG_DOC_1; THUE_1; SACH_THANH_LY; CT_MUON_LUU_TRU | độc giả 67, phiếu mượn 272, chi tiết mượn 751, phiếu trả 531, phiếu phạt 111, cuốn 475, giá 9, thủ thư 5, phòng 7, lượt thuê 51 |
| S2 (CN02) | Các mảnh k = 2 tương ứng | độc giả 67, phiếu mượn 281, chi tiết 737, phiếu trả 512, phạt 107, cuốn 434, giá 10, thủ thư 5, phòng 7, lượt thuê 51 |
| S3 (CN03) | Các mảnh k = 3 tương ứng | độc giả 66, phiếu mượn 278, chi tiết 713, phiếu trả 525, phạt 97, cuốn 460, giá 8, thủ thư 5, phòng 7, lượt thuê 48 |
| S1, S2, S3 | **Bản sao toàn phần:** CHI_NHANH, THE_LOAI, BANG_PHI_PHAT, LOAI_PHONG, DAU_SACH, TAC_GIA, DAU_SACH_TAC_GIA | 3, 6, 7, 2, 300, 28, 391 |

Mô hình cấp phát tổng quát (chương 7c): biến quyết định x_ij = 1 nếu mảnh Fi đặt tại Sj; cực tiểu Tổng chi phí = Σ lưu trữ (USC_k · size(Fj) · x_jk) + Σ truy vấn (xử lý PC_i + truyền thông TC_i), với ràng buộc thời gian đáp ứng, dung lượng lưu trữ và năng lực xử lý từng site. Bài toán là NP-complete nên nhóm dùng heuristic: (1) bỏ qua nhân bản, đặt mỗi mảnh tại site truy cập nhiều nhất (site của chi nhánh); (2) xét nhân bản cho từng quan hệ theo bảng chi phí trên.

## 5.8 Sơ đồ tổng thể hệ thống

Sơ đồ (vẽ ở phần báo cáo, file `btl/phan_tan/so_do_tong_the.dot`): ba site S1, S2, S3 nối qua WAN; mỗi site gồm DBMS cục bộ MariaDB, CSDL cục bộ chứa các mảnh của chi nhánh và bản sao danh mục; tầng trên là lược đồ toàn cục + lược đồ phân mảnh + lược đồ cấp phát; ứng dụng thủ thư ở mỗi chi nhánh truy cập qua lớp trong suốt phân tán.

**Xử lý truy vấn phân tán (ví dụ):** báo cáo "độc giả trả muộn" toàn hệ thống = ∪_k γ_MaDocGia(PHIEU_PHAT_k ⋈ PHIEU_MUON_k): mỗi site tính cục bộ phần của mình rồi gửi kết quả gộp (vài chục bộ) về site yêu cầu, thay vì gửi toàn bộ bảng phạt. Truy vấn tìm sách liên chi nhánh dùng bán kết nối: gửi π_MaDauSach của kết quả tìm kiếm tới site khác, chỉ nhận về các cuốn khớp, giảm khối lượng truyền như mục đích của phép ⋉ ở chương 4.

## 5.9 Minh họa cài đặt trên MariaDB

`btl/sql/09_phan_tan.sql` (sinh bởi `btl/phan_tan/gen_phantan.py`) tạo 3 database `QLTV_CN01..03` trên cùng một máy chủ để mô phỏng 3 site, dùng `CREATE TABLE … AS SELECT … WHERE` (phép chọn), `… WHERE MaX IN (SELECT …)` (bán kết nối) và chọn cột (phép chiếu) để tạo mảnh; tạo view `pt_*` bằng UNION ALL / JOIN để tái thiết; bảng KIEM_TRA_PHAN_TAN ghi kết quả kiểm tra 3 quy tắc. Trên hệ thống thật, mỗi database đặt trên một máy chủ riêng và các view tái thiết dùng engine CONNECT/FederatedX hoặc lớp ứng dụng để truy cập site xa.
