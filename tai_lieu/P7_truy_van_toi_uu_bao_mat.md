# P7. Truy vấn báo cáo, tối ưu, bảo mật và kiểm thử

## 4.x Truy vấn hiển thị theo yêu cầu đề

Mỗi yêu cầu được cài đặt bằng một VIEW (tái sử dụng) và một procedure `sp_BC_*` có tham số chi nhánh (NULL = toàn hệ thống) để sắp xếp đúng yêu cầu. Ký hiệu đại số quan hệ theo chương 4: σ chọn, π chiếu, ⋈ kết nối tự nhiên, ⟕ kết nối ngoài trái, ∪ hợp, − trừ; phép gom nhóm γ và sắp xếp τ là phép mở rộng dùng để biểu diễn GROUP BY, ORDER BY.

Viết tắt: CT = CT_MUON, PM = PHIEU_MUON, CS = CUON_SACH, DS = DAU_SACH, TL = THE_LOAI, DG = DOC_GIA, N = NGUOI, PP = PHIEU_PHAT, LT = CT_MUON_LUU_TRU, STL = SACH_THANH_LY, TT = THU_THU, PD = PHONG_DOC, TP = PHIEU_THUE_PHONG.

| # | Yêu cầu | Đối tượng SQL | Biểu thức đại số quan hệ |
| --- | --- | --- | --- |
| 1 | Sách đang được mượn, sắp theo hạn trả | `v_SachDangMuon`, `sp_BC_SachDangMuon(p_MaChiNhanh)` | τ_HanTra( π_MaCuonSach, TenSach, MaDocGia, HoTen, NgayMuon, HanTra( σ_MaPhieuTra = NULL( CT ⋈ PM ⋈ CS ⋈ DS ⋈ DG ⋈ N ) ) ) |
| 1b | Sách đã được mượn trong khoảng [từ, đến] (cả đã trả và chưa trả), sắp theo hạn trả | `sp_BC_SachDaMuon(p_MaChiNhanh, p_TuNgay, p_DenNgay)` | τ_HanTra( π_MaCuonSach, TenSach, MaDocGia, HoTen, NgayMuon, HanTra, NgayTra( σ_TuNgay ≤ NgayMuon ≤ DenNgay( CT ⋈ PM ⋈ CS ⋈ DS ⋈ DG ⋈ N ) ⟕ PT ) ) |
| 2 | Sách quá hạn, sắp theo số ngày quá hạn | `sp_BC_SachQuaHan(p_MaChiNhanh, p_Ngay)` | τ_SoNgayQuaHan↓( π_…, SoNgayQuaHan = p_Ngay − HanTra( σ_MaPhieuTra = NULL ∧ HanTra < p_Ngay( CT ⋈ PM ⋈ CS ⋈ DS ⋈ DG ⋈ N ) ) ) |
| 3 | Đầu sách theo lượt mượn nhiều nhất | `v_LuotMuonDauSach`, `sp_BC_DauSachLuotMuon(p_MaChiNhanh)` | M = π_MaPhieuMuon, MaDauSach(CT ⋈ CS) ∪ π_MaPhieuMuon, MaDauSach(LT ⋈ STL); τ_LuotMuon↓( DS ⟕ γ_MaDauSach; COUNT(*)→LuotMuon( M ⋈ PM ⋈ TT ) ) |
| 4 | Độc giả trả muộn, sắp theo tổng phạt rồi số sách trả muộn | `v_PhatTraMuon`, `sp_BC_DocGiaTraMuon(p_MaChiNhanh)` | P = π_MaDocGia, SoTien(PP ⋈ PM) ∪ π_MaDocGia, TienPhat(σ_TienPhat > 0(LT ⋈ PM)); τ_TongPhat↓, SoSach↓( γ_MaDocGia; SUM(SoTien)→TongPhat, COUNT(*)→SoSach(P) ⋈ N ) |
| 5 | Sách sắp hết hạn sử dụng (dưới 2 năm) | `v_SachSapHetHan`, `sp_BC_SachSapHetHan(p_MaChiNhanh)` | τ_TuoiTho( π_MaCuonSach, TenSach, MaChiNhanh, TuoiThoConLaiThang( σ_TuoiThoConLaiThang < 24( CS ⋈ DS ⋈ GIA_SACH ⋈ PHONG_KHO ) ) ) |
| 6 | Phòng đọc có / chưa có người dùng tại một thời điểm t | `sp_BC_PhongTaiThoiDiem(p_MaChiNhanh, p_ThoiDiem)` | Đang dùng: D = π_MaPhongDoc( σ_TrangThai='DaDuyet' ∧ BatDau ≤ t < KetThuc(TP) ); Trống: π_MaPhongDoc(PD) − D. SQL dùng PD ⟕ σ_…(TP) để trả cả hai nhóm trong một bảng. |

Cách hiểu yêu cầu 1: đề ghi "danh sách sách đã được mượn, sắp xếp theo thời gian hạn trả". Vì chỉ sách chưa trả mới còn ý nghĩa theo dõi hạn trả, nhóm lấy cách hiểu chính là sách đang được mượn (σ MaPhieuTra = NULL, procedure `sp_BC_SachDangMuon`). Để không bỏ sót cách hiểu theo nghĩa rộng (mọi lượt mượn, kể cả đã trả), nhóm cài đặt thêm `sp_BC_SachDaMuon` có lọc theo khoảng ngày mượn; trên giao diện, ô "Chỉ sách đang được mượn (chưa trả)" chuyển giữa hai cách hiểu (Hình 4.1 và 4.1b).

Ghi chú: báo cáo 3 và 4 hợp (∪) thêm dữ liệu từ bảng lưu trữ để lượt mượn và tiền phạt của các cuốn đã thanh lý không bị mất khỏi thống kê. Ví dụ phạt dự kiến của báo cáo 2: sách tham khảo quá hạn 84 ngày = 200.000 + 30.000 × 84 = 2.720.000đ.

## 4.y Tối ưu truy vấn bằng chỉ mục

InnoDB tự tạo chỉ mục cho PK, UNIQUE và mọi khóa ngoại. Nhóm bổ sung 6 chỉ mục phục vụ điều kiện lọc và sắp xếp:

| Chỉ mục | Phục vụ |
| --- | --- |
| IX_CTMUON_ChuaTra_HanTra (MaPhieuTra, HanTra) | Báo cáo 1, 2; fn_SoSachDangMuon trong TRG2 |
| IX_CUONSACH_TuoiTho (TuoiThoConLaiThang) | Báo cáo 5 |
| IX_THUE_Phong_ThoiGian (MaPhongDoc, TrangThai, BatDau, KetThuc) | TRG7 kiểm tra trùng giờ; báo cáo 6 |
| IX_PHIEUPHAT_ChuaTT (DaThanhToan) | fn_NoPhat, TX3 |
| IX_NGUOI_Ten, IX_DAUSACH_TenSach | Tìm kiếm độc giả, đầu sách |

Kết quả `EXPLAIN` đo trên dữ liệu 3 tháng:

| Truy vấn | Trước khi có chỉ mục | Sau khi có chỉ mục |
| --- | --- | --- |
| Sách đang mượn sắp theo hạn trả | Bắt đầu từ DOC_GIA (quét index 200 dòng), *Using temporary; Using filesort* | Bắt đầu từ CT_MUON qua IX_CTMUON_ChuaTra_HanTra (ref const, 452 dòng, *Using index*), không còn bảng tạm và sắp xếp ngoài |
| Sách tuổi thọ < 24 tháng | type ALL, quét 1.369 dòng | type range trên IX_CUONSACH_TuoiTho, chỉ đọc các cuốn có tuổi thọ dưới 24 tháng (khoảng 150 dòng) |

## 4.z An toàn bảo mật

- Hai vai trò: r_ThuThu (thực thi các procedure nghiệp vụ hằng ngày, tra cứu, 6 báo cáo; SELECT 2 view) và r_QuanLy (kế thừa r_ThuThu, thực thi mọi procedure và đọc mọi bảng).
- Không cấp quyền INSERT/UPDATE/DELETE trên bảng cho ai: mọi thay đổi đi qua procedure (SQL SECURITY DEFINER), nên trigger, ràng buộc và kiểm tra trong transaction không thể bị bỏ qua. MariaDB không có DENY, nên nguyên tắc là cấp quyền tối thiểu.
- Tài khoản mẫu: `tt_cn01` (r_ThuThu), `ql_thuvien` (r_QuanLy). Kiểm chứng: `tt_cn01` gọi `sp_BC_SachSapHetHan` thành công, nhưng `SELECT … FROM CUON_SACH` bị từ chối (ERROR 1142).

## 4.t Kiểm thử ràng buộc, trigger và transaction

File `08_test.sql` gồm 52 ca kiểm thử tự động. Mỗi ca chạy một lệnh thông qua thủ tục kiểm thử (dùng dynamic SQL và EXIT HANDLER để bắt lỗi), so mã lỗi hoặc giá trị thực tế với kết quả mong đợi rồi ghi vào bảng KET_QUA_KIEM_THU. Cả 52 ca đều đạt. Bảng dưới tóm tắt theo nhóm, chi tiết từng ca ở cuối mục.

| Nhóm | Ca hợp lệ | Ca bị chặn / kiểm tra |
| --- | --- | --- |
| TRG1 + TX1 | Mượn đúng 10 cuốn | 11 cuốn qua TX1 → E101 và không phiếu nào được tạo (ROLLBACK); chèn tay cuốn thứ 11 → E101; danh sách có mã cuốn bị lặp → E104 |
| TRG2 | — | Mượn cuốn đang được mượn → E104; DG0001 đang giữ 50 cuốn mượn thêm → E102 |
| TRG3 + TX2 | Trả muộn 5 ngày 2 cuốn trong 1 phiếu trả; phiếu phạt = cơ bản + 5 × phạt/ngày | Trả cuốn không mượn → E108; sửa phiếu trả đã trả → E106; ngày trả trước ngày mượn → E105 |
| TRG4 | Số lượng trên giá giảm/tăng đúng bằng số cuốn của giá đó được mượn/trả | Toàn hệ thống: SoLuongHienCo khớp 100% |
| TRG5 | Tuổi thọ giảm 1 tháng sau khi mượn | — |
| TRG6 + TX4 | Nhập lô 3 cuốn, mã TR0901-001…003; cuốn hết tuổi thọ tự chuyển ChoThanhLy | Sách TK vào giá TR → E301 và đầu sách mới không được tạo (ROLLBACK); giá đầy → E304; chuyển giá sai thể loại → E301 |
| TX5 | Thanh lý: cuốn chuyển sang SACH_THANH_LY, rời CUON_SACH | — |
| TRG7 + TX7 | Thuê 2 giờ = 100.000đ | Trùng giờ → E201; vượt sức chứa → E202; hội thảo 1 giờ → E203; còn nợ phạt → E110; lẻ phút → CHECK |
| Báo giá thuê phòng | Hội thảo 3 giờ = 900.000đ; mọi lượt thuê đã lưu có tiền khớp công thức báo giá | — |
| Tuổi thọ theo thời gian | Hai tháng sau ngày nhập, cuốn truyện còn 180 − 2 = 178 tháng | Chạy lại với ngày sớm hơn không làm tuổi thọ tăng lên |
| TRG8 | Xóa độc giả không giữ sách, không nợ | Đang giữ sách → E404; còn nợ phạt → E405; sửa mã → E406 |
| TX3 | Thanh toán phạt | Không còn nợ → E109 |
| TX6 | Đăng ký với 2 SĐT, thẻ hết hạn sau 1 năm | SĐT sai → CHECK và không còn bản ghi NGUOI (ROLLBACK); không có SĐT → E408 |
| Ràng buộc | — | Đầu sách mã TK nhưng thể loại TR → CHECK; không phiếu > 10 cuốn; không độc giả > 50 cuốn; không 2 lượt thuê trùng giờ |

## Bảng mã lỗi nghiệp vụ

| Mã | Ý nghĩa | Nơi phát sinh |
| --- | --- | --- |
| E100 | Phiếu mượn/trả không có cuốn nào | TX1, TX2 |
| E101 | Quá 10 cuốn mỗi lần mượn | TRG1, TX1 |
| E102 | Độc giả đã giữ 50 cuốn | TRG2 |
| E103 | Thẻ hết hạn | TX1, TX7 |
| E104 | Cuốn không có trên giá, hoặc bị lặp trong danh sách mượn | TRG2, TX1 |
| E105 | Ngày trả trước ngày mượn | TRG3 |
| E106 | Sửa phiếu trả của dòng đã trả | TRG3 |
| E107 | Phiếu trả và phiếu mượn khác độc giả | TRG3 |
| E108 | Cuốn không do độc giả mượn hoặc đã trả | TX2 |
| E109 | Không có khoản phạt chưa thanh toán | TX3 |
| E110 | Còn nợ phạt, không được thuê phòng | TX7 |
| E201 | Phòng trùng giờ | TRG7 |
| E202 | Vượt sức chứa phòng | TX7 |
| E203 | Số giờ thuê sai quy định loại phòng | TX7 |
| E204 | Ngoài giờ mở cửa chi nhánh | TX7 |
| E205 | Không tìm thấy phòng | TX7 |
| E301 | Giá chỉ chứa sách cùng thể loại | TRG6 |
| E302 | Đầu sách còn cuốn, không xóa được | sp_DauSach_Xoa |
| E303 | Cuốn đã có lịch sử mượn, phải thanh lý | sp_CuonSach_Xoa |
| E304 | Giá sách đã đầy | TRG6 |
| E305 | Sửa mã cuốn sách | TRG6 |
| E306 | Số lượng nhập < 1 | TX4 |
| E401 | Thủ thư trưởng không thuộc chi nhánh | sp_ChiNhanh_Sua |
| E402 | Không tìm thấy / độc giả bị khóa | nhiều procedure |
| E403 | Xóa thủ thư đang là trưởng chi nhánh | sp_ThuThu_Xoa |
| E404 | Xóa độc giả còn giữ sách | TRG8 |
| E405 | Xóa độc giả còn nợ phạt | TRG8 |
| E406 | Sửa mã độc giả | TRG8 |
| E407 | Bảng con ISA không khớp LoaiNguoi | TRG8 |
| E408 | Độc giả phải có ít nhất 1 SĐT | TX6 |
