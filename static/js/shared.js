/**
 * NiftyOps Trading Terminal — Shared JS Module v2.0
 * Handles: Theme, Sidebar, Clock, Toast, Session, Shortcuts, Polling
 */

(function () {
    'use strict';

    /* ── Namespace ─────────────────────────────────────────── */
    const NiftyOps = {

        /* ── Boot ──────────────────────────────────────────── */
        init() {
            this.initTheme();
            this.initSidebar();
            this.initClock();
            this.initShortcuts();
            this.initSessionStatus();
        },

        /* ── Theme Manager ─────────────────────────────────── */
        initTheme() {
            const saved = localStorage.getItem('niftyops_theme') || 'dark';
            document.documentElement.setAttribute('data-theme', saved);

            const toggleBtn = document.getElementById('theme-toggle');
            if (toggleBtn) {
                this._syncThemeIcon(toggleBtn, saved);
                toggleBtn.addEventListener('click', () => {
                    const current = document.documentElement.getAttribute('data-theme');
                    const next = current === 'dark' ? 'light' : 'dark';
                    document.documentElement.setAttribute('data-theme', next);
                    localStorage.setItem('niftyops_theme', next);
                    this._syncThemeIcon(toggleBtn, next);
                    window.dispatchEvent(new CustomEvent('niftyops:theme-changed', { detail: next }));
                });
            }
        },

        _syncThemeIcon(btn, theme) {
            btn.innerHTML = theme === 'dark' ? '☀️' : '🌙';
            btn.setAttribute('aria-label', theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
            btn.title = theme === 'dark' ? 'Light Mode (Alt+T)' : 'Dark Mode (Alt+T)';
        },

        /* ── Sidebar Manager ───────────────────────────────── */
        initSidebar() {
            const shell = document.querySelector('.app-shell');
            const collapseBtn = document.getElementById('btn-collapse-sidebar');
            const mobileBtn = document.getElementById('btn-mobile-sidebar');

            // Restore saved state
            if (window.innerWidth > 768) {
                const saved = localStorage.getItem('niftyops_sidebar') || 'expanded';
                if (saved === 'collapsed') shell?.classList.add('sidebar-collapsed');
            }

            collapseBtn?.addEventListener('click', () => {
                const collapsed = shell.classList.toggle('sidebar-collapsed');
                localStorage.setItem('niftyops_sidebar', collapsed ? 'collapsed' : 'expanded');
            });

            mobileBtn?.addEventListener('click', () => {
                shell?.classList.toggle('sidebar-mobile-open');
            });

            // Close mobile sidebar on outside click
            document.addEventListener('click', (e) => {
                if (window.innerWidth <= 768) {
                    const sidebar = document.querySelector('.sidebar');
                    if (sidebar && !sidebar.contains(e.target) && !mobileBtn?.contains(e.target)) {
                        shell?.classList.remove('sidebar-mobile-open');
                    }
                }
            });
        },

        /* ── IST Clock ─────────────────────────────────────── */
        initClock() {
            const clockEl = document.getElementById('live-clock');
            const sidebarClock = document.getElementById('sidebar-clock-time');
            const marketEl = document.getElementById('market-status');

            const tick = () => {
                const now = new Date();
                const utc = now.getTime() + now.getTimezoneOffset() * 60000;
                const ist = new Date(utc + 19800000); // +5:30

                const h = String(ist.getHours()).padStart(2, '0');
                const m = String(ist.getMinutes()).padStart(2, '0');
                const s = String(ist.getSeconds()).padStart(2, '0');
                const timeStr = `${h}:${m}:${s} IST`;

                if (clockEl) clockEl.textContent = timeStr;
                if (sidebarClock) sidebarClock.textContent = timeStr;

                if (marketEl) {
                    const day = ist.getDay();
                    const t = ist.getHours() * 100 + ist.getMinutes();
                    let label, cls;

                    if (day === 0 || day === 6) { label = 'CLOSED'; cls = 'badge-neutral'; }
                    else if (t >= 900 && t < 915)  { label = 'PRE-OPEN'; cls = 'badge-warning'; }
                    else if (t >= 915 && t < 1530) { label = '🟢 OPEN'; cls = 'badge-success'; }
                    else { label = 'CLOSED'; cls = 'badge-neutral'; }

                    marketEl.innerHTML = `<span class="badge ${cls}">${label}</span>`;
                }
            };

            tick();
            setInterval(tick, 1000);
        },

        /* ── Session Status ────────────────────────────────── */
        async initSessionStatus() {
            await this.refreshSessionStatus();
        },

        async refreshSessionStatus() {
            const dots  = document.querySelectorAll('.session-status-dot');
            const texts = document.querySelectorAll('.session-status-text');
            try {
                const res  = await fetch('/api/session-status');
                const data = await res.json();
                const ok   = data.has_session;

                dots.forEach(d => {
                    d.classList.toggle('active', ok);
                    d.style.background = ok ? 'var(--green)' : 'var(--red)';
                });
                texts.forEach(t => {
                    t.textContent = ok ? 'Session Active' : 'Session Inactive';
                    t.className = `session-status-text text-sm font-semi ${ok ? 'text-success' : 'text-error'}`;
                });

                return data;
            } catch (_) {
                dots.forEach(d => d.style.background = 'var(--text-subtle)');
                texts.forEach(t => t.textContent = 'Offline');
                return null;
            }
        },

        /* ── Toast Notifications ───────────────────────────── */
        showToast(message, type = 'info', duration = 3500) {
            let container = document.querySelector('.toast-container');
            if (!container) {
                container = Object.assign(document.createElement('div'), { className: 'toast-container' });
                document.body.appendChild(container);
            }

            const ICONS = { success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️' };
            const toast = document.createElement('div');
            toast.className = `toast toast-${type}`;
            toast.setAttribute('role', 'alert');
            toast.setAttribute('aria-live', 'polite');
            toast.innerHTML = `
                <span class="toast-icon">${ICONS[type] || ICONS.info}</span>
                <span class="toast-msg">${this._escapeHtml(message)}</span>
                <span class="toast-close" title="Dismiss">✕</span>
            `;

            const close = () => {
                toast.classList.remove('toast-show');
                setTimeout(() => toast.remove(), 300);
            };

            toast.querySelector('.toast-close').addEventListener('click', close);
            container.appendChild(toast);
            requestAnimationFrame(() => requestAnimationFrame(() => toast.classList.add('toast-show')));
            setTimeout(close, duration);
        },

        /* ── Keyboard Shortcuts ────────────────────────────── */
        initShortcuts() {
            document.addEventListener('keydown', (e) => {
                const inInput = ['INPUT', 'TEXTAREA', 'SELECT'].includes(e.target.tagName);

                // Alt+T = toggle theme (works everywhere)
                if (e.altKey && e.key === 't') {
                    e.preventDefault();
                    document.getElementById('theme-toggle')?.click();
                    return;
                }

                if (inInput) return;

                if (e.ctrlKey) {
                    const nav = { d: '/', a: '/analyzer', j: '/journal', s: '/settings' };
                    const dest = nav[e.key?.toLowerCase()];
                    if (dest) { e.preventDefault(); window.location.href = dest; return; }
                }

                if (e.key === 'F11') {
                    const iframe = document.querySelector('.chart-panel iframe');
                    if (iframe) {
                        e.preventDefault();
                        if (!document.fullscreenElement) iframe.requestFullscreen().catch(() => {});
                        else document.exitFullscreen();
                    }
                }
            });
        },

        /* ── Task Poller ───────────────────────────────────── */
        pollTaskStatus(taskId, onUpdate, onComplete, onError, intervalMs = 2000) {
            const id = setInterval(async () => {
                try {
                    const res = await fetch(`/api/task/${taskId}`);
                    if (!res.ok) throw new Error(`HTTP ${res.status}`);
                    const data = await res.json();

                    if (onUpdate) onUpdate(data);

                    if (data.status === 'COMPLETED') {
                        clearInterval(id);
                        if (onComplete) onComplete(data);
                    } else if (data.status === 'FAILED') {
                        clearInterval(id);
                        if (onError) onError(data.error || 'Task failed');
                    }
                } catch (err) {
                    clearInterval(id);
                    if (onError) onError(err.message);
                }
            }, intervalMs);
            return id;
        },

        /* ── Fetch Wrapper with Retry ──────────────────────── */
        async apiFetch(url, opts = {}, retries = 2) {
            const defaults = { headers: { 'Content-Type': 'application/json' } };
            const options = { ...defaults, ...opts, headers: { ...defaults.headers, ...(opts.headers || {}) } };
            for (let i = 0; i <= retries; i++) {
                try {
                    const res = await fetch(url, options);
                    if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
                    return await res.json();
                } catch (err) {
                    if (i === retries) throw err;
                    await this._sleep(500 * (i + 1));
                }
            }
        },

        /* ── Number Formatters ─────────────────────────────── */
        formatINR(num) {
            if (num == null || isNaN(num)) return '—';
            return new Intl.NumberFormat('en-IN', {
                style: 'currency', currency: 'INR', maximumFractionDigits: 2
            }).format(num);
        },

        formatNum(num, decimals = 2) {
            if (num == null || isNaN(num)) return '—';
            return new Intl.NumberFormat('en-IN', {
                minimumFractionDigits: decimals, maximumFractionDigits: decimals
            }).format(num);
        },

        formatPct(num) {
            if (num == null || isNaN(num)) return '—';
            return (num >= 0 ? '+' : '') + num.toFixed(2) + '%';
        },

        formatDate(dateStr) {
            if (!dateStr) return '—';
            return new Date(dateStr).toLocaleDateString('en-IN', {
                day: '2-digit', month: 'short', year: 'numeric'
            });
        },

        formatTime(dateStr) {
            if (!dateStr) return '—';
            return new Date(dateStr).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
        },

        todayIST() {
            const utc = Date.now() + new Date().getTimezoneOffset() * 60000;
            return new Date(utc + 19800000).toISOString().slice(0, 10);
        },

        /* ── Debounce / Throttle ───────────────────────────── */
        debounce(fn, wait = 300) {
            let t;
            return function (...args) {
                clearTimeout(t);
                t = setTimeout(() => fn.apply(this, args), wait);
            };
        },

        throttle(fn, limit = 16) {
            let last = 0;
            return function (...args) {
                const now = Date.now();
                if (now - last >= limit) { last = now; fn.apply(this, args); }
            };
        },

        /* ── LocalStorage helpers ──────────────────────────── */
        ls: {
            NS: 'niftyops',
            get(key, fallback = null) {
                try { return JSON.parse(localStorage.getItem(`${this.NS}_${key}`)) ?? fallback; } catch { return fallback; }
            },
            set(key, val) {
                try { localStorage.setItem(`${this.NS}_${key}`, JSON.stringify(val)); } catch {}
            },
            remove(key) { localStorage.removeItem(`${this.NS}_${key}`); }
        },

        /* ── Tab System ────────────────────────────────────── */
        initTabs(container) {
            const tabs = container.querySelectorAll('[data-tab]');
            const panels = container.querySelectorAll('[data-panel]');

            tabs.forEach(tab => {
                tab.addEventListener('click', () => {
                    const target = tab.dataset.tab;
                    tabs.forEach(t => t.classList.remove('active'));
                    panels.forEach(p => p.classList.remove('active'));
                    tab.classList.add('active');
                    container.querySelector(`[data-panel="${target}"]`)?.classList.add('active');
                });
            });
        },

        /* ── Modal System ──────────────────────────────────── */
        openModal(id) {
            const modal = document.getElementById(id);
            if (!modal) return;
            modal.style.display = 'flex';
            requestAnimationFrame(() => modal.classList.add('visible'));
            document.body.style.overflow = 'hidden';
            // Focus first input
            setTimeout(() => modal.querySelector('input, select, textarea')?.focus(), 100);

            // Close on backdrop click
            modal.addEventListener('click', (e) => {
                if (e.target === modal) this.closeModal(id);
            }, { once: true });

            // ESC key
            const escHandler = (e) => { if (e.key === 'Escape') { this.closeModal(id); document.removeEventListener('keydown', escHandler); } };
            document.addEventListener('keydown', escHandler);
        },

        closeModal(id) {
            const modal = document.getElementById(id);
            if (!modal) return;
            modal.classList.remove('visible');
            setTimeout(() => { modal.style.display = 'none'; }, 300);
            document.body.style.overflow = '';
        },

        /* ── Private Utilities ─────────────────────────────── */
        _escapeHtml(str) {
            return String(str)
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;');
        },

        _sleep(ms) { return new Promise(r => setTimeout(r, ms)); },
    };

    /* ── Global Exposure ───────────────────────────────────── */
    window.NiftyOps = NiftyOps;

    /* Helper convenience aliases — callable as bare globals in any template */
    window.showToast   = (msg, type, dur) => NiftyOps.showToast(msg, type, dur);
    window.escapeHtml  = (s) => NiftyOps._escapeHtml(s);
    window.todayIST    = () => NiftyOps.todayIST();
    window.formatINR   = (n) => NiftyOps.formatINR(n);
    window.formatNum   = (n, d) => NiftyOps.formatNum(n, d);
    window.formatPct   = (n) => NiftyOps.formatPct(n);

    /* ── Boot on DOM ready ─────────────────────────────────── */
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => NiftyOps.init());
    } else {
        NiftyOps.init();
    }
})();
