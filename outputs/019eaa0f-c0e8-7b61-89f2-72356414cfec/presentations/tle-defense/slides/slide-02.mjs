import { C, dot, header, hline, rect, text, vline } from "./common.mjs";

export async function slide02(presentation) {
  const slide = presentation.slides.add();
  header(slide, "研究框架：公开编目数据的误差统计模型", 2);
  text(slide, "以目标 s、TLE 历元 i、预报时长 h 为索引，把轨道传播问题转化为误差样本的统计推断问题。", 74, 96, 1060, 32, { size: 21, color: C.ink, bold: true });

  rect(slide, 82, 148, 1040, 382, "#FAFDFF", { fill: C.line, width: 1 }, 8);
  vline(slide, 168, 190, 276, C.deep, 3);

  const rows = [
    ["数据层", "TLE_{s,i}", "平均轨道根数 + 历元 epoch + B* 阻力项", "同一目标 s 的历史 TLE 序列"],
    ["传播层", "r_pred(t*) = SGP4(TLE_{s,i}, h)", "t* = epoch_i + h，h ∈ {1,3,7} 天", "旧 TLE 给出目标时刻的位置预报"],
    ["误差层", "e_{s,i,h} = r_pred(t*) - r_ref(t*)", "E_{s,i,h}=||e_{s,i,h}||₂；e_RIC = C e", "新 TLE 在 t* 附近提供公开体系内参考"],
    ["统计层", "D_{g,h} = {E_{s,i,h}: orbit(s)=g}", "θ=f(D)：中位数、RMSE、分位数、增长指数", "按轨道类型 g 和时长 h 汇总推断"],
  ];

  rows.forEach((row, idx) => {
    const y = 184 + idx * 76;
    hline(slide, 206, y + 55, 860, idx === rows.length - 1 ? "#FFFFFF" : "#E6EEF4", 1);
    dot(slide, 168, y + 20, 7, idx === 1 ? C.orange : C.deep);
    text(slide, row[0], 92, y + 4, 64, 28, { size: 17, color: idx === 1 ? C.orange : C.deep, bold: true, align: "right" });
    text(slide, row[1], 218, y, 330, 28, { size: 19, color: idx === 1 ? C.orange : C.deep, bold: true });
    text(slide, row[2], 570, y, 310, 28, { size: 15.5, color: C.ink });
    text(slide, row[3], 902, y - 2, 180, 34, { size: 14.5, color: C.muted, lineSpacing: 1.05 });
  });

  rect(slide, 164, 554, 850, 48, "#FFF8F4", { fill: "#F3CAB8", width: 1 }, 8);
  text(slide, "核心观点", 194, 566, 112, 22, { size: 18, color: C.orange, bold: true });
  text(slide, "TLE 预报误差不是单一平均数，而是随 h、g 和长尾样本共同变化的分布。", 324, 564, 610, 24, { size: 18, color: C.ink, bold: true });
  return slide;
}
