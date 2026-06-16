import { C, arrow, header, rect, text } from "./common.mjs";

export async function slide11(presentation) {
  const slide = presentation.slides.add();
  header(slide, "讨论：协方差传播与结论边界", 11);
  text(slide, "标量误差回答“多大”，协方差回答“向哪个方向不确定”；局限性决定结论应如何表述。", 74, 92, 1030, 30, { size: 21, bold: true });

  rect(slide, 92, 150, 440, 100, "#FAFDFF", { fill: C.line, width: 1 }, 8);
  text(slide, "Σ(Δt) = ΦΣ₀Φᵀ + Q", 128, 178, 370, 36, { size: 31, color: C.deep, bold: true, align: "center" });
  text(slide, "误差向量 e(t) 可估计 TEME / RIC 经验协方差", 120, 226, 380, 20, { size: 15, color: C.muted, align: "center" });

  rect(slide, 112, 338, 170, 86, C.pale, { fill: C.line, width: 1 }, 8);
  text(slide, "误差向量", 136, 360, 122, 24, { size: 18, color: C.deep, bold: true, align: "center" });
  text(slide, "[R, I, C]", 138, 392, 118, 20, { size: 15, color: C.ink, align: "center" });
  arrow(slide, 302, 382, 410, 382, C.blue);
  rect(slide, 430, 330, 210, 102, "#FFF8F4", { fill: "#F3CAB8", width: 1 }, 8);
  text(slide, "经验协方差", 458, 356, 150, 24, { size: 18, color: C.orange, bold: true, align: "center" });
  text(slide, "按轨道类型 × 天数估计", 456, 390, 152, 30, { size: 14, color: C.ink, align: "center" });
  rect(slide, 430, 452, 210, 46, C.pale, { fill: C.line, width: 1 }, 8);
  text(slide, "过程噪声 Q：随时间膨胀", 448, 462, 174, 22, { size: 16, color: C.deep, bold: true, align: "center" });

  const notes = [
    ["参考口径", "新 TLE 仍是平均根数，不是精密定轨真值。"],
    ["样本相关", "同一目标的多历元误差可能存在时间相关。"],
    ["外部扰动", "空间天气、阻力和机动未在统计模型中显式解释。"],
  ];
  notes.forEach((d, i) => {
    const y = 154 + i * 88;
    rect(slide, 700, y, 420, 64, i === 1 ? "#FFF8F4" : "#F7FBFE", { fill: i === 1 ? "#F3CAB8" : C.line, width: 1 }, 8);
    text(slide, d[0], 724, y + 18, 110, 24, { size: 18, color: i === 1 ? C.orange : C.deep, bold: true });
    text(slide, d[1], 846, y + 14, 235, 32, { size: 15.5, color: C.ink, lineSpacing: 1.05 });
  });

  rect(slide, 126, 512, 940, 58, "#FAFDFF", { fill: C.line, width: 1 }, 8);
  text(slide, "结论边界", 154, 528, 125, 24, { size: 19, color: C.orange, bold: true });
  text(slide, "本文结论应理解为公开 TLE 数据体系下的相对预报误差统计，而非替代精密定轨评估。", 292, 526, 680, 28, { size: 18, color: C.ink, bold: true });
  return slide;
}
