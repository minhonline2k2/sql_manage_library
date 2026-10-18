-- =====================================================================
-- 08_test.sql – Kiểm thử tự động 8 trigger, 7 transaction và ràng buộc
-- Chạy SAU 05_seed.sql. Mỗi ca chạy một lệnh và so kết quả với kỳ vọng:
--   'OK' = lệnh phải thành công; 'Exxx' = phải bị chặn với mã lỗi đó;
--   'CK' = phải bị chặn bởi một ràng buộc CHECK.
-- Ca kiểm tra giá trị chạy một câu SELECT trả 1 giá trị và so với kỳ vọng.
-- Kết quả ghi vào bảng KET_QUA_KIEM_THU (PASS/FAIL). Script làm thay đổi dữ liệu → chạy trên bản demo.
-- =====================================================================
SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;
USE QLTV;

DROP TABLE IF EXISTS KET_QUA_KIEM_THU;
CREATE TABLE KET_QUA_KIEM_THU (
  STT INT AUTO_INCREMENT PRIMARY KEY, MaCa VARCHAR(12), MoTa VARCHAR(200),
  KyVong VARCHAR(60), ThucTe VARCHAR(60), KetQua CHAR(4), ThongBao VARCHAR(300));

DELIMITER //
CREATE OR REPLACE PROCEDURE sp_KT_Lenh(IN p_Ma VARCHAR(12), IN p_MoTa VARCHAR(200), IN p_Lenh TEXT, IN p_KyVong VARCHAR(60))
BEGIN
  DECLARE v_Msg VARCHAR(300) DEFAULT '';
  DECLARE v_Tt VARCHAR(20) DEFAULT 'OK';
  BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
      GET DIAGNOSTICS CONDITION 1 v_Msg = MESSAGE_TEXT;
      SET v_Tt = CASE WHEN v_Msg REGEXP '^E[0-9]{3}:' THEN LEFT(v_Msg, 4)
                      WHEN v_Msg LIKE 'CONSTRAINT%' THEN 'CK' ELSE 'SQL' END;
      ROLLBACK;
    END;
    SET @kt_sql = p_Lenh;
    PREPARE kt FROM @kt_sql; EXECUTE kt; DEALLOCATE PREPARE kt;
  END;
  INSERT INTO KET_QUA_KIEM_THU(MaCa, MoTa, KyVong, ThucTe, KetQua, ThongBao)
  VALUES (p_Ma, p_MoTa, p_KyVong, v_Tt, IF(v_Tt = p_KyVong, 'PASS', 'FAIL'), v_Msg);
END //

CREATE OR REPLACE PROCEDURE sp_KT_GiaTri(IN p_Ma VARCHAR(12), IN p_MoTa VARCHAR(200), IN p_Select TEXT, IN p_KyVong VARCHAR(60))
BEGIN
  SET @kt_sql = CONCAT('SELECT (', p_Select, ') INTO @kt_v');
  PREPARE kt FROM @kt_sql; EXECUTE kt; DEALLOCATE PREPARE kt;
  INSERT INTO KET_QUA_KIEM_THU(MaCa, MoTa, KyVong, ThucTe, KetQua)
  VALUES (p_Ma, p_MoTa, p_KyVong, CAST(@kt_v AS CHAR), IF(CAST(@kt_v AS CHAR) = p_KyVong, 'PASS', 'FAIL'));
END //
DELIMITER ;

-- Ngày thao tác kiểm thử (sau kỳ dữ liệu)
SET @d = '2026-10-05';
-- Độc giả "sạch" ở CN02: thẻ còn hạn, không giữ sách, không nợ  → dùng cho các ca mượn/trả
SELECT d.MaNguoi INTO @dg FROM DOC_GIA d JOIN THE_DOC_GIA t ON t.MaDocGia = d.MaNguoi
WHERE d.MaChiNhanh = 'CN02' AND t.NgayHetHan > '2026-12-31' AND fn_SoSachDangMuon(d.MaNguoi) = 0 AND fn_NoPhat(d.MaNguoi) = 0
ORDER BY d.MaNguoi LIMIT 1;
SELECT d.MaNguoi INTO @dg2 FROM DOC_GIA d JOIN THE_DOC_GIA t ON t.MaDocGia = d.MaNguoi
WHERE d.MaChiNhanh = 'CN02' AND t.NgayHetHan > '2026-12-31' AND fn_SoSachDangMuon(d.MaNguoi) = 0 AND fn_NoPhat(d.MaNguoi) = 0
  AND d.MaNguoi <> @dg ORDER BY d.MaNguoi LIMIT 1;
-- độc giả không giữ sách nhưng còn nợ phạt (từ dữ liệu 3 tháng)
SELECT MaNguoi INTO @dg_no FROM DOC_GIA WHERE fn_SoSachDangMuon(MaNguoi) = 0 AND fn_NoPhat(MaNguoi) > 0 LIMIT 1;
SELECT 'TT006' INTO @tt;
-- 11 cuốn đang trên giá ở CN02, tuổi thọ > 1
SELECT JSON_ARRAYAGG(MaCuonSach) INTO @ds11 FROM (
  SELECT cs.MaCuonSach FROM CUON_SACH cs JOIN GIA_SACH g ON g.MaGia = cs.MaGia JOIN PHONG_KHO k ON k.MaPhongKho = g.MaPhongKho
  WHERE k.MaChiNhanh = 'CN02' AND cs.TrangThai = 'TrenGia' AND cs.TuoiThoConLaiThang > 1 ORDER BY cs.MaCuonSach LIMIT 11) x;
SET @ds10 = JSON_REMOVE(@ds11, '$[10]');
SET @c1 = JSON_UNQUOTE(JSON_EXTRACT(@ds10, '$[0]'));
SET @c11 = JSON_UNQUOTE(JSON_EXTRACT(@ds11, '$[10]'));
SELECT MaGia, TuoiThoConLaiThang INTO @gia_c1, @tt_c1 FROM CUON_SACH WHERE MaCuonSach = @c1;
SELECT SoLuongHienCo INTO @sl_gia FROM GIA_SACH WHERE MaGia = @gia_c1;
-- số cuốn trong 10 cuốn sẽ mượn nằm cùng giá với @c1, và trong 2 cuốn sẽ trả
SELECT COUNT(*) INTO @n_muon FROM CUON_SACH cs JOIN JSON_TABLE(@ds10, '$[*]' COLUMNS (Ma VARCHAR(10) CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci PATH '$')) j ON j.Ma = cs.MaCuonSach WHERE cs.MaGia = @gia_c1;
SELECT COUNT(*) INTO @n_tra FROM CUON_SACH WHERE MaGia = @gia_c1 AND MaCuonSach IN (@c1, JSON_UNQUOTE(JSON_EXTRACT(@ds10, '$[1]')));

-- ===== TX1 + TRG1, TRG2, TRG4, TRG5 =====================================
CALL sp_KT_Lenh('TX1-a', 'Mượn 11 cuốn trong 1 phiếu bị chặn',
  CONCAT('CALL sp_MuonSach(', QUOTE(@dg), ',', QUOTE(@tt), ',', QUOTE(@ds11), ',', QUOTE(@d), ',@pm)'), 'E101');
CALL sp_KT_GiaTri('TX1-b', 'Sau khi bị chặn không có phiếu mượn nào được tạo (ROLLBACK)',
  CONCAT('SELECT COUNT(*) FROM PHIEU_MUON WHERE MaDocGia = ', QUOTE(@dg), ' AND NgayMuon = ', QUOTE(@d)), '0');
CALL sp_KT_Lenh('TX1-c', 'Mượn đúng 10 cuốn hợp lệ',
  CONCAT('CALL sp_MuonSach(', QUOTE(@dg), ',', QUOTE(@tt), ',', QUOTE(@ds10), ',', QUOTE(@d), ',@pm)'), 'OK');
CALL sp_KT_Lenh('TRG1', 'Chèn trực tiếp cuốn thứ 11 vào phiếu đã có 10 cuốn',
  CONCAT('INSERT INTO CT_MUON(MaPhieuMuon, MaCuonSach, HanTra) VALUES (@pm, ', QUOTE(@c11), ', ''2026-10-20'')'), 'E101');
CALL sp_KT_GiaTri('TRG4-a', 'Số lượng trên giá giảm đúng bằng số cuốn của giá đó vừa được mượn',
  CONCAT('SELECT SoLuongHienCo FROM GIA_SACH WHERE MaGia = ', QUOTE(@gia_c1)), CAST(@sl_gia - @n_muon AS CHAR));
CALL sp_KT_GiaTri('TRG5', 'Tuổi thọ cuốn sách giảm 1 tháng sau khi mượn',
  CONCAT('SELECT TuoiThoConLaiThang FROM CUON_SACH WHERE MaCuonSach = ', QUOTE(@c1)), CAST(@tt_c1 - 1 AS CHAR));
CALL sp_KT_GiaTri('TX1-d', 'Hạn trả = ngày mượn + số ngày mượn của thể loại/đầu sách',
  CONCAT('SELECT HanTra = fn_HanTra(', QUOTE(@c1), ', ', QUOTE(@d), ') FROM CT_MUON WHERE MaPhieuMuon = @pm AND MaCuonSach = ', QUOTE(@c1)), '1');
CALL sp_KT_Lenh('TRG2-a', 'Mượn cuốn đang được người khác mượn',
  CONCAT('CALL sp_MuonSach(', QUOTE(@dg2), ', ', QUOTE(@tt), ', JSON_ARRAY(', QUOTE(@c1), '), ', QUOTE(@d), ', @x)'), 'E104');
CALL sp_KT_Lenh('TRG2-b', 'Độc giả DG0001 đang giữ 50 cuốn mượn thêm 1 cuốn',
  CONCAT('CALL sp_MuonSach(''DG0001'', ''TT002'', JSON_ARRAY((SELECT cs.MaCuonSach FROM CUON_SACH cs JOIN GIA_SACH g ON g.MaGia=cs.MaGia ',
         'WHERE g.MaPhongKho LIKE ''CN01%'' AND cs.TrangThai=''TrenGia'' LIMIT 1)), ''2026-09-20'', @x)'), 'E102');

-- ===== TX2 + TRG3, TRG4 ===================================================
CALL sp_KT_Lenh('TX2-a', 'Trả cuốn mà độc giả không mượn',
  CONCAT('CALL sp_TraSach(', QUOTE(@dg), ',', QUOTE(@tt), ', JSON_ARRAY(''XX0000-001''), ', QUOTE(@d), ', @pt, @phat)'), 'E108');
CALL sp_KT_Lenh('TX2-b', 'Trả muộn 5 ngày 2 cuốn (1 phiếu trả, nhiều cuốn)',
  CONCAT('CALL sp_TraSach(', QUOTE(@dg), ',', QUOTE(@tt), ', JSON_ARRAY(', QUOTE(@c1), ', JSON_UNQUOTE(JSON_EXTRACT(', QUOTE(@ds10), ', ''$[1]''))), ',
         'DATE_ADD((SELECT HanTra FROM CT_MUON WHERE MaPhieuMuon = @pm AND MaCuonSach = ', QUOTE(@c1), '), INTERVAL 5 DAY), @pt, @phat)'), 'OK');
CALL sp_KT_GiaTri('TRG3-a', 'Phiếu phạt tự lập cho cuốn trả muộn, tiền = cơ bản + 5 × phạt/ngày',
  CONCAT('SELECT pp.SoTien = bp.PhatCoBan + 5 * bp.PhatMoiNgay FROM PHIEU_PHAT pp JOIN BANG_PHI_PHAT bp ON bp.MaTheLoai = LEFT(pp.MaCuonSach, 2) ',
         'AND bp.NgayApDung = (SELECT MAX(NgayApDung) FROM BANG_PHI_PHAT WHERE MaTheLoai = LEFT(pp.MaCuonSach,2)) WHERE pp.MaPhieuMuon = @pm AND pp.MaCuonSach = ', QUOTE(@c1)), '1');
CALL sp_KT_GiaTri('TRG4-b', 'Số lượng trên giá tăng đúng bằng số cuốn của giá đó vừa được trả',
  CONCAT('SELECT SoLuongHienCo FROM GIA_SACH WHERE MaGia = ', QUOTE(@gia_c1)), CAST(@sl_gia - @n_muon + @n_tra AS CHAR));
CALL sp_KT_Lenh('TRG3-b', 'Sửa phiếu trả của dòng mượn đã trả',
  CONCAT('UPDATE CT_MUON SET MaPhieuTra = 1 WHERE MaPhieuMuon = @pm AND MaCuonSach = ', QUOTE(@c1)), 'E106');
CALL sp_KT_Lenh('TRG3-c', 'Ngày trả trước ngày mượn',
  CONCAT('CALL sp_TraSach(', QUOTE(@dg), ',', QUOTE(@tt), ', JSON_ARRAY(JSON_UNQUOTE(JSON_EXTRACT(', QUOTE(@ds10), ', ''$[2]''))), ''2026-10-01'', @pt2, @phat2)'), 'E105');

-- ===== TX3 =============================================================
CALL sp_KT_Lenh('TX7-a', 'Độc giả còn nợ phạt thuê phòng bị chặn',
  CONCAT('CALL sp_ThuePhong(', QUOTE(@dg), ', ''CN02-N1'', ', QUOTE(@tt), ', ''2026-10-08 09:00'', ''2026-10-08 11:00'', 4, ', QUOTE(@d), ', @t, @tien)'), 'E110');
CALL sp_KT_Lenh('TRG8-b', 'Xóa độc giả không giữ sách nhưng còn nợ tiền phạt', CONCAT('CALL sp_DocGia_Xoa(', QUOTE(@dg_no), ')'), 'E405');
CALL sp_KT_Lenh('TX3-a', 'Thanh toán phạt', CONCAT('CALL sp_ThanhToanPhat(', QUOTE(@dg), ',', QUOTE(@d), ', @tien)'), 'OK');
CALL sp_KT_Lenh('TX3-b', 'Thanh toán khi không còn khoản nợ', CONCAT('CALL sp_ThanhToanPhat(', QUOTE(@dg), ',', QUOTE(@d), ', @tien)'), 'E109');

-- ===== TX7 + TRG7 =======================================================
CALL sp_KT_Lenh('TX7-b', 'Thuê phòng nhóm 2 giờ hợp lệ',
  CONCAT('CALL sp_ThuePhong(', QUOTE(@dg), ', ''CN02-N1'', ', QUOTE(@tt), ', ''2026-10-08 09:00'', ''2026-10-08 11:00'', 4, ', QUOTE(@d), ', @t, @tien)'), 'OK');
CALL sp_KT_GiaTri('TX7-c', 'Tiền thuê = 2 giờ × 50.000đ', 'SELECT TongTien FROM PHIEU_THUE_PHONG WHERE MaPhieuThue = @t', '100000');
CALL sp_KT_Lenh('TRG7', 'Thuê trùng khung giờ 10:00–12:00',
  CONCAT('CALL sp_ThuePhong(', QUOTE(@dg2), ', ''CN02-N1'', ', QUOTE(@tt), ', ''2026-10-08 10:00'', ''2026-10-08 12:00'', 4, ', QUOTE(@d), ', @t2, @tien2)'), 'E201');
CALL sp_KT_Lenh('TX7-d', 'Số người vượt sức chứa',
  CONCAT('CALL sp_ThuePhong(', QUOTE(@dg), ', ''CN02-N2'', ', QUOTE(@tt), ', ''2026-10-09 09:00'', ''2026-10-09 10:00'', 99, ', QUOTE(@d), ', @t3, @tien3)'), 'E202');
CALL sp_KT_Lenh('TX7-e', 'Thuê phòng hội thảo 1 giờ (tối thiểu 2 giờ)',
  CONCAT('CALL sp_ThuePhong(', QUOTE(@dg), ', ''CN02-H1'', ', QUOTE(@tt), ', ''2026-10-09 09:00'', ''2026-10-09 10:00'', 20, ', QUOTE(@d), ', @t4, @tien4)'), 'E203');
CALL sp_KT_Lenh('CK-THUE', 'Thuê lẻ phút (CHECK giờ tròn)',
  CONCAT('CALL sp_ThuePhong(', QUOTE(@dg), ', ''CN02-N3'', ', QUOTE(@tt), ', ''2026-10-09 09:30'', ''2026-10-09 11:30'', 4, ', QUOTE(@d), ', @t5, @tien5)'), 'CK');

-- ===== TX6 + TRG8 =======================================================
CALL sp_KT_Lenh('TX6-a', 'Đăng ký độc giả mới với 2 số điện thoại',
  'CALL sp_DangKyDocGia(''Trần'',''Minh'',''Khôi'',''1999-03-15'',''M'',''5'',''Dịch Vọng'',''Cầu Giấy'',''Hà Nội'',''khoi.test@gmail.com'',''["0911111111","0922222222"]'',''CN01'',''2026-10-05'',@ma,@the)', 'OK');
CALL sp_KT_GiaTri('TX6-b', 'Độc giả mới có thẻ hết hạn sau 1 năm', 'SELECT NgayHetHan FROM THE_DOC_GIA WHERE MaDocGia = @ma', '2027-10-05');
SELECT COUNT(*) INTO @so_nguoi FROM NGUOI;
CALL sp_KT_Lenh('TX6-c', 'Đăng ký với số điện thoại sai định dạng',
  'CALL sp_DangKyDocGia(''Lê'',NULL,''Na'',''2001-01-01'',''F'',NULL,NULL,NULL,''Hà Nội'',NULL,''["0911111112","12345"]'',''CN01'',''2026-10-05'',@ma2,@the2)', 'CK');
CALL sp_KT_GiaTri('TX6-d', 'Sau lỗi SĐT không còn bản ghi NGUOI nào được thêm (ROLLBACK)', 'SELECT COUNT(*) FROM NGUOI', CAST(@so_nguoi AS CHAR));
CALL sp_KT_Lenh('TX6-e', 'Đăng ký không có số điện thoại',
  'CALL sp_DangKyDocGia(''Lê'',NULL,''Na'',''2001-01-01'',''F'',NULL,NULL,NULL,''Hà Nội'',NULL,''[]'',''CN01'',''2026-10-05'',@ma3,@the3)', 'E408');
CALL sp_KT_Lenh('TRG8-a', 'Xóa độc giả DG0001 đang giữ sách', 'CALL sp_DocGia_Xoa(''DG0001'')', 'E404');
CALL sp_KT_Lenh('TRG8-c', 'Sửa mã độc giả', 'UPDATE DOC_GIA SET MaNguoi = ''DG9999'' WHERE MaNguoi = ''DG0002''', 'E406');
CALL sp_KT_Lenh('TRG8-d', 'Xóa độc giả mới đăng ký (không giữ sách, không nợ)', 'CALL sp_DocGia_Xoa(@ma)', 'OK');

-- ===== TX4 + TRG6 =======================================================
CALL sp_KT_Lenh('TX4-a', 'Nhập lô 3 cuốn đầu sách mới vào giá đúng thể loại',
  'CALL sp_NhapLoSach(''TR0901'',''Dế Mèn phiêu lưu ký'',''NXB Kim Đồng'',2020,NULL,''["Tô Hoài"]'',3,''CN01-K1-TR1'',''2026-10-05'',@sl)', 'OK');
CALL sp_KT_GiaTri('TX4-b', 'Mã cuốn sinh đúng định dạng đầu sách + STT',
  'SELECT GROUP_CONCAT(MaCuonSach ORDER BY STT) FROM CUON_SACH WHERE MaDauSach = ''TR0901''', 'TR0901-001,TR0901-002,TR0901-003');
CALL sp_KT_Lenh('TX4-c', 'Nhập sách tham khảo vào giá truyện',
  'CALL sp_NhapLoSach(''TK0901'',''Sổ tay kiểm thử'',NULL,2024,NULL,''["Ban biên tập"]'',2,''CN01-K1-TR1'',''2026-10-05'',@sl)', 'E301');
CALL sp_KT_GiaTri('TX4-d', 'Đầu sách TK0901 không được tạo vì giao dịch bị ROLLBACK',
  'SELECT COUNT(*) FROM DAU_SACH WHERE MaDauSach = ''TK0901''', '0');
CALL sp_KT_Lenh('TRG6-a', 'Chuyển cuốn truyện sang giá tham khảo', 'CALL sp_CuonSach_ChuyenGia(''TR0901-001'', ''CN01-K1-TK1'')', 'E301');
UPDATE GIA_SACH g SET g.SucChua = (SELECT COUNT(*) FROM CUON_SACH c WHERE c.MaGia = g.MaGia) WHERE g.MaGia = 'CN01-K1-TR1';
CALL sp_KT_Lenh('TRG6-b', 'Nhập thêm vào giá đã đầy',
  'CALL sp_NhapLoSach(''TR0901'',NULL,NULL,NULL,NULL,NULL,1,''CN01-K1-TR1'',''2026-10-05'',@sl)', 'E304');
UPDATE GIA_SACH SET SucChua = 100 WHERE MaGia = 'CN01-K1-TR1';
CALL sp_KT_Lenh('CK-DAUSACH', 'Đầu sách mã TK nhưng thể loại TR (CHECK)',
  'INSERT INTO DAU_SACH(MaDauSach, MaTheLoai, TenSach) VALUES (''TK0999'', ''TR'', ''Sai'')', 'CK');

-- ===== TX5 + TRG6 (tự chuyển ChoThanhLy) =================================
UPDATE CUON_SACH SET TuoiThoConLaiThang = 0 WHERE MaCuonSach = 'TR0901-003';
CALL sp_KT_GiaTri('TRG6-c', 'Cuốn trên giá hết tuổi thọ tự chuyển ChoThanhLy',
  'SELECT TrangThai FROM CUON_SACH WHERE MaCuonSach = ''TR0901-003''', 'ChoThanhLy');
CALL sp_KT_Lenh('TX5-a', 'Thanh lý sách hết niên hạn', 'CALL sp_ThanhLySach(''2026-10-05'', @sotl)', 'OK');
CALL sp_KT_GiaTri('TX5-b', 'Cuốn đã chuyển sang SACH_THANH_LY và rời khỏi CUON_SACH',
  'SELECT CONCAT((SELECT COUNT(*) FROM SACH_THANH_LY WHERE MaCuonSach=''TR0901-003''), (SELECT COUNT(*) FROM CUON_SACH WHERE MaCuonSach=''TR0901-003''))', '10');

-- ===== Toàn vẹn tổng thể =================================================
CALL sp_KT_GiaTri('TV-1', 'SoLuongHienCo của mọi giá khớp số cuốn không đang mượn',
  'SELECT COUNT(*) FROM GIA_SACH g WHERE g.SoLuongHienCo <> (SELECT COUNT(*) FROM CUON_SACH c WHERE c.MaGia = g.MaGia AND c.TrangThai <> ''DangMuon'')', '0');
CALL sp_KT_GiaTri('TV-2', 'Không độc giả nào giữ quá 50 cuốn', 'SELECT MAX(fn_SoSachDangMuon(MaNguoi)) <= 50 FROM DOC_GIA', '1');
CALL sp_KT_GiaTri('TV-3', 'Không phiếu mượn nào quá 10 cuốn',
  'SELECT COUNT(*) FROM (SELECT MaPhieuMuon FROM CT_MUON GROUP BY MaPhieuMuon HAVING COUNT(*) > 10) x', '0');
CALL sp_KT_GiaTri('TV-4', 'Không có 2 lượt thuê đã duyệt trùng giờ cùng phòng',
  'SELECT COUNT(*) FROM PHIEU_THUE_PHONG a JOIN PHIEU_THUE_PHONG b ON a.MaPhongDoc=b.MaPhongDoc AND a.MaPhieuThue<b.MaPhieuThue AND a.TrangThai=''DaDuyet'' AND b.TrangThai=''DaDuyet'' AND a.BatDau<b.KetThuc AND a.KetThuc>b.BatDau', '0');

SELECT MaCa, KetQua, KyVong, ThucTe, MoTa FROM KET_QUA_KIEM_THU ORDER BY STT;
SELECT KetQua, COUNT(*) AS SoCa FROM KET_QUA_KIEM_THU GROUP BY KetQua;
