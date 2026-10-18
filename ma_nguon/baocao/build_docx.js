// Chuyển BaoCao.md (tập con Markdown) sang Word theo thể thức báo cáo: A4, Times New Roman 13,
// lề trái 3 cm, phải 2 cm, trên/dưới 2 cm; trang bìa, mục lục, đánh số trang.
// Chạy: node build_docx.js BaoCao.md BaoCao_BTL_QLTV.docx
const fs = require("fs"), path = require("path");
const D = require("docx");
const { Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell, WidthType, ShadingType,
  AlignmentType, ImageRun, PageBreak, TableOfContents, Footer, PageNumber, LevelFormat, BorderStyle, TabStopType } = D;

const [src, out] = process.argv.slice(2);
const md = fs.readFileSync(src, "utf8").split("\n");
const base = path.dirname(path.resolve(src));
const FONT = "Times New Roman", MONO = "Consolas";
const CM = 567;                                   // 1 cm = 567 DXA
const W = 11906 - 3 * CM - 2 * CM;                // bề rộng vùng chữ A4

// ---------- inline: **đậm**, *nghiêng*, `mã`
function runs(text, o = {}) {
  const res = [];
  const re = /(\*\*[^*]+\*\*|`[^`]+`|\*[^*\s][^*]*\*)/g;
  let i = 0, m;
  const push = (t, extra = {}) => { if (t) res.push(new TextRun({ text: t, font: FONT, size: o.size || 26, ...o.run, ...extra })); };
  while ((m = re.exec(text))) {
    push(text.slice(i, m.index));
    const t = m[0];
    if (t.startsWith("**")) push(t.slice(2, -2), { bold: true });
    else if (t.startsWith("`")) res.push(new TextRun({ text: t.slice(1, -1), font: MONO, size: Math.round((o.size || 26) * 0.85), ...o.run }));
    else push(t.slice(1, -1), { italics: true });
    i = m.index + t.length;
  }
  push(text.slice(i));
  return res;
}
const P = (text, o = {}) => new Paragraph({ children: runs(text, o), spacing: { after: 120, line: 312 }, alignment: o.align ?? AlignmentType.JUSTIFIED, ...o.para });

// ---------- bảng
function table(lines) {
  const rows = lines.map(l => l.trim().replace(/^\|/, "").replace(/\|$/, "").split(/(?<!\\)\|/).map(c => c.trim().replace(/\\\|/g, "|")));
  const n = Math.max(...rows.map(r => r.length));
  // độ rộng cột theo độ dài nội dung (căn bậc hai để cột dài không lấn hết)
  const len = Array.from({ length: n }, (_, j) => Math.max(4, ...rows.map(r => Math.sqrt((r[j] || "").length + 4) * 10)));
  const tong = len.reduce((a, b) => a + b, 0);
  const cw = len.map(x => Math.floor(W * x / tong)); cw[n - 1] += W - cw.reduce((a, b) => a + b, 0);
  const size = n >= 6 ? 18 : 21;
  const bd = { style: BorderStyle.SINGLE, size: 4, color: "808080" };
  return new Table({
    width: { size: W, type: WidthType.DXA }, columnWidths: cw,
    rows: rows.map((r, i) => new TableRow({
      tableHeader: i === 0, cantSplit: true,
      children: Array.from({ length: n }, (_, j) => new TableCell({
        width: { size: cw[j], type: WidthType.DXA },
        borders: { top: bd, bottom: bd, left: bd, right: bd },
        shading: i === 0 ? { type: ShadingType.CLEAR, fill: "D9E2F3", color: "auto" } : undefined,
        margins: { top: 40, bottom: 40, left: 80, right: 80 },
        children: [new Paragraph({ children: runs(r[j] || "", { size, run: i === 0 ? { bold: true } : {} }), alignment: AlignmentType.LEFT })],
      })),
    })),
  });
}

// ---------- ảnh PNG
function image(file, cap) {
  const buf = fs.readFileSync(path.resolve(base, file));
  const w = buf.readUInt32BE(16), h = buf.readUInt32BE(20);
  const maxW = W / 1440 * 96, maxH = 23.5 * 37.8;       // px ở 96 dpi
  const s = Math.min(maxW / w, maxH / h, 1);
  return [
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 120 }, keepNext: true,
      children: [new ImageRun({ type: "png", data: buf, transformation: { width: Math.round(w * s), height: Math.round(h * s) } })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 240 }, children: runs(cap, { size: 24, run: { italics: true } }) }),
  ];
}

// ---------- trang bìa
const cover = [
  ["HỌC VIỆN CÔNG NGHỆ BƯU CHÍNH VIỄN THÔNG", 28, true], ["KHOA CÔNG NGHỆ THÔNG TIN", 28, true], ["", 26], ["", 26], ["", 26],
  ["BÀI TẬP LỚN", 36, true], ["MÔN: CÁC HỆ THỐNG CƠ SỞ DỮ LIỆU", 30, true], ["", 26],
  ["ĐỀ TÀI: XÂY DỰNG HỆ THỐNG QUẢN LÝ THƯ VIỆN", 32, true], ["", 26], ["", 26],
].map(([t, s, b]) => new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 160 }, children: [new TextRun({ text: t, font: FONT, size: s, bold: !!b })] }));
const info = [["Giảng viên", "TS. Phan Thị Hà"], ["Lớp", "[Mã lớp]"], ["Nhóm", "[Số nhóm]"], ["Hệ quản trị CSDL", "MariaDB"]];
for (const [k, v] of info) cover.push(new Paragraph({ indent: { left: 2600 }, tabStops: [{ type: TabStopType.LEFT, position: 5200 }], spacing: { after: 100 },
  children: [new TextRun({ text: `${k}:\t${v}`, font: FONT, size: 26 })] }));
cover.push(new Paragraph({ indent: { left: 2600 }, spacing: { before: 120, after: 100 }, children: [new TextRun({ text: "Thành viên nhóm:", font: FONT, size: 26, bold: true })] }));
const tv = Array.from({ length: 5 }, (_, i) => [String(i + 1), "[Họ và tên]", "[Mã học viên]"]);
cover.push(new Table({ width: { size: 6500, type: WidthType.DXA }, columnWidths: [700, 3500, 2300], alignment: AlignmentType.CENTER,
  rows: [["STT", "Họ và tên", "Mã học viên"], ...tv].map((r, i) => new TableRow({ children: r.map((c, j) => new TableCell({
    width: { size: [700, 3500, 2300][j], type: WidthType.DXA },
    shading: i === 0 ? { type: ShadingType.CLEAR, fill: "D9E2F3", color: "auto" } : undefined,
    children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: c, font: FONT, size: 24, bold: i === 0 })] })] })) })) }));
cover.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 1600 }, children: [new TextRun({ text: "Hà Nội, tháng 11 năm 2026", font: FONT, size: 26, italics: true })] }));
cover.push(new Paragraph({ children: [new PageBreak()] }));
cover.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 240 }, children: [new TextRun({ text: "MỤC LỤC", font: FONT, size: 30, bold: true })] }));
cover.push(new TableOfContents("Mục lục", { hyperlink: true, headingStyleRange: "1-2" }));

// ---------- thân
const body = [];
let i = 0, firstH1 = true;
while (i < md.length) {
  const l = md[i];
  if (l.startsWith("```")) {                       // khối mã
    const code = []; i++;
    while (i < md.length && !md[i].startsWith("```")) code.push(md[i++]);
    i++;
    code.forEach((c, k) => body.push(new Paragraph({
      shading: { type: ShadingType.CLEAR, fill: "F2F2F2", color: "auto" },
      spacing: { after: 0, line: 240, before: k === 0 ? 80 : 0 }, keepLines: true,
      children: [new TextRun({ text: c.replace(/\t/g, "  ") || " ", font: MONO, size: 16 })] })));
    body.push(new Paragraph({ spacing: { after: 120 }, children: [] }));
    continue;
  }
  if (/^\|/.test(l)) {                              // bảng
    const t = [];
    while (i < md.length && /^\|/.test(md[i])) t.push(md[i++]);
    body.push(table(t.filter(x => !/^\|[\s\-:|]+\|\s*$/.test(x))));
    body.push(new Paragraph({ spacing: { after: 120 }, children: [] }));
    continue;
  }
  let m;
  if ((m = l.match(/^(#{1,4}) (.*)/))) {
    const lv = m[1].length;
    if (lv === 1) {
      if (!firstH1) body.push(new Paragraph({ children: [new PageBreak()] }));
      firstH1 = false;
    }
    body.push(new Paragraph({ heading: [HeadingLevel.HEADING_1, HeadingLevel.HEADING_2, HeadingLevel.HEADING_3, HeadingLevel.HEADING_4][lv - 1],
      alignment: lv === 1 ? AlignmentType.CENTER : AlignmentType.LEFT, keepNext: true, children: runs(m[2], { size: [32, 28, 26, 26][lv - 1], run: { bold: true } }) }));
  } else if ((m = l.match(/^!\[(.*)\]\((.*)\)/))) {
    body.push(...image(m[2], m[1]));
  } else if ((m = l.match(/^(\s*)- (\[[ x]\] )?(.*)/))) {
    body.push(new Paragraph({ numbering: { reference: "bullet", level: m[1].length >= 2 ? 1 : 0 }, spacing: { after: 60, line: 300 }, children: runs(m[3]), alignment: AlignmentType.JUSTIFIED }));
  } else if ((m = l.match(/^(\s*)(\d+)\. (.*)/))) {
    body.push(new Paragraph({ indent: { left: 567 + (m[1].length >= 2 ? 567 : 0), hanging: 340 }, spacing: { after: 60, line: 300 },
      children: [new TextRun({ text: `${m[2]}.\t`, font: FONT, size: 26 }), ...runs(m[3])], tabStops: [{ type: TabStopType.LEFT, position: 567 }], alignment: AlignmentType.JUSTIFIED }));
  } else if (l.trim() === "") {
  } else {
    body.push(P(l));
  }
  i++;
}

const doc = new Document({
  creator: "Nhóm BTL", title: "Báo cáo BTL – Hệ thống quản lý thư viện",
  features: { updateFields: true },
  styles: {
    default: { document: { run: { font: FONT, size: 26 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", run: { font: FONT, size: 32, bold: true, color: "000000" }, paragraph: { spacing: { before: 240, after: 240 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", run: { font: FONT, size: 28, bold: true, color: "000000" }, paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", run: { font: FONT, size: 26, bold: true, italics: true, color: "000000" }, paragraph: { spacing: { before: 180, after: 100 }, outlineLevel: 2 } },
    ],
  },
  numbering: { config: [{ reference: "bullet", levels: [
    { level: 0, format: LevelFormat.BULLET, text: "–", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 567, hanging: 283 } } } },
    { level: 1, format: LevelFormat.BULLET, text: "+", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 1134, hanging: 283 } } } }] }] },
  sections: [
    { properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 2 * CM, bottom: 2 * CM, left: 3 * CM, right: 2 * CM } } }, children: cover },
    { properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 2 * CM, bottom: 2 * CM, left: 3 * CM, right: 2 * CM }, pageNumbers: { start: 1 } } },
      footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 22 })] })] }) },
      children: body },
  ],
});
Packer.toBuffer(doc).then(b => { fs.writeFileSync(out, b); console.log("wrote", out, b.length); });
