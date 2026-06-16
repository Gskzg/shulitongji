export async function slide01(presentation) {
  const slide = presentation.slides.add();
  slide.shapes.add({ geometry:'rect', position:{left:0,top:0,width:1280,height:720}, fill:'#fff', line:{fill:{type:'none'}} });
  slide.images.add({ path:'/Users/macbook/Documents/数理统计大作业/outputs/figures/error_growth_median_iqr.png', position:{left:100, top:100, width:600, height:400}, fit:'contain', alt:'growth' });
  return slide;
}
