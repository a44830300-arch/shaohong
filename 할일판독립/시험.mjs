// 서버 코드 시험 (Cloudflare 없이 Node.js로): node 시험.mjs
import worker from "./src/worker.js";
import fs from "node:fs";

const kv = new Map();
const ICS = `BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VTIMEZONE
TZID:Asia/Seoul
BEGIN:STANDARD
TZOFFSETFROM:+0900
TZOFFSETTO:+0900
TZNAME:KST
DTSTART:19700101T000000
END:STANDARD
END:VTIMEZONE
BEGIN:VEVENT
UID:once
DTSTART;TZID=Asia/Seoul:20261130T183000
DTEND;TZID=Asia/Seoul:20261130T203000
SUMMARY:오오야마 (경민이)
END:VEVENT
BEGIN:VEVENT
UID:class
DTSTART;TZID=Asia/Seoul:20260901T090000
DTEND;TZID=Asia/Seoul:20260901T101500
RRULE:FREQ=WEEKLY;BYDAY=WE,TH;UNTIL=20261218T000000Z
EXDATE;TZID=Asia/Seoul:20261203T090000
SUMMARY:공업수학II
END:VEVENT
BEGIN:VEVENT
UID:class
RECURRENCE-ID;TZID=Asia/Seoul:20261202T090000
DTSTART;TZID=Asia/Seoul:20261202T100000
DTEND;TZID=Asia/Seoul:20261202T111500
SUMMARY:공업수학II (보강)
END:VEVENT
BEGIN:VEVENT
UID:allday
DTSTART;VALUE=DATE:20261209
DTEND;VALUE=DATE:20261210
SUMMARY:기말고사
END:VEVENT
END:VCALENDAR`;

const realFetch = globalThis.fetch;
globalThis.fetch = async (u, o) => {
  u = String(u);
  if (u.startsWith("https://cal.test/")) return new Response(ICS);
  if (u.startsWith("https://api.todoist.com/")) return new Response(JSON.stringify({ results: [
    { id: "1", content: "🗿 나들로그: 동백", priority: 4, section_id: "S", labels: [], due: { date: "2026-11-28", is_recurring: false } },
    { id: "2", content: "기말고사 공부", priority: 1, due: { date: "2026-12-01T05:00:00Z" } },
    { id: "3", content: "지난 일", priority: 2, due: { date: "2026-11-20" } },
  ], next_cursor: null }));
  return realFetch(u, o);
};
const env = {
  APP_PASSWORD: "pw-test", TODOIST_TOKEN: "x", ICAL_URL: "https://cal.test/a.ics",
  BOARD: { get: async (k) => kv.get(k) ?? null, put: async (k, v) => void kv.set(k, v) },
  ASSETS: { fetch: async () => new Response("ASSET") },
};
const call = (path, opts = {}, cookie = "") => worker.fetch(new Request("https://h.test" + path, { ...opts, headers: { "content-type": "application/json", cookie } }), env);

let r = await call("/");
console.log("잠금 화면:", (await r.text()).includes("비밀번호"));
r = await call("/api/login", { method: "POST", body: JSON.stringify({ password: "wrong" }) });
console.log("틀린 비번 거절:", r.status === 403);
r = await call("/api/login", { method: "POST", body: JSON.stringify({ password: "pw-test" }) });
const cookie = r.headers.get("set-cookie").split(";")[0];
console.log("로그인:", r.status === 200);
console.log("잠금 없이 api 막힘:", (await call("/api/db?name=period")).status === 401);
await call("/api/db?name=period", { method: "POST", body: JSON.stringify({ data: { items: [1] } }) }, cookie);
console.log("저장→읽기:", JSON.stringify((await (await call("/api/db?name=period", {}, cookie)).json()).data));
const tool = async (server, t, args) => (await (await call("/api/tool", { method: "POST", body: JSON.stringify({ server, tool: t, args }) }, cookie)).json());
console.log("섹션:", (await tool("Todoist", "find-tasks", { sectionId: "S" })).payload.tasks.map((t) => t.id + t.priority));
console.log("검색:", (await tool("Todoist", "find-tasks", { filter: "search: 시험 | search: 기말" })).payload.tasks.map((t) => t.content + " " + t.dueDate));
console.log("날짜(오늘부터 7일+밀린 것):", (await tool("Todoist", "find-tasks-by-date", { startDate: "2026-11-28", daysCount: 7 })).payload.tasks.map((t) => t.id));
const ev = await tool("Google Calendar", "list_events", { startTime: "2026-11-30T00:00:00", endTime: "2026-12-11T00:00:00" });
console.log(ev.error || ev.payload.events.map((e) => `${e.summary} ${e.start.dateTime || e.start.date}`).join("\n"));
