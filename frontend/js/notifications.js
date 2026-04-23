/**
 * Sistema de Notificaciones y Alertas (SGAC)
 */

let pollingInterval = null;
// Mantiene registro de actividades ya alertadas para no spamear el sonido
let alertedActivities = new Set(); 

/**
 * Muestra una notificación visual en pantalla (Toast)
 * @param {string} message - El mensaje a mostrar
 * @param {string} type - 'success', 'warning', o 'danger'
 */
window.showToast = function(message, type = 'success') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    // Icono basado en el tipo
    let icon = '✅';
    if (type === 'danger') icon = '🔴';
    if (type === 'warning') icon = '⚠️';

    toast.innerHTML = `<span>${icon}</span> <span>${message}</span>`;
    
    container.appendChild(toast);

    // Auto-eliminar después de 4 segundos
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(100%)';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
};

/**
 * Genera un tono de alerta moderno usando Web Audio API nativo
 */
window.playAlertSound = function() {
    try {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        if (!AudioContext) return;
        
        const ctx = new AudioContext();
        
        // Oscilador 1: Tono principal (curva descendente)
        const osc1 = ctx.createOscillator();
        const gain1 = ctx.createGain();
        
        osc1.type = 'sine';
        osc1.frequency.setValueAtTime(880, ctx.currentTime); // A5
        osc1.frequency.exponentialRampToValueAtTime(440, ctx.currentTime + 0.1); // Baja a A4
        
        gain1.gain.setValueAtTime(0, ctx.currentTime);
        gain1.gain.linearRampToValueAtTime(0.5, ctx.currentTime + 0.05);
        gain1.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.5);
        
        osc1.connect(gain1);
        gain1.connect(ctx.destination);
        
        osc1.start(ctx.currentTime);
        osc1.stop(ctx.currentTime + 0.5);

        // Oscilador 2: Armónico corto
        const osc2 = ctx.createOscillator();
        const gain2 = ctx.createGain();
        
        osc2.type = 'triangle';
        osc2.frequency.setValueAtTime(1320, ctx.currentTime + 0.1); // E6
        
        gain2.gain.setValueAtTime(0, ctx.currentTime + 0.1);
        gain2.gain.linearRampToValueAtTime(0.3, ctx.currentTime + 0.15);
        gain2.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.3);
        
        osc2.connect(gain2);
        gain2.connect(ctx.destination);
        
        osc2.start(ctx.currentTime + 0.1);
        osc2.stop(ctx.currentTime + 0.4);

    } catch (e) {
        console.warn("Web Audio API no soportado o bloqueado por interacción del usuario", e);
    }
};

/**
 * Compara hora actual con hora de cada actividad y alerta si faltan <= 60 mins
 */
window.checkHourlyAlerts = function(activities) {
    if (!activities || activities.length === 0) return;

    const now = new Date();
    // Validar mes y año: Abril 2026
    if (now.getFullYear() !== 2026 || now.getMonth() !== 3) return;

    const currentDay = now.getDate();

    activities.forEach(act => {
        // Solo alertamos actividades del día actual que tengan un campo 'time'
        if (act.day_of_april === currentDay && act.time) {
            const [hours, minutes] = act.time.split(':');
            const actDate = new Date(2026, 3, currentDay, hours, minutes);
            
            // Diferencia en milisegundos y minutos
            const diffMs = actDate - now;
            const diffMins = Math.floor(diffMs / 60000);

            // Si faltan entre 0 y 60 minutos, y no hemos alertado aún
            if (diffMins > 0 && diffMins <= 60 && !alertedActivities.has(act.id)) {
                alertedActivities.add(act.id);
                window.playAlertSound();
                window.showToast(`Faltan ${diffMins} min para: ${act.title}`, 'warning');
            }
        }
    });
};

/**
 * Inicia el polling cada 60 segundos para re-verificar alertas
 * @param {Function} getActivitiesCallback - Promesa que devuelve las actividades actualizadas
 */
window.startNotificationPolling = function(getActivitiesCallback) {
    if (pollingInterval) clearInterval(pollingInterval);
    
    // Polling interval: 60,000 ms (60 segundos)
    pollingInterval = setInterval(async () => {
        try {
            // Obtenemos actividades frescas
            const activities = await getActivitiesCallback();
            window.checkHourlyAlerts(activities);
        } catch (e) {
            console.error("Error en polling de notificaciones", e);
        }
    }, 60000);
};
