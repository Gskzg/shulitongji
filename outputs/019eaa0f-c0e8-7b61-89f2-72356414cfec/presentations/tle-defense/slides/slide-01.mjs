import { C, coverBars, metric, rect, text } from "./common.mjs";

export async function slide01(presentation) {
  const slide = presentation.slides.add();
  coverBars(slide);
  text(slide, "TLE/SGP4 轨道预报误差统计分析", 72, 146, 900, 58, { size: 44, color: "#E6461A", bold: true });
  text(slide, "公开 TLE 数据下的1/3/7天预报误差、增长规律与轨道类型差异", 76, 218, 900, 34, { size: 22, color: C.ink });
  rect(slide, 76, 285, 82, 5, C.orange);
  text(slide, "数据：Space-Track gp_history，2025-01-01 至 2025-03-31", 76, 318, 780, 32, { size: 18, color: C.muted });
  text(slide, "报告人：", 914, 636, 260, 26, { size: 16, color: C.ink, align: "right" });
  metric(slide, "75", "NORAD目标：LEO/MEO/GEO各25个", 76, 405, 270, 92, C.blue);
  metric(slide, "16,214", "历史TLE记录", 374, 405, 250, 92, C.blue);
  metric(slide, "43,125", "预报误差样本", 652, 405, 260, 92, C.orange);
  text(slide, "Q & A", 604, 681, 80, 24, { size: 13, color: C.ink, align: "center" });
  return slide;
}
