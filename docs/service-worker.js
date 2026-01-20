/**
 * Service Worker for Figurine Gallery
 * Provides aggressive caching for SVG figures and assets
 */

const CACHE_NAME = 'figurine-gallery-v1';
const ASSETS_TO_CACHE = [
    '/',
    '/index.html',
    '/css/styles.css',
    '/js/app.js',
    '/js/grid-manager.js',
    '/js/slip-view.js',
    '/js/data-service.js',
    '/js/minimap.js'
];

// Install event - cache core assets
self.addEventListener('install', (event) => {
    console.log('[SW] Installing service worker...');
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('[SW] Caching core assets');
                return cache.addAll(ASSETS_TO_CACHE);
            })
            .then(() => self.skipWaiting())
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    console.log('[SW] Activating service worker...');
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames
                    .filter((name) => name !== CACHE_NAME)
                    .map((name) => {
                        console.log('[SW] Deleting old cache:', name);
                        return caches.delete(name);
                    })
            );
        }).then(() => self.clients.claim())
    );
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);
    
    // Only cache same-origin requests
    if (url.origin !== location.origin) {
        return;
    }
    
    // Strategy: Cache-first for SVG figures (immutable)
    if (url.pathname.includes('/assets/figures/') && url.pathname.endsWith('.svg')) {
        event.respondWith(
            caches.open(CACHE_NAME).then((cache) => {
                return cache.match(event.request).then((cachedResponse) => {
                    if (cachedResponse) {
                        // Return cached version
                        return cachedResponse;
                    }
                    
                    // Fetch from network and cache
                    return fetch(event.request).then((networkResponse) => {
                        // Clone the response before caching
                        cache.put(event.request, networkResponse.clone());
                        return networkResponse;
                    });
                });
            })
        );
        return;
    }
    
    // Strategy: Network-first for HTML, JS, CSS (can update)
    if (url.pathname.endsWith('.html') || 
        url.pathname.endsWith('.js') || 
        url.pathname.endsWith('.css') ||
        url.pathname === '/') {
        event.respondWith(
            fetch(event.request)
                .then((networkResponse) => {
                    // Update cache with new version
                    caches.open(CACHE_NAME).then((cache) => {
                        cache.put(event.request, networkResponse.clone());
                    });
                    return networkResponse;
                })
                .catch(() => {
                    // Fallback to cache if offline
                    return caches.match(event.request);
                })
        );
        return;
    }
    
    // Default: try network, fallback to cache
    event.respondWith(
        fetch(event.request)
            .catch(() => caches.match(event.request))
    );
});
