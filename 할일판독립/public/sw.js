// 앱 설치용 최소 서비스워커: 항상 인터넷에서 새로 받고, 끊겼을 때만 마지막 화면을 보여 줌
const C = "halilpan-v1";
self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", (e) => e.waitUntil(self.clients.claim()));
self.addEventListener("fetch", (e) => {
  const r = e.request;
  if (r.method !== "GET" || new URL(r.url).origin !== location.origin || new URL(r.url).pathname.startsWith("/api/")) return;
  e.respondWith(fetch(r).then((res) => {
    if (res.ok) { const copy = res.clone(); caches.open(C).then((c) => c.put(r, copy)); }
    return res;
  }).catch(() => caches.match(r)));
});
