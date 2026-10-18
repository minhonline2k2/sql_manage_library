# Giao diện tối giản – Hệ thống quản lý thư viện

Chỉ gọi stored procedure / view của CSDL `QLTV`; mọi luật nghiệp vụ nằm trong MariaDB.

    pip install streamlit pymysql pandas
    # tùy chọn: QLTV_HOST, QLTV_PORT, QLTV_USER (mặc định ql_thuvien), QLTV_PASSWORD (mặc định QuanLy@2026)
    streamlit run app.py

Mở thẳng một chức năng: `http://localhost:8501/?trang=6&bc=3` (trang 0–6 theo menu, bc = số báo cáo 1–6).
Chức năng: mượn sách; trả sách & phạt; phòng đọc (đặt phòng, thêm/sửa/xóa phòng); độc giả (tìm, đăng ký, sửa, gia hạn, xóa);
sách & kho (đầu sách, cuốn sách: chuyển giá/xóa, nhập lô/thanh lý, giá sách, phòng kho); thủ thư & chi nhánh (tìm, thêm, sửa, xóa, đổi trưởng); 6 báo cáo.

Kiểm thử giao diện + chụp màn hình cho báo cáo (cần playwright + chromium, chạy trên CSDL vừa dựng):

    sh ../sql/build_all.sh -uroot -p && python3 chup_man_hinh.py ../anh

Script tự bấm 23 thao tác thêm/sửa/xóa/mượn/trả, ghi kết quả vào `../anh/ket_qua_giao_dien.json` (hiện 23/23 PASS).
