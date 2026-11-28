// 화면 미리보기용 로컬 서버 (가짜 Todoist·캘린더 자료): node 로컬실행.mjs → http://127.0.0.1:8788
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import worker from "./src/worker.js";

const kv = new Map();
const types = { ".html": "text/html; charset=utf-8", ".js": "text/javascript", ".png": "image/png", ".webmanifest": "application/manifest+json" };
const realFetch = globalThis.fetch;
globalThis.fetch = async (u, o) => {
  u = String(u);
  if (u.startsWith("https://cal.test/")) return new Response(`BEGIN:VCALENDAR\nBEGIN:VEVENT\nUID:a\nDTSTART:20261130T093000Z\nDTEND:20261130T113000Z\nSUMMARY:오오야마 (경민이)\nEND:VEVENT\nBEGIN:VEVENT\nUID:b\nDTSTART;VALUE=DATE:20261209\nDTEND;VALUE=DATE:20261210\nSUMMARY:기말고사\nEND:VEVENT\nEND:VCALENDAR`);
  if (u.startsWith("https://api.todoist.com/")) {
    if (u.includes("/completed/")) return new Response(JSON.stringify({ items: [{ id: "9", content: "🗿 나들로그: 끝난 글", section_id: "6hqfQg4Q9MMprpjc", completed_at: "2026-11-27T03:00:00Z" }] }));
    if (o && o.method === "POST") return new Response(JSON.stringify({ id: String(Date.now()), content: JSON.parse(o.body || "{}").content || "x", section_id: "6hqfQg4Q9MMprpjc", labels: JSON.parse(o.body || "{}").labels || [] }));
    return new Response(JSON.stringify({ results: [
      { id: "1", content: "🗿 나들로그: 동백 명소", priority: 1, section_id: "6hqfQg4Q9MMprpjc", labels: [] },
      { id: "2", content: "🗿 나들로그: 감귤 체험", priority: 1, section_id: "6hqfQg4Q9MMprpjc", labels: ["진행중"] },
      { id: "3", content: "계획 옮겨적기", priority: 4, labels: [], due: { date: new Date(Date.now() + 9 * 3600e3).toISOString().slice(0, 10) } },
    ] }));
  }
  return realFetch(u, o);
};
const env = {
  APP_PASSWORD: "local-test-1234", TODOIST_TOKEN: "x", ICAL_URL: "https://cal.test/a.ics",
  BOARD: { get: async (k) => kv.get(k) ?? null, put: async (k, v) => void kv.set(k, v) },
  ASSETS: { fetch: async (req) => {
    let p = new URL(req.url).pathname; if (p === "/") p = "/index.html";
    const f = path.join(import.meta.dirname, "public", p);
    return fs.existsSync(f) ? new Response(fs.readFileSync(f), { headers: { "content-type": types[path.extname(f)] || "application/octet-stream" } }) : new Response("없음", { status: 404 });
  } },
};
http.createServer(async (req, res) => {
  const chunks = []; for await (const c of req) chunks.push(c);
  const r = await worker.fetch(new Request("http://127.0.0.1:8788" + req.url, { method: req.method, headers: req.headers, body: chunks.length ? Buffer.concat(chunks) : undefined }), env);
  const h = Object.fromEntries(r.headers); if (h["set-cookie"]) h["set-cookie"] = h["set-cookie"].replace("; Secure", "");
  res.writeHead(r.status, h); res.end(Buffer.from(await r.arrayBuffer()));
}).listen(8788, "127.0.0.1", () => console.log("ready http://127.0.0.1:8788"));
