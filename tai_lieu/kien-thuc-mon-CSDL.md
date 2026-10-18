# Tri thức môn "Các hệ thống CSDL" – PTIT (TS. Phan Thị Hà)

Tổng hợp từ 11 bộ slide: Ch1-2 Giới thiệu · Ch3a ERD · Ch3b Lược đồ quan hệ · Ch3c Chuẩn hóa · Ch4 Đại số quan hệ (2 bản) · Ch5 SQL · Ch6 Trigger · Ch7a/b/c CSDL phân tán.
Mục "Cách thể hiện" ở mỗi chương ghi lại ký hiệu và lối trình bày của giảng viên — khi làm bài/giải thích thì bám theo đúng các quy ước này.

---

## Ch1–2. Giới thiệu môn học
- Nội dung: mô hình quan hệ → thiết kế (ERD, quan hệ, chuẩn hóa) → đại số quan hệ → SQL → tối ưu truy vấn → an toàn DL, Trigger → CSDL phân tán → vấn đề nâng cao, BTL.
- Thời lượng: LT 24 tiết, tiểu luận/BT 6 tiết, tự học 30 tiết. Giáo trình: Garcia-Molina, Ullman, Widom – *Database Systems: The Complete Book*.
- Đánh giá: chuyên cần 10%, **BTL 90%** (30% báo cáo qua email tuần cuối; 60% demo theo lịch thi).
- HQT CSDL: tạo lập CSDL + điều khiển mọi truy nhập; quản lý khối lượng lớn, truy nhập đồng thời, an toàn dữ liệu.
- **7 bước thiết kế CSDL quan hệ**: (1) Phân tích yêu cầu → (2) Thiết kế mức khái niệm → (3) Thiết kế mức logic → (4) Chuẩn hóa → (5) Xây dựng mức vật lý → (6) Thiết kế an toàn bảo mật → (7) Hiệu chỉnh; sau đó xây dựng ứng dụng.

## Ch3a. Mô hình thực thể – liên kết (ERD)
**Khái niệm**: thực thể (cụ thể/trừu tượng), tập thực thể, thuộc tính, miền giá trị. Thuộc tính: đơn/kép, đơn trị/đa trị, dẫn xuất, rỗng (Null). Liên kết (relationship) có thể có thuộc tính mô tả; "sự tham gia".

**Ký hiệu (Chen, slide tô màu)**:
| Ký hiệu | Ý nghĩa |
|---|---|
| Chữ nhật | Tập thực thể · Chữ nhật kép: tập thực thể yếu |
| Hình thoi | Liên kết · Thoi kép: liên kết xác định (cho thực thể yếu) |
| Ellipse | Thuộc tính · gạch chân = khóa chính · ellipse kép = đa trị · ellipse nét đứt = dẫn xuất · gạch chân nét đứt = thuộc tính phân biệt của thực thể yếu |
| Đường đôi R═E | Tham gia đầy đủ (total) · đường đơn = tham gia một phần |
| Chân gà (crow's foot) ở đầu E | phía "nhiều"; cách khác: ghi 1 / M / N trên đường nối |
| Tam giác ISA | Cụ thể hóa/tổng quát hóa; ghi `disjoint` = phân tách; đường đôi phía trên = tổng quát hóa đầy đủ |
| Hộp bao quanh liên kết | Kết hợp (aggregation) – coi liên kết như thực thể |
| (min,max) trên đường nối | Ràng buộc cấu trúc số lượng tham gia |

**Lực lượng liên kết**: 1:1, 1:M, M:1, M:M. **Tham gia**: đầy đủ (mọi thực thể tham gia ≥1) / một phần.

**Khóa**: siêu khóa (mọi tập cha của siêu khóa cũng là siêu khóa) → khóa dự bị (siêu khóa tối thiểu) → khóa chính (chọn 1; phải xác định duy nhất và hiếm khi thay đổi). Ràng buộc khóa: 2 thực thể không trùng giá trị trên toàn bộ thuộc tính khóa.

**Đặt thuộc tính của liên kết**: 1:M → có thể chuyển sang phía M; 1:1 → sang phía nào cũng được; M:M → phải để trên liên kết.

**Thực thể yếu**: không đủ thuộc tính làm khóa; phụ thuộc tập thực thể xác định (sở hữu) qua liên kết xác định (M:1, tham gia đầy đủ). Khóa = PK thực thể xác định + thuộc tính phân biệt (khóa bán phần). VD: LOAN 1—loan-payment—N PAYMENT(payment-number).

**Cụ thể hóa** (trên xuống) / **Tổng quát hóa** (dưới lên) – trong sơ đồ không phân biệt. Kế thừa thuộc tính và liên kết; đơn kế thừa / đa kế thừa. **3 ràng buộc**: (1) thành viên – theo mệnh đề (điều kiện) hoặc do người dùng xác định; (2) giao nhau / không giao nhau (disjoint/overlapping); (3) toàn bộ / một phần.

**Thực thể kết hợp & quan hệ nhiều ngôi**: VD works-on(EMPLOYEE, BRANCH, JOB) + MANAGER quản lý → dùng aggregation thay vì quan hệ 4 ngôi. VD STARS–MOVIES–STUDIOS: quan hệ 3 ngôi `contract` có thể chuyển thành thực thể CONTRACT với các liên kết star-of, movie-of, studio-of, producing-studio.

**Ví dụ chuẩn trong slide**: CUSTOMER–borrower–LOAN; CUSTOMER với thuộc tính kép (name = first/middle/last; address = street(num, name, apt), city, state, zipcode), phone-num đa trị, age dẫn xuất từ date-of-birth; PERSON ISA INSTRUCTOR/STUDENT, INSTRUCTOR ISA ADJUNCT/REGULAR-FACULTY/ADMINISTRATOR.

## Ch3b. Lược đồ quan hệ & ánh xạ ERD → quan hệ
**Thuật ngữ**: Quan hệ = Bảng = Tệp; Bộ = Hàng = Bản ghi; Thuộc tính = Cột = Trường. Bậc = số thuộc tính; Lực lượng = số bộ. CSDL quan hệ = tập các quan hệ đã chuẩn hóa, tên phân biệt.
**Tính chất quan hệ**: tên riêng; thuộc tính tên riêng, có miền; giá trị nguyên tố; các bộ phân biệt; thứ tự cột và hàng không quan trọng (thực tế ảnh hưởng hiệu năng). Hai thể hiện tương đương nếu chỉ khác thứ tự hàng/cột.

**Quy tắc ánh xạ**:
1. **Thực thể thường** → 1 quan hệ; thuộc tính đơn → cột; định danh → PK. Thuộc tính **kép** → chỉ lấy các thành phần đơn. Thuộc tính **đa trị** → tách bảng thứ 2: (PK bảng 1 làm FK, giá trị đa trị), PK = cả hai; đặt tên theo ngữ nghĩa.
2. **Thực thể yếu** → quan hệ mới gồm thuộc tính của nó + PK của thực thể xác định (FK); PK = PK xác định + thuộc tính phân biệt. VD DEPENDENT(first-name, middle-name, last-name, employee-id, DOB, gender).
3. **1–N**: PK phía 1 thành FK ở phía N. (1–N và N–1 đối xứng.)
4. **N–N**: tạo quan hệ mới C; PK = tổ hợp PK hai bên (đồng thời là FK); thuộc tính của liên kết đưa vào C.
5. **1–1**: PK bên này làm FK bên kia; nên đặt FK ở bên **tham gia bắt buộc** (tránh NULL). Bảng tóm tắt: 1–1 thường → FK + UNIQUE; một bên toàn phần → đặt FK ở bên toàn phần; thực thể phụ thuộc → FK ở bảng phụ thuộc; hai bên toàn phần → gộp bảng hoặc FK + UNIQUE NOT NULL; liên kết có thuộc tính → đưa vào bảng chứa FK. VD NURSE(nurse-id, name, date-of-birth, center-name) – CARE CENTER(center-name, location, date-assigned).
6. **Đệ quy 1–N**: thêm FK đệ quy tham chiếu PK chính bảng đó. VD `NHAN_VIEN(employee-id PK, name, birthdate, manager-id FK REFERENCES NHAN_VIEN)`.
7. **Đệ quy N–N**: bảng thực thể + bảng liên kết có PK gồm 2 thuộc tính (tên tùy ý) cùng lấy giá trị từ PK. VD ITEM(item-num, name, unit-cost), COMPONENT(part-num, component-num, quantity).
8. **Thực thể kết hợp / nhiều ngôi**: tương tự N–N; 3 quan hệ; tùy có/không gán định danh. VD works-on(emp-id, Branch-id, job-title), PK = cả 3, đều là FK.
9. **Cha–con (ISA)**: bảng cha chứa thuộc tính chung + PK + thuộc tính phân biệt (discriminator, vd emp-type = 'H'/'S'/'C'); mỗi bảng con có PK = PK cha (FK, `ON DELETE CASCADE`) + thuộc tính riêng. VD EMPLOYEE → HOURLY-EMP(hr-rate), SALARIED-EMP(salary, stock-opt), CONSULTANT(contract-num, billing-rate).
- Ký hiệu thay thế cho cụ thể hóa: vòng tròn `o` = overlapping, `d` = disjoint; total/partial.

## Ch3c. Chuẩn hóa – Phụ thuộc hàm
**PTH** A→B: mỗi giá trị A ứng với duy nhất một giá trị B; là tính chất của lược đồ (bất biến theo thời gian), không của một thể hiện. Vế trái = đối tượng xác định, vế phải = hệ quả. PTH hiển nhiên (Y ⊆ X) bỏ qua.

**Luật suy diễn**: IR1 phản xạ (Y⊆X ⇒ X→Y), IR2 tăng trưởng (X→Y ⇒ XZ→YZ), IR3 bắc cầu — **hệ tiên đề Armstrong** (đúng và đủ); IR4 chiếu/tách, IR5 hợp/cộng, IR6 giả bắc cầu (X→Y, YZ→W ⇒ XZ→W).

**Bao đóng** F⁺ = mọi PTH suy được từ F. Kiểm tra X→Y ∈ F⁺ ⇔ Y ⊆ X⁺.
Thuật toán (trình bày dạng pseudocode Pascal-like):
- `Closure(X, F)`: X⁺←X; repeat oldX⁺←X⁺; for mỗi W→Z∈F: if W⊆X⁺ then X⁺←X⁺∪Z; until oldX⁺ = X⁺.
- `Member(F, X→Y)`: true nếu Y ⊆ Closure(X,F).
- **Phủ**: G phủ F nếu F ⊆ G⁺; F ≡ G nếu F⁺ = G⁺.
- `Nonredundant(F)`: G←F; for mỗi X→Y∈G: if Member(G−{X→Y}, X→Y) then loại.
- Thuộc tính dư thừa ở vế trái/phải; **tối giản trái** (= PTH đầy đủ), **tối giản phải**, **tối giản** (trái + phải + Y≠∅).
- `Left-Reduce`: với mỗi A∈X, nếu Member(F,(X−A)→Y) thì bỏ A. `Right-Reduce`: với mỗi A∈Y, nếu Member(F−{X→Y}∪{X→(Y−A)}, X→A) thì bỏ A. `Reduce(G)` = Right-Reduce(Left-Reduce(G)) rồi loại X→∅.
- **Phủ tối thiểu**: (1) vế phải 1 thuộc tính; (2) không dư thừa; (3) tối giản trái. `MinCover`: tách vế phải → Left-Reduce → Nonredundant. VD G={A→BCE, AB→DE, BI→J} ⇒ F={A→B, A→C, A→D, A→E, BI→J}.
- Bài tập slide: tối giản F={A→BC, B→C, AB→D}; G={B→A, D→A, BA→D}.

**Khóa của lược đồ**: X là khóa nếu X→A1…An ∈ F⁺ và không tập con thực sự nào làm được. Thuộc tính khóa = thuộc một khóa dự bị nào đó; còn lại là không khóa.

**Các dạng chuẩn** (N1NF → 1NF → 2NF → 3NF → BCNF → 4NF → 5NF):
- **1NF**: giá trị nguyên tố, đơn trị, không có thuộc tính suy diễn.
- **2NF**: 1NF + mọi thuộc tính không khóa phụ thuộc **đầy đủ** vào mọi khóa. Cách đưa về: tách thuộc tính phụ thuộc bộ phận khóa ra bảng riêng (PK = phần khóa đó); phần còn lại giữ khóa cũ.
- **3NF**: ∀ X→A: X là siêu khóa **hoặc** A là thuộc tính khóa (≡ 2NF + không có thuộc tính không khóa phụ thuộc bắc cầu vào khóa). Cách 1: tìm phủ tối thiểu, tách PTH bắc cầu ra bảng mới. Cách 2 (tổng hợp): phủ tối thiểu G → mỗi PTH thành 1 bảng → nếu không bảng nào chứa khóa dự bị của R thì thêm 1 bảng chứa khóa.
- **BCNF**: ∀ X→A với A⊈X: X là siêu khóa. VD R(A,B,C), F={AB→C, C→A}, khóa AB: không BCNF vì C→A.
- Phân tách cần: (1) kết nối không mất thông tin, (2) bảo toàn PTH. Về 3NF có thuật toán đảm bảo cả hai; về BCNF thì **không** có.
- Phân tách BCNF: chọn PTH vi phạm X→Y, tính X⁺; R1 = X⁺, R2 = (R − X⁺) ∪ X; chiếu PTH và lặp.

## Ch4. Ngôn ngữ đại số quan hệ
Ngôn ngữ **thủ tục**; toán hạng là quan hệ, kết quả là quan hệ. **5 phép cơ bản**: chọn σ, chiếu π, hợp ∪, trừ −, tích Đề-các ×. **Mở rộng**: giao ∩, kết nối (θ, bằng, tự nhiên ⋈/*, ngoài ⟕ ⟖ ⟗, bán kết nối ⋉), chia ÷. Đổi tên ρ.

**Cách thể hiện mỗi phép (khung chuẩn của slide)**: *Loại · Ký hiệu · Khuôn dạng chung · Lược đồ kết quả · Kích thước kết quả · Ví dụ* + bảng R/S/T minh họa.
| Phép | Khuôn dạng | Ghi chú |
|---|---|---|
| Chọn σ | σ_(mệnh đề)(R) | lát cắt ngang; \|kq\| ≤ \|R\|; dùng =,≠,<,≤,>,≥, ∧, ∨, ¬ |
| Chiếu π | π_(ds thuộc tính)(R) | lát cắt dọc; tự loại bộ trùng |
| Hợp ∪ | r ∪ s | r, s **khả hợp** (cùng bậc, miền thuộc tính thứ i giống nhau); \|kq\| ≤ \|r\|+\|s\| |
| Trừ − | r − s | khả hợp; \|kq\| ≤ \|r\| |
| Tích × | r × s | đổi tên thuộc tính trùng (T.A, X.A); \|kq\| = \|r\|·\|s\| |
| Giao ∩ | r ∩ s ≡ r − (r − s) | khả hợp |
| θ-join | r ⋈_(pred) s ≡ σ_pred(r × s) | equi-join khi mọi điều kiện là "="; không loại cột trùng |
| Tự nhiên | r ⋈ s (slide còn viết r * s) | bằng trên các thuộc tính cùng tên, chỉ giữ một lần; bậc = tổng − số thuộc tính chung |
| Ngoài trái/phải/đủ | ⟕ ⟖ ⟗ | bộ không khớp được giữ, điền null. VD r(A,B)={(a,b),(c,d),(b,c)}, s(A,C)={(a,d),(s,t),(b,d)} |
| Bán kết nối | r ⋉_(pred) s ≡ π_(thuộc tính r)(r ⋈_pred s) | giảm số bộ cần xử lý → hữu ích trong môi trường **phân tán** |
| Chia ÷ | r(X) ÷ s(Y), kq trên X−Y | r ÷ s ≡ π_(X−Y)(r) − π_(X−Y)((π_(X−Y)(r) × s) − r); dùng cho truy vấn "**mọi**/tất cả" |
| Đổi tên ρ | ρ_x(r), ρ_x(A1,…,An)(r) | |

**CSDL ví dụ dùng xuyên suốt**:
- Trường học: S = STUDENTS(s#, name, age, major, gpa, hours_completed); C = COURSES(c#, term, name, dept, enrollment); P = PROFESSORS(p#, name, dept, yrs_teaching, area); TA = TAKES(s#, c#, term, grade); TE = TEACH(p#, c#, term).
- Nhà cung cấp: S(snum, name, status, city), P(pnum, name, color, weight, city), J(jnum, name, numworkers, city), SPJ(snum, pnum, jnum, qty, date).
- Bài tập: SanPham(ten, gia, loai), CungCap(MaCC, tenSP, SoLuong).

**Phong cách giải**: nêu "Cách tiếp cận" từng bước (chọn → chiếu), rồi viết "Biểu thức truy vấn hoàn chỉnh" lồng nhau; bài phức tạp chia thành T1, T2, … với chú thích `//`. Hay có mục "Biểu thức sau sai, vì sao?":
- "chỉ đăng ký Spring 2003": π(term = Spring 2003) − π(term ≠ Spring 2003), không chỉ chọn.
- "linh kiện được cả S1 và S2 cung cấp": σ(s#='S1' ∧ s#='S2') luôn sai → dùng giao: A − (A − B).
- "nhà cung cấp cấp mọi linh kiện": chỉ 5 phép cơ bản: π_s#[π_(s#,p#)(spj) − (π_s#(spj) × π_p#(p) − π_(s#,p#)(spj))]; với phép chia: π_(s#,p#)(spj) ÷ π_p#(p).
- "chỉ vận chuyển linh kiện xanh": π_s#(spj ⋈ σ_(color=blue)(p)) − π_s#(spj ⋈ σ_(color≠blue)(p)).

## Ch5. SQL
- Lịch sử: IBM San Jose, System R (1974–79), SQUARE → SEQUEL → SQL; chuẩn ANSI, ISO, FIPS. Gồm **DDL** và **DML**.
- **Ký pháp cú pháp**: VIẾT HOA = từ khóa; *nghiêng* = tham số người dùng; `{a|b}` bắt buộc chọn một; `[...]` tùy chọn; tablename, column, data type, constraint, condition, columnlist, tablelist, conditionlist, expression.
- **DDL**: CREATE SCHEMA AUTHORIZATION, CREATE TABLE, NOT NULL, UNIQUE, PRIMARY KEY, FOREIGN KEY, DEFAULT, CHECK, CREATE INDEX, CREATE VIEW, ALTER TABLE, DROP TABLE/INDEX/VIEW.
- Kiểu dữ liệu: INT, REAL/FLOAT, CHAR(n), VARCHAR(n), NUMERIC(p,d) (NUMERIC(10,2) ≤ ±99,999,999.99), DATE 'yyyy-mm-dd', TIME 'hh:mm:ss', DATETIME/TIMESTAMP.
- PRIMARY KEY không cho NULL; UNIQUE cho phép NULL (nhiều NULL). FK: `beer CHAR(20) REFERENCES Beers(name)` hoặc `FOREIGN KEY (beer) REFERENCES Beers(name) ON DELETE SET NULL ON UPDATE CASCADE`.
- CHECK mức cột (kiểm tra khi cột thay đổi) và mức bản ghi `CHECK(bar = 'Joe''s Bar' OR price <= 5.00)`. DEFAULT: `addr CHAR(50) DEFAULT '123 Sesame St'`.
- ALTER TABLE … ADD | MODIFY | DROP {PRIMARY KEY | COLUMN c | CONSTRAINT name} → nên đặt tên ràng buộc.
- Index: `CREATE [UNIQUE] INDEX idx ON t(col)`; `DROP INDEX idx ON t`.
- Procedure: `CREATE OR REPLACE PROCEDURE name(params) AS … BEGIN … [EXCEPTION …] END;`
- DROP TABLE chỉ khi bảng không còn tham gia quan hệ nào.
- **DML**: INSERT, SELECT, WHERE, GROUP BY, HAVING, ORDER BY, UPDATE, DELETE, COMMIT, ROLLBACK; toán tử BETWEEN, IS NULL, LIKE, IN/NOT IN, EXISTS/NOT EXISTS, DISTINCT; hàm COUNT, MIN, MAX, SUM, AVG; hàm dòng LOWER, UPPER, ROUND, PI, SQRT, POWER, CONVERT.
- `SELECT [ALL|DISTINCT] columnlist FROM tablelist [WHERE] [GROUP BY] [HAVING] [ORDER BY [ASC|DESC]]` — ORDER BY luôn cuối, mặc định ASC. Quy tắc GROUP BY: mọi cột trong SELECT không phải hàm thống kê phải có trong GROUP BY; HAVING lọc trên nhóm, WHERE lọc trên hàng.
- UPDATE/DELETE không có WHERE → tác động mọi bản ghi.
- Subquery VD: quán bán Miller cùng giá với Bud ở quán Joe (Sells(bar, beer, price)).
- Kết nối: liệt kê bảng ở FROM (tích Đề-các) + điều kiện kết nối ở WHERE (thường PK = FK); INNER JOIN, LEFT/RIGHT/FULL JOIN … ON, NATURAL JOIN.
- Tập hợp: UNION (loại trùng) / UNION ALL; INTERSECT (Access dùng IN); MINUS = EXCEPT (Access dùng NOT IN).
- VIEW: `CREATE VIEW PRODUCT_3 AS SELECT P_DESCRIPT, P_ONHAND, P_PRICE FROM PRODUCT WHERE P_PRICE > 50.00;` – bảng gốc = base tables.
- **Transaction**: START TRANSACTION / BEGIN WORK … COMMIT | ROLLBACK; **ACID** (nguyên tố, nhất quán, biệt lập, bền vững). ROLLBACK quay về COMMIT gần nhất; Oracle tự COMMIT khi chạy DDL. VD chuyển 500 giữa 2 tài khoản với `SELECT … FOR UPDATE`.
- Trigger kiểu MySQL trong Ch5: `CREATE TRIGGER ins_sum BEFORE INSERT ON account FOR EACH ROW SET @sum = @sum + NEW.amount;` BEFORE/AFTER; INSERT/UPDATE/DELETE; `DROP TRIGGER test.ins_sum`.

## Ch6. Trigger (T-SQL / SQL Server; slide tiếng Anh)
- Trigger = thủ tục chỉ được "đánh thức" khi xảy ra sự kiện (insert/delete/update trên một quan hệ, kết thúc giao dịch).
- Dùng để: cài đặt luật nghiệp vụ (vd tạo khoản vay khi tài khoản bị thấu chi), đảm bảo toàn vẹn, duy trì dữ liệu liên quan (thuộc tính dẫn xuất, dữ liệu tổng hợp).
- Thành phần: **Event** (thay đổi cụ thể; trước/sau) + **Action** (truy vấn, sửa DB, tạo bảng, gọi thủ tục).
```sql
CREATE TRIGGER TriggerName
ON {TableName|ViewName}
[WITH ENCRYPTION]
{FOR | AFTER | INSTEAD OF}
{[DELETE] [,] [INSERT] [,] [UPDATE]}
AS
BEGIN
  SQL_Statements
END
```
- FOR = AFTER: chạy sau sự kiện; **không dùng AFTER cho VIEW**. INSTEAD OF: chạy thay cho sự kiện. WITH ENCRYPTION: ẩn mã trigger.
- Bảng logic **inserted** / **deleted** (cùng lược đồ với bảng gốc). `IF UPDATE(col) [AND|OR UPDATE(col2)]`.
- Ví dụ: đếm số dòng chèn vào Customers (`select @InsertedRow = count(*) from inserted`); chặn sửa CustomerID (`if UPDATE(CUSTOMERID) … rollback transaction`); xóa dây chuyền OrderItems khi xóa Orders (`delete from OrderItems where OrderID in (select OrderID from deleted)`).
- `ALTER TRIGGER` (cùng cú pháp), `DROP TRIGGER TriggerName`.

## Ch7a. Tổng quan CSDL phân tán
- Hệ phân tán: tập thành phần tự trị cộng tác qua mạng, thể hiện như một hệ đơn lẻ. Phân tán chức năng / dữ liệu / điều khiển.
- Xử lý truyền thống (mỗi ứng dụng một tệp, dư thừa) → xử lý CSDL tập trung (độc lập dữ liệu, không dư thừa) → **CSDLPT**: tập các CSDL quan hệ logic với nhau, phân tán trên mạng; HQT CSDLPT làm sự phân tán **trong suốt** với người dùng. Hai khía cạnh: tính phân tán + mối quan hệ logic.
- **Đặc điểm (so với tập trung)**: điều khiển không tập trung (DBA toàn cục + DBA cục bộ, tự trị vị trí); độc lập dữ liệu + **trong suốt phân tán**; dư thừa có chủ đích (nhân bản tăng tính cục bộ, sẵn sàng; lợi khi nhiều đọc ít ghi); độ tin cậy giao dịch; cải tiến hiệu năng (phân mảnh + cục bộ hóa; song song liên truy vấn và nội truy vấn); dễ mở rộng; toàn vẹn – phục hồi – điều khiển tương tranh qua giao tác nguyên tố.
- Ưu: chia sẻ dữ liệu & điều khiển phân tán, tin cậy & sẵn sàng, tăng tốc truy vấn. Nhược: chi phí phát triển, khó phát hiện lỗi, chi phí xử lý (trao đổi thông báo) tăng.
- **Mô hình tham chiếu** (mở rộng ANSI/SPARC 3 mức: external/conceptual/internal): Lược đồ toàn cục → Lược đồ phân mảnh (ánh xạ 1-nhiều; mảnh = biểu thức ĐSQH trên quan hệ toàn cục) → Lược đồ cấp phát (R_ij = mảnh i của R tại site j) → Lược đồ ánh xạ cục bộ → DBMS cục bộ → CSDL cục bộ. VD R thành R1..R4 trên 3 site: site1{R11,R21}, site2{R12,R22}, site3{R23,R33,R43}.
- Trong suốt phân mảnh (mức cao nhất, làm việc trên quan hệ toàn cục) > trong suốt cấp phát (làm trên mảnh, không cần biết vị trí). Phân mảnh ≠ cấp phát.
- CSDLPT đồng nhất (cùng HQT) / không đồng nhất (cần chuyển đổi mô hình dữ liệu).
- Thành phần tại mỗi site: DB, DC (truyền dữ liệu), DD (từ điển mở rộng), DDB. Truy nhập từ xa trực tiếp hoặc qua middleware.
- **3 chiều kiến trúc**: phân tán, không đồng nhất, tự trị (thiết kế, truyền thông, thực thi). Kiến trúc: **Client/Server** (multi-client/single server: nút cổ chai, single point of failure; multi-client/multi-server), **Peer-to-peer** (ES → GCS → LCS → LIS), **Multi-DBMS** (GES, LES, GCS, LCS, LIS), federated DBMS.

## Ch7b. Thiết kế CSDLPT – Phân mảnh ngang
- Thông tin cần: CSDL (quan hệ, thuộc tính, PTH, liên kết), ứng dụng (truy vấn, vị trí, tần số); mạng & hệ thống máy **chỉ dùng cho cấp phát**, không cho phân mảnh.
- Thiết kế = phân mảnh + cấp phát. Mảnh = đơn vị truy xuất. Nhược: ứng dụng xung đột, view trải nhiều mảnh tốn chi phí kết nối, khó kiểm tra toàn vẹn.
- Kiểu: **ngang** (phép chọn), **dọc** (phép chiếu, giữ khóa), **hỗn hợp**.
- **3 quy tắc đúng đắn**:
  1. Đầy đủ: mọi mục dữ liệu (bộ / thuộc tính) của R phải nằm trong ít nhất một mảnh.
  2. Tái thiết (phục hồi): ngang R = ∪Ri; dọc R = ⋈Ri.
  3. Tách biệt: ngang Ri ∩ Rj = ∅; dọc các mảnh chỉ chung thuộc tính khóa.
  - Bài kiểm tra: R(A1..A6) → R1(A1,A5,A6), R2(A1,A3,A4), R3(A1,A6): **sai** — thiếu A2 (vi phạm đầy đủ), A6 có ở R1 và R3 (vi phạm tách biệt; A1 là khóa).
- Lược đồ liên kết ví dụ: PAY(TITLE, SAL) —L1→ EMP(ENO, ENAME, TITLE); EMP —L2→ ASG(ENO, PNO, RESP, DUR) ←L3— PROJ(PNO, PNAME, BUDGET, LOC). Owner ở đầu đuôi, member ở đầu mũi tên.
- **Vị từ đơn giản** p_j: A_i θ value; Pr = {p1..pm}. **Vị từ hội sơ cấp (minterm)** m = ∧ p_k* (p_k* là p_k hoặc ¬p_k). sel(m), acc(q), acc(m).
- Phân mảnh ngang cơ sở (nguyên thủy): R_i = σ_(m_i)(R); số mảnh = số minterm (sau khi loại mâu thuẫn).
- **Đầy đủ** của Pr: mọi bộ trong cùng một mảnh minterm có cùng xác suất được mọi ứng dụng truy nhập. **Cực tiểu**: mọi vị từ đều **liên đới** — p_i liên đới ⇔ acc(m_i)/card(f_i) ≠ acc(m_j)/card(f_j). VD PROJ theo LOC + BUDGET ≤ 200000 là đầy đủ; thêm JNAME = "Instrumentation" thì không cực tiểu.
- **COM_MIN(R, Pr)**: tìm p_i phân hoạch R theo quy tắc ("phân hoạch thành ≥ 2 phần được ít nhất một ứng dụng truy nhập khác nhau") → Pr' ← p_i; Pr ← Pr − p_i; F ← f_i; lặp: tìm p_j phân hoạch một mảnh f_k của Pr' → thêm vào Pr', F; nếu có p_k ∈ Pr' không còn liên đới thì loại; until Pr' đầy đủ.
- **PHORIZONTAL(R, Pr)**: Pr' ← COM_MIN(R, Pr); xác định M (minterm); xác định tập phép kéo theo I giữa các p_i ∈ Pr'; loại m_i mâu thuẫn với I. VD p1: att = v1, p2: att = v2 ⇒ I: p1 ⇒ ¬p2, ¬p1 ⇒ p2 → loại m(p1∧p2) và m(¬p1∧¬p2).
- VD PAY: Pr = {SAL ≤ 30000, SAL > 30000} → Pr' = {p1} → PAY1 = σ_(SAL≤30000), PAY2 = σ_(SAL>30000). VD PROJ: LOC ∈ {Montreal, New York, Paris} × BUDGET ≤/> 200000 → 6 mảnh PROJ1..6, PROJ2 và PROJ5 rỗng.
- **Phân mảnh ngang dẫn xuất**: phân mảnh member theo semijoin với các mảnh của owner: R_i = R ⋉ S_i. Chọn theo: đặc tính kết nối tốt hơn và phục vụ nhiều ứng dụng hơn. VD EMP_i = EMP ⋉ PAY_i; ASG_j = ASG ⋉ PROJ_j; ASG_ij = ASG ⋉ EMP_i. Có thể xảy ra dây chuyền (PAY → EMP → ASG).
- Bài tập mẫu: QLSV(MA, HT, QQ, NS, GT, DT, TB) — tự đặt 2 ứng dụng → Pr → COM_MIN → M → các mảnh; bài bán hàng (nhân viên – mặt hàng); bài quản lý dự án (≤ 10 dự án/nhân viên, ≥ 2 nhân viên/dự án, có người giám sát).

## Ch7c. Phân mảnh dọc, lai, cấp phát
- Phân mảnh dọc: mỗi mảnh = tập con thuộc tính + **khóa**; gom các thuộc tính hay được truy xuất cùng nhau.
- Quy trình: (1) Ma trận sử dụng **A** = use(q_i, A_j) ∈ {0,1} → (2) Ma trận lực hút **AA**: aff(A_i, A_j) = Σ_{k: use(q_k,A_i)=1 ∧ use(q_k,A_j)=1} Σ_l ref_l(q_k)·acc_l(q_k) → (3) **BEA** tạo ma trận tụ nhóm **CA** → (4) thuật toán phân mảnh (chia TA/BA).
- BEA: AM = Σ_i Σ_j aff(A_i,A_j)[aff(A_i,A_{j−1}) + aff(A_i,A_{j+1})]; bond(A_x, A_y) = Σ_z aff(A_z,A_x)·aff(A_z,A_y); **cont(A_i, A_k, A_j) = 2·bond(A_i,A_k) + 2·bond(A_k,A_j) − 2·bond(A_i,A_j)**; biên A0, A_{n+1} toàn 0. Bước: đặt cột 1, 2 → lần lượt chèn cột còn lại vào vị trí cont lớn nhất → sắp hàng theo thứ tự cột.
- Chia: TQ (chỉ truy xuất TA), BQ (chỉ BA), OQ (cả hai); CTQ, CBQ, COQ = Σ ref·acc; chọn điểm chia x (1 ≤ x ≤ n) cực đại **z = CTQ·CBQ − COQ²**.
- **Ví dụ chuẩn PROJ(A1 = PNO, A2 = PNAME, A3 = BUDGET, A4 = LOC)**: q1 SELECT BUDGET WHERE PNO; q2 SELECT PNAME, BUDGET; q3 SELECT PNAME WHERE LOC; q4 SELECT SUM(BUDGET) WHERE LOC. A = [[1,0,1,0],[0,1,1,0],[0,1,0,1],[0,0,1,1]]. acc: q1 = 15/20/10, q2 = 5/0/0, q3 = 25/25/25, q4 = 3/0/0. AA = [[45,0,45,0],[0,80,5,75],[45,5,53,3],[0,75,3,78]]. BEA: cont(A0,A3,A1) = 8820, cont(A1,A3,A2) = 10150 ⇒ A1 A3 A2; cont(A0,A4,A1) = 270, cont(A1,A4,A3) = −7014, cont(A3,A4,A2) = 23486, cont(A2,A4,A5) = 23730 ⇒ thứ tự **A1 A3 A2 A4**. Chia: z1 = −2025, **z2 = 45·75 − 8² = 3311**, z3 = −6084 ⇒ PROJ1{PNO, BUDGET}, PROJ2{PNO, PNAME, LOC}.
- **Phân mảnh lai**: ngang rồi dọc hoặc ngược lại (cây R → HF → R1, R2 → VF → R11, R12, …); khôi phục: VF dùng kết nối, HF dùng hợp.
- **Nhân bản**: toàn phần / có lựa chọn. **Bài toán cấp phát**: cho F = {F_i}, S = {S_j}, Q = {q_k}, tìm phân bổ tối ưu (chi phí tối thiểu: lưu trữ + truyền thông + xử lý; hoặc hiệu năng: thời gian đáp ứng/thông lượng) với ràng buộc thời gian đáp ứng, lưu trữ, xử lý. Biến x_ij = 1 nếu F_i lưu tại S_j.
  - Thông tin: sel_i(F_j), size(F_j) = card·length; RR_ij, UR_ij, u_ij, r_ij; USC_k, LPC_k; g_ij, fsize.
  - STC_jk = USC_k · size(F_j) · x_jk; PC_i = AC_i + IE_i + CC_i; TC_i = TCU_i + TCR_i.
  - Bài toán NP-complete (tương tự knapsack, luồng mạng) → heuristic: bỏ nhân bản trước, xử lý nhân bản ở bước 2.

---
### Phong cách trình bày chung của bộ slide
- Tiếng Việt học thuật (Ch6 bằng tiếng Anh), mỗi slide = tiêu đề + gạch đầu dòng ngắn, ví dụ bằng bảng dữ liệu nhỏ (cột A, B, C, D với giá trị a, b, yes/no, số).
- Thuật toán viết dạng pseudocode `Begin … End {TÊN}` hoặc `Tên(tham số) { … }`, có Input/Output (Đầu vào/Đầu ra).
- Mỗi phép toán/khái niệm: định nghĩa → ký hiệu → ví dụ → bài tập ("Bài tập 1, 2, …"), thường kèm câu "vì sao sai?".
- Ví dụ kinh điển tiếng Anh (bank: CUSTOMER/LOAN/ACCOUNT; beers: Sells/Beers/Drinkers; supplier–parts–jobs; EMP/PROJ/ASG/PAY của Özsu & Valduriez).
- Ký hiệu thường gặp: ⇒ cho hệ quả/ghi chú; PK gạch chân; FK ghi "FK REFERENCES".
