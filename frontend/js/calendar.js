/**
 * Lógica del Calendario de SGAC (Abril 2026)
 */

// Variables globales para el estado del calendario
let currentActivities = [];
let countdownInterval = null;

/**
 * Renderiza la cuadrícula de los 30 días de Abril
 */
window.renderCalendar = function(activities) {
    currentActivities = activities;
    const grid = document.getElementById('calendar-grid');
    if (!grid) return;
    
    grid.innerHTML = '';
    
    // Encabezados de días
    const daysOfWeek = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'];
    daysOfWeek.forEach(d => {
        const header = document.createElement('div');
        header.className = 'day-header';
        header.textContent = d;
        grid.appendChild(header);
    });

    // Abril 2026 empieza en Miércoles (índice 3: Dom=0, Lun=1, Mar=2, Mié=3)
    const firstDayIndex = 3;
    const totalDays = 30;
    
    // Días vacíos iniciales para desplazar la cuadrícula
    for (let i = 0; i < firstDayIndex; i++) {
        const emptyCell = document.createElement('div');
        emptyCell.className = 'day-cell empty';
        grid.appendChild(emptyCell);
    }

    // Día actual (para resaltar si estamos en Abril 2026)
    const today = new Date();
    const isApril2026 = today.getFullYear() === 2026 && today.getMonth() === 3;
    const currentDay = isApril2026 ? today.getDate() : null;

    // Celdas iterativas de Abril (1 al 30)
    for (let day = 1; day <= totalDays; day++) {
        const cell = document.createElement('div');
        cell.className = 'day-cell';
        if (day === currentDay) cell.classList.add('today');
        
        // Atributo auxiliar para la vista móvil responsive
        cell.dataset.dayName = daysOfWeek[(firstDayIndex + day - 1) % 7];
        
        const num = document.createElement('span');
        num.className = 'day-number';
        num.textContent = day;
        cell.appendChild(num);

        // Filtrar actividades de este día
        const dayActivities = activities.filter(a => a.day_of_april === day);
        let hasHighPriority = false;

        // Renderizar pastillas visuales de actividades
        dayActivities.forEach(act => {
            if (act.priority_id === 1) hasHighPriority = true;
            cell.appendChild(window.renderActivityChip(act));
        });

        // Indicador visual de urgencia
        if (hasHighPriority) {
            const indicator = document.createElement('div');
            indicator.className = 'indicator-high';
            cell.appendChild(indicator);
        }

        cell.addEventListener('click', () => window.openDayModal(day, dayActivities));
        grid.appendChild(cell);
    }
};

/**
 * Crea un chip visual para una actividad con su estado de prioridad
 */
window.renderActivityChip = function(activity) {
    const chip = document.createElement('div');
    let pClass = 'chip-low';
    let emoji = '🟢';
    
    if (activity.priority_id === 1) { pClass = 'chip-high'; emoji = '🔴'; }
    else if (activity.priority_id === 2) { pClass = 'chip-med'; emoji = '🟡'; }

    // Si tiene checklist y está todo completado, el emoji cambia
    const allDone = activity.checklist && activity.checklist.length > 0 && activity.checklist.every(item => item.done);
    if (allDone) emoji = '✅';

    chip.className = `activity-chip ${pClass}`;
    chip.innerHTML = `<span>${emoji}</span> <span>${activity.title}</span>`;
    return chip;
};

/**
 * Abre el panel asimétrico lateral (Glassmorfismo) para ver/editar actividades
 */
window.openDayModal = function(day, dayActivities) {
    const overlay = document.getElementById('modal-overlay');
    const content = document.getElementById('modal-content-list');
    const title = document.getElementById('modal-day-title');
    if (!overlay || !content || !title) return;

    title.textContent = `Actividades del ${day} de Abril`;
    content.innerHTML = '';

    if (dayActivities.length === 0) {
        content.innerHTML = '<p class="text-muted" style="margin-top: 1rem;">No hay actividades para este día. Haz clic en "+" para crear una.</p>';
    } else {
        dayActivities.forEach(act => {
            const div = document.createElement('div');
            div.style.padding = '1rem';
            div.style.border = '1px solid var(--border-color)';
            div.style.borderRadius = 'var(--radius-sm)';
            div.style.marginTop = '1rem';
            div.innerHTML = `<h4 style="margin-bottom:0.5rem; color:var(--text-main);">${act.title}</h4>
                             <p style="font-size:0.9rem; color:var(--text-muted);">${act.description || 'Sin descripción detallada.'}</p>`;
            content.appendChild(div);
        });
    }

    // Activa la animación del modal
    overlay.classList.add('active');
};

/**
 * Cierra el modal lateral
 */
window.closeModal = function() {
    const overlay = document.getElementById('modal-overlay');
    if (overlay) overlay.classList.remove('active');
};

/**
 * Inicializa los chips de filtro por prioridad en el header
 */
window.initPriorityFilter = function() {
    const chips = document.querySelectorAll('.filter-chip');
    chips.forEach(chip => {
        chip.addEventListener('click', async (e) => {
            // Manejar clase active visual
            chips.forEach(c => c.classList.remove('active'));
            e.target.classList.add('active');
            
            // Invocar funciones de api.js para filtrar
            const priority = e.target.dataset.priority;
            let filtered = [];
            if (priority === 'all') {
                filtered = await window.getAprilActivities();
            } else {
                filtered = await window.filterByPriority(priority);
            }
            window.renderCalendar(filtered);
        });
    });
};

/**
 * Busca la próxima actividad con hora y arranca una cuenta regresiva visual
 */
window.startCountdown = function(activities) {
    const banner = document.getElementById('countdown-banner');
    if (!banner) return;
    
    if (countdownInterval) clearInterval(countdownInterval);

    const now = new Date();
    let nextActivity = null;
    let minDiff = Infinity;

    // Busca la actividad más cercana en el futuro que posea un campo "time"
    activities.forEach(act => {
        if (act.time) {
            const [hours, minutes] = act.time.split(':');
            const actDate = new Date(2026, 3, act.day_of_april, hours, minutes);
            const diff = actDate - now;
            if (diff > 0 && diff < minDiff) {
                minDiff = diff;
                nextActivity = { ...act, actDate };
            }
        }
    });

    if (!nextActivity) {
        banner.classList.add('hidden');
        return;
    }

    banner.classList.remove('hidden');
    
    countdownInterval = setInterval(() => {
        const currentTime = new Date();
        const diff = nextActivity.actDate - currentTime;
        
        if (diff <= 0) {
            clearInterval(countdownInterval);
            banner.textContent = `¡Es hora de: ${nextActivity.title}!`;
            return;
        }

        const h = Math.floor((diff / (1000 * 60 * 60)) % 24);
        const m = Math.floor((diff / 1000 / 60) % 60);
        const s = Math.floor((diff / 1000) % 60);

        banner.textContent = `⏳ Próxima actividad en ${h}h ${m}m ${s}s: ${nextActivity.title}`;
    }, 1000);
};

/**
 * Muestra popup automático al cargar si hay una actividad Alta hoy
 */
window.showDailyPopup = function(activities) {
    const today = new Date();
    // Validamos que estemos en Abril 2026
    if (today.getFullYear() !== 2026 || today.getMonth() !== 3) return;
    
    const currentDay = today.getDate();
    const highPriorityToday = activities.find(a => a.day_of_april === currentDay && a.priority_id === 1);
    
    // Si notifications.js ya está cargado y tenemos un toast
    if (highPriorityToday && window.showToast) {
        window.showToast(`📌 Destacada de hoy: ${highPriorityToday.title}`, 'danger');
    }
};
