# 할일판 앱 만들기: 작업목록.html(샤오홍슈) + ../할일판2/index.html(스케줄) → index.html (탭 2개)
# 스케줄 페이지는 shadow DOM 안에 넣어 글씨체·색·아이디가 서로 섞이지 않게 한다.
import re, pathlib
D = pathlib.Path(__file__).parent
p1 = (D / "작업목록.html").read_text(encoding="utf-8")
p2 = (D.parent / "할일판2" / "index.html").read_text(encoding="utf-8")

css2 = re.search(r"<style>(.*?)</style>", p2, re.S).group(1)
css2 = css2.replace(':root:not([data-theme="light"])', ":host").replace(':root[data-theme="dark"]', ':host([data-theme="dark"])').replace(":root", ":host")
css2 = re.sub(r"(?m)^body \{", ":host {", css2)
css2 = "*, *::before, *::after { box-sizing: border-box; }\n:host { display: block; min-height: 100vh; }\n[hidden] { display: none !important; }\n" + css2
html2 = re.search(r"</style>(.*?)<script>", p2, re.S).group(1).strip()
js2 = re.search(r"<script>(.*?)</script>", p2, re.S).group(1)
js2 = js2.replace("document.getElementById(", "ROOT.getElementById(").replace("document.querySelector", "ROOT.querySelector")
fonts = "https://fonts.googleapis.com/css2?family=Gaegu:wght@400;700&family=IBM+Plex+Sans+KR:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500&display=swap"

shell_css = """
/* ── 앱 탭 (2026-11-28: 스케줄표 + 샤오홍슈 작업목록을 한 앱 두 페이지로) ── */
body { padding-bottom: calc(64px + env(safe-area-inset-bottom, 0px)); }
body[data-tab="schedule"] > .wrap, body[data-tab="schedule"] > .toast { display: none !important; }
body[data-tab="xhs"] > #schedule-app { display: none; }
.apptabs { position: fixed; left: 0; right: 0; bottom: 0; z-index: 50; display: flex; justify-content: center; gap: 6px;
  padding: 6px max(16px, env(safe-area-inset-left, 0px)) calc(6px + env(safe-area-inset-bottom, 0px));
  background: var(--surface); border-top: 1px solid var(--line); }
.apptabs button { flex: 1; max-width: 220px; display: flex; flex-direction: column; align-items: center; gap: 1px;
  padding: 6px 8px; border: 0; border-radius: 10px; background: transparent; color: var(--muted);
  font: 600 13px/1.2 var(--font-body); cursor: pointer; }
.apptabs button span { font-size: 20px; line-height: 1; }
.apptabs button[aria-selected="true"] { background: var(--accent-soft); color: var(--accent); }
.toast { bottom: calc(76px + env(safe-area-inset-bottom, 0px)) !important; }
@media print { .apptabs { display: none; } }
"""
shell_html = """
<div id="schedule-app"></div>
<nav class="apptabs" role="tablist" aria-label="페이지">
  <button type="button" role="tab" data-tab="schedule"><span>🗓️</span>스케줄</button>
  <button type="button" role="tab" data-tab="xhs"><span>📮</span>샤오홍슈 작업목록</button>
</nav>
<script>
/* 스케줄 페이지 (원본 할일판2/index.html) */
(() => {
const HOST = document.getElementById("schedule-app");
const ROOT = HOST.attachShadow({ mode: "open" });
ROOT.innerHTML = %s + %s;
%s
})();
/* 탭 넘기기: 마지막으로 본 탭을 기억 (이 기기에만) */
(() => {
  const tabs = document.querySelectorAll(".apptabs button");
  const show = (t) => {
    document.body.dataset.tab = t;
    tabs.forEach((b) => b.setAttribute("aria-selected", String(b.dataset.tab === t)));
    try { localStorage.setItem("app-tab", t); } catch {}
    document.title = t === "schedule" ? "스케줄표" : "샤오홍슈 작업목록";
    window.scrollTo(0, 0);
    if (t === "schedule") requestAnimationFrame(() => window.dispatchEvent(new Event("resize")));
  };
  let t = location.hash === "#xhs" ? "xhs" : location.hash === "#schedule" ? "schedule" : null;
  if (!t) { try { t = localStorage.getItem("app-tab"); } catch {} }
  show(t === "xhs" ? "xhs" : "schedule");
  tabs.forEach((b) => b.addEventListener("click", () => show(b.dataset.tab)));
})();
</script>
"""
import json
shell_html = shell_html % (json.dumps("<style>" + css2 + "</style>").replace("<", "\u003c"),
                           json.dumps(html2).replace("<", "\u003c"), js2)
out = p1.replace("<title>샤오홍슈 작업목록</title>", "<title>할일판</title>")
out = re.sub(r'<link rel="stylesheet" href="[^"]+">', f'<link rel="stylesheet" href="{fonts}">', out, count=1)
out = out.replace("</style>", shell_css + "</style>", 1)
i = out.rindex("</body>")
out = out[:i] + shell_html + out[i:]
(D / "index.html").write_text(out, encoding="utf-8")
print("ok", len(out))
