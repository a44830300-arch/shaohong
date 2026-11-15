// 매일 날씨지도 업데이트용 코드 (2026-11-15부터 "분실물" 파일에 매일 1장씩 등록).
// use_figma에 그대로 넣되, 아래 DATA 자리표시는 kma_4days.sh 출력 JSON, WEEKDAY 자리표시는 오늘 요일 한 글자(예: "월")로 바꾼다.
// 파일: 분실물 fileKey 4N53vLKWZHasdvc5TXDe2p / 페이지 "날씨"(0:1)
//  - 틀: 이름에 "칸_북_" 칸이 들어 있는 프레임(처음엔 샤오홍슈 파일 899:2를 붙여 넣은 것)
//  - 아이콘 모음: 이름이 "아이콘 모음"으로 시작하는 프레임(tpl_sun·tpl_partly·tpl_cloudy·tpl_rain)
// 동작: 맨 아래(최신) 줄의 세트 [날씨지도 + 오른쪽 분실물 안내]를 복제해 아래 새 줄로 두고
//       이름을 "날씨지도 MM/DD (요일)" / "분실물 안내 MM/DD (요일)"로 바꾼 뒤 날씨지도에 4구역 × 4일 값을 넣는다.
//       같은 날짜 이름의 프레임이 이미 있으면 새로 만들지 않고 그것을 고친다. 결과 첫 두 줄: MAP id, GUIDE id.
const DATA = __DATA__;
const WEEKDAY = '__WEEKDAY__';
const KO = {sun:'해', partly:'구름조금', cloudy:'흐림', rain:'비'};
const page = figma.root.children.find(p => p.name === '날씨') || figma.root.children[0];
await figma.setCurrentPageAsync(page);
const lib = page.children.find(n => n.name.startsWith('아이콘 모음'));
if (!lib) return 'ERROR: 아이콘 모음 프레임이 없음';
const tpl = {}; for (const c of lib.children) if (c.name.startsWith('tpl_')) tpl[c.name.slice(4)] = c;
const maps = page.children.filter(n => n.type === 'FRAME' && n !== lib && n.findOne(x => /^칸_북_/.test(x.name)));
if (!maps.length) return 'ERROR: 날씨지도 틀 프레임이 없음';
const md = DATA.dates.map(d => { const [, m, dd] = d.split('-'); return `${+m}.${dd}`; });
const [, M0, D0] = DATA.dates[0].split('-');
const todayName = `날씨지도 ${M0}/${D0} (${WEEKDAY})`;
// 세트 = 같은 줄에 있는 [날씨지도, 분실물 안내(오른쪽)]. 매일 맨 아래(최신) 줄을 통째로 복제해 그 아래 새 줄로 둔다.
const guideName = `분실물 안내 ${M0}/${D0} (${WEEKDAY})`;
const companionOf = m => page.children.find(n => n.type === 'FRAME' && n !== lib && !maps.includes(n) && Math.abs(n.y - m.y) < 5 && n.x > m.x);
let post = maps.find(n => n.name === todayName);
let guide = post ? companionOf(post) : null;
if (!post) {
  const latest = maps.reduce((a, b) => (b.y > a.y ? b : a));
  const latestGuide = companionOf(latest);
  const dy = latest.height + 200;
  post = latest.clone(); page.appendChild(post); post.x = latest.x; post.y = latest.y + dy; post.name = todayName;
  if (latestGuide) { guide = latestGuide.clone(); page.appendChild(guide); guide.x = latestGuide.x; guide.y = latestGuide.y + dy; }
}
if (guide) guide.name = guideName;
async function setText(t, s) {
  if (!t) return; const fonts = t.characters.length ? t.getRangeAllFontNames(0, t.characters.length) : [t.fontName];
  for (const f of fonts) await figma.loadFontAsync(f); t.characters = s;
}
const log = ['MAP ' + post.id + ' ' + post.name, 'GUIDE ' + (guide ? guide.id + ' ' + guide.name : '없음')];
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
figma.viewport.scrollAndZoomIntoView([post]);
return log;
