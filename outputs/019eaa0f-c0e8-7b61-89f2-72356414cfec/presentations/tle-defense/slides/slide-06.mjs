import { C, header, metric, smallTable, text } from "./common.mjs";

export async function slide06(presentation) {
  const slide = presentation.slides.add();
  header(slide, "数据构建：平衡抽样支持三类轨道比较", 6);
  text(slide, "每类轨道抽取 25 个公开编目目标，形成 LEO、MEO、GEO 三组可比较样本。", 74, 96, 1030, 32, { size: 21, bold: true });

  metric(slide, "25", "LEO：低轨地球观测/气象目标", 74, 160, 310, 95, C.blue);
  metric(slide, "25", "MEO：GPS operational satellites", 424, 160, 310, 95, C.green);
  metric(slide, "25", "GEO：地球同步气象/通信目标", 774, 160, 310, 95, C.orange);

  smallTable(slide, [
    ["轨道类型", "1天样本", "3天样本", "7天样本", "目标数"],
    ["GEO", "4,641", "4,393", "4,188", "25"],
    ["LEO", "7,813", "7,651", "7,291", "25"],
    ["MEO", "2,447", "2,423", "2,278", "25"],
  ], 106, 322, [170, 160, 160, 160, 140], 42, { size: 15, headerSize: 15 });

  text(slide, "数据来源：Space-Track gp_history，时间窗口 2025-01-01 至 2025-03-31。标准化后得到 16,214 条 TLE 记录和 43,125 条误差样本。", 106, 520, 900, 44, { size: 17, color: C.muted, lineSpacing: 1.08 });
  return slide;
}
