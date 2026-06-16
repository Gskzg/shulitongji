import { C, axisArrow, dot, ellipse, header, hline, rect, text, vline } from "./common.mjs";

export async function slide03(presentation) {
  const slide = presentation.slides.add();
  header(slide, "原理一：TLE 平均根数经 SGP4 传播为位置序列", 3);
  text(slide, "TLE 给出历元处的平均轨道根数；SGP4 在指定时长 h 上输出 TEME 坐标系下的位置和速度。", 74, 96, 1060, 30, { size: 21, bold: true });

  rect(slide, 76, 148, 1028, 96, "#FAFDFF", { fill: C.line, width: 1 }, 8);
  text(slide, "TLE_i = {epoch_i, i, Ω, e, ω, M, n, B*}", 112, 170, 430, 30, { size: 22, color: C.deep, bold: true });
  text(slide, "r_i(t_i+h), v_i(t_i+h) = SGP4(TLE_i, h)", 590, 170, 444, 30, { size: 22, color: C.orange, bold: true });
  text(slide, "i, Ω, e, ω, M, n 表示轨道根数；B* 表示阻力相关项；h 为预报时长。", 112, 210, 840, 22, { size: 15.5, color: C.muted });

  rect(slide, 108, 296, 940, 170, "#FFFFFF", { fill: C.line, width: 1 }, 8);
  text(slide, "传播时长 h", 132, 318, 116, 24, { size: 17, color: C.deep, bold: true });
  axisArrow(slide, 210, 382, 760, C.deep);
  text(slide, "TLE历元\nepoch_i", 184, 402, 92, 34, { size: 13.5, color: C.ink, align: "center", lineSpacing: 1.02 });
  text(slide, "+1d", 380, 406, 70, 22, { size: 14.5, color: C.ink, align: "center" });
  text(slide, "+3d", 572, 406, 70, 22, { size: 14.5, color: C.ink, align: "center" });
  text(slide, "+7d", 888, 406, 70, 22, { size: 14.5, color: C.ink, align: "center" });

  const points = [
    [218, 382, 18, "TLE 历元"],
    [414, 376, 34, "r_i(t_i+1)"],
    [606, 366, 54, "r_i(t_i+3)"],
    [920, 348, 82, "r_i(t_i+7)"],
  ];
  points.forEach(([x, y, rad, label], idx) => {
    if (idx > 0) ellipse(slide, x - rad / 2, y - rad / 2, rad, rad, idx === 3 ? "#FFF4ED" : "#F7FBFE", { fill: idx === 3 ? "#F3CAB8" : C.line, width: 1 });
    dot(slide, x, y, idx === 0 ? 6 : 5, idx === 0 ? C.deep : C.orange);
    if (idx > 0) text(slide, label, x - 60, y - 48, 120, 20, { size: 13.5, color: C.orange, bold: true, align: "center" });
    vline(slide, x, 382, 22, C.line, 1);
  });
  text(slide, "椭圆示意传播不确定性随 h 扩大，并非真实轨道尺度。", 650, 448, 350, 18, { size: 13, color: C.muted, align: "right" });

  rect(slide, 118, 508, 430, 78, "#F7FBFE", { fill: C.line, width: 1 }, 8);
  text(slide, "误差积累机制", 146, 526, 145, 24, { size: 18, color: C.deep, bold: true });
  text(slide, "初始根数误差、SGP4 模型近似、阻力与空间天气、机动或编目更新都会随传播时长累积。", 300, 520, 205, 40, { size: 14.5, color: C.ink, lineSpacing: 1.06 });

  rect(slide, 620, 508, 430, 78, "#FFF8F4", { fill: "#F3CAB8", width: 1 }, 8);
  text(slide, "统计入口", 648, 526, 110, 24, { size: 18, color: C.orange, bold: true });
  text(slide, "后续 TLE 可提供同一公开编目体系下的近似参考，用于构造可重复的预报误差样本。", 770, 520, 220, 40, { size: 14.5, color: C.ink, lineSpacing: 1.06 });
  return slide;
}
