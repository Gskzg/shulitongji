import { C, axisArrow, dot, header, hline, rect, text, vline } from "./common.mjs";

export async function slide04(presentation) {
  const slide = presentation.slides.add();
  header(slide, "原理二：同一目标时刻的两条轨道差分定义误差", 4);
  text(slide, "旧 TLE 传播到目标时刻 t* 形成预报位置；新 TLE 在 t* 附近传播到同一时刻形成参考位置。", 74, 94, 1060, 30, { size: 21, bold: true });

  rect(slide, 80, 146, 1040, 248, "#FFFFFF", { fill: C.line, width: 1 }, 8);
  axisArrow(slide, 160, 312, 850, C.deep);
  text(slide, "时间 t", 980, 322, 70, 22, { size: 14.5, color: C.deep, bold: true });

  const ti = 230;
  const tstar = 630;
  const tj = 690;
  const refStart = 565;
  const refEnd = 755;
  vline(slide, ti, 216, 118, C.deep, 2);
  vline(slide, tstar, 176, 168, C.orange, 3);
  vline(slide, tj, 230, 104, C.green, 2);
  hline(slide, refStart, 198, refEnd - refStart, "#F3CAB8", 8);
  text(slide, "参考 TLE 搜索窗：t* ± 12h", refStart + 16, 166, 170, 22, { size: 13.5, color: C.orange, bold: true, align: "center" });
  text(slide, "t_i 旧TLE历元", ti - 58, 342, 116, 20, { size: 13.5, color: C.deep, align: "center" });
  text(slide, "t* = t_i + h", tstar - 78, 342, 104, 20, { size: 13.5, color: C.orange, bold: true, align: "center" });
  text(slide, "t_j 新TLE历元", tj - 22, 366, 118, 20, { size: 13.5, color: C.green, align: "center" });

  const pred = [[230, 286], [360, 270], [500, 252], [630, 230], [760, 214], [900, 196]];
  const ref = [[560, 268], [630, 274], [700, 282], [780, 292], [860, 300]];
  pred.forEach(([x, y], idx) => {
    dot(slide, x, y, idx === 3 ? 6 : 4, C.blue);
    if (idx > 0) hline(slide, pred[idx - 1][0], (pred[idx - 1][1] + y) / 2, x - pred[idx - 1][0], "#AEDFF0", 3);
  });
  ref.forEach(([x, y], idx) => {
    dot(slide, x, y, idx === 1 ? 6 : 4, C.orange);
    if (idx > 0) hline(slide, ref[idx - 1][0], (ref[idx - 1][1] + y) / 2, x - ref[idx - 1][0], "#F5B99B", 3);
  });
  vline(slide, tstar, 230, 44, C.red, 3);
  text(slide, "r_pred(t*)", 505, 214, 108, 20, { size: 14, color: C.blue, bold: true, align: "center" });
  text(slide, "r_ref(t*)", 646, 276, 96, 20, { size: 14, color: C.orange, bold: true, align: "center" });
  text(slide, "e(t*)", 586, 242, 58, 22, { size: 15, color: C.red, bold: true, align: "center" });

  rect(slide, 96, 424, 520, 132, "#FAFDFF", { fill: C.line, width: 1 }, 8);
  text(slide, "误差向量与标量误差", 124, 440, 230, 24, { size: 18, color: C.deep, bold: true });
  text(slide, "e_{s,i,h} = r_pred(t*) - r_ref(t*)", 124, 476, 360, 26, { size: 20, color: C.deep, bold: true });
  text(slide, "E_{s,i,h} = ||e_{s,i,h}||₂", 124, 510, 300, 26, { size: 20, color: C.orange, bold: true });
  text(slide, "E 用于误差量级统计；e 向量保留方向信息。", 124, 536, 390, 18, { size: 13.5, color: C.ink });

  rect(slide, 670, 424, 420, 132, "#FFF8F4", { fill: "#F3CAB8", width: 1 }, 8);
  text(slide, "RIC 分解", 698, 440, 120, 24, { size: 18, color: C.orange, bold: true });
  text(slide, "e_RIC = C_TEME→RIC · e", 698, 476, 330, 24, { size: 18, color: C.deep, bold: true });
  text(slide, "= [e_R, e_I, e_C]ᵀ", 698, 504, 220, 24, { size: 18, color: C.deep, bold: true });
  text(slide, "R 径向、I 沿迹、C 法向；用于估计协方差 Σ_{g,h}。", 698, 532, 320, 20, { size: 14, color: C.ink });
  return slide;
}
