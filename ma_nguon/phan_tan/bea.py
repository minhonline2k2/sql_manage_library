"""Phân mảnh dọc NGUOI (phần độc giả) theo thuật toán BEA – chương 7c."""
A = ["A1 HoTen", "A2 NgaySinh", "A3 DiaChi", "A4 Email"]   # khóa MaNguoi không đưa vào ma trận, mảnh nào cũng chứa
n = len(A)
use = {  # q: tập chỉ số thuộc tính (0-based), không tính khóa
 "q1": {0},             # tra cứu tên độc giả khi mượn/trả
 "q2": {0, 3},          # gửi email nhắc hạn trả
 "q3": {1, 2},          # thống kê độ tuổi theo khu vực
 "q4": {0, 1, 2},       # in/cấp lại thẻ
}
acc = {"q1": [45, 30, 25], "q2": [25, 20, 15], "q3": [40, 30, 30], "q4": [5, 3, 2]}   # lượt/ngày tại S1,S2,S3; ref = 1
Q = list(use)
print("Ma trận sử dụng A:")
for q in Q: print(q, [1 if j in use[q] else 0 for j in range(n)])
aff = [[sum(sum(acc[q]) for q in Q if i in use[q] and j in use[q]) for j in range(n)] for i in range(n)]
print("\nMa trận AA:"); [print(A[i][:2], r) for i, r in enumerate(aff)]
def bond(x, y):   # x,y: chỉ số hoặc None (A0/An+1)
    if x is None or y is None: return 0
    return sum(aff[z][x] * aff[z][y] for z in range(n))
def cont(i, k, j): return 2 * bond(i, k) + 2 * bond(k, j) - 2 * bond(i, j)
order = [0, 1]
for k in range(2, n):
    best = None
    for pos in range(len(order) + 1):
        left = order[pos - 1] if pos > 0 else None
        right = order[pos] if pos < len(order) else None
        c = cont(left, k, right)
        print(f"cont({'A0' if left is None else 'A'+str(left+1)}, A{k+1}, {'A'+str(n+1) if right is None else 'A'+str(right+1)}) = {c}")
        if best is None or c > best[0]: best = (c, pos)
    order.insert(best[1], k)
    print(" → thứ tự:", ["A%d" % (x + 1) for x in order])
print("\nMa trận CA (hàng, cột theo thứ tự trên):")
for i in order: print("A%d" % (i + 1), [aff[i][j] for j in order])
print("\nChọn điểm chia:")
res = []
for x in range(1, n):
    TA, BA = set(order[:x]), set(order[x:])
    TQ = [q for q in Q if use[q] <= TA]; BQ = [q for q in Q if use[q] <= BA]; OQ = [q for q in Q if q not in TQ + BQ]
    C = lambda qs: sum(sum(acc[q]) for q in qs)
    z = C(TQ) * C(BQ) - C(OQ) ** 2
    res.append((z, x))
    print(f"x={x}: TA={sorted('A%d'%(i+1) for i in TA)} BA={sorted('A%d'%(i+1) for i in BA)} TQ={TQ} BQ={BQ} OQ={OQ} CTQ={C(TQ)} CBQ={C(BQ)} COQ={C(OQ)} z={z}")
print("max z:", max(res))
