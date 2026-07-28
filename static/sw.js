const CACHE = "streaming-v3";
const APP_SHELL = ["/series-list", "/movies"];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(APP_SHELL)));
  self.skipWaiting();
});

self.addEventListener("activate", (e) => {
  e.waitUntil(caches.keys().then((keys) =>
    Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
  ));
  self.clients.claim();
});

self.addEventListener("fetch", (e) => {
  const url = new URL(e.request.url);
  // Network-only (nunca cacheia, nunca serve stale):
  //   /video, /api  → conteúdo/estado dinâmico
  //   /watch, /     → player e home dependem do episódio/progresso atual;
  //                   servir cache velho num soluço de rede trazia episódio-fantasma
  if (url.pathname.startsWith("/video") ||
      url.pathname.startsWith("/api") ||
      url.pathname.startsWith("/watch") ||
      url.pathname === "/") return;

  // Pôsteres e estáticos: cache-first (conteúdo imutável) — não refaz download
  // a cada página nem deixa card em branco num soluço de rede.
  if (url.pathname.startsWith("/poster/") || url.pathname.startsWith("/static/")) {
    e.respondWith(
      caches.match(e.request).then((hit) =>
        hit ||
        fetch(e.request).then((res) => {
          if (res.ok && e.request.method === "GET") {
            const clone = res.clone();
            caches.open(CACHE).then((c) => c.put(e.request, clone));
          }
          return res;
        })
      )
    );
    return;
  }

  e.respondWith(
    fetch(e.request)
      .then((res) => {
        if (res.ok && e.request.method === "GET") {
          const clone = res.clone();
          caches.open(CACHE).then((c) => c.put(e.request, clone));
        }
        return res;
      })
      .catch(() => caches.match(e.request))
  );
});
