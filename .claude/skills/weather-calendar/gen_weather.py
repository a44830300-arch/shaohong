#!/usr/bin/env python3
# 제주 날씨달력 카드 생성기 (강정준비준 전용) — 사용: python3 gen_weather.py data.json 출력경로(확장자 없이)
# data.json: {"month":"10月","sunrise":"06:47~06:59","sunset":"17:48~17:36","note":"28日起明显降温",
#             "source":"AccuWeather","days":[["26","rain",16,26,"80%"], ... 14개]}
# icon 종류: sun(맑음) partly(구름조금/대체로흐림) cloudy(흐림) rain(비·소나기)
import json, sys, base64, io
# 아이콘은 icons/ 폴더의 PNG를 그대로 읽는다 (스크립트를 짧게 유지해 크레딧 절약)
import os, struct
_HERE = os.path.dirname(os.path.abspath(__file__))
ICONS, _SIZE = {}, {}
for _k in ("sun", "partly", "cloudy", "rain", "drop"):
    _raw = open(os.path.join(_HERE, "icons", _k + ".png"), "rb").read()
    ICONS[_k] = base64.b64encode(_raw).decode()
    _SIZE[_k] = struct.unpack(">II", _raw[16:24])  # PNG 머리에서 가로·세로
W, H = 1080, 1350
# 격자: 칸 124×280, 가로·세로 간격 모두 12, 좌우 여백 70 (1080 = 70 + 124×7 + 12×6 + 70)
CW, CH, GAP, LEFT, TOP = 124, 280, 12, 70, 400
COLX = [LEFT + i*(CW+GAP) for i in range(7)]
ROWY = [TOP, TOP + CH + GAP]
RIGHT = COLX[-1] + CW  # 1010
PAD = 9  # 칸 안쪽 여백
NAMES = {"sun":"해","partly":"구름조금","cloudy":"흐림","rain":"비","drop":"물방울"}
SCALE = {"sun":1.15,"partly":1.15,"cloudy":1.15,"rain":1.15,"drop":0.8}
def img(kind, cx, cy):
    w, h = _SIZE[kind]
    w, h = w*SCALE[kind], h*SCALE[kind]
    return f'<image id="아이콘_{NAMES[kind]}" x="{cx-w/2:.1f}" y="{cy-h/2:.1f}" width="{w:.1f}" height="{h:.1f}" href="data:image/png;base64,{ICONS[kind]}"/>'
import re
FONT_LATIN = "Inter"          # 숫자·영문
FONT_CJK = "Noto Sans SC"     # 한자 (Inter에는 한자가 없음)
_CJK = re.compile(r"([\u3000-\u303f\u4e00-\u9fff\uff00-\uffef]+)")
def t(txt, x, y, size, color, weight, anchor="start", tid=None, shadow=False):
    f = ' filter="url(#txtShadow)"' if shadow else ""
    i = f' id="{tid}"' if tid else ""
    parts = [p for p in _CJK.split(txt) if p]
    has_cjk = any(_CJK.fullmatch(p) for p in parts)
    if not has_cjk:
        body, fam = txt, FONT_LATIN
    else:
        fam = FONT_CJK
        body = "".join(p if _CJK.fullmatch(p) else f'<tspan font-family="{FONT_LATIN}">{p}</tspan>' for p in parts)
    return f'<text{i} x="{x}" y="{y}" font-family="{fam}" font-size="{size}" font-weight="{weight}" fill="{color}" text-anchor="{anchor}"{f}>{body}</text>'
def build(d):
    wk = ["周一","周二","周三","周四","周五","周六","周日"]
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
    '<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7FA3C6"/><stop offset="1" stop-color="#B9CCDD"/></linearGradient>',
    '<filter id="paperShadow" x="-10%" y="-10%" width="130%" height="130%"><feDropShadow dx="0" dy="6" stdDeviation="8" flood-color="#000" flood-opacity=".22"/></filter>',
    '<filter id="tagShadow" x="-10%" y="-10%" width="130%" height="140%"><feDropShadow dx="0" dy="4" stdDeviation="5" flood-color="#000" flood-opacity=".18"/></filter>',
    '<filter id="txtShadow" x="-20%" y="-30%" width="140%" height="170%"><feDropShadow dx="0" dy="1.5" stdDeviation="1.6" flood-color="#1B2C40" flood-opacity=".45"/></filter></defs>',
    f'<rect id="배경_하늘사진으로_교체" width="{W}" height="{H}" fill="url(#sky)"/>',
    '<g id="월_태그" filter="url(#tagShadow)"><path id="태그_배경" d="M12 210 L290 176 L278 274 L22 300 Z" fill="#E8803C"/></g>',
    t(d["month"], 75, 268, 74, "#2A1A0E", 600, tid="월"),
    '<g id="포스트잇"><rect id="포스트잇_종이" x="724" y="72" width="286" height="248" fill="#FFF7D4" filter="url(#paperShadow)"/>',
    '<rect id="테이프" x="918" y="62" width="130" height="38" fill="#E8162B" fill-opacity=".95" transform="rotate(30 983 81)"/>',
    t("日出 "+d["sunrise"], 867, 132, 27, "#141414", 700, "middle", "일출"),
    t("日落 "+d["sunset"], 867, 168, 27, "#141414", 700, "middle", "일몰"),
    t(d.get("note",""), 867, 234, 28, "#141414", 700, "middle", "한마디"), '</g>', '<g id="요일">']
    for i, w_ in enumerate(wk):
        o.append(t(w_, COLX[i]+PAD, 386, 30, "#E8121F" if i == 6 else "#141414", 500, tid=f"요일_{w_}"))
    o.append('</g><g id="날짜_칸들">')
    for n, (lab, kind, lo, hi, pop) in enumerate(d["days"][:14]):
        r, c = divmod(n, 7); x, y = COLX[c], ROWY[r]; cx = x + CW/2
        o += [f'<g id="칸_{lab}">',
              f'<rect id="칸_배경" x="{x}" y="{y}" width="{CW}" height="{CH}" rx="2" fill="#FFFFFF" fill-opacity=".22"/>',
              t(lab, x+PAD, y+36, 32, "#FFFFFF", 600, tid="날짜", shadow=True),
              img(kind, cx, y+86),
              t(f"{lo}°", cx, y+160, 33, "#1A3CF5", 500, "middle", "최저기온"),
              t(f"{hi}°", cx, y+204, 33, "#FF3B3B", 500, "middle", "최고기온"),
              img("drop", x+PAD+10, y+CH-22),
              t(pop, x+PAD+24, y+CH-15, 19, "#FFFFFF", 600, tid="강수확률", shadow=True), '</g>']
    o.append('</g>')
    o.append(t("数据来源："+d.get("source","AccuWeather"), RIGHT, ROWY[1]+CH+40, 25, "#FFFFFF", 700, "end", "출처", shadow=True))
    o.append('</svg>')
    return "\n".join(o)
if __name__ == "__main__":
    data = json.load(open(sys.argv[1])); name = sys.argv[2]
    if len(data.get("note", "")) > 14:
        print("경고: 포스트잇 한마디가 14자를 넘어 칸 밖으로 나갈 수 있어요. 더 짧게 줄이세요.")
    if len(data["days"]) != 14:
        print("경고: days가 14개가 아니에요:", len(data["days"]))
    os.makedirs(os.path.dirname(os.path.abspath(name)), exist_ok=True)
    open(name + ".svg", "w", encoding="utf-8").write(build(data))
    print("wrote", name + ".svg")
