export async function slide01(presentation) {
  const slide = presentation.slides.add();
  slide.shapes.add({ geometry:'rect', position:{left:0, top:0, width:1280, height:90}, fill:'#00A6D6', line:{fill:{type:'none'}} });
  const title = slide.shapes.add({ geometry:'rect', position:{left:80, top:25, width:600, height:50}, fill:{type:'none'}, line:{fill:{type:'none'}} });
  title.text = '测试标题';
  title.text.fontSize = 40; title.text.bold = true; title.text.color = '#ffffff';
  const body = slide.shapes.add({ geometry:'rect', position:{left:100, top:150, width:600, height:80}, fill:{type:'none'}, line:{fill:{type:'none'}} });
  body.text = '正文内容'; body.text.fontSize=28; body.text.color='#222222';
  return slide;
}
