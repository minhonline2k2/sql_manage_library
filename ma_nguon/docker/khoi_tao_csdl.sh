#!/bin/bash
# Container db chạy file này một lần khi volume dữ liệu còn trống: dựng CSDL QLTV giống sql/build_all.sh.
# Dựng lại bằng tay (xóa dữ liệu đã đổi): docker compose exec db bash /docker-entrypoint-initdb.d/khoi_tao_csdl.sh
set -e
for f in 01_schema.sql 02_function_procedure.sql 03_trigger.sql 04_transaction.sql \
         05_seed.sql 06_view_baocao.sql 07_index_baomat.sql; do
  echo ">> $f"
  mariadb --default-character-set=utf8mb4 -uroot -p"$MARIADB_ROOT_PASSWORD" < "/sql/$f" > /dev/null
done
