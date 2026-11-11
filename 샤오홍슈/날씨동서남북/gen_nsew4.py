#!/usr/bin/env python3
# 제주 동서남북 날씨 카드 4일치 (피그마용 SVG) — 기상청 제주 4개 관측소 데이터
import json, sys, base64, struct, math, os, re

ICON_DIR = "/home/user/shaohong/.claude/skills/weather-calendar/icons"
def icon(kind, cx, cy, scale, iid):
    raw = open(os.path.join(ICON_DIR, kind + ".png"), "rb").read()
    w, h = struct.unpack(">II", raw[16:24]); w, h = w*scale, h*scale
    return f'<image id="{iid}" x="{cx-w/2:.1f}" y="{cy-h/2:.1f}" width="{w:.1f}" height="{h:.1f}" href="data:image/png;base64,{base64.b64encode(raw).decode()}"/>'

CJK = re.compile(r"([　-〿一-鿿＀-￯·]+)")
def t(txt, x, y, size, color, weight, anchor="start", tid=None, ls=0):
    parts = [p for p in CJK.split(txt) if p]
    if any(CJK.fullmatch(p) for p in parts):
        fam = "Noto Sans SC, WenQuanYi Zen Hei"
        body = "".join(p if CJK.fullmatch(p) else f'<tspan font-family="Inter">{p}</tspan>' for p in parts)
    else:
        fam, body = "Inter", txt
    i = f' id="{tid}"' if tid else ""
    l = f' letter-spacing="{ls}"' if ls else ""
    return f'<text{i} x="{x}" y="{y}" font-family="{fam}" font-size="{size}" font-weight="{weight}" fill="{color}" text-anchor="{anchor}"{l}>{body}</text>'

W, H = 1080, 1350
# 제주 해안선 (경도, 위도) — 단순화한 실루엣
COAST = [(126.163,33.300),(126.200,33.360),(126.262,33.410),(126.320,33.452),(126.400,33.480),
 (126.480,33.508),(126.540,33.520),(126.620,33.538),(126.700,33.553),(126.760,33.560),
 (126.830,33.540),(126.880,33.515),(126.915,33.490),(126.945,33.462),(126.930,33.430),
 (126.880,33.380),(126.830,33.330),(126.760,33.290),(126.680,33.265),(126.580,33.240),
 (126.480,33.240),(126.410,33.235),(126.340,33.225),(126.290,33.200),(126.240,33.210),(126.190,33.245)]
LON0, LAT0, K = 126.15, 33.58, 720
COSL = math.cos(math.radians(33.4))
X0, Y0 = 300, 540
def proj(lon, lat): return (X0 + (lon-LON0)*K*COSL, Y0 + (LAT0-lat)*K)

def smooth(pts):  # 닫힌 캣멀-롬 → 베지어
    n = len(pts); d = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
    for i in range(n):
        p0, p1, p2, p3 = pts[i-1], pts[i], pts[(i+1)%n], pts[(i+2)%n]
        c1 = (p1[0]+(p2[0]-p0[0])/6, p1[1]+(p2[1]-p0[1])/6)
        c2 = (p2[0]-(p3[0]-p1[0])/6, p2[1]-(p3[1]-p1[1])/6)
        d += f" C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}"
    return d + " Z"


def build(d):
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
     '<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7FA3C6"/><stop offset="1" stop-color="#C9D9E6"/></linearGradient>',
     '<linearGradient id="land" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8DBF7A"/><stop offset="1" stop-color="#5E9A5A"/></linearGradient>',
     '<filter id="cardShadow" x="-15%" y="-15%" width="130%" height="140%"><feDropShadow dx="0" dy="6" stdDeviation="9" flood-color="#1B2C40" flood-opacity=".22"/></filter>',
     '<filter id="islandShadow" x="-10%" y="-20%" width="120%" height="150%"><feDropShadow dx="0" dy="8" stdDeviation="10" flood-color="#1B2C40" flood-opacity=".25"/></filter></defs>',
     f'<rect id="배경_하늘사진으로_교체" width="{W}" height="{H}" fill="url(#sky)"/>']
    o += ['<g id="제목">',
      t("JEJU · WEATHER", 540, 70, 24, "#FFFFFF", 700, "middle", "영문_머리", ls=6),
      t("济州东西南北天气", 540, 148, 68, "#1B2C40", 900, "middle", "제목"),
      f'<rect id="날짜_알약" x="{540-230}" y="170" width="460" height="52" rx="26" fill="#E8803C"/>',
      t(d["date_label"], 540, 206, 27, "#FFFFFF", 700, "middle", "날짜"), '</g>']
    pts = [proj(*p) for p in COAST]
    o.append(f'<g id="제주_지도"><path id="제주섬" d="{smooth(pts)}" fill="url(#land)" stroke="#FFFFFF" stroke-width="4" filter="url(#islandShadow)"/>')
    hx, hy = proj(126.533, 33.362)
    o.append(f'<path id="한라산" d="M{hx-30:.1f} {hy+14:.1f} L{hx:.1f} {hy-20:.1f} L{hx+30:.1f} {hy+14:.1f} Z" fill="#3F7444" opacity=".85"/>')
    o.append(t("汉拿山", hx, hy+40, 19, "#FFFFFF", 700, "middle", "한라산_이름"))
    o.append('</g>')
    days = d["days"]; HB = 50  # 방향 띠 높이
    # 가로 카드(북·남): 4칸 / 세로 카드(서·동): 4줄
    box = {"N": (200, 240, 680, 236), "S": (200, 884, 680, 236),
           "W": (14, 490, 262, 380), "E": (804, 490, 262, 380)}
    o.append('<g id="동서남북_카드">')
    for s in d["stations"]:
        x, y, w, h = box[s["dir"]]
        dx, dy = proj(s["lon"], s["lat"])
        if s["dir"] == "N": ax, ay = dx, y+h
        elif s["dir"] == "S": ax, ay = dx, y
        elif s["dir"] == "W": ax, ay = x+w, dy
        else: ax, ay = x, dy
        g = [f'<g id="카드_{s["ko"]}">',
             f'<line id="연결선" x1="{ax:.1f}" y1="{ay:.1f}" x2="{dx:.1f}" y2="{dy:.1f}" stroke="#FFFFFF" stroke-width="3" stroke-dasharray="6 6"/>',
             f'<circle id="관측소_점" cx="{dx:.1f}" cy="{dy:.1f}" r="10" fill="#E8121F" stroke="#FFFFFF" stroke-width="4"/>',
             f'<rect id="카드_배경" x="{x}" y="{y}" width="{w}" height="{h}" rx="22" fill="#FFFFFF" fill-opacity=".95" filter="url(#cardShadow)"/>',
             f'<rect id="방향_띠" x="{x}" y="{y}" width="{w}" height="{HB}" rx="22" fill="{s["color"]}"/>',
             f'<rect x="{x}" y="{y+28}" width="{w}" height="22" fill="{s["color"]}"/>',
             t(s["dir_zh"] + " · " + s["zh"], x+w/2, y+35, 26, "#FFFFFF", 800, "middle", "방향_지역")]
        for i, (dd, f) in enumerate(zip(days, s["f"])):
            rain = f["pop"] >= 60
            if s["dir"] in "NS":
                cw = w/4; cx = x + cw*i; mid = cx + cw/2; top = y + HB
                g.append(f'<g id="{dd["d"]}">')
                if rain: g.append(f'<rect id="비오는날_강조" x="{cx+6:.1f}" y="{top+6}" width="{cw-12:.1f}" height="{h-HB-14}" rx="14" fill="#DCEBF7"/>')
                if i: g.append(f'<line x1="{cx:.1f}" y1="{top+14}" x2="{cx:.1f}" y2="{y+h-14}" stroke="#E3E8EE" stroke-width="2"/>')
                g += [t(f'{dd["d"]} {dd["wd"]}', mid, top+31, 22, "#1B2C40", 800, "middle", "날짜"),
                      icon(f["icon"], mid, top+69, 0.6, "아이콘"),
                      t(f'{f["tmin"]}~{f["tmax"]}°', mid, top+122, 32, "#141414", 800, "middle", "기온"),
                      t(f["wf"], mid, top+150, 19, "#333333", 700, "middle", "날씨"),
                      t(f'降水 {f["pop"]}%', mid, top+175, 18, "#1F6FB2" if rain else "#555555", 700 if rain else 500, "middle", "강수"),
                      '</g>']
            else:
                rh = (h-HB)/4; ry = y + HB + rh*i; mid = ry + rh/2
                g.append(f'<g id="{dd["d"]}">')
                if rain: g.append(f'<rect id="비오는날_강조" x="{x+6}" y="{ry+4:.1f}" width="{w-12}" height="{rh-8:.1f}" rx="12" fill="#DCEBF7"/>')
                if i: g.append(f'<line x1="{x+14}" y1="{ry:.1f}" x2="{x+w-14}" y2="{ry:.1f}" stroke="#E3E8EE" stroke-width="2"/>')
                g += [t(dd["d"], x+16, mid-4, 22, "#1B2C40", 800, "start", "날짜"),
                      t(dd["wd"], x+16, mid+22, 18, "#555555", 600, "start", "요일"),
                      icon(f["icon"], x+104, mid, 0.5, "아이콘"),
                      t(f'{f["tmin"]}~{f["tmax"]}°', x+w-14, mid+2, 28, "#141414", 800, "end", "기온"),
                      t(f'降水 {f["pop"]}%', x+w-14, mid+27, 17, "#1F6FB2" if rain else "#555555", 700 if rain else 500, "end", "강수"),
                      '</g>']
        g.append('</g>')
        o += g
    o.append('</g>')
    o += ['<g id="아래">',
      f'<rect id="한마디_배경" x="160" y="1150" width="760" height="74" rx="37" fill="#FFF7D4" filter="url(#cardShadow)"/>',
      t(d["note"], 540, 1198, 31, "#141414", 800, "middle", "한마디"),
      t(d["source"], 540, 1290, 20, "#1B2C40", 500, "middle", "출처"), '</g>', '</svg>']
    return "\n".join(o)

if __name__ == "__main__":
    d = json.load(open(sys.argv[1], encoding="utf-8"))
    open(sys.argv[2] + ".svg", "w", encoding="utf-8").write(build(d))
    print("saved", sys.argv[2] + ".svg")
