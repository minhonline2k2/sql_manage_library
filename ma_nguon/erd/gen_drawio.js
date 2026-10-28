// Chuyển ERD (bố cục neato) sang XML của draw.io, giữ nguyên vị trí và ký hiệu.
// Cách dùng: neato -Tjson erd.dot > erd.json && node gen_drawio.js erd.json > erd.drawio
// Mở draw.io → Extras → Edit Diagram → dán nội dung erd.drawio → OK (hoặc File → Open).
const fs = require("fs");
const g = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const TL = 1.5;                                   // phóng to cho dễ chỉnh trên draw.io
const H = parseFloat(g.bb.split(",")[3]);
const esc = s => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

// ký hiệu chân gà của Graphviz → draw.io
const DAU = { teetee: "ERmandOne", teeodot: "ERzeroToOne", crowodot: "ERzeroToMany", crowtee: "ERoneToMany" };

function nhan(n) {
  return (n.label || n.name).replace(/\\n/g, "<br>").replace(/<U>/g, "<u>").replace(/<\/U>/g, "</u>");
}

function kieu(n) {
  const st = n.style || "", kep = n.peripheries === "2", nen = n.fillcolor || "#FFFFFF";
  const k = ["html=1", "whiteSpace=wrap", "fontFamily=Arial", "fontSize=12", `fillColor=${nen}`,
             `strokeColor=${n.color === "gray30" ? "#4D4D4D" : n.color || "#000000"}`];   // gray30 = khóa bán phần
  if (st.includes("dashed")) k.push("dashed=1");
  if (n.penwidth) k.push(`strokeWidth=${n.penwidth}`);
  if (n.shape === "box") k.push(kep ? "shape=ext;double=1" : "rounded=0");
  else if (n.shape === "diamond") k.push("shape=rhombus;perimeter=rhombusPerimeter", ...(kep ? ["double=1"] : []));
  else if (n.shape === "ellipse") k.push(kep ? "ellipse;shape=doubleEllipse;perimeter=ellipsePerimeter" : "ellipse");
  else if (n.shape === "invtriangle" || n.shape === "triangle")
    k.push("triangle;direction=south;perimeter=trianglePerimeter;verticalAlign=top;spacingTop=6");
  return k.join(";") + ";";
}

const o = ['<mxfile><diagram name="ERD"><mxGraphModel dx="1600" dy="1200" grid="1" gridSize="10" page="0"><root>',
           '<mxCell id="0"/><mxCell id="1" parent="0"/>'];
const id = i => "n" + i;

for (const n of g.objects) {
  if (!n.pos) continue;
  const [x, y] = n.pos.split(",").map(Number);
  const w = parseFloat(n.width) * 72 * TL, h = parseFloat(n.height) * 72 * TL;
  o.push(`<mxCell id="${id(n._gvid)}" value="${esc(nhan(n))}" style="${kieu(n)}" vertex="1" parent="1">` +
         `<mxGeometry x="${(x * TL - w / 2).toFixed(1)}" y="${((H - y) * TL - h / 2).toFixed(1)}" width="${w.toFixed(1)}" height="${h.toFixed(1)}" as="geometry"/></mxCell>`);
}

g.edges.forEach((e, i) => {
  const k = ["html=1", "rounded=0", "strokeColor=#000000", "fontFamily=Arial", "fontSize=11", "endSize=12", "startSize=12",
             "startArrow=none", "endArrow=none", "startFill=0", "endFill=0"];
  if (e.color === "black:white:black") k.push("shape=link");               // đường đôi (ISA đầy đủ)
  if (e.dir === "forward" && DAU[e.arrowhead]) k.push(`endArrow=${DAU[e.arrowhead]}`);
  if (e.dir === "back" && DAU[e.arrowtail]) k.push(`startArrow=${DAU[e.arrowtail]}`);
  const eid = "e" + i;
  o.push(`<mxCell id="${eid}" value="${esc(e.label || "")}" style="${k.join(";")};" edge="1" parent="1" ` +
         `source="${id(e.tail)}" target="${id(e.head)}"><mxGeometry relative="1" as="geometry"/></mxCell>`);
  // nhãn đặt sát đầu đường nối (headlabel ở phía target, taillabel ở phía source)
  for (const [nd, vt] of [[e.headlabel, 0.75], [e.taillabel, -0.75]])
    if (nd) o.push(`<mxCell id="${eid}${vt > 0 ? "h" : "t"}" value="${esc(nd)}" style="edgeLabel;html=1;fontSize=11;labelBackgroundColor=#FFFFFF;" ` +
                   `vertex="1" connectable="0" parent="${eid}"><mxGeometry x="${vt}" relative="1" as="geometry"><mxPoint y="-10" as="offset"/></mxGeometry></mxCell>`);
});

o.push("</root></mxGraphModel></diagram></mxfile>");
process.stdout.write(o.join("\n") + "\n");
