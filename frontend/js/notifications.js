/**
 * ============================================================
 *  SGAC — Módulo de Notificaciones Inteligentes
 *  Archivo:  notifications.js
 *  Cargado:  ANTES de calendar.js (ver index.html)
 *
 *  Expone en window (consumidos por calendar.js e index.html):
 *    · window.showToast(msg, type, duration?)
 *    · window.checkHourlyAlerts(activities)
 *    · window.startNotificationPolling(getActivitiesFn)
 *    · window.lastAlertedActivityId   ← corrige bug en calendar.js:252
 *
 *  Todo lo demás es privado al IIFE — no contamina window.
 * ============================================================
 */

(function () {
    'use strict';

    /* ─── 0. GUARD: evitar doble carga ─────────────────────────────────── */
    if (window.__sgacNotificationsLoaded) {
        console.warn('[SGAC Notifications] Ya cargado — omitiendo re-inicialización.');
        return;
    }
    window.__sgacNotificationsLoaded = true;

    /* ─── 1. ESTADO PRIVADO ─────────────────────────────────────────────── */
    /**
     * Corrige el bug de calendar.js:252 donde lastAlertedActivityId
     * se usa sin haber sido declarada (variable global implícita).
     * Al declararla aquí, antes de que calendar.js cargue, el bug queda
     * resuelto sin modificar calendar.js.
     */
    window.lastAlertedActivityId = null;

    /** Set de alertas ya disparadas para esta sesión. Clave: "id_umbral" */
    const _alertedUpcoming = new Set();
    /** Set de actividades ya notificadas como vencidas en esta sesión */
    const _alertedOverdue = new Set();
    /** Set de actividades de prioridad alta ya alertadas en esta sesión */
    const _alertedHighPrio = new Set();

    /** ID del intervalo de polling — evita duplicados y memory leaks */
    let _pollingInterval = null;

    /** Historial de notificaciones para el panel visual (máx 20) */
    const _history = [];
    const MAX_HISTORY = 20;

    /* ─── 2. UTILIDAD: reproducir beep con Web Audio API ────────────────── */
    function _playBeep(freq = 660, duration = 0.25, volume = 0.15) {
        try {
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.frequency.value = freq;
            osc.type = 'sine';
            gain.gain.setValueAtTime(volume, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + duration);
            osc.start();
            osc.stop(ctx.currentTime + duration);
        } catch (_) { /* ignorar si el navegador bloquea audio */ }
    }

    /* ─── 3. TOAST ─────────────────────────────────────────────────────── */
    /**
     * Muestra un toast no intrusivo en la esquina inferior-derecha.
     * Compatible con el uso existente en calendar.js:
     *   window.showToast(mensaje, 'success' | 'warning' | 'danger' | 'info')
     *
     * @param {string} message  Texto del toast
     * @param {string} type     'success' | 'warning' | 'danger' | 'info'
     * @param {number} duration Duración en ms (default 4000)
     */
    window.showToast = function (message, type = 'info', duration = 4000) {
        const container = document.getElementById('toast-container');
        if (!container) return;

        /* Icono según tipo */
        const icons = {
            success: '✅',
            warning: '⚠️',
            danger: '❌',
            info: '🔔',
        };
        const icon = icons[type] || icons.info;

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'polite');
        toast.innerHTML = `
            <span class="toast-icon">${icon}</span>
            <span class="toast-msg">${message}</span>
            <button class="toast-close" aria-label="Cerrar notificación">×</button>
        `;

        /* Cerrar manualmente */
        toast.querySelector('.toast-close').addEventListener('click', () => _dismissToast(toast));

        container.appendChild(toast);

        /* Auto-dismiss */
        const timer = setTimeout(() => _dismissToast(toast), duration);

        /* Detener timer si el usuario pasa el mouse por encima */
        toast.addEventListener('mouseenter', () => clearTimeout(timer));
        toast.addEventListener('mouseleave', () => {
            setTimeout(() => _dismissToast(toast), 1500);
        });

        /* Guardar en historial */
        _addToHistory(message, type);
        _updateBadge();
    };

    function _dismissToast(toast) {
        if (!toast || toast._dismissing) return;
        toast._dismissing = true;
        toast.style.animation = 'sgacToastOut 0.3s forwards';
        setTimeout(() => toast.remove(), 300);
    }

    /* ─── 4. HISTORIAL Y PANEL DE NOTIFICACIONES ────────────────────────── */
    function _addToHistory(message, type) {
        _history.unshift({
            id: Date.now() + Math.random(),
            message,
            type,
            time: new Date().toLocaleTimeString('es-CL', { hour: '2-digit', minute: '2-digit' }),
            read: false,
        });
        if (_history.length > MAX_HISTORY) _history.pop();
    }

    function _unreadCount() {
        return _history.filter(n => !n.read).length;
    }

    function _updateBadge() {
        const badge = document.getElementById('sgac-notif-badge');
        if (!badge) return;
        const count = _unreadCount();
        badge.textContent = count > 9 ? '9+' : count;
        badge.style.display = count > 0 ? 'flex' : 'none';
    }

    function _renderPanel() {
        const list = document.getElementById('sgac-notif-list');
        if (!list) return;
        list.innerHTML = '';

        if (_history.length === 0) {
            list.innerHTML = '<li class="sgac-notif-empty">Sin notificaciones recientes</li>';
            return;
        }

        _history.forEach(n => {
            const li = document.createElement('li');
            li.className = `sgac-notif-item sgac-notif-${n.type}${n.read ? ' sgac-notif-read' : ''}`;
            li.innerHTML = `
                <span class="sgac-notif-item-msg">${n.message}</span>
                <span class="sgac-notif-item-time">${n.time}</span>
            `;
            li.addEventListener('click', () => {
                n.read = true;
                li.classList.add('sgac-notif-read');
                _updateBadge();
            });
            list.appendChild(li);
        });
    }

    /* ─── 5. INYECTAR BOTÓN DE CAMPANA EN EL SIDEBAR ────────────────────── */
    function _injectNotifButton() {
        /* No duplicar */
        if (document.getElementById('sgac-notif-btn')) return;

        const sidebar = document.getElementById('sidebar');
        if (!sidebar) return;

        /* Crear wrapper */
        const wrapper = document.createElement('div');
        wrapper.id = 'sgac-notif-wrapper';
        wrapper.className = 'sgac-notif-wrapper';

        wrapper.innerHTML = `
            <button id="sgac-notif-btn"
                    class="sgac-notif-btn"
                    aria-label="Ver notificaciones"
                    title="Notificaciones">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
                     stroke="currentColor" stroke-width="2"
                     stroke-linecap="round" stroke-linejoin="round">
                    <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
                    <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
                </svg>
                <span id="sgac-notif-badge" class="sgac-notif-badge" style="display:none">0</span>
            </button>

            <div id="sgac-notif-panel" class="sgac-notif-panel" aria-hidden="true">
                <div class="sgac-notif-header">
                    <span>🔔 Notificaciones</span>
                    <button id="sgac-notif-clear" class="sgac-notif-clear-btn"
                            title="Limpiar todas">Limpiar</button>
                </div>
                <ul id="sgac-notif-list" class="sgac-notif-list"></ul>
            </div>
        `;

        /* Insertar antes del footer del sidebar */
        const footer = sidebar.querySelector('.sidebar-footer');
        if (footer) {
            sidebar.insertBefore(wrapper, footer);
        } else {
            sidebar.appendChild(wrapper);
        }

        /* Toggle del panel */
        const btn = wrapper.querySelector('#sgac-notif-btn');
        const panel = wrapper.querySelector('#sgac-notif-panel');

        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const isOpen = panel.classList.toggle('sgac-notif-panel--open');
            panel.setAttribute('aria-hidden', String(!isOpen));
            if (isOpen) {
                /* Marcar como leídas al abrir */
                _history.forEach(n => { n.read = true; });
                _updateBadge();
                _renderPanel();
            }
        });

        /* Cerrar al hacer clic fuera */
        document.addEventListener('click', (e) => {
            if (!wrapper.contains(e.target)) {
                panel.classList.remove('sgac-notif-panel--open');
                panel.setAttribute('aria-hidden', 'true');
            }
        }, { passive: true });

        /* Limpiar historial */
        wrapper.querySelector('#sgac-notif-clear').addEventListener('click', () => {
            _history.length = 0;
            _updateBadge();
            _renderPanel();
        });
    }

    /* ─── 6. RESUMEN DIARIO ─────────────────────────────────────────────── */
    function _showDailySummary(activities) {
        const today = new Date();
        /* Solo aplica si es Abril 2026 (mismo criterio que el sistema actual) */
        if (today.getFullYear() !== 2026 || today.getMonth() !== 3) return;

        const todayDay = today.getDate();
        const todayActs = activities.filter(a => a.day_of_april === todayDay);
        const pending = todayActs.filter(a => !a.completed).length;
        const completed = todayActs.filter(a => a.completed).length;
        const highPrio = todayActs.filter(a => a.priority_id === 3 && !a.completed).length;

        if (todayActs.length === 0) {
            window.showToast('📋 No tienes actividades para hoy', 'info', 5000);
        } else {
            let msg = `📋 Hoy tienes <b>${todayActs.length}</b> actividad${todayActs.length !== 1 ? 'es' : ''}`;
            if (pending > 0) msg += ` · ${pending} pendiente${pending !== 1 ? 's' : ''}`;
            if (completed > 0) msg += ` · ${completed} completada${completed !== 1 ? 's' : ''}`;
            if (highPrio > 0) msg += ` · <b style="color:#EF4444">⚠️ ${highPrio} alta prioridad</b>`;
            window.showToast(msg, 'info', 7000);
        }
    }

    /* ─── 7. ALERTAS DE TIEMPO (próximas y vencidas) ────────────────────── */
    /**
     * Evalúa las actividades del día actual contra la hora actual.
     * Solo dispara cada alerta UNA vez por sesión (usa los Sets privados).
     *
     * @param {Array} activities Lista completa de actividades del mes
     */
    function _evaluateTimeAlerts(activities) {
        const now = new Date();
        if (now.getFullYear() !== 2026 || now.getMonth() !== 3) return;

        const todayDay = now.getDate();

        activities.forEach(act => {
            if (act.day_of_april !== todayDay) return;
            if (!act.time) return;

            const parts = act.time.split(':');
            if (parts.length < 2) return;

            const h = parseInt(parts[0], 10);
            const m = parseInt(parts[1], 10);
            if (isNaN(h) || isNaN(m)) return;

            const actDate = new Date(2026, 3, todayDay, h, m);
            const diffMs = actDate - now;
            const diffMinutes = Math.floor(diffMs / 1000 / 60);

            /* ── B. ACTIVIDAD VENCIDA ───────────────────────────────────── */
            if (diffMs < 0 && !act.completed) {
                const key = `overdue_${act.id}`;
                if (!_alertedOverdue.has(key)) {
                    _alertedOverdue.add(key);
                    const minsAgo = Math.abs(diffMinutes);
                    const emojiStr = act.emoji ? `${act.emoji} ` : '';
                    window.showToast(
                        `⏰ Actividad vencida hace ${minsAgo}m: <b>${emojiStr}${act.title}</b>`,
                        'danger',
                        6000
                    );
                    _playBeep(440, 0.4, 0.12);
                }
                return; /* ya vencida, no evaluar próximas */
            }

            /* ── A. PRÓXIMA — umbrales: 60m, 30m, 10m ──────────────────── */
            const thresholds = [
                { limit: 65, label: '1 hora', key: '60', freq: 880 },
                { limit: 33, label: '30 minutos', key: '30', freq: 660 },
                { limit: 12, label: '10 minutos', key: '10', freq: 1100 },
            ];

            for (const t of thresholds) {
                if (diffMinutes <= t.limit) {
                    const alertKey = `${act.id}_${t.key}`;
                    if (!_alertedUpcoming.has(alertKey)) {
                        _alertedUpcoming.add(alertKey);

                        /* Prioridad alta → tipo warning especial */
                        const isHigh = act.priority_id === 3;
                        const type = isHigh ? 'danger' : 'warning';
                        const prefix = isHigh ? '🔴 [Alta]' : '🔔';
                        const emojiStr = act.emoji ? `${act.emoji} ` : '';

                        window.showToast(
                            `${prefix} Falta ${t.label} para: <b>${emojiStr}${act.title}</b>`,
                            type,
                            6000
                        );
                        _playBeep(t.freq, 0.3, 0.15);
                    }
                    break; /* solo el umbral más próximo */
                }
            }

            /* ── C. PRIORIDAD ALTA al abrir sistema ─────────────────────── */
            if (act.priority_id === 3 && !act.completed && diffMs > 0) {
                const key = `high_${act.id}`;
                if (!_alertedHighPrio.has(key)) {
                    _alertedHighPrio.add(key);
                    /* No disparar toast separado si ya se disparó como "próxima"
                       — evitar spam. Solo si faltan más de 65 minutos. */
                    if (diffMinutes > 65) {
                        const emojiStr = act.emoji ? `${act.emoji} ` : '';
                        window.showToast(
                            `🔴 Actividad de alta prioridad hoy: <b>${emojiStr}${act.title}</b> (${act.time})`,
                            'warning',
                            7000
                        );
                    }
                }
            }
        });
    }

    /* ─── 8. checkHourlyAlerts (llamado al iniciar el sistema) ──────────── */
    /**
     * Punto de entrada desde index.html al cargar la página.
     * Evalúa alertas iniciales + muestra resumen diario.
     *
     * @param {Array} activities Lista completa de actividades
     */
    window.checkHourlyAlerts = function (activities) {
        if (!Array.isArray(activities)) return;

        /* Pequeño delay para que los toasts no aparezcan antes de que
           la UI termine de renderizar */
        setTimeout(() => {
            _showDailySummary(activities);
            _evaluateTimeAlerts(activities);
        }, 1200);
    };

    /* ─── 9. startNotificationPolling (polling cada 60s) ────────────────── */
    /**
     * Inicia un intervalo de polling seguro.
     * Llama a getActivitiesFn() cada 60s para evaluar alertas frescas.
     * Anti-duplicate: si ya hay un polling activo, lo cancela primero.
     * Anti-memory-leak: el intervalId es privado en el IIFE.
     *
     * @param {Function} getActivitiesFn  Función async que retorna actividades
     */
    window.startNotificationPolling = function (getActivitiesFn) {
        if (typeof getActivitiesFn !== 'function') return;

        /* Cancelar polling anterior si existe */
        if (_pollingInterval) {
            clearInterval(_pollingInterval);
            _pollingInterval = null;
        }

        _pollingInterval = setInterval(async () => {
            try {
                const activities = await getActivitiesFn();
                if (Array.isArray(activities)) {
                    _evaluateTimeAlerts(activities);
                }
            } catch (err) {
                /* No interrumpir el polling por un error de red */
                console.warn('[SGAC Notifications] Error en polling:', err.message);
            }
        }, 60_000); /* cada 60 segundos */

        console.log('[SGAC Notifications] Polling iniciado (60s)');
    };

    /* ─── 10. INICIALIZACIÓN (cuando el DOM esté listo) ─────────────────── */
    function _init() {
        _injectNotifButton();
        console.log('[SGAC Notifications] Módulo cargado correctamente ✅');
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', _init);
    } else {
        /* DOM ya listo (script cargado defer/async o al final del body) */
        _init();
    }

})();
