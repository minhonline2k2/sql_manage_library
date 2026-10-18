"""Lớp truy cập CSDL: chỉ gọi stored procedure / view, không chứa luật nghiệp vụ."""
import os
import pymysql
import pandas as pd

CAU_HINH = dict(
    host=os.getenv("QLTV_HOST", "127.0.0.1"),
    port=int(os.getenv("QLTV_PORT", "3306")),
    user=os.getenv("QLTV_USER", "ql_thuvien"),
    password=os.getenv("QLTV_PASSWORD", "QuanLy@2026"),
    database="QLTV",
    charset="utf8mb4",
    autocommit=True,
)


class LoiNghiepVu(Exception):
    """Lỗi do CSDL từ chối (SIGNAL Exxx, CHECK, khóa ngoại...)."""


def ket_noi():
    return pymysql.connect(**CAU_HINH)


def goi(ten_proc, *tham_so, so_out=0):
    """Gọi procedure. Trả về (list DataFrame kết quả, list giá trị OUT)."""
    cn = ket_noi()
    try:
        with cn.cursor() as cur:
            ds_in = ", ".join(["%s"] * len(tham_so))
            ds_out = ", ".join(f"@o{i}" for i in range(so_out))
            ds = ", ".join(x for x in (ds_in, ds_out) if x)
            cur.execute(f"CALL {ten_proc}({ds})", tham_so)
            bang = []
            while True:
                if cur.description:
                    cot = [c[0] for c in cur.description]
                    bang.append(pd.DataFrame(cur.fetchall(), columns=cot))
                if not cur.nextset():
                    break
            out = []
            if so_out:
                cur.execute("SELECT " + ", ".join(f"@o{i}" for i in range(so_out)))
                out = list(cur.fetchone())
            return bang, out
    except pymysql.MySQLError as e:
        thong_bao = e.args[1] if len(e.args) > 1 else str(e)
        raise LoiNghiepVu(thong_bao) from None
    finally:
        cn.close()


def bang(ten_proc, *tham_so):
    kq, _ = goi(ten_proc, *tham_so)
    return kq[0] if kq else pd.DataFrame()


def doc(sql, tham_so=()):
    """Chỉ dùng cho danh sách chọn (combobox) từ bảng danh mục."""
    cn = ket_noi()
    try:
        return pd.read_sql(sql, cn, params=tham_so)
    finally:
        cn.close()
