// claude.ai 밖에서도 할일판이 그대로 돌게 해 주는 연결 부품.
// 앱 코드는 window.claude.use("db") / use("mcp")를 부르는데, 그걸 우리 서버(/api)로 바꿔 줌.
(() => {
  const toLogin = (r) => { if (r.status === 401) { location.replace("/"); throw new Error("login"); } return r; };
  const post = (u, body) => fetch(u, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) }).then(toLogin);

  const watchers = [];
  async function pull(w) {
    try {
      const r = await fetch("/api/db?name=" + encodeURIComponent(w.name), { cache: "no-store" }).then(toLogin);
      if (!r.ok) throw new Error(r.status);
      const rec = await r.json();
      if (w.v === rec.v && w.seen) return;
      w.v = rec.v; w.seen = true;
      w.cb({ exists: !!rec.exists, data: () => rec.data, metadata: { fromCache: false } });
    } catch (e) { if (!w.seen && w.err) w.err(e); }
  }
  setInterval(() => { if (document.visibilityState === "visible") watchers.forEach(pull); }, 20000);
  document.addEventListener("visibilitychange", () => { if (document.visibilityState === "visible") watchers.forEach(pull); });

  const db = {
    doc(path) {
      const name = String(path).replace(/^board\//, "");
      return {
        async set(data) {
          const r = await post("/api/db?name=" + encodeURIComponent(name), { data });
          if (!r.ok) throw new Error("save " + r.status);
          const rec = await r.json();
          watchers.filter((w) => w.name === name).forEach((w) => (w.v = rec.v));
          return rec;
        },
        onSnapshot(cb, err) { const w = { name, cb, err, v: null, seen: false }; watchers.push(w); pull(w); return () => watchers.splice(watchers.indexOf(w), 1); },
      };
    },
  };

  const mcp = {
    async callTool(server, tool, args) {
      const r = await post("/api/tool", { server, tool, args });
      if (!r.ok) throw new Error((await r.text()).slice(0, 200));
      return r.json();
    },
  };

  window.claude = { use: async (name) => (name === "db" ? db : name === "mcp" ? mcp : null) };

  if ("serviceWorker" in navigator) navigator.serviceWorker.register("/sw.js").catch(() => {});
})();
