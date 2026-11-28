# 할일판 독립 앱 화면 만들기
# 할일판/할일판앱.html(claude.ai용)을 가져와 연결 부품(shim.js)·앱 설치 정보를 붙여 public/index.html로 만든다.
# 할일판을 고친 뒤: python 할일판/합치기.py → python 할일판독립/만들기.py → (할일판독립 폴더에서) npx wrangler deploy
import pathlib, re

here = pathlib.Path(__file__).resolve().parent
src = (here.parent / "할일판" / "할일판앱.html").read_text(encoding="utf-8")

head_add = (
    '<link rel="manifest" href="/manifest.webmanifest">\n'
    '<meta name="theme-color" content="#fdf6e3">\n'
    '<link rel="icon" href="/icon-192.png">\n'
    '<link rel="apple-touch-icon" href="/icon-192.png">\n'
    '<script src="/shim.js"></script>\n'
)
out, n = re.subn(r'(<meta name="viewport"[^>]*>\n)', lambda m: m.group(1) + head_add, src, count=1)
assert n == 1, "viewport 줄을 못 찾음"
# claude.ai 안내 문구를 독립 앱에 맞게
out = out.replace("claude.ai에서 열어 주세요", "잠시 뒤 다시 열어 주세요").replace("claude.ai에서 열어야", "연결이 돼야")
(here / "public" / "index.html").write_text(out, encoding="utf-8")

# 아이콘 (없을 때만 만듦)
for size in (192, 512):
    p = here / "public" / f"icon-{size}.png"
    if p.exists():
        continue
    from PIL import Image, ImageDraw, ImageFont
    im = Image.new("RGB", (size, size), "#fdf6e3")
    d = ImageDraw.Draw(im)
    s = size / 512
    d.rounded_rectangle([96 * s, 80 * s, 416 * s, 448 * s], radius=40 * s, fill="#ffffff", outline="#2b2b2b", width=int(14 * s))
    d.rectangle([180 * s, 56 * s, 332 * s, 112 * s], fill="#e4572e")
    for i, y in enumerate((190, 280, 370)):
        y *= s
        d.rounded_rectangle([140 * s, y - 26 * s, 192 * s, y + 26 * s], radius=8 * s, outline="#2b2b2b", width=int(10 * s))
        if i < 2:
            d.line([(150 * s, y), (165 * s, y + 16 * s), (196 * s, y - 24 * s)], fill="#e4572e", width=int(14 * s))
        d.line([(222 * s, y), (370 * s, y)], fill="#2b2b2b", width=int(14 * s))
    im.save(p)
print("만듦:", here / "public" / "index.html")
