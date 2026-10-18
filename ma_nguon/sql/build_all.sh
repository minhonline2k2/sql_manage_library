#!/bin/sh
# Dựng lại toàn bộ CSDL QLTV từ đầu. Dùng: sh build_all.sh [-u user -p]
# Tham số truyền thẳng cho client mariadb (vd: sh build_all.sh -uroot -p)
set -e
cd "$(dirname "$0")"
for f in 01_schema.sql 02_function_procedure.sql 03_trigger.sql 04_transaction.sql \
         05_seed.sql 06_view_baocao.sql 07_index_baomat.sql; do
  echo ">> $f"
  mariadb --default-character-set=utf8mb4 "$@" < "$f" > /dev/null
done
echo "Xong. Chạy kiểm thử (làm thay đổi dữ liệu): mariadb --default-character-set=utf8mb4 $* QLTV < 08_test.sql"
