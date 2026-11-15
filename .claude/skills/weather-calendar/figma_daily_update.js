// 매일 날씨지도(피그마 899:2) 업데이트용 코드. use_figma에 그대로 넣되, 첫 줄 DATA만 kma_4days.sh 출력으로 바꾼다.
// 파일: dnlLDtgRZ4Kk2VjlhmlhU8 / 프레임: 899:2 "2 (달력·팻말 크게 수정본)" / 아이콘 모음: 907:2 (tpl_sun·tpl_partly·tpl_cloudy·tpl_rain)
const DATA = __DATA__;
const POST_ID = '899:2', LIB_ID = '907:2';
const KO = {sun:'해', partly:'구름조금', cloudy:'흐림', rain:'비'};
const post = await figma.getNodeByIdAsync(POST_ID);
const lib = await figma.getNodeByIdAsync(LIB_ID);
const tpl = {}; for (const c of lib.children) if (c.name.startsWith('tpl_')) tpl[c.name.slice(4)] = c;
const md = DATA.dates.map(d => { const [, m, dd] = d.split('-'); return `${+m}.${dd}`; });
async function setText(t, s) {
  if (!t) return; const fonts = t.characters.length ? t.getRangeAllFontNames(0, t.characters.length) : [t.fontName];
  for (const f of fonts) await figma.loadFontAsync(f); t.characters = s;
}
const log = [];
for (const key of ['북', '서', '동', '남']) {
  const cells = post.findAll(n => (n.type === 'FRAME' || n.type === 'GROUP') && new RegExp('^칸_' + key + '_').test(n.name))
    .sort((a, b) => (Math.round(a.absoluteTransform[1][2] / 20) - Math.round(b.absoluteTransform[1][2] / 20)) || (a.absoluteTransform[0][2] - b.absoluteTransform[0][2]));
  const rows = DATA[key];
  for (let i = 0; i < cells.length && i < rows.length; i++) {
    const cell = cells[i]; const [day, icon, tmin, tmax, pop] = rows[i];
    await setText(cell.findOne(n => n.type === 'TEXT' && n.name === '날짜'), day);
    await setText(cell.findOne(n => n.type === 'TEXT' && n.name === '최저기온'), tmin === '--' ? '--' : tmin + '°');
    await setText(cell.findOne(n => n.type === 'TEXT' && n.name === '최고기온'), tmax === '--' ? '--' : tmax + '°');
    await setText(cell.findOne(n => n.type === 'TEXT' && n.name === '강수확률'), pop);
    const old = cell.children.find(n => n.name.startsWith('아이콘_') && n.name !== '아이콘_물방울');
    if (old && tpl[icon] && old.name !== '아이콘_' + KO[icon]) {
      const cx = old.x + old.width / 2, cy = old.y + old.height / 2;
      const c = tpl[icon].clone(); const idx = cell.children.indexOf(old);
      cell.insertChild(idx, c); c.name = '아이콘_' + KO[icon];
      c.x = cx - c.width / 2; c.y = cy - c.height / 2; old.remove();
    }
    cell.name = `칸_${key}_${md[i]}`;
    if (cell.parent.name.startsWith('날짜칸_')) cell.parent.name = `날짜칸_${key}_${md[i]}`;
    log.push(`${key} ${md[i]} ${icon} ${tmin}/${tmax} ${pop}`);
  }
}
const range = post.findOne(n => n.type === 'TEXT' && /^\d+\.\d+-\d+\.\d+$/.test(n.characters));
await setText(range, `${md[0]}-${md[md.length - 1]}`); if (range) range.name = `${md[0]}-${md[md.length - 1]}`;
const title = post.findOne(n => n.type === 'TEXT' && /^\d+月济州岛分区域天气/.test(n.characters));
if (title) { const m = +DATA.dates[0].split('-')[1]; await setText(title, title.characters.replace(/^\d+月/, m + '月')); title.name = title.characters; }
return log;
