import { C, dot, header, hline, rect, text, vline } from "./common.mjs";

export async function slide05(presentation) {
  const slide = presentation.slides.add();
  header(slide, "原理三：从误差样本到统计量、增长律与检验", 5);
  text(slide, "对每个轨道类型 g 和预报时长 h，先形成误差样本集 D_{g,h}，再估计统计量和不确定性。", 74, 94, 1060, 30, { size: 21, bold: true });

  rect(slide, 82, 146, 1040, 410, "#FFFFFF", { fill: C.line, width: 1 }, 8);
  vline(slide, 604, 172, 354, C.line, 1.5);
  hline(slide, 110, 352, 982, C.line, 1.5);

  const sections = [
    [118, 172, C.deep, "A. 误差样本与量级统计", "D_{g,h} = {E_{s,i,h} | orbit(s)=g}", "median(D)、RMSE = √(n⁻¹ΣE²)、q₀.₉₅\n中位数刻画典型误差；RMSE 和 q₀.₉₅刻画长尾风险。"],
    [642, 172, C.orange, "B. 误差增长律", "m_g(h)=median(D_{g,h}) = a_g h^{b_g}", "log m_g(h)=log a_g + b_g log h\nb_g > 1 表示短期误差随时长超线性增长。"],
    [118, 378, C.blue, "C. Bootstrap / BCa 区间", "D*_{g,h,b} ~ resample(D_{g,h}),  θ*_b=f(D*)", "CI_pct=[q₂.₅%, q₉₇.₅%]；CI_BCa 修正偏差和偏态\n用于均值、中位数、RMSE 等统计量的不确定性估计。"],
    [642, 378, C.green, "D. 轨道差异与协方差", "Σ_{g,h}=Cov(e_RIC),   Σ(h)=ΦΣ₀Φᵀ+Q", "Levene 检查方差齐性；Kruskal-Wallis 检验三组差异；\nMann-Whitney U 进行两两比较。"],
  ];

  sections.forEach(([x, y, color, title, formula, desc]) => {
    dot(slide, x, y + 11, 6, color);
    text(slide, title, x + 18, y, 360, 24, { size: 18, color, bold: true });
    text(slide, formula, x + 18, y + 38, 420, 28, { size: 18, color: C.deep, bold: true });
    text(slide, desc, x + 18, y + 76, 410, 50, { size: 14.5, color: C.ink, lineSpacing: 1.08 });
  });

  rect(slide, 206, 578, 760, 34, "#FAFDFF", { fill: C.line, width: 1 }, 8);
  text(slide, "符号：g∈{LEO,MEO,GEO}，h∈{1,3,7}天，s 为目标，i 为旧 TLE 历元，b 为 Bootstrap 重采样编号。", 226, 585, 720, 18, { size: 14.5, color: C.muted, align: "center" });
  return slide;
}
