import { C, header, image, smallTable, text } from "./common.mjs";

export async function slide09(presentation) {
  const slide = presentation.slides.add();
  header(slide, "结论三：中位数误差近似幂律增长", 9);
  text(slide, "在 1 到 7 天尺度内，用 E(t)=a·t^b 描述中位数误差增长，三类轨道拟合优度均较高。", 74, 92, 1030, 30, { size: 21, bold: true });

  await image(slide, "outputs/figures/error_growth_median_iqr.png", 74, 138, 660, 430, "error growth curve");
  smallTable(slide, [
    ["轨道", "幂律模型", "R²"],
    ["LEO", "0.092·t^1.536", "1.000"],
    ["MEO", "0.156·t^1.292", "0.982"],
    ["GEO", "0.592·t^1.471", "0.989"],
  ], 790, 190, [90, 210, 80], 48, { size: 15, headerSize: 15 });

  text(slide, "b>1 表明短期误差增长具有超线性特征；GEO 的初始误差水平更高，LEO 的增长指数最大。", 790, 414, 380, 92, { size: 18, color: C.ink, fill: "#F7FBFE", line: { fill: C.line, width: 1 }, radius: 8, insets: { top: 14, right: 16, bottom: 12, left: 16 } });
  return slide;
}
