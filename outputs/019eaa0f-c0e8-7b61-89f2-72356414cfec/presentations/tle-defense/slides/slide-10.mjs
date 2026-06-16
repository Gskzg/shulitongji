import { C, callout, header, image, smallTable, text } from "./common.mjs";

export async function slide10(presentation) {
  const slide = presentation.slides.add();
  header(slide, "结论四：Bootstrap更稳健，GEO差异最显著", 10);
  text(slide, "长尾分布下，区间估计和组间检验都要避免过度依赖正态假设。", 74, 92, 1030, 30, { size: 21, bold: true });

  await image(slide, "outputs/figures/ci_gaussian_vs_bootstrap.png", 66, 140, 520, 360, "confidence interval comparison");

  smallTable(slide, [
    ["轨道", "1天BCa", "3天BCa", "7天BCa"],
    ["GEO", "[0.605,0.658]", "[2.518,2.717]", "[10.680,11.914]"],
    ["LEO", "[0.089,0.094]", "[0.483,0.508]", "[1.773,1.886]"],
    ["MEO", "[0.160,0.173]", "[0.538,0.570]", "[2.040,2.170]"],
  ], 626, 146, [70, 140, 140, 150], 42, { size: 12.4, headerSize: 12.4 });

  smallTable(slide, [
    ["天数", "Kruskal-Wallis p值", "Levene p值"],
    ["1", "<1e-300", "4.13e-99"],
    ["3", "<1e-300", "1.78e-44"],
    ["7", "<1e-300", "2.64e-33"],
  ], 626, 340, [80, 210, 170], 42, { size: 13.5, headerSize: 13.5 });

  callout(slide, "Bootstrap结论", "BCa 区间能反映偏态和偏差修正；中位数区间相对稳定，适合描述典型精度。", 104, 520, 430, 82, C.blue);
  callout(slide, "轨道差异结论", "GEO 在 1/3/7 天均显著高于 LEO、MEO；LEO 与 MEO 在 3天和7天差异不显著。", 654, 520, 430, 82, C.orange);
  return slide;
}
