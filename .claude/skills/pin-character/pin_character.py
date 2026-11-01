"""핀 캐릭터 SVG 만들기 도구.

쓰는 법:  python3 pin_character.py <포즈이름> <저장할.svg>
포즈는 아래 POSES에 있다. 새 포즈는 POSES에 하나 더 넣어서 만든다.
좌표는 '핀 기준 좌표'(원래 핀 61x86, 뾰족한 끝 = (30.5, 83))다.
"""
import math, sys

RED = "#EF3D32"     # 핀·팔다리 색 (피그마 원본 핀 색)
DARK = "#2B2B2B"    # 소품(깃대·체크무늬 등)
PIN = ("M30.5 2C13.4 2 2 16.5412 2 35.2371C2 56.0102 30.5 83.0153 30.5 83.0153"
       "C30.5 83.0153 59 56.0102 59 35.2371C59 16.5412 47.6 2 30.5 2Z")
HOLE = ("M30.5004 43.5459C35.7471 43.5459 40.0004 38.8956 40.0004 33.1593"
        "C40.0004 27.4229 35.7471 22.7727 30.5004 22.7727C25.2537 22.7727 21.0004 27.4229 21.0004 33.1593"
        "C21.0004 38.8956 25.2537 43.5459 30.5004 43.5459Z")

LIMB_W, OUTLINE_W, HAND_R = 6, 12, 5.5   # 팔다리 굵기, 흰 테두리 굵기, 손 크기


def _layer(pose, color, w, extra):
    s = "".join(f'<path d="{d}" stroke="{color}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>'
                for d in pose["limbs"])
    s += "".join(f'<circle cx="{x}" cy="{y}" r="{pose.get("hand_r", HAND_R) + extra}" fill="{color}"/>' for x, y in pose["hands"])
    for r in pose["shoes"]:  # r = (x, y, w, h, 회전각, 회전중심x, 회전중심y)
        x, y, sw, sh, *rot = r
        t = f' transform="rotate({rot[0]} {rot[1]} {rot[2]})"' if rot else ""
        st = f' stroke="{color}" stroke-width="{extra * 2}"' if extra else ""
        s += f'<rect x="{x}" y="{y}" width="{sw}" height="{sh}" rx="4"{t} fill="{color}"{st}/>'
    return s


def build(name, pose):
    w, h = pose["size"]
    tx, ty = pose["move"]
    return f'''<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" fill="none" xmlns="http://www.w3.org/2000/svg">
<g id="{name}">
{pose.get("effects", "")}
<g id="캐릭터" transform="translate({tx} {ty}) rotate({pose.get("tilt", 0)} 30.5 {pose.get("pivot_y", 45)})">
<g id="흰 테두리">{pose.get("prop_outline", "")}{_layer(pose, "white", OUTLINE_W, 3)}<path d="{PIN}" fill="white" stroke="white" stroke-width="8" stroke-linejoin="round"/></g>
{pose.get("prop", "")}
<g id="팔다리">{_layer(pose, RED, LIMB_W, 0)}</g>
<g id="핀"><path d="{PIN}" fill="{RED}"/><path d="{HOLE}" fill="white"/></g>
{pose.get("prop_front", "")}
</g>
</g>
</svg>'''


def motion_lines(paths, gid="효과선", width=3.5):
    """속도선·흔들기선 같은 연한 빨간 효과선 (캔버스 좌표)."""
    return (f'<g id="{gid}" stroke="{RED}" stroke-width="{width}" stroke-linecap="round" opacity="0.45">'
            + "".join(f'<path d="{d}"/>' for d in paths) + "</g>")


def checker_flag(x0=88, y0=-36, W=34, H=22, cols=4, rows=3, pole="M80.2 15 L88.6 -37"):
    """펄럭이는 체크무늬 깃발. (흰 테두리용, 본체) 두 개를 돌려준다."""
    def m(u, v):
        return x0 + u * W - v * H * 0.15, y0 + v * H + 3.2 * math.sin(2 * math.pi * u)

    def poly(u0, v0, u1, v1, n=4):
        p = [m(u0 + (u1 - u0) * i / n, v0) for i in range(n + 1)]
        p += [m(u1, v0 + (v1 - v0) * i / n) for i in range(1, n + 1)]
        p += [m(u1 - (u1 - u0) * i / n, v1) for i in range(1, n + 1)]
        p += [m(u0, v1 - (v1 - v0) * i / n) for i in range(1, n)]
        return "M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in p) + "Z"
    outer = poly(0, 0, 1, 1, 16)
    cells = "".join(f'<path d="{poly(c / cols, r / rows, (c + 1) / cols, (r + 1) / rows)}" fill="{DARK}"/>'
                    for r in range(rows) for c in range(cols) if (r + c) % 2 == 0)
    outline = (f'<path d="{pole}" stroke="white" stroke-width="10" stroke-linecap="round"/>'
               f'<path d="{outer}" fill="white" stroke="white" stroke-width="7" stroke-linejoin="round"/>')
    body = (f'<g id="깃발"><path d="{pole}" stroke="{DARK}" stroke-width="3.5" stroke-linecap="round"/>'
            f'<path d="{outer}" fill="white" stroke="{DARK}" stroke-width="1.8" stroke-linejoin="round"/>{cells}</g>')
    return outline, body



def music_notes(notes, gid="음표"):
    """연한 빨간 음표 효과 (캔버스 좌표). notes = [(x, y, 크기, 겹음표?)], (x, y) = 음표 머리 가운데."""
    out = ""
    for x, y, k, double in notes:
        hx, hy, h = 4.2 * k, 3.2 * k, 15 * k   # 머리 가로·세로 반지름, 기둥 길이
        sx = x + hx - 0.9 * k
        head = f'<ellipse cx="{x}" cy="{y}" rx="{hx:.2f}" ry="{hy:.2f}" transform="rotate(-20 {x} {y})"/>'
        if double:
            x2, y2 = x + 11 * k, y - 3 * k
            head += f'<ellipse cx="{x2}" cy="{y2}" rx="{hx:.2f}" ry="{hy:.2f}" transform="rotate(-20 {x2} {y2})"/>'
            sx2 = x2 + hx - 0.9 * k
            stem = (f'<path d="M{sx:.2f} {y:.2f}V{y - h:.2f}L{sx2:.2f} {y2 - h:.2f}V{y2:.2f}" fill="none" '
                    f'stroke-width="{2.4 * k:.2f}" stroke-linejoin="round"/>'
                    f'<path d="M{sx:.2f} {y - h + 4 * k:.2f}L{sx2:.2f} {y2 - h + 4 * k:.2f}" stroke-width="{2.4 * k:.2f}"/>')
        else:
            stem = (f'<path d="M{sx:.2f} {y:.2f}V{y - h:.2f}Q{sx + 2 * k:.2f} {y - h + 6 * k:.2f} {sx + 7 * k:.2f} {y - h + 8 * k:.2f}" '
                    f'fill="none" stroke-width="{2.4 * k:.2f}" stroke-linecap="round"/>')
        out += head + stem
    return f'<g id="{gid}" fill="{RED}" stroke="{RED}" opacity="0.45">{out}</g>'


def microphone(hand=(69, 23), head=(60, 7), r=6, hw=5.5, tail=6):
    """손에 든 마이크. (흰 테두리용, 본체) 두 개를 돌려준다."""
    (hx, hy), (mx, my) = hand, head
    dx, dy = hx - mx, hy - my
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    px, py = -uy, ux
    k = r / 6
    bx, by = hx + ux * tail, hy + uy * tail            # 손잡이 끝 (손 아래로 조금 나옴)
    cx, cy = mx + ux * (r - 1), my + uy * (r - 1)      # 손잡이 시작 (머리 아래)
    handle = f"M{cx:.2f} {cy:.2f} L{bx:.2f} {by:.2f}"
    c1 = (mx + ux * (r + 0.5), my + uy * (r + 0.5))    # 머리 아래 은색 고리
    c2 = (mx + ux * (r + 3.5 * k), my + uy * (r + 3.5 * k))
    collar = f"M{c1[0]:.2f} {c1[1]:.2f} L{c2[0]:.2f} {c2[1]:.2f}"
    grill = ""
    for o in [i * 2.6 * k for i in (-2, -1, 0, 1, 2)]:
        half = math.sqrt(r * r - o * o) - 2.6 * k
        if half > 0.5:
            grill += (f'<path d="M{mx + px * half + ux * o:.2f} {my + py * half + uy * o:.2f} '
                      f'L{mx - px * half + ux * o:.2f} {my - py * half + uy * o:.2f}" '
                      f'stroke="#8A8A8A" stroke-width="{1.1 * k:.2f}" stroke-linecap="round"/>')
    outline = (f'<path d="{handle}" stroke="white" stroke-width="{hw + 7}" stroke-linecap="round"/>'
               f'<circle cx="{mx}" cy="{my}" r="{r + 3.5}" fill="white"/>')
    body = (f'<g id="마이크"><path d="{handle}" stroke="{DARK}" stroke-width="{hw}" stroke-linecap="round"/>'
            f'<path d="{collar}" stroke="#8A8A8A" stroke-width="{hw + 2}" stroke-linecap="round"/>'
            f'<circle cx="{mx}" cy="{my}" r="{r}" fill="{DARK}"/>{grill}</g>')
    return outline, body


def yellowtail(x, y, angle=30, k=1.0):
    """방어 (등은 푸른 남색, 배는 은색, 몸 가운데 노란 줄, 노란 갈래 꼬리).
    (x, y) = 입 위치, 기본 모양은 머리가 왼쪽. (흰 테두리용, 본체) 두 개를 돌려준다."""
    body = "M0 0C4 -8 18 -11 32 -6C36 -4 39 -2 41 0C39 2 36 4 32 6C18 11 4 8 0 0Z"
    back = "M0 0C4 -8 18 -11 32 -6C36 -4 39 -2 41 0C28 -1.5 12 -2 0 0Z"
    tail = "M38 0L50 -10L47 0L50 10Z"
    fins = "M18 -9.5L24 -14L27 -7.5Z M22 8.5L27 12L28 6.5Z"
    t = f'transform="translate({x} {y}) rotate({angle}) scale({k})"'
    lw, ow = 1.4 / k, 8 / k   # 크기를 키워도 선 굵기·흰 테두리 굵기는 그대로
    outline = (f'<g {t}><path d="{body}" fill="white" stroke="white" stroke-width="{ow:.2f}" stroke-linejoin="round"/>'
               f'<path d="{tail}" fill="white" stroke="white" stroke-width="{ow:.2f}" stroke-linejoin="round"/>'
               f'<path d="{fins}" fill="white" stroke="white" stroke-width="{ow:.2f}" stroke-linejoin="round"/></g>')
    fish = (f'<g id="방어" {t}>'
            f'<path d="{fins}" fill="#2E5C8A" stroke="{DARK}" stroke-width="{lw:.2f}" stroke-linejoin="round"/>'
            f'<path d="{tail}" fill="#F6C343" stroke="{DARK}" stroke-width="{lw:.2f}" stroke-linejoin="round"/>'
            f'<path d="{body}" fill="#DDE6EE"/><path d="{back}" fill="#2E5C8A"/>'
            f'<path d="M7 -0.6C17 -2.2 29 -1.6 39 0" stroke="#F6C343" stroke-width="2.6" stroke-linecap="round"/>'
            f'<path d="M12 -6.5Q15 0 12 6" stroke="{DARK}" stroke-width="{lw * 0.8:.2f}" opacity="0.5"/>'
            f'<path d="{body}" stroke="{DARK}" stroke-width="{lw:.2f}" stroke-linejoin="round"/>'
            f'<circle cx="5.5" cy="-2" r="2" fill="white" stroke="{DARK}" stroke-width="{lw * 0.6:.2f}"/><circle cx="5.9" cy="-2" r="1" fill="{DARK}"/>'
            f'<path d="M0 0L3 1.2" stroke="{DARK}" stroke-width="{lw * 0.8:.2f}" stroke-linecap="round"/></g>')
    return outline, fish


def fishing_rod(butt=(16, 72), bend=(66, 34), ctrl=(94, 10), tip=(114, 22), reel=(28, 66)):
    """휘어진 낚싯대 + 릴. (흰 테두리용, 본체) 두 개를 돌려준다. 낚싯줄은 따로 그린다."""
    rod = f"M{butt[0]} {butt[1]} L{bend[0]} {bend[1]} Q{ctrl[0]} {ctrl[1]} {tip[0]} {tip[1]}"
    gx, gy = butt[0] + (bend[0] - butt[0]) * 0.38, butt[1] + (bend[1] - butt[1]) * 0.38
    grip = f"M{butt[0]} {butt[1]} L{gx:.2f} {gy:.2f}"
    rx, ry = reel
    outline = (f'<path d="{rod}" stroke="white" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>'
               f'<path d="{grip}" stroke="white" stroke-width="11" stroke-linecap="round"/>'
               f'<circle cx="{rx}" cy="{ry}" r="7.5" fill="white"/>')
    body = (f'<g id="낚싯대"><path d="{rod}" stroke="{DARK}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="{grip}" stroke="{DARK}" stroke-width="5.5" stroke-linecap="round"/>'
            f'<circle cx="{rx}" cy="{ry}" r="4.5" fill="{DARK}"/><circle cx="{rx}" cy="{ry}" r="1.8" fill="#8A8A8A"/></g>')
    return outline, body


_mic_outline, _mic = microphone(hand=(74, 26), head=(56, 1), r=10.5, hw=8, tail=9)

_rod_outline, _rod = fishing_rod()
_fish_outline, _fish = yellowtail(124, 44, angle=72, k=1.15)
_line = '<path id="낚싯줄" d="M114 22 L124 44" stroke="#2B2B2B" stroke-width="1.3" stroke-linecap="round"/>'
# 앞으로 뻗은 왼팔 (핀 몸 앞으로 지나가서 따로 한 번 더 그린다)
_front_arm = "M10 47 L13 62 L32 60"

_flag_outline, _flag = checker_flag()

POSES = {
    # 🏃 뛰는 핀 (올레_러닝핀.svg)
    "run": dict(
        size=(140, 120), move=(42, 16), tilt=10, pivot_y=42, hand_r=5,
        limbs=["M10 44 L-3 51 L-11 61", "M22 62 L13 74 L1 72", "M40 60 L54 68 L50 83", "M51 44 L65 49 L70 37"],
        hands=[(-11, 61), (70, 37)],
        shoes=[(-8, 67, 14, 8, -20, -1, 71), (45, 80, 15, 8)],
        effects=motion_lines(["M8 38H24", "M2 50H18", "M6 62H16"], "속도선"),
    ),
    # 👋 손 흔드는 핀 (올레_환영핀.svg)
    "wave": dict(
        size=(150, 134), move=(26, 32), tilt=-8,
        limbs=["M51 42 L82 6", "M10 46 L0 57 L3 68", "M24 63 L22 85", "M37 63 L39 85"],
        hands=[(82, 6), (3, 68)],
        shoes=[(11, 82, 15, 8), (35, 82, 15, 8)],
        prop_front=motion_lines(["M94 -3 Q100 7 93 17", "M102 -10 Q112 7 101 24",
                                 "M70 -10 Q63 -1 67 8", "M76 -18 Q83 -22 90 -18"], "흔들기선"),
    ),
    # 🏁 도착 깃발 든 핀 (올레_도착깃발핀.svg)
    "flag": dict(
        size=(160, 164), move=(22, 64), tilt=-8,
        limbs=["M51 42 L82 6", "M10 46 L0 57 L3 68", "M24 63 L22 85", "M37 63 L39 85"],
        hands=[(82, 6), (3, 68)],
        shoes=[(11, 82, 15, 8), (35, 82, 15, 8)],
        prop_outline=_flag_outline, prop=_flag,
        effects=motion_lines(["M139 32 Q144 39 139 46", "M146 27 Q153 39 146 51"], "펄럭선", 3),
    ),
    # 🎤 노래 부르는 핀 (노래핀.svg)
    "sing": dict(
        size=(190, 160), move=(50, 56), tilt=-10, pivot_y=50,
        limbs=["M51 43 L79 42 L74 26", "M10 45 L-6 35 L-14 15", "M24 63 L22 85", "M37 62 L48 72 L46 84"],
        hands=[(74, 26), (-14, 15)],
        shoes=[(11, 82, 15, 8), (40, 81, 15, 8, -14, 47, 85)],
        prop_outline=_mic_outline + '<path d="M51 43 L79 42 L74 26 L58 22Z" fill="white" stroke="white" stroke-width="6" stroke-linejoin="round"/>',
        # 마이크는 핀 앞에 둬서 입에 댄 것처럼 보이게 하고, 마이크 잡은 손을 그 위에 한 번 더 그린다
        prop_front=_mic + f'<circle id="마이크 잡은 손" cx="74" cy="26" r="{HAND_R}" fill="{RED}"/>'
                   + motion_lines(["M7 0 L-1 -7", "M19 -8 L15 -17", "M32 -10 L33 -20"], "노래선", 3.5),
        effects=music_notes([(124, 40, 1.35, False), (146, 22, 1.15, True), (162, 58, 1.0, False), (140, 82, 0.85, False), (22, 44, 1.0, False)]),
    ),
    # 🎣 방어 잡는 핀 (방어낚시핀.svg)
    "fishing": dict(
        size=(198, 118), move=(22, 8), tilt=-12, pivot_y=50,
        limbs=["M51 43 L70 47 L62 37", _front_arm, "M24 63 L15 74 L10 85", "M38 61 L52 71 L57 83"],
        hands=[(62, 37)],
        shoes=[(2, 82, 15, 8), (50, 80, 15, 8, -10, 57, 84)],
        prop_outline=_rod_outline + _fish_outline + '<path d="M114 22 L124 44" stroke="white" stroke-width="4"/>',
        prop=_line + _fish,
        # 낚싯대·앞팔은 핀 앞에 그려서 두 손으로 잡은 것처럼 보이게 한다
        prop_front=(f'<g id="앞팔"><path d="{_front_arm}" stroke="white" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>'
                    f'<path d="{_front_arm}" stroke="{RED}" stroke-width="{LIMB_W}" stroke-linecap="round" stroke-linejoin="round"/></g>'
                    + _rod
                    + f'<g id="낚싯대 잡은 손" fill="{RED}" stroke="white" stroke-width="1.5"><circle cx="32" cy="60" r="{HAND_R}"/><circle cx="62" cy="37" r="{HAND_R}"/></g>'
                    + motion_lines(["M-4 12 L-12 6", "M-8 24 L-17 22",
                                    "M108 62 Q102 66 104 74", "M152 64 Q158 70 154 78", "M146 46 L152 42"], "효과선", 3)),
    ),
}

def build_fish_point(name="방어 포인트", k=1.6):
    """방어만으로 만든 위치 포인트. 머리를 아래로 내리꽂는 방어, 입 끝 = 실제 위치."""
    w, h = 88, 116
    mx, my = 42, 106          # 입 끝(위치를 가리키는 점)
    o, f = yellowtail(mx, my, angle=-78, k=k)
    fx = motion_lines(["M10 10 L10 28", "M5 38 L5 50", "M78 6 L78 20", "M83 30 L83 42"], "효과선", 3.5)
    return f'''<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" fill="none" xmlns="http://www.w3.org/2000/svg">
<g id="{name}">
{fx}
<g id="흰 테두리">{o}</g>
{f}
</g>
</svg>'''


if __name__ == "__main__":
    pose, out = sys.argv[1], sys.argv[2]
    title = sys.argv[3] if len(sys.argv) > 3 else "핀 캐릭터"
    # "yellowtail" = 핀 없이 방어만으로 만든 포인트
    svg = build_fish_point(title) if pose == "yellowtail" else build(title, POSES[pose])
    open(out, "w").write(svg)
    print("저장:", out)
