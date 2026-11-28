// 할일판 독립 앱 서버 (Cloudflare Worker)
// - 잠금: 비밀번호를 한 번 넣으면 1년 동안 그 기기에서 바로 열림
// - /api/db   : 체크·작업목록 저장 칸 (KV)
// - /api/tool : 앱이 claude.ai에서 쓰던 Todoist·구글 캘린더 도구를 같은 모양으로 흉내 냄
import ICAL from "ical.js";

const TD_API = "https://api.todoist.com/api/v1";
const KST = 9 * 3600 * 1000; // 한국은 서머타임 없음 → +9 고정

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    try {
      if (url.pathname === "/api/login" && req.method === "POST") return login(req, env);
      if (url.pathname === "/manifest.webmanifest" || url.pathname.startsWith("/icon")) return env.ASSETS.fetch(req);
      const ok = await authed(req, env);
      if (!ok) {
        if (url.pathname.startsWith("/api/")) return json({ error: "login" }, 401);
        return new Response(LOGIN_HTML, { headers: { "content-type": "text/html; charset=utf-8", "cache-control": "no-store" } });
      }
      if (url.pathname === "/api/db") return db(req, env, url);
      if (url.pathname === "/api/tool" && req.method === "POST") return tool(req, env);
      return env.ASSETS.fetch(req);
    } catch (e) {
      return json({ error: String(e && e.message || e) }, 500);
    }
  },
};

// ---------- 잠금 ----------
async function sign(env) {
  const key = await crypto.subtle.importKey("raw", new TextEncoder().encode(env.APP_PASSWORD || ""), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const sig = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode("halilpan-ok"));
  return [...new Uint8Array(sig)].map((b) => b.toString(16).padStart(2, "0")).join("");
}
async function authed(req, env) {
  if (!env.APP_PASSWORD) return false;
  const m = (req.headers.get("cookie") || "").match(/(?:^|;\s*)hp=([0-9a-f]{64})/);
  return !!m && m[1] === (await sign(env));
}
async function login(req, env) {
  const { password } = await req.json().catch(() => ({}));
  if (!env.APP_PASSWORD || password !== env.APP_PASSWORD) {
    await new Promise((r) => setTimeout(r, 1000));
    return json({ ok: false }, 403);
  }
  return new Response(JSON.stringify({ ok: true }), {
    headers: { "content-type": "application/json", "set-cookie": `hp=${await sign(env)}; Max-Age=31536000; Path=/; HttpOnly; Secure; SameSite=Lax` },
  });
}

// ---------- 저장 칸 ----------
async function db(req, env, url) {
  const name = url.searchParams.get("name") || "";
  if (!/^[a-z0-9_-]{1,40}$/.test(name)) return json({ error: "bad name" }, 400);
  const key = "board/" + name;
  if (req.method === "GET") {
    const v = await env.BOARD.get(key);
    return json(v ? JSON.parse(v) : { exists: false });
  }
  if (req.method === "POST") {
    const { data } = await req.json();
    const rec = { exists: true, data, v: Date.now() };
    await env.BOARD.put(key, JSON.stringify(rec));
    return json(rec);
  }
  return json({ error: "method" }, 405);
}

// ---------- 도구 흉내 ----------
async function tool(req, env) {
  const { server, tool: name, args = {} } = await req.json();
  let payload;
  if (server === "Todoist") payload = await todoist(env, name, args);
  else if (server === "Google Calendar" && name === "list_events") payload = await calendar(env, args);
  else return json({ error: "unknown tool " + server + "/" + name }, 400);
  return json({ payload });
}

// Todoist
async function td(env, path, opts = {}) {
  const r = await fetch(TD_API + path, {
    ...opts,
    headers: { authorization: "Bearer " + env.TODOIST_TOKEN, "content-type": "application/json", ...(opts.headers || {}) },
  });
  if (!r.ok) throw new Error("Todoist " + r.status + " " + (await r.text()).slice(0, 200));
  return r.status === 204 ? {} : r.json();
}
async function allTasks(env) {
  const out = []; let cursor = null;
  for (let i = 0; i < 30; i++) {
    const p = await td(env, "/tasks?limit=200" + (cursor ? "&cursor=" + encodeURIComponent(cursor) : ""));
    out.push(...(p.results || []));
    cursor = p.next_cursor;
    if (!cursor) break;
  }
  return out;
}
function kstYmd(ms) { return new Date(ms + KST).toISOString().slice(0, 10); }
function kstIso(ms) { return new Date(ms + KST).toISOString().slice(0, 19) + "+09:00"; }
function dueDate(due) {
  if (!due || !due.date) return undefined;
  const d = due.date;
  if (/Z$/.test(d)) return new Date(new Date(d).getTime() + KST).toISOString().slice(0, 19); // 한국 시각으로
  return d;
}
function mapTask(t) {
  return {
    id: t.id,
    content: t.content,
    description: t.description || "",
    priority: "p" + (5 - (t.priority || 1)),
    projectId: t.project_id,
    sectionId: t.section_id || undefined,
    parentId: t.parent_id || undefined,
    labels: t.labels || [],
    dueDate: dueDate(t.due),
    recurring: !!(t.due && t.due.is_recurring),
    duration: t.duration || undefined,
    checked: !!t.checked,
    addedAt: t.added_at,
    completedAt: t.completed_at || undefined,
  };
}
async function todoist(env, name, a) {
  if (name === "find-tasks") {
    let list = (await allTasks(env)).map(mapTask);
    if (a.sectionId) list = list.filter((t) => t.sectionId === a.sectionId);
    if (a.filter) {
      const words = [...a.filter.matchAll(/search:\s*([^|&()]+)/g)].map((m) => m[1].trim()).filter(Boolean);
      if (words.length) list = list.filter((t) => words.some((w) => t.content.includes(w)));
    }
    if (a.searchText) list = list.filter((t) => t.content.includes(a.searchText));
    return { tasks: list, hasMore: false };
  }
  if (name === "find-tasks-by-date") {
    const today = kstYmd(Date.now());
    const base = !a.startDate || a.startDate === "today" ? today : a.startDate;
    const end = new Date(Date.parse(base + "T00:00:00Z") + (a.daysCount || 1) * 86400000).toISOString().slice(0, 10);
    const withOverdue = !a.startDate || a.startDate === "today";
    const list = (await allTasks(env)).map(mapTask).filter((t) => {
      const d = t.dueDate && t.dueDate.slice(0, 10);
      if (!d) return false;
      return (d >= base && d < end) || (withOverdue && d < today);
    });
    return { tasks: list, hasMore: false };
  }
  if (name === "find-completed-tasks") {
    const since = (a.since || kstYmd(Date.now() - 7 * 86400000)) + "T00:00:00+09:00";
    const until = (a.until || kstYmd(Date.now())) + "T23:59:59+09:00";
    const out = []; let cursor = null;
    for (let i = 0; i < 10; i++) {
      const q = new URLSearchParams({ since: new Date(since).toISOString(), until: new Date(until).toISOString(), limit: "200" });
      if (a.sectionId) q.set("section_id", a.sectionId);
      if (cursor) q.set("cursor", cursor);
      const p = await td(env, "/tasks/completed/by_completion_date?" + q);
      out.push(...(p.items || []).map(mapTask));
      cursor = p.next_cursor;
      if (!cursor) break;
    }
    return { tasks: out, hasMore: false };
  }
  if (name === "update-tasks") {
    const tasks = [];
    for (const t of a.tasks || []) {
      const body = {};
      if (t.labels) body.labels = t.labels;
      if (t.content) body.content = t.content;
      tasks.push(mapTask(await td(env, "/tasks/" + t.id, { method: "POST", body: JSON.stringify(body) })));
    }
    return { tasks };
  }
  if (name === "complete-tasks") {
    for (const id of a.ids || []) await td(env, "/tasks/" + id + "/close", { method: "POST" });
    return { completed: a.ids || [] };
  }
  if (name === "add-tasks") {
    const tasks = [];
    for (const t of a.tasks || []) {
      const body = { content: t.content };
      if (t.sectionId) body.section_id = t.sectionId;
      if (t.projectId) body.project_id = t.projectId;
      if (t.labels && t.labels.length) body.labels = t.labels;
      tasks.push(mapTask(await td(env, "/tasks", { method: "POST", body: JSON.stringify(body) })));
    }
    return { tasks };
  }
  throw new Error("이 Todoist 도구는 아직 없음: " + name);
}

// 구글 캘린더 (비공개 iCal 주소를 읽어서 기간 안 일정을 펼침)
let icsCache = { at: 0, text: "" };
async function icsText(env) {
  if (Date.now() - icsCache.at < 3 * 60 * 1000 && icsCache.text) return icsCache.text;
  const r = await fetch(env.ICAL_URL, { cf: { cacheTtl: 0 } });
  if (!r.ok) throw new Error("캘린더 " + r.status);
  icsCache = { at: Date.now(), text: await r.text() };
  return icsCache.text;
}
const kstLocalToMs = (s) => Date.parse(s.slice(0, 19) + "Z") - KST; // "2026-11-30T00:00:00" (한국 시각) → ms
function fmt(t) {
  if (t.isDate) return { date: `${t.year}-${String(t.month).padStart(2, "0")}-${String(t.day).padStart(2, "0")}` };
  return { dateTime: kstIso(t.toJSDate().getTime()), timeZone: "Asia/Seoul" };
}
function msOf(t) { return t.isDate ? Date.parse(fmt(t).date + "T00:00:00Z") - KST : t.toJSDate().getTime(); }

async function calendar(env, a) {
  const rs = a.startTime ? kstLocalToMs(a.startTime) : Date.now();
  const re = a.endTime ? kstLocalToMs(a.endTime) : rs + 7 * 86400000;
  const comp = new ICAL.Component(ICAL.parse(await icsText(env)));
  for (const tz of comp.getAllSubcomponents("vtimezone")) ICAL.TimezoneService.register(tz);
  const vevents = comp.getAllSubcomponents("vevent");
  const masters = new Map(), exceptions = [];
  for (const v of vevents) (v.hasProperty("recurrence-id") ? exceptions : (masters.set(v.getFirstPropertyValue("uid") + "", v), null));
  const events = new Map();
  for (const v of masters.values()) events.set(v.getFirstPropertyValue("uid") + "", new ICAL.Event(v, { strictExceptions: false }));
  for (const x of exceptions) {
    const ev = events.get(x.getFirstPropertyValue("uid") + "");
    if (ev) ev.relateException(x); else events.set("x" + Math.random(), new ICAL.Event(x));
  }
  const out = [];
  const push = (item, s, e, id) => {
    const sm = msOf(s), em = e ? msOf(e) : sm + 3600000;
    if (!(sm < re && em > rs)) return;
    const st = (item.component.getFirstPropertyValue("status") || "confirmed").toString().toLowerCase();
    out.push({ id, summary: item.summary || "", location: item.location || "", description: item.description || "", status: st, start: fmt(s), end: e ? fmt(e) : fmt(s), _ms: sm });
  };
  for (const ev of events.values()) {
    if (!ev.startDate) continue;
    if (ev.isRecurring()) {
      const it = ev.iterator();
      let t, n = 0;
      while ((t = it.next()) && n++ < 5000) {
        if (msOf(t) >= re) break;
        const d = ev.getOccurrenceDetails(t);
        push(d.item, d.startDate, d.endDate, ev.uid + "_" + msOf(t));
      }
    } else push(ev, ev.startDate, ev.endDate, ev.uid);
  }
  out.sort((x, y) => x._ms - y._ms);
  return { events: out.slice(0, a.pageSize || 250).map(({ _ms, ...e }) => e) };
}

function json(o, status = 200) {
  return new Response(JSON.stringify(o), { status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });
}

const LOGIN_HTML = `<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>할일판</title>
<link rel="manifest" href="/manifest.webmanifest"><meta name="theme-color" content="#fdf6e3">
<style>
:root{--bg:#fdf6e3;--card:#fff;--ink:#2b2b2b;--line:#e5dcc3;--accent:#e4572e}
@media (prefers-color-scheme:dark){:root{--bg:#1d1b17;--card:#2a2722;--ink:#eee;--line:#45403a}}
body{margin:0;min-height:100vh;display:grid;place-items:center;background:var(--bg);color:var(--ink);font-family:system-ui,"Apple SD Gothic Neo","Malgun Gothic",sans-serif}
form{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:28px 22px;width:min(320px,calc(100vw - 32px));box-sizing:border-box;text-align:center}
h1{font-size:20px;margin:0 0 6px}p{margin:0 0 18px;font-size:14px;opacity:.7}
input{width:100%;box-sizing:border-box;font-size:17px;padding:12px;border:1px solid var(--line);border-radius:10px;background:transparent;color:inherit}
button{margin-top:12px;width:100%;font-size:17px;padding:12px;border:0;border-radius:10px;background:var(--accent);color:#fff;font-weight:700}
.err{color:var(--accent);font-size:14px;min-height:20px;margin-top:10px}
</style></head><body>
<form id="f"><h1>📋 할일판</h1><p>처음 한 번만 비밀번호를 넣어 주세요</p>
<input id="pw" type="password" autocomplete="current-password" placeholder="비밀번호" aria-label="비밀번호" autofocus>
<button>열기</button><div class="err" id="err"></div></form>
<script>
document.getElementById("f").addEventListener("submit", async (e) => {
  e.preventDefault();
  const r = await fetch("/api/login", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ password: document.getElementById("pw").value }) });
  if (r.ok) location.replace("/"); else document.getElementById("err").textContent = "비밀번호가 달라요";
});
</script></body></html>`;
