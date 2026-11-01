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
}

if __name__ == "__main__":
    pose, out = sys.argv[1], sys.argv[2]
    open(out, "w").write(build(sys.argv[3] if len(sys.argv) > 3 else "핀 캐릭터", POSES[pose]))
    print("저장:", out)
