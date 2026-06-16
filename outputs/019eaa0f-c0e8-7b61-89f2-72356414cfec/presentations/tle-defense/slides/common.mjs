import fs from "node:fs/promises";

export const W = 1280;
export const H = 720;

export const C = {
  blue: "#08A8DC",
  blue2: "#78D5EF",
  deep: "#1D5E8C",
  orange: "#F05A28",
  ink: "#222831",
  muted: "#607080",
  pale: "#F4F8FB",
  line: "#D8E6EF",
  white: "#FFFFFF",
  red: "#D94B3D",
  green: "#2B9C6A",
};

export const font = "PingFang SC";
export const root = "/Users/macbook/Documents/数理统计大作业";

export function rect(slide, x, y, w, h, fill = C.white, line = { fill: { type: "none" } }, radius = 0) {
  const s = slide.shapes.add({
    geometry: "rect",
    position: { left: x, top: y, width: w, height: h },
    fill,
    line,
    borderRadius: radius,
  });
  return s;
}

export function ellipse(slide, x, y, w, h, fill = C.white, line = { fill: C.line, width: 1 }) {
  return slide.shapes.add({
    geometry: "ellipse",
    position: { left: x, top: y, width: w, height: h },
    fill,
    line,
  });
}

export function hline(slide, x, y, w, color = C.line, thickness = 2) {
  return rect(slide, x, y - thickness / 2, w, thickness, color);
}

export function vline(slide, x, y, h, color = C.line, thickness = 2) {
  return rect(slide, x - thickness / 2, y, thickness, h, color);
}

export function dot(slide, x, y, r = 5, fill = C.blue, line = { fill: { type: "none" } }) {
  return ellipse(slide, x - r, y - r, 2 * r, 2 * r, fill, line);
}

export function axisArrow(slide, x, y, w, color = C.deep) {
  hline(slide, x, y, w - 12, color, 2);
  slide.shapes.add({
    geometry: "triangle",
    position: { left: x + w - 16, top: y - 7, width: 14, height: 14 },
    fill: color,
    line: { fill: { type: "none" } },
  });
}

export function text(slide, value, x, y, w, h, opts = {}) {
  const s = rect(slide, x, y, w, h, opts.fill ?? { type: "none" }, opts.line ?? { fill: { type: "none" } }, opts.radius ?? 0);
  s.text = value;
  s.text.typeface = opts.typeface ?? font;
  s.text.fontSize = opts.size ?? 20;
  s.text.color = opts.color ?? C.ink;
  s.text.bold = !!opts.bold;
  if (opts.italic) s.text.italic = true;
  if (opts.align) s.text.alignment = opts.align;
  if (opts.valign) s.text.verticalAlignment = opts.valign;
  s.text.wrap = "square";
  s.text.insets = opts.insets ?? { top: 4, right: 4, bottom: 4, left: 4 };
  if (opts.lineSpacing) s.text.lineSpacing = opts.lineSpacing;
  return s;
}

export function header(slide, title, page) {
  rect(slide, 0, 0, W, H, C.white);
  rect(slide, 0, 0, W, 58, C.blue);
  rect(slide, 960, 0, 320, 58, C.blue2);
  rect(slide, 40, 13, 5, 32, C.orange);
  text(slide, title, 56, 12, 850, 34, { size: 20, color: C.white, bold: true, valign: 2 });
  rect(slide, 0, 668, W, 52, C.blue2);
  rect(slide, 0, 668, 930, 52, C.blue);
  text(slide, String(page), 610, 681, 60, 24, { size: 15, color: C.ink, align: "center", valign: 2 });
  text(slide, "TLE/SGP4 轨道预报误差统计分析", 40, 635, 420, 20, { size: 11, color: C.muted });
}

export function coverBars(slide) {
  rect(slide, 0, 0, W, H, C.white);
  rect(slide, 0, 604, W, 116, C.blue2);
  rect(slide, 0, 604, 830, 116, C.blue);
  rect(slide, 0, 604, 160, 116, C.blue2);
}

export function bulletList(slide, items, x, y, w, opts = {}) {
  let cy = y;
  for (const item of items) {
    text(slide, "□", x, cy + 1, 22, 22, { size: 16, color: C.muted, align: "center" });
    text(slide, item, x + 34, cy, w - 34, opts.itemH ?? 38, { size: opts.size ?? 18, color: opts.color ?? C.ink, lineSpacing: 1.08 });
    cy += opts.gap ?? 46;
  }
}

export function metric(slide, value, label, x, y, w, h, accent = C.blue) {
  rect(slide, x, y, w, h, C.pale, { fill: C.line, width: 1 }, 8);
  rect(slide, x, y, 6, h, accent);
  text(slide, value, x + 18, y + 12, w - 28, 34, { size: 25, color: accent, bold: true });
  text(slide, label, x + 18, y + 50, w - 28, 36, { size: 14, color: C.muted });
}

export function smallTable(slide, rows, x, y, colW, rowH = 34, opts = {}) {
  const totalW = colW.reduce((a, b) => a + b, 0);
  rows.forEach((row, r) => {
    const isHeader = r === 0;
    rect(slide, x, y + r * rowH, totalW, rowH, isHeader ? C.deep : (r % 2 ? "#FFFFFF" : "#F7FBFE"), { fill: C.line, width: 0.8 });
    let cx = x;
    row.forEach((cell, c) => {
      text(slide, String(cell), cx + 4, y + r * rowH + 3, colW[c] - 8, rowH - 6, {
        size: isHeader ? (opts.headerSize ?? 13) : (opts.size ?? 13),
        color: isHeader ? C.white : C.ink,
        bold: isHeader,
        align: opts.align?.[c] ?? (c === 0 ? "left" : "center"),
        valign: 2,
      });
      cx += colW[c];
    });
  });
}

export async function image(slide, relPath, x, y, w, h, alt = "") {
  const bytes = await fs.readFile(`${root}/${relPath}`);
  slide.images.add({
    dataUrl: `data:image/png;base64,${bytes.toString("base64")}`,
    position: { left: x, top: y, width: w, height: h },
    fit: "contain",
    alt,
  });
}

export function callout(slide, title, body, x, y, w, h, accent = C.orange) {
  rect(slide, x, y, w, h, "#FFF8F4", { fill: "#F3CAB8", width: 1 }, 8);
  rect(slide, x, y, 6, h, accent);
  text(slide, title, x + 18, y + 12, w - 28, 24, { size: 16, color: accent, bold: true });
  text(slide, body, x + 18, y + 42, w - 30, h - 52, { size: 14, color: C.ink, lineSpacing: 1.08 });
}

export function arrow(slide, x1, y1, x2, y2, color = C.blue) {
  const w = Math.max(1, x2 - x1);
  rect(slide, x1, y1 - 2, w - 10, 4, color);
  slide.shapes.add({
    geometry: "triangle",
    position: { left: x2 - 14, top: y2 - 8, width: 16, height: 16 },
    fill: color,
    line: { fill: { type: "none" } },
  });
}
