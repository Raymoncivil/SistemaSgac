// Estado de la aplicación
let currentUser = null;
let activities = [];
let token = null;
let logoutTimer = null;
const INACTIVITY_TIMEOUT_MS = 60 * 1000;

// API base URL
const API_BASE = window.location.origin;

// Elementos DOM (se asignan en DOMContentLoaded)
let calendarEl = null;
let loginModal = null;
let activityModal = null;
let priorityPopup = null;
let loginBtn = null;
let logoutBtn = null;

// Inicializar aplicación
document.addEventListener('DOMContentLoaded', () => {
    // Re-consultar elementos del DOM ahora que el documento está cargado
    calendarEl = document.getElementById('calendar');
    loginModal = document.getElementById('login-modal');
    activityModal = document.getElementById('activity-modal');
    priorityPopup = document.getElementById('priority-popup');
    loginBtn = document.getElementById('login-btn');
    logoutBtn = document.getElementById('logout-btn');

    console.log('[app] DOM cargado, elementos:', {
        loginBtn: !!loginBtn,
        loginModal: !!loginModal,
        calendarEl: !!calendarEl
    });

    renderCalendar();
    setupEventListeners();
});

// Configurar event listeners
function setupEventListeners() {
    if (loginBtn && loginModal) {
        loginBtn.addEventListener('click', (e) => {
            console.log('[app] Click en loginBtn', e);
            try {
                // Intentar mostrar modal por inline style
                loginModal.style.display = 'block';
                // También eliminar clase hidden por si la prioridad CSS la oculta
                loginModal.classList.remove('hidden');
            } catch (err) {
                console.error('[app] Error mostrando loginModal:', err);
            }
        });
    }
    if (logoutBtn) {
        logoutBtn.addEventListener('click', logout);
    }

    document.querySelectorAll('.close').forEach(close => {
        close.addEventListener('click', (e) => {
            const modal = e.target.closest('.modal');
            if (modal) modal.style.display = 'none';
        });
    });

    const loginForm = document.getElementById('login-form');
    if (loginForm) loginForm.addEventListener('submit', handleLogin);

    const activityForm = document.getElementById('activity-form');
    if (activityForm) activityForm.addEventListener('submit', handleActivitySubmit);

    // Click en días para crear actividad
    if (calendarEl) {
        calendarEl.addEventListener('click', (e) => {
            if (e.target.classList.contains('day') && !e.target.classList.contains('day-header')) {
                const date = e.target.dataset.date;
                openActivityModal(date);
            }
        });
    }
}

async function authorizedFetch(url, options = {}) {
    const mergedOptions = {
        ...options,
        headers: {
            ...(options.headers || {}),
            'Authorization': `Bearer ${token}`
        }
    };

    const response = await fetch(url, mergedOptions);
    if (response.status === 401) {
        alert('Tu sesión expiró. Vuelve a iniciar sesión.');
        logout();
        return null;
    }

    return response;
}

// Renderizar calendario
function renderCalendar() {
    const daysOfWeek = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'];
    const month = 3; // Abril (0-indexed)
    const year = 2026;
    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = 30;
    
    calendarEl.innerHTML = '';
    
    // Headers de días
    daysOfWeek.forEach(day => {
        const header = document.createElement('div');
        header.className = 'day day-header';
        header.textContent = day;
        calendarEl.appendChild(header);
    });
    
    // Días vacíos antes del 1
    for (let i = 0; i < firstDay; i++) {
        const emptyDay = document.createElement('div');
        emptyDay.className = 'day';
        calendarEl.appendChild(emptyDay);
    }
    
    // Días del mes
    for (let day = 1; day <= daysInMonth; day++) {
        const dayEl = document.createElement('div');
        dayEl.className = 'day';
        const dateStr = `${year}-${String(month+1).padStart(2,'0')}-${String(day).padStart(2,'0')}`;
        dayEl.dataset.date = dateStr;
        dayEl.innerHTML = `<div class="day-num">${day}</div>`;
        
        // Agregar actividades del día
        const dayActivities = activities.filter(a => a.date === dateStr);
        dayActivities.forEach(activity => {
            const activityEl = document.createElement('div');
            const priorityClass = getPriorityClass(activity.priority_id);
            activityEl.className = `activity ${priorityClass}`;
            activityEl.innerHTML = `<span title="${activity.title}">📌 ${activity.title}</span>`;
            activityEl.addEventListener('click', (e) => {
                e.stopPropagation();
                showActivityDetails(activity);
            });
            dayEl.appendChild(activityEl);
        });
        
        calendarEl.appendChild(dayEl);
    }
}

// Mostrar detalles de actividad
function showActivityDetails(activity) {
    alert(`Actividad: ${activity.title}\nFecha: ${activity.date}\nDescripción: ${activity.description || 'N/A'}\nChecklist: ${activity.checklist ? activity.checklist.length + ' items' : '0 items'}`);
}

// Manejar login
async function handleLogin(e) {
    e.preventDefault();
    const rut = document.getElementById('rut').value;
    const password = document.getElementById('password').value;
    console.log('[app] handleLogin called', { rutProvided: !!rut });

    try {
        const response = await fetch(`${API_BASE}/api/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ rut, password })
        });

        if (response.ok) {
            const data = await response.json();
            token = data.access_token;
            currentUser = {
                id: data.user_id,
                role: data.role,
                rut: data.rut,
                name: data.full_name
            };
            showLoggedInState();
            if (loginModal) loginModal.style.display = 'none';
            startLogoutTimer();
            loadActivities();
            const lf = document.getElementById('login-form'); if (lf) lf.reset();
        } else {
            const text = await response.text().catch(() => null);
            console.warn('[app] login failed, status=', response.status, text);
            alert('Credenciales inválidas o error del servidor.');
        }
    } catch (error) {
        console.error('[app] Error en login:', error);
        alert(`No se pudo conectar al servidor. Asegura que la API esté corriendo en ${API_BASE}`);
    }
}

// Cargar actividades
async function loadActivities() {
    try {
        const response = await authorizedFetch(`${API_BASE}/api/activities/`);
        if (!response) {
            return;
        }

        if (response.ok) {
            const data = await response.json();
            activities = (data || []).map((activity) => {
                const day = String(activity.day_of_april).padStart(2, '0');
                return { ...activity, date: `2026-04-${day}` };
            });
            renderCalendar();
            showPriorityPopup();
        }
    } catch (error) {
        console.error('Error cargando actividades:', error);
    }
}

// Manejar submit de actividad
async function handleActivitySubmit(e) {
    e.preventDefault();
    const title = document.getElementById('title').value;
    const description = document.getElementById('description').value;
    const dateStr = document.getElementById('date').value;
    const priorityId = document.getElementById('priority').value || null;
    const checklist = [];
    
    // Opciones de checklist (simuladas)
    const checklistInputs = document.querySelectorAll('.checklist-item');
    checklistInputs.forEach(input => {
        if (input.value) {
            checklist.push({ text: input.value, done: false });
        }
    });
    
    try {
        const response = await authorizedFetch(`${API_BASE}/api/activities/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                title: `📌 ${title}`,
                description,
                day_of_april: Number(dateStr.split('-')[2]),
                priority_id: priorityId,
                checklist: checklist.length > 0 ? checklist : null
            })
        });

        if (!response) {
            return;
        }

        if (response.ok) {
            loadActivities();
            activityModal.style.display = 'none';
            document.getElementById('activity-form').reset();
        }
    } catch (error) {
        console.error('Error creando actividad:', error);
    }
}

// Abrir modal de actividad
function openActivityModal(date) {
    if (!currentUser) {
        alert('Debes iniciar sesión');
        return;
    }
    document.getElementById('date').value = date;
    document.getElementById('modal-title').textContent = `Nueva Actividad - ${date}`;
    activityModal.style.display = 'block';
}

// Mostrar popup de prioridades
function showPriorityPopup() {
    const priorityActivities = activities.filter(a => a.priority_id);
    if (priorityActivities.length > 0) {
        const list = document.getElementById('priority-list');
        list.innerHTML = '';
        priorityActivities.forEach(activity => {
            const li = document.createElement('li');
            const priority = {1: '🔴 Alta', 2: '🟡 Media', 3: '🟢 Baja'};
            li.textContent = `${priority[activity.priority_id] || 'N/A'}: ${activity.title} (${activity.date})`;
            list.appendChild(li);
        });
        priorityPopup.style.display = 'block';
        // Notificación sonora simulada
        playNotificationSound();
    }
}

// Reproducir notificación sonora
function playNotificationSound() {
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const gain = audioContext.createGain();
    oscillator.connect(gain);
    gain.connect(audioContext.destination);
    
    oscillator.frequency.value = 800;
    oscillator.type = 'sine';
    gain.gain.setValueAtTime(0.3, audioContext.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
    
    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + 0.5);
}

// Logout automático (1 minuto) por inactividad
function startLogoutTimer() {
    clearTimeout(logoutTimer);
    logoutTimer = setTimeout(() => {
        alert('Sesión expirada. Debes iniciar sesión nuevamente.');
        logout();
    }, INACTIVITY_TIMEOUT_MS);
}

// Logout
function logout() {
    if (token) {
        fetch(`${API_BASE}/api/auth/logout`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` }
        }).catch(() => null);
    }
    currentUser = null;
    activities = [];
    token = null;
    showLoggedOutState();
    renderCalendar();
    clearTimeout(logoutTimer);
}

// Estados de UI
function showLoggedInState() {
    loginBtn.style.display = 'none';
    logoutBtn.style.display = 'block';
}

function showLoggedOutState() {
    loginBtn.style.display = 'block';
    logoutBtn.style.display = 'none';
}

// Reiniciar timeout con actividad del usuario (en memoria)
["click", "keydown", "mousemove", "scroll"].forEach((eventName) => {
    document.addEventListener(eventName, () => {
        if (token) startLogoutTimer();
    });
});

// Utilidad para clase de prioridad
function getPriorityClass(priorityId) {
    const classes = { 1: 'priority-high', 2: 'priority-medium', 3: 'priority-low' };
    return classes[priorityId] || '';
}