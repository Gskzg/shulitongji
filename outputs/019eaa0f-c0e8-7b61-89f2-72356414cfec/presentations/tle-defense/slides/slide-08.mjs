import { C, callout, header, image, text } from "./common.mjs";

export async function slide08(presentation) {
  const slide = presentation.slides.add();
  header(slide, "结论二：误差分布右偏且长尾明显", 8);
  text(slide, "误差主体集中在低值区，少数极端样本拉长右尾并推高均值和 RMSE。", 74, 92, 1030, 30, { size: 21, bold: true });

  await image(slide, "outputs/figures/error_boxplot_by_orbit_horizon.png", 62, 140, 540, 390, "error boxplot");
  await image(slide, "outputs/figures/error_distribution_log10.png", 622, 140, 520, 390, "error distribution");

  callout(slide, "分布证据", "箱线图显示各轨道随时间上移；log 分布显示尾部样本远离主体。", 170, 540, 360, 76, C.orange);
  callout(slide, "统计含义", "后续区间估计和轨道差异检验要采用 Bootstrap 与非参数方法。", 675, 540, 380, 76, C.blue);
  return slide;
}
