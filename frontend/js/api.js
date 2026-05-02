/**
 * Capa de Comunicación con el API (SGAC)
 * Maneja la autenticación, el token en memoria y las peticiones al backend.
 */
console.log(">>> api.js cargando... <<<");

const API_BASE = "";
let memToken = sessionStorage.getItem('sgac_token');
let inactivityTimer = null;
const INACTIVITY_TIMEOUT = 60000; // 1 minuto (según requerimiento)

// Resetea el temporizador de inactividad
function resetInactivityTimer() {
    if (inactivityTimer) clearTimeout(inactivityTimer);
    if (memToken) {
        inactivityTimer = setTimeout(() => {
            console.warn("Sesión expirada por inactividad");
            window.logout();
        }, INACTIVITY_TIMEOUT);
    }
}

// Escuchar eventos globales para resetear el timer de actividad
['click', 'keydown', 'mousemove', 'scroll', 'touchstart'].forEach(evt => {
    document.addEventListener(evt, resetInactivityTimer, { passive: true });
});

/**
 * Wrapper genérico para peticiones al API con manejo de JWT
 */
async function apiFetch(endpoint, options = {}) {
    const headers = { ...options.headers };
    
    if (memToken) {
        headers['Authorization'] = `Bearer ${memToken}`;
    }
    
    // Si no es un FormData (subida de archivos), agregamos Content-Type JSON
    if (!(options.body instanceof FormData) && !headers['Content-Type']) {
        headers['Content-Type'] = 'application/json';
    }

    try {
        const res = await fetch(`${API_BASE}${endpoint}`, { ...options, headers });
        
        if (res.status === 401) {
            // Token inválido o expirado
            window.logout();
            throw new Error("No autorizado");
        }
        
        return res;
    } catch (err) {
        console.error("Error en apiFetch:", err);
        throw err;
    }
}

/**
 * Inicia sesión en el sistema
 */
window.login = async function(rut, password) {
    try {
        const res = await apiFetch('/api/auth/login', {
            method: 'POST',
            body: JSON.stringify({ rut, password })
        });
        
        if (res.ok) {
            const data = await res.json();
            memToken = data.access_token;
            sessionStorage.setItem('sgac_token', memToken);
            sessionStorage.setItem('sgac_role', data.role);
            sessionStorage.setItem('sgac_name', data.full_name);
            resetInactivityTimer();
            // Redirigir al calendario principal
            window.location.href = "/";
        } else {
            const errorData = await res.text();
            console.error("Error del servidor:", errorData);
            alert("Error al iniciar sesión: " + errorData);
            if (window.triggerLoginError) window.triggerLoginError();
        }
    } catch (error) {
        console.error("Excepción en login:", error);
        alert("No se pudo conectar con el servidor: " + error.message);
        if (window.triggerLoginError) window.triggerLoginError();
    }
};

/**
 * Cierra la sesión activa
 */
window.logout = async function() {
    if (memToken) {
        try {
            await apiFetch('/api/auth/logout', { method: 'POST' });
        } catch (e) {
            // Ignoramos errores de red durante el logout
        }
    }
    memToken = null;
    sessionStorage.removeItem('sgac_token');
    sessionStorage.removeItem('sgac_role');
    sessionStorage.removeItem('sgac_name');
    if (inactivityTimer) clearTimeout(inactivityTimer);
    
    // Redirigir a login si no estamos ahí
    if (!window.location.pathname.endsWith('login.html')) {
        window.location.href = "/frontend/login.html";
    }
};

/**
 * Obtiene todas las actividades del mes (Abril)
 */
window.getAprilActivities = async function() {
    const res = await apiFetch('/api/activities/');
    if (res.ok) return await res.json();
    return [];
};

/**
 * Obtiene las actividades de un día específico (1-30)
 */
window.getActivitiesByDay = async function(day) {
    const activities = await window.getAprilActivities();
    return activities.filter(a => a.day_of_april === Number(day));
};

/**
 * Filtra las actividades por ID de prioridad
 */
window.filterByPriority = async function(priorityId) {
    const activities = await window.getAprilActivities();
    return activities.filter(a => a.priority_id == priorityId);
};

/**
 * Crea una nueva actividad
 */
window.createActivity = async function(data) {
    const res = await apiFetch('/api/activities/', {
        method: 'POST',
        body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error("Error creando actividad");
    return await res.json();
};

/**
 * Actualiza una actividad existente
 */
window.updateActivity = async function(id, data) {
    const res = await apiFetch(`/api/activities/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error("Error actualizando actividad");
    return await res.json();
};

/**
 * Elimina una actividad
 */
window.deleteActivity = async function(id) {
    const res = await apiFetch(`/api/activities/${id}`, {
        method: 'DELETE'
    });
    if (!res.ok) throw new Error("Error eliminando actividad");
    return true;
};

/**
 * Sube una imagen asociada a una actividad
 */
window.uploadImage = async function(id, file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const res = await apiFetch(`/api/activities/${id}/image`, {
        method: 'POST',
        body: formData
    });
    if (!res.ok) throw new Error("Error subiendo imagen");
    return await res.json();
};
