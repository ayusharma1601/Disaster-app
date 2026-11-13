const CACHE_NAME = 'disaster-app-v1';
const STATIC_ASSETS = [
    '/',
    '/terms',
    '/static/manifest.json',
    '/static/vendor/three.min.js',
    '/static/vendor/OrbitControls.js',
    '/static/vendor/leaflet.css',
    '/static/vendor/leaflet.js',
    '/static/textures/earth_atmos_4096.jpg',
    '/static/textures/earth_clouds_2048.png',
    '/static/textures/earth_night_4096.jpg',
    '/static/data/dhemaji_zones.geojson',
    '/static/icons/icon-192.png',
    '/static/icons/icon-512.png'
];

// Install: Cache critical static assets locally
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            console.log('[ServiceWorker] Pre-caching static assets');
            return cache.addAll(STATIC_ASSETS).catch(err => {
                console.warn('[ServiceWorker] Some assets failed to precache:', err);
            });
        }).then(() => self.skipWaiting())
    );
});

// Activate: Clean up old caches
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keys) => {
            return Promise.all(
                keys.map((key) => {
                    if (key !== CACHE_NAME) {
                        console.log('[ServiceWorker] Removing old cache:', key);
                        return caches.delete(key);
                    }
                })
            );
        }).then(() => self.clients.claim())
    );
});

// Fetch: Network-first for dynamic API, Cache-first for static assets
self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);

    // Dynamic API endpoints: Try Network, fallback to Cache or Offline JSON
    if (url.pathname.startsWith('/api/')) {
        event.respondWith(
            fetch(event.request)
                .then((response) => {
                    // Clone and save successful API response into cache for offline viewing
                    if (event.request.method === 'GET' && response.status === 200) {
                        const copy = response.clone();
                        caches.open(CACHE_NAME).then((cache) => cache.put(event.request, copy));
                    }
                    return response;
                })
                .catch(async () => {
                    // Network failed: return cached copy if available
                    const cachedResponse = await caches.match(event.request);
                    if (cachedResponse) {
                        return cachedResponse;
                    }
                    // If no cached API data, return fallback offline indicator
                    return new Response(
                        JSON.stringify({ offline: true, message: "Operating in zero-network cached mode." }),
                        { headers: { 'Content-Type': 'application/json' } }
                    );
                })
        );
        return;
    }

    // Static Assets & Navigation: Cache-First with Network Fallback
    event.respondWith(
        caches.match(event.request).then((cachedResponse) => {
            if (cachedResponse) {
                return cachedResponse;
            }
            return fetch(event.request).then((networkResponse) => {
                if (networkResponse && networkResponse.status === 200 && event.request.method === 'GET') {
                    const copy = networkResponse.clone();
                    caches.open(CACHE_NAME).then((cache) => cache.put(event.request, copy));
                }
                return networkResponse;
            }).catch(() => {
                // If navigation fails completely, return cached index
                if (event.request.mode === 'navigate') {
                    return caches.match('/');
                }
            });
        })
    );
});
