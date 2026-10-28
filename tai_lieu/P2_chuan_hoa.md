# P2. Lược đồ quan hệ, phụ thuộc hàm, khóa và chuẩn hóa BCNF

Ký hiệu: khóa chính in **đậm**, khóa ngoại ghi `FK → BẢNG`. Thuộc tính dẫn xuất không lưu (Tuoi, ConHan, SoLuotMuon) được tính bằng function/view; SoLuongHienCo, SoTien, TongTien được lưu lại có chủ đích (giải thích ở 3.4).

## 3.1 Quy tắc ánh xạ đã dùng

| Thành phần ERD | Quy tắc ánh xạ | Kết quả |
| --- | --- | --- |
| Thực thể mạnh | Mỗi tập thực thể → 1 quan hệ, định danh → PK | CHI_NHANH, THE_LOAI, TAC_GIA, DAU_SACH, PHONG_KHO, GIA_SACH, … |
| Thuộc tính kép HoTen, DiaChi | Chỉ giữ các thành phần đơn | Ho, Dem, Ten; SoNha, Phuong, Quan, TinhTP |
| Thuộc tính đa trị SoDienThoai | Tách quan hệ mới (PK chủ + giá trị) | SDT_NGUOI |
| Thuộc tính đa trị tác giả → liên kết N:N viet | Quan hệ liên kết, PK = tổ hợp 2 PK | DAU_SACH_TAC_GIA |
| Thực thể yếu CUON_SACH, BANG_PHI_PHAT | PK = PK thực thể xác định + khóa bán phần | CUON_SACH(MaDauSach, STT) – thay bằng mã ghép MaCuonSach làm PK, (MaDauSach, STT) giữ làm khóa dự bị; BANG_PHI_PHAT(MaTheLoai, NgayApDung) |
| ISA disjoint toàn bộ | Bảng cha + bảng con dùng chung PK (FK → cha, ON DELETE CASCADE) + thuộc tính phân biệt | NGUOI(LoaiNguoi), DOC_GIA, THU_THU |
| 1:1 truong_chi_nhanh | FK đặt ở bên tham gia toàn bộ (CHI_NHANH), thêm UNIQUE | CHI_NHANH.MaThuThuTruong |
| 1:1 so_huu_the | FK + UNIQUE ở THE_DOC_GIA | THE_DOC_GIA.MaDocGia UNIQUE |
| 1:N | PK phía 1 thành FK phía N | DAU_SACH.MaTheLoai, CUON_SACH.MaGia, … |
| Đệ quy 1:N quan_ly | FK đệ quy tham chiếu chính bảng | THU_THU.MaQuanLy → THU_THU |
| N:N gom_sach có thuộc tính | Quan hệ mới, PK = (MaPhieuMuon, MaCuonSach), thêm HanTra | CT_MUON |
| Kết hợp tra_lai (1:N vào [gom_sach]) | FK phía nhiều đặt vào quan hệ của kết hợp | CT_MUON.MaPhieuTra (NULL khi chưa trả) |
| Kết hợp bi_phat (1:1 vào [gom_sach]) | Quan hệ mới tham chiếu PK của kết hợp + UNIQUE | PHIEU_PHAT(MaPhieuMuon, MaCuonSach) |
| Liên kết 3 ngôi muon | Thực thể kết hợp PHIEU_MUON giữ FK tới DOC_GIA, THU_THU; chi tiết tới CUON_SACH | PHIEU_MUON + CT_MUON |
| Liên kết 3 ngôi thue_phong (M:N:1) có thuộc tính | Quan hệ mới chứa PK của cả 3 tập thực thể làm FK + thuộc tính của liên kết. Khóa tự nhiên (MaDocGia, MaPhongDoc, BatDau) vì một độc giả thuê cùng phòng nhiều lần; dùng khóa thay thế MaPhieuThue cho gọn, còn ràng buộc "không trùng giờ trên một phòng" kiểm tra trong TX7. Phía THU_THU là 1 nên MaThuThuDuyet không cần nằm trong khóa | PHIEU_THUE_PHONG(MaPhieuThue, MaDocGia, MaPhongDoc, MaThuThuDuyet, …) |

## 3.2 Tập lược đồ quan hệ (23 quan hệ)

| # | Lược đồ | Khóa ngoại | Khóa dự bị khác |
| --- | --- | --- | --- |
| 1 | CHI_NHANH(**MaChiNhanh**, TenChiNhanh, DiaChi, GioMo, GioDong, MaThuThuTruong) | MaThuThuTruong → THU_THU | TenChiNhanh; MaThuThuTruong |
| 2 | NGUOI(**MaNguoi**, Ho, Dem, Ten, NgaySinh, GioiTinh, SoNha, Phuong, Quan, TinhTP, Email, LoaiNguoi) | — | Email |
| 3 | SDT_NGUOI(**MaNguoi, SoDienThoai**) | MaNguoi → NGUOI | — |
| 4 | DOC_GIA(**MaNguoi**, MaChiNhanh, NgayDangKy, TrangThai) | MaNguoi → NGUOI; MaChiNhanh → CHI_NHANH | — |
| 5 | THE_DOC_GIA(**SoThe**, MaDocGia, NgayCap, NgayHetHan) | MaDocGia → DOC_GIA | MaDocGia |
| 6 | THU_THU(**MaNguoi**, MaChiNhanh, NgayVaoLam, MaQuanLy) | MaNguoi → NGUOI; MaChiNhanh → CHI_NHANH; MaQuanLy → THU_THU | — |
| 7 | THE_LOAI(**MaTheLoai**, TenTheLoai, SoNgayMuon, TuoiThoNam) | — | TenTheLoai |
| 8 | BANG_PHI_PHAT(**MaTheLoai, NgayApDung**, PhatCoBan, PhatMoiNgay) | MaTheLoai → THE_LOAI | — |
| 9 | TAC_GIA(**MaTacGia**, TenTacGia, QuocTich) | — | — |
| 10 | DAU_SACH(**MaDauSach**, MaTheLoai, TenSach, NhaXuatBan, NamXuatBan, SoNgayMuonRieng) | MaTheLoai → THE_LOAI | — |
| 11 | DAU_SACH_TAC_GIA(**MaDauSach, MaTacGia**) | → DAU_SACH; → TAC_GIA | — |
| 12 | PHONG_KHO(**MaPhongKho**, MaChiNhanh, TenPhong, Tang) | MaChiNhanh → CHI_NHANH | (MaChiNhanh, TenPhong) |
| 13 | GIA_SACH(**MaGia**, MaPhongKho, MaTheLoai, SucChua, SoLuongHienCo) | → PHONG_KHO; → THE_LOAI | — |
| 14 | CUON_SACH(**MaCuonSach**, MaDauSach, STT, MaGia, NgayNhap, TuoiThoConLaiThang, TrangThai) | → DAU_SACH; → GIA_SACH | (MaDauSach, STT) |
| 15 | SACH_THANH_LY(**MaCuonSach**, MaDauSach, STT, NgayNhap, NgayThanhLy, LyDo) | MaDauSach → DAU_SACH | (MaDauSach, STT) |
| 16 | PHIEU_MUON(**MaPhieuMuon**, MaDocGia, MaThuThu, NgayMuon) | → DOC_GIA; → THU_THU | — |
| 17 | PHIEU_TRA(**MaPhieuTra**, MaDocGia, MaThuThu, NgayTra) | → DOC_GIA; → THU_THU | — |
| 18 | CT_MUON(**MaPhieuMuon, MaCuonSach**, HanTra, MaPhieuTra) | → PHIEU_MUON; → CUON_SACH; MaPhieuTra → PHIEU_TRA (NULL được) | — |
| 19 | PHIEU_PHAT(**MaPhieuPhat**, MaPhieuMuon, MaCuonSach, SoNgayTre, SoTien, DaThanhToan, NgayThanhToan) | (MaPhieuMuon, MaCuonSach) → CT_MUON | (MaPhieuMuon, MaCuonSach) |
| 20 | LOAI_PHONG(**MaLoaiPhong**, TenLoai, GiaMoiGio, SoGioToiThieu, SoGioToiDa) | — | TenLoai |
| 21 | PHONG_DOC(**MaPhongDoc**, MaChiNhanh, MaLoaiPhong, TenPhong, SucChua) | → CHI_NHANH; → LOAI_PHONG | (MaChiNhanh, TenPhong) |
| 22 | PHIEU_THUE_PHONG(**MaPhieuThue**, MaDocGia, MaPhongDoc, MaThuThuDuyet, NgayDat, BatDau, KetThuc, SoNguoi, MucDich, TongTien, TrangThai) | → DOC_GIA; → PHONG_DOC; MaThuThuDuyet → THU_THU | — |
| 23 | CT_MUON_LUU_TRU(**MaPhieuMuon, MaCuonSach**, HanTra, MaPhieuTra, TienPhat) | → PHIEU_MUON; → PHIEU_TRA; MaCuonSach → SACH_THANH_LY | — |

Quan hệ 23 là bảng lưu trữ: khi thanh lý, cuốn sách bị xóa khỏi CUON_SACH nên các dòng CT_MUON của nó (và tiền phạt đã nộp) được chuyển sang đây, giữ lịch sử mượn mà không vi phạm khóa ngoại.

Ghi chú: khóa ngoại vòng CHI_NHANH ↔ THU_THU được tạo bằng `ALTER TABLE` sau khi có cả hai bảng; MaThuThuTruong cho phép NULL trong lúc khởi tạo dữ liệu.

## 3.3 Phụ thuộc hàm, khóa và kiểm tra BCNF từng lược đồ

Cách làm theo bài giảng: với mỗi lược đồ, liệt kê tập F đã tối thiểu (vế phải 1 thuộc tính được gộp cho gọn), tính bao đóng của vế trái để tìm khóa, rồi kiểm tra định nghĩa BCNF: *mọi PTH không hiển nhiên X → A đều có X là siêu khóa*.

| # | Tập F | Khóa (từ bao đóng) | BCNF? |
| --- | --- | --- | --- |
| 1 CHI_NHANH | MaChiNhanh → TenChiNhanh, DiaChi, GioMo, GioDong, MaThuThuTruong; TenChiNhanh → MaChiNhanh; MaThuThuTruong → MaChiNhanh | {MaChiNhanh}⁺ = {TenChiNhanh}⁺ = {MaThuThuTruong}⁺ = toàn bộ → 3 khóa dự bị | Có: mọi vế trái là khóa |
| 2 NGUOI | MaNguoi → mọi thuộc tính; Email → MaNguoi | MaNguoi, Email | Có |
| 3 SDT_NGUOI | Không có PTH không hiển nhiên | Toàn bộ thuộc tính | Có |
| 4 DOC_GIA | MaNguoi → MaChiNhanh, NgayDangKy, TrangThai | MaNguoi | Có |
| 5 THE_DOC_GIA | SoThe → MaDocGia, NgayCap, NgayHetHan; MaDocGia → SoThe | SoThe, MaDocGia | Có |
| 6 THU_THU | MaNguoi → MaChiNhanh, NgayVaoLam, MaQuanLy | MaNguoi | Có |
| 7 THE_LOAI | MaTheLoai → TenTheLoai, SoNgayMuon, TuoiThoNam; TenTheLoai → MaTheLoai | MaTheLoai, TenTheLoai | Có |
| 8 BANG_PHI_PHAT | MaTheLoai, NgayApDung → PhatCoBan, PhatMoiNgay | (MaTheLoai, NgayApDung) | Có |
| 9 TAC_GIA | MaTacGia → TenTacGia, QuocTich | MaTacGia | Có |
| 10 DAU_SACH | MaDauSach → MaTheLoai, TenSach, NhaXuatBan, NamXuatBan, SoNgayMuonRieng | MaDauSach | Có |
| 11 DAU_SACH_TAC_GIA | Không có | Toàn bộ | Có |
| 12 PHONG_KHO | MaPhongKho → MaChiNhanh, TenPhong, Tang; MaChiNhanh, TenPhong → MaPhongKho | MaPhongKho; (MaChiNhanh, TenPhong) | Có |
| 13 GIA_SACH | MaGia → MaPhongKho, MaTheLoai, SucChua, SoLuongHienCo | MaGia | Có |
| 14 CUON_SACH | MaCuonSach → MaDauSach, STT, MaGia, NgayNhap, TuoiThoConLaiThang, TrangThai; MaDauSach, STT → MaCuonSach | MaCuonSach; (MaDauSach, STT) | Có |
| 15 SACH_THANH_LY | MaCuonSach → MaDauSach, STT, NgayNhap, NgayThanhLy, LyDo; MaDauSach, STT → MaCuonSach | MaCuonSach; (MaDauSach, STT) | Có |
| 16 PHIEU_MUON | MaPhieuMuon → MaDocGia, MaThuThu, NgayMuon | MaPhieuMuon | Có |
| 17 PHIEU_TRA | MaPhieuTra → MaDocGia, MaThuThu, NgayTra | MaPhieuTra | Có |
| 18 CT_MUON | MaPhieuMuon, MaCuonSach → HanTra, MaPhieuTra | (MaPhieuMuon, MaCuonSach) | Có |
| 19 PHIEU_PHAT | MaPhieuPhat → mọi thuộc tính; MaPhieuMuon, MaCuonSach → MaPhieuPhat | MaPhieuPhat; (MaPhieuMuon, MaCuonSach) | Có |
| 20 LOAI_PHONG | MaLoaiPhong → TenLoai, GiaMoiGio, SoGioToiThieu, SoGioToiDa; TenLoai → MaLoaiPhong | MaLoaiPhong, TenLoai | Có |
| 21 PHONG_DOC | MaPhongDoc → MaChiNhanh, MaLoaiPhong, TenPhong, SucChua; MaChiNhanh, TenPhong → MaPhongDoc | MaPhongDoc; (MaChiNhanh, TenPhong) | Có |
| 22 PHIEU_THUE_PHONG | MaPhieuThue → mọi thuộc tính | MaPhieuThue | Có |
| 23 CT_MUON_LUU_TRU | MaPhieuMuon, MaCuonSach → HanTra, MaPhieuTra, TienPhat | (MaPhieuMuon, MaCuonSach) | Có |

Trong quá trình xác định phụ thuộc hàm, nhóm có cân nhắc một số phụ thuộc nhưng không đưa vào tập F, vì các lý do sau:

- NGUOI: *Phuong → Quan*, *Quan → TinhTP* không đúng ở Việt Nam (nhiều quận/huyện có phường trùng tên, nhiều tỉnh có quận/huyện trùng tên), nên địa chỉ không gây phụ thuộc bắc cầu. Nếu nhóm quyết định coi chúng là PTH thì phải tách bảng PHUONG, QUAN, TINH.
- CUON_SACH: *MaGia → MaTheLoai* và *MaDauSach → MaTheLoai* đều đúng về nghiệp vụ, nhưng MaTheLoai không nằm trong CUON_SACH nên không vi phạm. Ràng buộc "giá và đầu sách cùng thể loại" là ràng buộc liên bảng, cài bằng trigger TRG6.
- CT_MUON: HanTra được tính từ NgayMuon và thể loại tại thời điểm mượn, nhưng sau đó là một giá trị được lưu lại tại lúc mượn (có thể gia hạn), không phải PTH trên các thuộc tính của CT_MUON.

## 3.4 Thuộc tính dẫn xuất được lưu

| Thuộc tính | Lý do lưu | Cách giữ đúng |
| --- | --- | --- |
| GIA_SACH.SoLuongHienCo | Đề yêu cầu "số lượng sách trên giá giảm/tăng" khi mượn/trả | Trigger TRG4 |
| PHIEU_PHAT.SoTien | Ảnh chụp số tiền tại thời điểm trả; phí phạt có thể đổi theo NgayApDung | Trigger TRG3 dùng fn_TinhTienPhat |
| PHIEU_THUE_PHONG.TongTien | Giá phòng có thể thay đổi sau khi đặt | Tính trong TX7 |
| CUON_SACH.TuoiThoConLaiThang | Trạng thái của cuốn, giảm theo thời gian và theo số lần mượn | Trigger TRG5 khi mượn; thủ tục sp_CapNhatTuoiTho do event ev_CapNhatTuoiTho gọi mỗi ngày |

## 3.5 Ví dụ quá trình chuẩn hóa từ dạng chưa chuẩn

Để minh họa phương pháp, xét "phiếu mượn" dạng giấy, ghi chung mọi thông tin:

PM(MaPhieuMuon, NgayMuon, MaDocGia, TenDocGia, SoDienThoai, MaThuThu, TenThuThu, {MaCuonSach, MaDauSach, TenSach, MaTheLoai, SoNgayMuon, HanTra})

**N1NF → 1NF.** Nhóm lặp {…} (một phiếu nhiều cuốn) và SoDienThoai đa trị vi phạm 1NF. Tách SĐT ra SDT_NGUOI; trải phẳng nhóm lặp, mỗi cuốn một dòng:

R(MaPhieuMuon, NgayMuon, MaDocGia, TenDocGia, MaThuThu, TenThuThu, MaCuonSach, MaDauSach, TenSach, MaTheLoai, SoNgayMuon, HanTra)

F = { MaPhieuMuon → NgayMuon, MaDocGia, MaThuThu;
      MaDocGia → TenDocGia;  MaThuThu → TenThuThu;
      MaCuonSach → MaDauSach;  MaDauSach → TenSach, MaTheLoai;  MaTheLoai → SoNgayMuon;
      MaPhieuMuon, MaCuonSach → HanTra }

**Tìm khóa** bằng thuật toán Closure: MaPhieuMuon và MaCuonSach không xuất hiện ở vế phải của PTH nào nên phải thuộc mọi khóa.
{MaPhieuMuon, MaCuonSach}⁺: khởi tạo {MaPhieuMuon, MaCuonSach} → thêm NgayMuon, MaDocGia, MaThuThu → TenDocGia, TenThuThu → MaDauSach → TenSach, MaTheLoai → SoNgayMuon → HanTra = toàn bộ R. Không tập con thực sự nào đủ ⇒ K = (MaPhieuMuon, MaCuonSach) là khóa duy nhất. Thuộc tính khóa: MaPhieuMuon, MaCuonSach.

**1NF → 2NF.** Có PTH bộ phận: MaPhieuMuon → NgayMuon, MaDocGia, MaThuThu (và theo bắc cầu TenDocGia, TenThuThu); MaCuonSach → MaDauSach (và TenSach, MaTheLoai, SoNgayMuon). Tách theo phần khóa mà chúng phụ thuộc:
- R1(MaPhieuMuon, NgayMuon, MaDocGia, TenDocGia, MaThuThu, TenThuThu)
- R2(MaCuonSach, MaDauSach, TenSach, MaTheLoai, SoNgayMuon)
- R3(MaPhieuMuon, MaCuonSach, HanTra)

**2NF → 3NF.** R1 có bắc cầu MaPhieuMuon → MaDocGia → TenDocGia và MaPhieuMuon → MaThuThu → TenThuThu; R2 có MaCuonSach → MaDauSach → MaTheLoai → SoNgayMuon. Theo cách 2 (tổng hợp từ phủ tối thiểu), mỗi PTH của phủ tối thiểu một lược đồ:
- PHIEU_MUON(MaPhieuMuon, NgayMuon, MaDocGia, MaThuThu)
- DOC_GIA(MaDocGia, TenDocGia), THU_THU(MaThuThu, TenThuThu)
- CUON_SACH(MaCuonSach, MaDauSach)
- DAU_SACH(MaDauSach, TenSach, MaTheLoai)
- THE_LOAI(MaTheLoai, SoNgayMuon)
- CT_MUON(MaPhieuMuon, MaCuonSach, HanTra) — chứa khóa K của R nên không cần thêm lược đồ khóa.

**3NF → BCNF.** Trong mỗi lược đồ trên, vế trái của mọi PTH đều là khóa của lược đồ đó ⇒ tất cả ở BCNF. Phép tách bảo toàn PTH (mỗi PTH nằm trọn trong một lược đồ) và kết nối không mất thông tin (CT_MUON chứa khóa của R). Kết quả trùng với các quan hệ 16, 18, 14, 10, 7 ở mục 3.2.

## 3.6 Ví dụ tìm phủ tối thiểu (thuật toán MinCover)

Phương án ban đầu của nhóm lưu cả MaTheLoai trong CUON_SACH, với tập PTH:

G = { MaCuonSach → MaDauSach, STT, MaTheLoai;  MaDauSach → MaTheLoai;  MaDauSach, STT → MaCuonSach;  MaDauSach, STT, MaTheLoai → MaCuonSach }

1. **Tách vế phải:** MaCuonSach → MaDauSach; MaCuonSach → STT; MaCuonSach → MaTheLoai; MaDauSach → MaTheLoai; MaDauSach, STT → MaCuonSach; MaDauSach, STT, MaTheLoai → MaCuonSach.
2. **Left-Reduce:** ở MaDauSach, STT, MaTheLoai → MaCuonSach, thử bỏ MaTheLoai: {MaDauSach, STT}⁺ = {MaDauSach, STT, MaCuonSach, MaTheLoai} chứa MaCuonSach ⇒ MaTheLoai thừa, PTH trở thành MaDauSach, STT → MaCuonSach (trùng PTH đã có). Ở MaDauSach, STT → MaCuonSach: {MaDauSach}⁺ = {MaDauSach, MaTheLoai}, {STT}⁺ = {STT}, đều không chứa MaCuonSach ⇒ không bỏ được.
3. **Nonredundant:** MaCuonSach → MaTheLoai: tính {MaCuonSach}⁺ trên G bỏ PTH này = {MaCuonSach, MaDauSach, STT, MaTheLoai} vẫn chứa MaTheLoai (bắc cầu qua MaDauSach) ⇒ loại.

**Phủ tối thiểu:** { MaCuonSach → MaDauSach; MaCuonSach → STT; MaDauSach → MaTheLoai; MaDauSach, STT → MaCuonSach }.

**Khóa:** {MaCuonSach}⁺ và {MaDauSach, STT}⁺ đều là toàn bộ lược đồ ⇒ hai khóa dự bị.

**Kiểm tra BCNF:** MaDauSach → MaTheLoai có vế trái không phải siêu khóa ⇒ vi phạm BCNF (cũng vi phạm 2NF, vì MaTheLoai là thuộc tính không khóa phụ thuộc bộ phận vào khóa (MaDauSach, STT)).

**Tách BCNF:** chọn PTH vi phạm MaDauSach → MaTheLoai, tính {MaDauSach}⁺ = {MaDauSach, MaTheLoai}: R1(MaDauSach, MaTheLoai) gộp vào DAU_SACH; R2 = CUON_SACH bỏ MaTheLoai. Đây là lý do thiết kế cuối cùng của CUON_SACH không có cột MaTheLoai; thể loại vẫn đọc được từ 2 ký tự đầu của mã.
