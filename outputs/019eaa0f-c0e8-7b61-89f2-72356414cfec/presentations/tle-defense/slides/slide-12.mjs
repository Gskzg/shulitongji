import { C, coverBars, metric, rect, text } from "./common.mjs";

export async function slide12(presentation) {
  const slide = presentation.slides.add();
  coverBars(slide);
  text(slide, "研究结论与应用价值", 82, 88, 560, 52, { size: 40, color: C.deep, bold: true });
  rect(slide, 86, 158, 84, 5, C.orange);
  text(slide, "公开 TLE 误差评估可以概括为误差定义、统计结论和方法价值三个层面。", 86, 184, 820, 28, { size: 20, color: C.ink, bold: true });

  metric(slide, "误差定义", "旧 TLE + SGP4 给出预报位置，未来 TLE 提供公开体系内的近似参考。", 92, 250, 340, 122, C.blue);
  metric(slide, "统计结论", "误差随 1/3/7 天增长，GEO 典型误差最高；分布长尾使 RMSE 明显放大。", 470, 250, 340, 122, C.orange);
  metric(slide, "方法价值", "Bootstrap/BCa 与非参数检验使结论不依赖单一平均值或正态假设。", 848, 250, 340, 122, C.green);

  text(slide, "项目交付：数据下载脚本、SGP4误差计算、Bootstrap/BCa、协方差表、轨道类型检验、图表与报告模板。", 86, 432, 1100, 32, { size: 19, color: C.ink, bold: true, align: "center" });
  text(slide, "谢谢聆听", 524, 514, 230, 44, { size: 38, color: C.blue, bold: true, align: "center" });
  text(slide, "Q & A", 594, 566, 90, 24, { size: 18, color: C.muted, align: "center" });
  return slide;
}
