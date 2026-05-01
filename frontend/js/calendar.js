/**
 * Lógica del Calendario de SGAC (Abril 2026)
 */

window.currentActivities = [];
let countdownInterval = null;

// ── Renderiza la cuadrícula de los 30 días de Abril ──────────────────────────
window.renderCalendar = function(activities) {
    window.currentActivities = activities;
    const grid = document.getElementById('calendar-grid');
    if (!grid) return;

    grid.innerHTML = '';

    const daysOfWeek = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'];
    daysOfWeek.forEach(d => {
        const header = document.createElement('div');
        header.className = 'day-header';
        header.textContent = d;
        grid.appendChild(header);
    });

    // Abril 2026 empieza en Miércoles (índice 3)
    const firstDayIndex = 3;
    const totalDays = 30;

    for (let i = 0; i < firstDayIndex; i++) {
        const emptyCell = document.createElement('div');
        emptyCell.className = 'day-cell empty';
        grid.appendChild(emptyCell);
    }

    const today = new Date();
    const isApril2026 = today.getFullYear() === 2026 && today.getMonth() === 3;
    const currentDay = isApril2026 ? today.getDate() : null;

    for (let day = 1; day <= totalDays; day++) {
        const cell = document.createElement('div');
        cell.className = 'day-cell';
        if (day === currentDay) cell.classList.add('today');
        cell.dataset.dayName = daysOfWeek[(firstDayIndex + day - 1) % 7];
        cell.dataset.day = day;

        const num = document.createElement('span');
        num.className = 'day-number';
        num.textContent = day;
        cell.appendChild(num);

        const dayActivities = activities.filter(a => a.day_of_april === day);
        let hasHighPriority = false;
        const MAX_VISIBLE_CHIPS = 3;

        dayActivities.slice(0, MAX_VISIBLE_CHIPS).forEach(act => {
            if (act.priority_id === 3) hasHighPriority = true;
            cell.appendChild(window.renderActivityChip(act));
        });

        if (dayActivities.length > MAX_VISIBLE_CHIPS) {
            const moreChip = document.createElement('div');
            moreChip.className = 'chip-more';
            moreChip.textContent = `+${dayActivities.length - MAX_VISIBLE_CHIPS} más`;
            cell.appendChild(moreChip);
            if (dayActivities.some(a => a.priority_id === 3)) hasHighPriority = true;
        }

        if (hasHighPriority) cell.classList.add('has-high-priority');
        cell.addEventListener('click', () => window.openDayModal(day, dayActivities));
        grid.appendChild(cell);
    }
};

// ── Chip de actividad en el calendario ───────────────────────────────────────
window.renderActivityChip = function(activity) {
    const chip = document.createElement('div');

    let bgClass = 'chip-low-bg';
    let dotClass = 'chip-low-dot';

    if (activity.priority_id === 3) { bgClass = 'chip-high-bg'; dotClass = 'chip-high-dot'; }
    else if (activity.priority_id === 2) { bgClass = 'chip-med-bg'; dotClass = 'chip-med-dot'; }

    // Indicador de completado en el chip
    const statusDot = activity.completed
        ? '<span style="width:6px;height:6px;border-radius:50%;background:#22C55E;display:inline-block;margin-right:2px;"></span>'
        : '<span style="width:6px;height:6px;border-radius:50%;background:#F59E0B;display:inline-block;margin-right:2px;"></span>';

    chip.className = `activity-chip ${bgClass}`;
    chip.innerHTML = `
        <span class="chip-dot ${dotClass}"></span>
        <span>${activity.emoji || ''}</span>
        <span class="chip-text">${activity.title}</span>
        ${statusDot}
    `;
    return chip;
};

// ── Drawer lateral ───────────────────────────────────────────────────────────
window.openDayModal = function(day, dayActivities) {
    const overlay = document.getElementById('drawer-overlay');
    const panel   = document.getElementById('drawer-panel');
    const content = document.getElementById('modal-content-list');
    const title   = document.getElementById('modal-day-title');
    if (!overlay || !content || !title) return;

    const daysOfWeek = ['Domingo','Lunes','Martes','Miércoles','Jueves','Viernes','Sábado'];
    const dayName = daysOfWeek[new Date(2026, 3, day).getDay()];
    title.textContent = `${dayName} ${day} de Abril`;
    content.innerHTML = '';

    if (dayActivities.length === 0) {
        content.innerHTML = '<p class="text-muted" style="margin-top:1rem;font-size:0.9rem;">No hay actividades planificadas para este día.</p>';
    } else {
        dayActivities.forEach(act => content.appendChild(window.renderActivityCard(act)));
    }

    const newBtn = document.createElement('button');
    newBtn.className = 'btn-primary';
    newBtn.style.marginTop = 'auto';
    newBtn.textContent = '+ Nueva actividad';
    newBtn.addEventListener('click', () => window.showCreateForm(day));
    content.appendChild(newBtn);

    overlay.classList.add('active');
    panel.classList.add('active');
};

window.closeModal = function() {
    document.getElementById('drawer-overlay')?.classList.remove('active');
    document.getElementById('drawer-panel')?.classList.remove('active');
};

// ── Filtros de prioridad ─────────────────────────────────────────────────────
window.initPriorityFilter = function() {
    const btns = document.querySelectorAll('.filter-btn');
    btns.forEach(btn => {
        btn.addEventListener('click', async (e) => {
            btns.forEach(c => c.classList.remove('active'));
            const targetBtn = e.target.closest('.filter-btn');
            targetBtn.classList.add('active');

            const priority = targetBtn.dataset.priority;
            const filtered = priority === 'all'
                ? await window.getAprilActivities()
                : await window.filterByPriority(priority);

            window.renderCalendar(filtered);
            const statsEl = document.getElementById('month-stats');
            if (statsEl) statsEl.textContent = `${filtered.length} actividades filtradas`;
        });
    });
};

// ── Cuenta regresiva ─────────────────────────────────────────────────────────
/* window.startCountdown = function(activities) {
    const banner = document.getElementById('countdown-banner');
    if (!banner) return;
    if (countdownInterval) clearInterval(countdownInterval);

    const now = new Date();
    let nextActivity = null;
    let minDiff = Infinity;

    activities.forEach(act => {
        if (act.time) {
            const [h, m] = act.time.split(':');
            const actDate = new Date(2026, 3, act.day_of_april, h, m);
            const diff = actDate - now;
            if (diff > 0 && diff < minDiff) { minDiff = diff; nextActivity = { ...act, actDate }; }
        }
    });

    if (!nextActivity) { banner.classList.add('hidden'); return; }
    banner.classList.remove('hidden');

    countdownInterval = setInterval(() => {
        const diff = nextActivity.actDate - new Date();
        if (diff <= 0) {
            clearInterval(countdownInterval);
            banner.innerHTML = `<span>⚡ ¡Es hora de: <b>${nextActivity.title}</b>!</span>`;
            banner.classList.add('urgent');
            return;
        }
        const h = Math.floor((diff / (1000 * 60 * 60)) % 24);
        const m = Math.floor((diff / 1000 / 60) % 60);
        banner.innerHTML = `
            <span style="font-size:10px;text-transform:uppercase;font-weight:700;">Siguiente • en ${h}h ${m}m</span>
            <span style="font-size:13px;color:var(--text-primary);">${nextActivity.title}</span>
        `;
        banner.classList.toggle('urgent', h === 0 && m < 60);
    }, 1000);
};
 */


window.startCountdown = function (activities) {
    const banner = document.getElementById('countdown-banner');
    if (!banner) return;

    if (countdownInterval) clearInterval(countdownInterval);

    const now = new Date();
    let nextActivity = null;
    let minDiff = Infinity;

    activities.forEach(act => {
        if (!act.time) return;

        const parts = act.time.split(':');
        if (parts.length < 2) return;

        const h = parseInt(parts[0]);
        const m = parseInt(parts[1]);

        const actDate = new Date(2026, 3, act.day_of_april, h, m);
        const diff = actDate - now;

        if (diff > 0 && diff < minDiff) {
            minDiff = diff;
            nextActivity = { ...act, actDate };
        }
    });

    if (!nextActivity) {
        banner.classList.add('hidden');
        return;
    }

    banner.classList.remove('hidden');

    countdownInterval = setInterval(() => {

        const diff = nextActivity.actDate - new Date();

        if (diff <= 0) {
            clearInterval(countdownInterval);

            const emojiStr = nextActivity.emoji ? `${nextActivity.emoji} ` : '';
            banner.innerHTML =
                `⚡ ¡Es hora de: <b>${emojiStr}${nextActivity.title}</b>!`;

            banner.classList.add('urgent');
            return;
        }

        const totalMinutes = Math.floor(diff / 1000 / 60);
        const h = Math.floor(totalMinutes / 60);
        const m = totalMinutes % 60;

        /* 🔔 ALERTA A 1 HORA */
        if (
            totalMinutes <= 60 &&
            lastAlertedActivityId !== nextActivity.id
        ) {
            lastAlertedActivityId = nextActivity.id;

            // sonido generado por navegador
            try {
                const ctx = new (window.AudioContext || window.webkitAudioContext)();
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();

                osc.connect(gain);
                gain.connect(ctx.destination);

                osc.frequency.value = 880;
                osc.type = 'sine';

                gain.gain.setValueAtTime(0.2, ctx.currentTime);

                osc.start();
                osc.stop(ctx.currentTime + 0.4);

            } catch (e) {}

            if (window.showToast) {
                const emojiStr = nextActivity.emoji ? `${nextActivity.emoji} ` : '';
                window.showToast(
                    `🔔 Falta 1 hora para: ${emojiStr}${nextActivity.title}`,
                    'warning'
                );
            }
        }

        banner.innerHTML = `
            <span style="font-size:10px;font-weight:700;">
                Siguiente • en ${h}h ${m}m
            </span>

            <span style="font-size:13px;">
                ${nextActivity.emoji ? nextActivity.emoji + ' ' : ''}${nextActivity.title}
            </span>
        `;

        banner.classList.toggle('urgent', totalMinutes <= 60);

    }, 1000);
};
















// ── Popup actividad destacada ────────────────────────────────────────────────
window.showDailyPopup = function(activities) {
    const today = new Date();
    if (today.getFullYear() !== 2026 || today.getMonth() !== 3) return;
    const currentDay = today.getDate();
    const high = activities.find(a => a.day_of_april === currentDay && a.priority_id === 3);
    if (high) {
        const popup = document.getElementById('popup-overlay');
        const popupTitle = document.getElementById('popup-title');
        if (popup && popupTitle) {
            popupTitle.textContent = high.title;
            setTimeout(() => popup.classList.add('active'), 800);
        }
    }
};

// Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        window.closeModal();
        document.getElementById('popup-overlay')?.classList.remove('active');
        document.getElementById('activity-detail-modal')?.remove();
    }
});

// ── CARD DE ACTIVIDAD (con indicador de estado y modal de detalle) ───────────
window.renderActivityCard = function(act) {
    const card = document.createElement('div');
    card.className = act.completed ? 'activity-card card-completed' : 'activity-card';
    card.style.position = 'relative'; // necesario para el indicador absoluto

    // Color según prioridad
    let stripColor = '#22C55E';
    if (act.priority_id === 3) stripColor = '#EF4444';
    else if (act.priority_id === 2) stripColor = '#F59E0B';

    // Indicador de estado
    const statusColor = act.completed ? '#22C55E' : '#F59E0B';
    const statusTitle = act.completed ? 'Realizada' : 'Pendiente';

    // Checklist progress
    let checklistHTML = '';
    if (act.checklist && act.checklist.length > 0) {
        const done  = act.checklist.filter(i => i.done).length;
        const total = act.checklist.length;
        const pct   = Math.round((done / total) * 100);
        checklistHTML = `
            <div style="margin-top:0.5rem;">
                <div style="height:4px;background:var(--border);border-radius:2px;overflow:hidden;">
                    <div style="width:${pct}%;height:100%;background:${stripColor};border-radius:2px;"></div>
                </div>
                <span style="font-size:0.7rem;color:var(--text-secondary);">${done}/${total} ítems completados</span>
            </div>`;
    }

    card.innerHTML = `
        <!-- Franja de prioridad -->
        <div class="card-priority-strip" style="background:${stripColor};"></div>

        <!-- Indicador de estado (🟡 pendiente / 🟢 realizada) -->
        <div class="card-status-dot"
             title="${statusTitle}"
             data-id="${act.id}"
             style="position:absolute;top:10px;right:10px;
                    width:13px;height:13px;border-radius:50%;
                    background:${statusColor};cursor:pointer;
                    box-shadow:0 0 0 2px var(--bg-primary),
                               0 0 0 3.5px ${statusColor};">
        </div>

        <!-- Header clicable → abre modal de detalle -->
        <div class="card-header" data-id="${act.id}"
             style="cursor:pointer;padding-right:1.5rem;">
            <span class="card-emoji">${act.emoji || '📅'}</span>
            <div style="flex:1;min-width:0;">
                <h4 class="card-title"
                    style="${act.completed ? 'text-decoration:line-through;color:var(--text-secondary);' : ''}">
                    ${act.title}
                </h4>
                ${act.time ? `<div style="font-size:0.75rem;color:var(--text-secondary);margin-bottom:0.25rem;display:flex;align-items:center;gap:0.25rem;"><span style="font-size:0.85rem">🕒</span> ${act.time}</div>` : ''}
                <p class="card-desc">${act.description || 'Sin descripción'}</p>
            </div>
        </div>

        ${checklistHTML}

        <!-- Acciones -->
        <div class="card-actions" style="margin-top:0.625rem;">
            <button class="btn-small btn-toggle-done"
                    style="color:${statusColor};">
                ${act.completed ? '↩ Pendiente' : '✓ Realizada'}
            </button>
            <button class="btn-small btn-edit">✏️ Editar</button>
            <button class="btn-small btn-delete"
                    style="color:#EF4444;border-color:rgba(239,68,68,0.3);">
                🗑️ Eliminar
            </button>
        </div>
    `;

    // Clic en header → modal de detalle
    card.querySelector('.card-header').addEventListener('click', () => {
        window.showActivityDetail(act);
    });

    // Clic en indicador de estado → toggle
    card.querySelector('.card-status-dot').addEventListener('click', async (e) => {
        e.stopPropagation();
        await window.toggleActivityDone(act, card);
    });

    // Botón toggle
    card.querySelector('.btn-toggle-done').addEventListener('click', async (e) => {
        e.stopPropagation();
        await window.toggleActivityDone(act, card);
    });

    // Botón editar
    card.querySelector('.btn-edit').addEventListener('click', (e) => {
        e.stopPropagation();
        window.showEditForm(act);
    });

    // Botón eliminar
    card.querySelector('.btn-delete').addEventListener('click', (e) => {
        e.stopPropagation();
        window.confirmDelete(act.id, card);
    });

    return card;
};

// ── Toggle completado ────────────────────────────────────────────────────────
window.toggleActivityDone = async function(act, cardEl) {
    try {
        const updated = await window.updateActivity(act.id, { completed: !act.completed });
        const idx = window.currentActivities.findIndex(a => a.id === act.id);
        if (idx !== -1) window.currentActivities[idx] = updated;

        const newCard = window.renderActivityCard(updated);
        cardEl.replaceWith(newCard);

        const dayActs = window.currentActivities.filter(a => a.day_of_april === updated.day_of_april);
        window.updateDayCell(updated.day_of_april, dayActs);

        window.showToast(
            updated.completed ? '✅ Marcada como realizada' : '↩ Marcada como pendiente',
            updated.completed ? 'success' : 'warning'
        );
    } catch (e) {
        window.showToast('❌ Error al actualizar estado', 'danger');
    }
};
// ── Modal de detalle de actividad ────────────────────────────────────────────
window.showActivityDetail = function(act) {
    document.getElementById('activity-detail-modal')?.remove();

    let stripColor = '#22C55E';
    if (act.priority_id === 3) stripColor = '#EF4444';
    else if (act.priority_id === 2) stripColor = '#F59E0B';

    const statusColor  = act.completed ? '#22C55E' : '#F59E0B';
    const statusLabel  = act.completed ? '✅ Realizada' : '🟡 Pendiente';
    const priorityName = act.priority_name
        || { 1: 'Baja', 2: 'Media', 3: 'Alta' }[act.priority_id]
        || '';

    const doneCnt  = (act.checklist || []).filter(i => i.done).length;
    const totalCnt = (act.checklist || []).length;

    // Crear overlay
    const overlay = document.createElement('div');
    overlay.id = 'activity-detail-modal';
    overlay.style.cssText = `
        position:fixed;inset:0;
        background:rgba(0,0,0,0.5);
        display:flex;align-items:center;justify-content:center;
        z-index:3000;
    `;

    // Crear card del modal
    const card = document.createElement('div');
    card.style.cssText = `
        background:var(--bg-primary);border-radius:14px;
        width:430px;max-width:95vw;max-height:88vh;
        overflow-y:auto;box-shadow:0 20px 50px rgba(0,0,0,0.25);
    `;
    card.addEventListener('click', e => e.stopPropagation());

    card.innerHTML = `
        <div style="height:6px;background:${stripColor};border-radius:14px 14px 0 0;"></div>
        <div style="padding:1.25rem 1.5rem 1rem;border-bottom:1px solid var(--border);
                    display:flex;align-items:flex-start;justify-content:space-between;gap:1rem;">
            <div style="display:flex;align-items:center;gap:0.75rem;">
                <span style="font-size:2.2rem;line-height:1;">${act.emoji || '📅'}</span>
                <div>
                    <h2 style="font-size:1.1rem;font-weight:700;margin:0;color:var(--text-primary);
                               ${act.completed ? 'text-decoration:line-through;' : ''}">
                        ${act.title}
                    </h2>
                    <div style="display:flex;align-items:center;gap:0.5rem;margin-top:0.3rem;flex-wrap:wrap;">
                        <span style="width:10px;height:10px;border-radius:50%;
                                     background:${statusColor};display:inline-block;"></span>
                        <span style="font-size:0.78rem;color:var(--text-secondary);">${statusLabel}</span>
                        <span style="font-size:0.78rem;color:var(--text-secondary);">•</span>
                        <span style="font-size:0.78rem;color:${stripColor};font-weight:600;">${priorityName}</span>
                        <span style="font-size:0.78rem;color:var(--text-secondary);">•</span>
                        <span style="font-size:0.78rem;color:var(--text-secondary);">📆 ${act.day_of_april} Abril</span>
                    </div>
                </div>
            </div>
            <button id="close-detail-modal"
                    style="font-size:1.5rem;color:var(--text-secondary);background:none;
                           border:none;cursor:pointer;line-height:1;flex-shrink:0;
                           padding:0.2rem 0.4rem;border-radius:4px;">×</button>
        </div>
        <div style="padding:1.25rem 1.5rem;">
            <div style="margin-bottom:1.125rem;">
                <p style="font-size:0.7rem;font-weight:700;text-transform:uppercase;
                           letter-spacing:0.06em;color:var(--text-secondary);margin-bottom:0.375rem;">
                    Descripción
                </p>
                <p style="font-size:0.875rem;color:var(--text-primary);line-height:1.6;margin:0;">
                    ${act.description || 'Sin descripción'}
                </p>
            </div>
            <div style="margin-bottom:1.25rem;">
                <p style="font-size:0.7rem;font-weight:700;text-transform:uppercase;
                           letter-spacing:0.06em;color:var(--text-secondary);margin-bottom:0.5rem;">
                    Checklist
                    ${totalCnt > 0
                        ? `<span id="checklist-counter" style="font-weight:400;">(${doneCnt}/${totalCnt})</span>`
                        : ''}
                </p>
                <div id="checklist-items-container"></div>
            </div>
            <div style="display:flex;gap:0.5rem;flex-wrap:wrap;">
                <button id="detail-btn-done"
                        style="flex:1;min-width:120px;padding:0.625rem;border-radius:6px;
                               font-weight:500;font-size:0.875rem;border:none;cursor:pointer;
                               background:${act.completed ? '#F59E0B' : '#22C55E'};color:white;">
                    ${act.completed ? '↩ Marcar pendiente' : '✓ Marcar realizada'}
                </button>
                <button id="detail-btn-edit"
                        style="flex:1;min-width:100px;padding:0.625rem;border-radius:6px;
                               font-weight:500;font-size:0.875rem;border:1px solid var(--border);
                               cursor:pointer;background:var(--bg-secondary);color:var(--text-primary);">
                    ✏️ Editar
                </button>
                <button id="detail-btn-delete"
                        style="padding:0.625rem 1rem;border-radius:6px;font-weight:500;
                               font-size:0.875rem;cursor:pointer;
                               border:1px solid rgba(239,68,68,0.3);
                               background:rgba(239,68,68,0.07);color:#EF4444;">
                    🗑️
                </button>
            </div>
        </div>
    `;

    overlay.appendChild(card);
    document.body.appendChild(overlay);

    // ── Construir checklist con createElement (no innerHTML) ──────────────────
    const container = card.querySelector('#checklist-items-container');

    if (!act.checklist || act.checklist.length === 0) {
        const empty = document.createElement('p');
        empty.style.cssText = 'color:var(--text-secondary);font-size:0.82rem;margin:0;';
        empty.textContent = 'Sin ítems en el checklist';
        container.appendChild(empty);
    } else {
        // Copia mutable del checklist para este modal
        let localChecklist = act.checklist.map(i => ({ ...i }));

        localChecklist.forEach((item, idx) => {
            const row = document.createElement('div');
            row.style.cssText = `
                display:flex;align-items:center;gap:0.5rem;
                padding:0.375rem 0;border-bottom:1px solid var(--border);
            `;





            const chk = document.createElement('input');
            chk.type    = 'checkbox';
            chk.checked = item.done;
            chk.style.cssText = 'width:16px;height:16px;cursor:pointer;accent-color:#4F46E5;flex-shrink:0;';

            const lbl = document.createElement('label');
            lbl.textContent = item.text;
            lbl.style.cssText = `
                font-size:0.84rem;cursor:pointer;
                ${item.done ? 'text-decoration:line-through;color:var(--text-secondary);' : 'color:var(--text-primary);'}
            `;

            // Evento de cambio
            chk.addEventListener('change', async () => {
                localChecklist[idx].done = chk.checked;

                // Actualizar estilo del label
                lbl.style.textDecoration = chk.checked ? 'line-through' : 'none';
                lbl.style.color = chk.checked
                    ? 'var(--text-secondary)'
                    : 'var(--text-primary)';

                // Actualizar contador
                const newDone = localChecklist.filter(i => i.done).length;
                const counter = card.querySelector('#checklist-counter');
                if (counter) counter.textContent = `(${newDone}/${localChecklist.length})`;

                try {
                    const updated = await window.updateActivity(act.id, {
                        checklist: localChecklist
                    });
                    // Sincronizar con currentActivities
                    const gIdx = window.currentActivities.findIndex(a => a.id === act.id);
                    if (gIdx !== -1) {
                        window.currentActivities[gIdx] = updated;
                        act.checklist = updated.checklist;
                        localChecklist = updated.checklist.map(i => ({ ...i }));
                    }
                    window.showToast(
                        chk.checked ? '✅ Ítem completado' : '↩ Ítem desmarcado',
                        chk.checked ? 'success' : 'warning'
                    );
                } catch (err) {
                    // Revertir si falla
                    chk.checked = !chk.checked;
                    localChecklist[idx].done = chk.checked;
                    lbl.style.textDecoration = chk.checked ? 'line-through' : 'none';
                    lbl.style.color = chk.checked
                        ? 'var(--text-secondary)'
                        : 'var(--text-primary)';
                    window.showToast('❌ Error al actualizar checklist', 'danger');
                }
            });

            row.appendChild(chk);
            row.appendChild(lbl);
            container.appendChild(row);
        });
    }

    // ── Eventos de botones ────────────────────────────────────────────────────

    // Cerrar al clic en overlay (fuera de la card)
    overlay.addEventListener('click', () => overlay.remove());

    // Cerrar con ×
    card.querySelector('#close-detail-modal').addEventListener('click', () => overlay.remove());

    // Toggle completado
    card.querySelector('#detail-btn-done').addEventListener('click', async () => {
        overlay.remove();
        const updated = await window.updateActivity(act.id, { completed: !act.completed }).catch(() => null);
        if (updated) {
            const idx = window.currentActivities.findIndex(a => a.id === act.id);
            if (idx !== -1) window.currentActivities[idx] = updated;
            const fresh = await window.getAprilActivities();
            window.currentActivities = fresh;
            const dayActs = fresh.filter(a => a.day_of_april === updated.day_of_april);
            window.updateDayCell(updated.day_of_april, dayActs);
            window.openDayModal(updated.day_of_april, dayActs);
            window.showToast(
                updated.completed ? '✅ Marcada como realizada' : '↩ Marcada como pendiente',
                updated.completed ? 'success' : 'warning'
            );
        }
    });

    // Editar
    card.querySelector('#detail-btn-edit').addEventListener('click', () => {
        overlay.remove();
        window.showEditForm(act);
    });

    // Eliminar
    card.querySelector('#detail-btn-delete').addEventListener('click', () => {
        overlay.remove();
        window.deleteActivity(act.id).then(async () => {
            window.currentActivities = window.currentActivities.filter(a => a.id !== act.id);
            const fresh = await window.getAprilActivities();
            window.currentActivities = fresh;
            const dayActs = fresh.filter(a => a.day_of_april === act.day_of_april);
            window.updateDayCell(act.day_of_april, dayActs);
            window.openDayModal(act.day_of_april, dayActs);
            window.showToast('🗑️ Actividad eliminada', 'success');
        }).catch(() => window.showToast('❌ Error al eliminar', 'danger'));
    });

    // Escape
    const escHandler = (e) => {
        if (e.key === 'Escape') {
            overlay.remove();
            document.removeEventListener('keydown', escHandler);
        }
    };
    document.addEventListener('keydown', escHandler);
};

// ── Formulario de creación ────────────────────────────────────────────────────
window.showCreateForm = function(day) {
    const content = document.getElementById('modal-content-list');
    content.innerHTML = `
    <div class="activity-form" id="activity-form">
      <div class="form-group" style="display:flex;gap:1rem;">
        <div style="flex:1;">
            <label class="form-label">Título *</label>
            <input id="f-title" class="form-input" type="text" maxlength="150" placeholder="Nombre de la actividad"/>
            <span class="form-error hidden" id="f-title-err">El título es requerido</span>
        </div>
        <div style="width:100px;">
            <label class="form-label">Hora</label>
            <input id="f-time" class="form-input" type="time"/>
        </div>
      </div>
      <div class="form-group">
        <label class="form-label">Emoji</label>
        <input id="f-emoji" class="form-input" type="text" maxlength="10" placeholder="📅"/>
        <div class="emoji-shortcuts">
          ${['📅','✅','⭐','🔥','📌','🎯','💡','⚠️'].map(e =>
            `<button class="emoji-btn" type="button" onclick="document.getElementById('f-emoji').value='${e}'">${e}</button>`
          ).join('')}
        </div>
      </div>
      <div class="form-group">
        <label class="form-label">Descripción</label>
        <textarea id="f-desc" class="form-textarea" maxlength="500" placeholder="Descripción opcional"></textarea>
      </div>
      <div class="form-group">
        <label class="form-label">Prioridad</label>
        <div class="priority-selector">
          <button class="priority-btn" type="button" data-pid="3" style="border-color:#EF4444">🔴 Alta</button>
          <button class="priority-btn" type="button" data-pid="2" style="border-color:#F59E0B">🟡 Media</button>
          <button class="priority-btn sel" type="button" data-pid="1" style="border-color:#22C55E">🟢 Baja</button>
        </div>
      </div>
      <div class="form-group">
        <label class="form-label">Checklist</label>
        <div class="checklist-input-row">
          <input id="f-check-input" class="form-input" type="text" placeholder="Nuevo ítem"/>
          <button id="f-check-add" type="button" class="btn-small">+ Agregar</button>
        </div>
        <div id="f-checklist" class="checklist-preview"></div>
      </div>
      <div style="display:flex;gap:0.5rem;margin-top:1rem;">
        <button id="f-save" class="btn-primary" type="button">Guardar</button>
        <button class="btn-small" type="button" id="f-cancel">Cancelar</button>
      </div>
    </div>`;

    // Eventos prioridad
    const pBtns = content.querySelectorAll('.priority-btn');
    pBtns.forEach(btn => btn.addEventListener('click', () => {
        pBtns.forEach(b => b.classList.remove('sel'));
        btn.classList.add('sel');
    }));

    // Checklist
    const checkAdd   = content.querySelector('#f-check-add');
    const checkInput = content.querySelector('#f-check-input');
    const checkList  = content.querySelector('#f-checklist');
    checkAdd.addEventListener('click', () => {
        const val = checkInput.value.trim();
        if (!val) return;
        const row = document.createElement('div');
        row.className = 'checklist-item-row';
        row.innerHTML = `<span>${val}</span><button type="button" onclick="this.parentElement.remove()">✕</button>`;
        checkList.appendChild(row);
        checkInput.value = '';
    });

    // Guardar
    content.querySelector('#f-save').addEventListener('click', () => window.submitCreateForm(day));

    // Cancelar
    content.querySelector('#f-cancel').addEventListener('click', () => {
        window.openDayModal(day, window.currentActivities.filter(a => a.day_of_april === day));
    });
};

window.submitCreateForm = async function(day) {
    const title    = document.getElementById('f-title').value.trim();
    const titleErr = document.getElementById('f-title-err');

    if (!title) { titleErr.classList.remove('hidden'); return; }
    titleErr.classList.add('hidden');

    const saveBtn = document.getElementById('f-save');
    saveBtn.textContent = 'Guardando...';
    saveBtn.disabled = true;

    const emoji      = document.getElementById('f-emoji').value.trim();
    const desc       = document.getElementById('f-desc').value.trim();
    const selPriority = document.querySelector('.priority-btn.sel');
    const priorityId  = selPriority ? Number(selPriority.dataset.pid) : 1;
    const timeVal     = document.getElementById('f-time').value || null;
    const checklist   = Array.from(
        document.querySelectorAll('#f-checklist .checklist-item-row span')
    ).map(span => ({ text: span.textContent, done: false }));

    try {
        const newAct = await window.createActivity({ title, day, priority_id: priorityId, time: timeVal, description: desc, emoji, checklist });
        window.currentActivities.push(newAct);
        const dayActs = window.currentActivities.filter(a => a.day_of_april === day);
        window.updateDayCell(day, dayActs);
        window.openDayModal(day, dayActs);
        window.showToast('✅ Actividad creada', 'success');
    } catch (err) {
        saveBtn.textContent = 'Guardar';
        saveBtn.disabled = false;
        window.showToast('❌ ' + (err.message || 'Error al crear'), 'danger');
    }
};

// ── Formulario de edición ─────────────────────────────────────────────────────
window.showEditForm = function(activity) {
    window.showCreateForm(activity.day_of_april);

    document.getElementById('f-title').value = activity.title || '';
    document.getElementById('f-time').value  = activity.time || '';
    document.getElementById('f-emoji').value = activity.emoji || '';
    document.getElementById('f-desc').value  = activity.description || '';

    document.querySelectorAll('.priority-btn').forEach(b => {
        b.classList.toggle('sel', Number(b.dataset.pid) === activity.priority_id);
    });

    const checkList = document.getElementById('f-checklist');
    (activity.checklist || []).forEach(item => {
        const row = document.createElement('div');
        row.className = 'checklist-item-row';
        row.innerHTML = `<span>${item.text}</span><button type="button" onclick="this.parentElement.remove()">✕</button>`;
        checkList.appendChild(row);
    });

    const saveBtn = document.getElementById('f-save');
    saveBtn.textContent = 'Actualizar';
    saveBtn.onclick = () => window.submitUpdateForm(activity.id, activity.day_of_april);
};

window.submitUpdateForm = async function(activityId, day) {
    const title    = document.getElementById('f-title').value.trim();
    const titleErr = document.getElementById('f-title-err');

    if (!title) { titleErr.classList.remove('hidden'); return; }
    titleErr.classList.add('hidden');

    const saveBtn = document.getElementById('f-save');
    saveBtn.textContent = 'Guardando...';
    saveBtn.disabled = true;

    const emoji       = document.getElementById('f-emoji').value.trim();
    const desc        = document.getElementById('f-desc').value.trim();
    const selPriority = document.querySelector('.priority-btn.sel');
    const priorityId  = selPriority ? Number(selPriority.dataset.pid) : 1;
    const timeVal     = document.getElementById('f-time').value || null;
    const checklist   = Array.from(
        document.querySelectorAll('#f-checklist .checklist-item-row span')
    ).map(span => ({ text: span.textContent, done: false }));

    try {
        const updatedAct = await window.updateActivity(activityId, { title, priority_id: priorityId, time: timeVal, description: desc, emoji, checklist });
        const idx = window.currentActivities.findIndex(a => a.id === activityId);
        if (idx !== -1) window.currentActivities[idx] = updatedAct;
        const dayActs = window.currentActivities.filter(a => a.day_of_april === day);
        window.updateDayCell(day, dayActs);
        window.openDayModal(day, dayActs);
        window.showToast('✅ Actividad actualizada', 'success');
    } catch (e) {
        saveBtn.textContent = 'Actualizar';
        saveBtn.disabled = false;
        window.showToast('❌ ' + e.message, 'danger');
    }
};

// ── Confirmación de eliminación ───────────────────────────────────────────────
window.confirmDelete = function(activityId, cardEl) {
    const act = window.currentActivities.find(a => a.id === activityId);
    cardEl.innerHTML = `
      <div class="confirm-delete-box">
        <p>¿Eliminar esta actividad?</p>
        <div style="display:flex;gap:0.5rem;justify-content:center;margin-top:0.75rem;">
          <button class="btn-primary" id="btn-confirm-del"
                  style="background:#EF4444;width:auto;padding:0.4rem 0.875rem;">
            Sí, eliminar
          </button>
          <button class="btn-small" id="btn-cancel-del">Cancelar</button>
        </div>
      </div>`;

    cardEl.querySelector('#btn-confirm-del').addEventListener('click', async () => {
    try {
        await window.deleteActivity(activityId);
        cardEl.remove();
        window.showToast('🗑️ Actividad eliminada', 'success');
        // Recargar desde API y actualizar drawer
        const fresh = await window.getAprilActivities();
        window.currentActivities = fresh;
        if (act) {
            const dayActs = fresh.filter(a => a.day_of_april === act.day_of_april);
            window.updateDayCell(act.day_of_april, dayActs);
            // Reabrir el drawer con datos frescos
            window.openDayModal(act.day_of_april, dayActs);
        }
    } catch (e) {
        window.showToast('❌ Error al eliminar', 'danger');
        if (act) {
            const newCard = window.renderActivityCard(act);
            cardEl.replaceWith(newCard);
        }
    }
});   

    cardEl.querySelector('#btn-cancel-del').addEventListener('click', () => {
        if (act) {
            const newCard = window.renderActivityCard(act);
            cardEl.replaceWith(newCard);
        }
    });
};

// ── Actualizar chips del día en el calendario ─────────────────────────────────
window.updateDayCell = function(day, activities) {
    const cell = document.querySelector(`.day-cell[data-day="${day}"]`);
    if (!cell) return;

    Array.from(cell.children).forEach(child => {
        if (!child.classList.contains('day-number')) child.remove();
    });
    cell.classList.remove('has-high-priority');

    let hasHighPriority = false;
    const MAX_VISIBLE_CHIPS = 3;

    activities.slice(0, MAX_VISIBLE_CHIPS).forEach(act => {
        if (act.priority_id === 3) hasHighPriority = true;
        cell.appendChild(window.renderActivityChip(act));
    });

    if (activities.length > MAX_VISIBLE_CHIPS) {
        const more = document.createElement('div');
        more.className = 'chip-more';
        more.textContent = `+${activities.length - MAX_VISIBLE_CHIPS} más`;
        cell.appendChild(more);
        if (activities.some(a => a.priority_id === 3)) hasHighPriority = true;
    }

    if (hasHighPriority) cell.classList.add('has-high-priority');
};
