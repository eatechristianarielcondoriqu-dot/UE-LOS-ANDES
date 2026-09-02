/* ============================================================================
   REPORTES DE ASISTENCIA - JavaScript
   ============================================================================ */

document.addEventListener('DOMContentLoaded', function() {
    initializeEditModal();
    initializeDeleteModal();
    updateDateTime();
    setInterval(updateDateTime, 1000);
});

/**
 * Actualizar fecha y hora en tiempo real
 */
function updateDateTime() {
    const now = new Date();
    
    const dateOptions = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    const timeOptions = { hour: '2-digit', minute: '2-digit', second: '2-digit' };
    
    const dateStr = now.toLocaleDateString('es-ES', dateOptions);
    const timeStr = now.toLocaleTimeString('es-ES', timeOptions);
    
    const dateElement = document.getElementById('current-date');
    const timeElement = document.getElementById('current-time');
    
    if (dateElement) {
        dateElement.textContent = dateStr.charAt(0).toUpperCase() + dateStr.slice(1);
    }
    if (timeElement) {
        timeElement.textContent = timeStr;
    }
}

/**
 * Transferencia de datos al modal de edición
 */
function initializeEditModal() {
    const modalEditAsistencia = document.getElementById('modalEditAsistencia');
    
    if (modalEditAsistencia) {
        modalEditAsistencia.addEventListener('show.bs.modal', function(event) {
            const button = event.relatedTarget;

            const idAsistencia = button.getAttribute('data-id');
            const estado = button.getAttribute('data-estado');

            // Inyectar valores
            document.getElementById('edit_id_asistencia').value = idAsistencia;
            document.getElementById('edit_estado').value = estado;
        });
    }
}

/**
 * Transferencia de datos al modal de eliminación
 */
function initializeDeleteModal() {
    const modalDeleteAsistencia = document.getElementById('modalDeleteAsistencia');
    
    if (modalDeleteAsistencia) {
        modalDeleteAsistencia.addEventListener('show.bs.modal', function(event) {
            const button = event.relatedTarget;

            const idAsistencia = button.getAttribute('data-id');

            document.getElementById('delete_id_asistencia').value = idAsistencia;
        });
    }
}

/**
 * Log de eventos para depuración
 */
console.log('✓ Script de Reportes de Asistencia cargado correctamente');