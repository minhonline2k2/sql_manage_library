# Hệ thống quản lý thư viện – BTL môn Các hệ thống CSDL (PTIT)

CSDL quản lý thư viện 3 chi nhánh trên **MariaDB 10.11**: 23 bảng, 18 trigger, 7 transaction (procedure), dữ liệu vận hành 3 tháng (01/07–30/09/2026), thiết kế CSDL phân tán 3 site, giao diện Streamlit chỉ gọi procedure/view.

Kết quả kiểm thử: SQL **47/47**, phân tán **36/36**, giao diện **23/23**.

## Cấu trúc

```
tai_lieu/     đề bài, báo cáo Word (BaoCao_BTL_QLTV.docx), nội dung các chương P1–P8, phân công
ma_nguon/
  sql/        01_schema … 07_index_baomat (dựng CSDL), 08_test (47 ca), 09_phan_tan (3 site, 36 ca)
  app/        giao diện Streamlit (app.py, db.py) + kiểm thử Playwright (chup_man_hinh.py)
  baocao/     script ghép báo cáo Markdown → Word
  erd/, phan_tan/, anh/   sơ đồ ERD, thiết kế phân tán, ảnh chụp giao diện
  docker-compose.yml, Dockerfile, docker/   chạy bằng Docker
  cai_dat_ubuntu.sh                         cài môi trường trên Ubuntu
  requirements.txt                          phiên bản Python đã kiểm thử
```

## Cách 1 – Docker (Windows, macOS, Linux)

### Bước 1 – Cài Git và Docker (làm một lần)

**Git:** tải ở https://git-scm.com/downloads (Windows: cài Git for Windows, giữ các lựa chọn mặc định). Ubuntu: `sudo apt-get install -y git`.

**Windows 10/11 – Docker Desktop**

1. Bật WSL 2: mở PowerShell bằng **Run as administrator**, chạy `wsl --install`, rồi khởi động lại máy. Máy đã có WSL thì chạy `wsl --update`.
2. Tải Docker Desktop ở https://www.docker.com/products/docker-desktop/ → *Download for Windows – AMD64* (máy chip ARM chọn ARM64). Chạy file cài, giữ lựa chọn **Use WSL 2 instead of Hyper-V**, khởi động lại nếu được hỏi.
3. Mở Docker Desktop, chấp nhận điều khoản; có thể bỏ qua bước đăng nhập. Đợi góc dưới bên trái báo **Engine running**.
4. Yêu cầu máy: bật ảo hóa (Intel VT-x / AMD-V) trong BIOS, RAM từ 8 GB (tối thiểu 4 GB). Docker Desktop miễn phí cho cá nhân và học tập.

**macOS – Docker Desktop**

Tải ở https://www.docker.com/products/docker-desktop/, chọn **Apple Silicon** (chip M1–M4) hoặc **Intel**, kéo Docker vào Applications rồi mở; hoặc `brew install --cask docker`. Đợi biểu tượng cá voi trên thanh menu báo đang chạy.

**Ubuntu 22.04/24.04 – Docker Engine** (đã kiểm thử trên 22.04)

```bash
sudo apt-get update
sudo apt-get install -y docker.io docker-compose-v2
sudo usermod -aG docker $USER      # đăng xuất rồi đăng nhập lại để dùng docker không cần sudo
```

**Kiểm tra** (mọi hệ điều hành):

```bash
docker --version
docker compose version
docker run --rm hello-world
```

Lỗi hay gặp:

| Lỗi | Cách xử lý |
| --- | --- |
| `Cannot connect to the Docker daemon`, `error during connect … dockerDesktopLinuxEngine` | Docker Desktop chưa chạy: mở và đợi **Engine running** |
| `WSL 2 installation is incomplete` / cần cập nhật kernel | PowerShell (admin): `wsl --update`, rồi mở lại Docker Desktop |
| `Virtualization support not detected` | Bật VT-x / AMD-V (SVM) trong BIOS |
| `permission denied … docker.sock` (Linux) | Chưa đăng xuất/đăng nhập lại sau lệnh `usermod`, hoặc tạm thêm `sudo` trước `docker` |
| `port is already allocated` | Đổi cổng (xem cuối mục này) |

### Bước 2 – Tải code và chạy

```bash
git clone https://github.com/minhonline2k2/sql_manage_library.git
cd sql_manage_library/ma_nguon
docker compose up -d --build
```

Mở **http://localhost:8501**. Lần đầu mất vài phút để tải image; container `db` tự dựng CSDL `QLTV` (khoảng 20 giây). Lấy bản mới nhất về sau này: `git pull` rồi `docker compose up -d --build`.

### Bước 3 – Kiểm thử và thao tác thường dùng

Các lệnh dưới đây chạy được cả trong PowerShell, cmd và bash (đứng ở thư mục `ma_nguon`):

| Việc | Lệnh |
| --- | --- |
| Kiểm thử SQL (47 ca, làm thay đổi dữ liệu) | `docker compose exec -T db sh -c "mariadb --default-character-set=utf8mb4 -uroot -proot QLTV < /sql/08_test.sql"` |
| Kiểm thử phân tán (36 ca) | `docker compose exec -T db sh -c "mariadb --default-character-set=utf8mb4 -uroot -proot < /sql/09_phan_tan.sql"` |
| Dựng lại CSDL sạch | `docker compose exec -T db bash /docker-entrypoint-initdb.d/khoi_tao_csdl.sh` |
| Mở MariaDB dòng lệnh | `docker compose exec db mariadb -uroot -proot QLTV` |
| Xem log / tắt / xóa sạch | `docker compose logs -f` · `docker compose down` · `docker compose down -v` |

Kết nối bằng HeidiSQL/DBeaver: `127.0.0.1`, cổng `3307`, user `root` / `root` (hoặc `ql_thuvien` / `QuanLy@2026`). Trùng cổng thì đổi:

- bash (Linux, macOS, Git Bash): `APP_PORT=8502 DB_PORT=3308 docker compose up -d`
- PowerShell: `$env:APP_PORT=8502; $env:DB_PORT=3308; docker compose up -d`

Sửa code trong `ma_nguon/app/` là giao diện cập nhật ngay (thư mục được mount vào container). Sửa file SQL thì chạy lệnh "Dựng lại CSDL sạch".

## Cách 2 – Máy ảo Ubuntu 22.04/24.04 (đủ cả quy trình dựng báo cáo)

```bash
git clone https://github.com/minhonline2k2/sql_manage_library.git ~/qltv && cd ~/qltv
sudo bash ma_nguon/cai_dat_ubuntu.sh        # MariaDB 10.11, Graphviz, Node 20, Python venv ~/qltv-venv, supervisor
cd ma_nguon/sql && sudo sh build_all.sh      # dựng CSDL
```

Giao diện chạy sẵn dưới supervisor tại `http://<IP máy ảo>:8501`, tự bật cùng máy: `sudo supervisorctl status|restart|stop qltv-app`.

Kiểm thử và dựng lại báo cáo (các script kết nối root qua socket nên chạy bằng sudo):

```bash
cd ~/qltv/ma_nguon/sql
sudo mariadb --default-character-set=utf8mb4 QLTV < 08_test.sql | tail -2     # 47 PASS
sudo sh build_all.sh && sudo mariadb --default-character-set=utf8mb4 < 09_phan_tan.sql > /dev/null
sudo mariadb QLTV -e "SELECT KetQua, COUNT(*) FROM KIEM_TRA_PHAN_TAN GROUP BY KetQua"   # 36 PASS

PY="sudo PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/ms-playwright $HOME/qltv-venv/bin/python"
sudo sh build_all.sh && cd ../baocao && $PY gen_tudien.py && $PY gen_muc4.py > muc4_tudong.md
cd ../sql && sudo sh build_all.sh && cd ../app && $PY chup_man_hinh.py ../anh         # 23/23
cd ../baocao && $PY assemble.py && node build_docx.js BaoCao.md ../../tai_lieu/BaoCao_BTL_QLTV.docx
```

## Lưu ý

- Mật khẩu trong repo (`root`, `QuanLy@2026`, `ThuThu@2026`) là tài khoản demo cho CSDL chạy trên máy cá nhân, không dùng cho hệ thống thật.
- Mọi luật nghiệp vụ nằm trong CSDL (CHECK, trigger, procedure); lỗi nghiệp vụ trả về dạng `Exxx: …` (bảng mã lỗi ở mục 4.12 báo cáo).
- Báo cáo Word còn để trống bìa (lớp, nhóm, họ tên, mã học viên); mở Word → cập nhật mục lục trước khi nộp.
