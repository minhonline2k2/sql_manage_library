#!/bin/bash
# Cài môi trường chạy BTL QLTV trên Ubuntu 22.04/24.04 (một máy, 3 site giả lập bằng 3 database).
# Chạy: sudo bash cai_dat_ubuntu.sh
# Cài: MariaDB >= 10.11, Graphviz, Node.js + docx (package-lock.json), Python venv ~/qltv-venv (requirements.txt + chromium).
set -e
[ "$(id -u)" = 0 ] || { echo "Cần chạy bằng sudo"; exit 1; }
U="${SUDO_USER:-root}"; H=$(getent passwd "$U" | cut -d: -f6)
SRC="$(cd "$(dirname "$0")" && pwd)"   # thư mục ma_nguon
export DEBIAN_FRONTEND=noninteractive
. /etc/os-release

apt-get update -q
apt-get install -y -q curl ca-certificates
# Ubuntu 24.04 có sẵn MariaDB 10.11 và Node 18; bản cũ hơn thì lấy MariaDB, Node 20 từ kho chính thức
if dpkg --compare-versions "$VERSION_ID" lt 24.04; then
  curl -LsS https://r.mariadb.com/downloads/mariadb_repo_setup | bash -s -- --mariadb-server-version=10.11
  curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
  NODE_PKG=nodejs
else
  NODE_PKG="nodejs npm"
fi
apt-get install -y -q mariadb-server mariadb-client graphviz python3-venv python3-pip $NODE_PKG \
  fonts-liberation fonts-dejavu-core
systemctl enable --now mariadb

V=$(mariadb -N -e "SELECT VERSION()")
dpkg --compare-versions "${V%%-*}" ge 10.11 || { echo "MariaDB $V < 10.11"; exit 1; }

sudo -u "$U" python3 -m venv "$H/qltv-venv"
sudo -u "$U" "$H/qltv-venv/bin/pip" install -q -r "$SRC/requirements.txt"
"$H/qltv-venv/bin/playwright" install-deps chromium
sudo -u "$U" "$H/qltv-venv/bin/playwright" install chromium
(cd "$SRC/baocao" && sudo -u "$U" npm ci --no-audit --no-fund)

# Giao diện chạy dưới supervisor, tự bật cùng máy: sudo supervisorctl status | restart | stop qltv-app
apt-get install -y -q supervisor
cat > /etc/supervisor/conf.d/qltv-app.conf <<EOF
[program:qltv-app]
command=$H/qltv-venv/bin/streamlit run app.py --server.headless true --server.port 8501 --browser.gatherUsageStats false
directory=$SRC/app
user=$U
environment=HOME="$H",USER="$U"
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
redirect_stderr=true
stdout_logfile=/var/log/supervisor/qltv-app.log
stdout_logfile_maxbytes=10MB
stdout_logfile_backups=3
EOF
systemctl enable --now supervisor
supervisorctl reread && supervisorctl update

echo "Xong: MariaDB $V, $(dot -V 2>&1), node $(node -v), $("$H/qltv-venv/bin/python" -V)"
