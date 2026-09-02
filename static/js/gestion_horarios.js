/* ============================================================================
   GESTIÓN DE HORARIOS - JavaScript
   ============================================================================ */

document.addEventListener('DOMContentLoaded', function() {
    initializeEditModal();
    initializeDeleteModal();
});

/**
 * Transferencia de datos al modal de edición
 */
function initializeEditModal() {
    const modalEditHorario = document.getElementById('modalEditHorario');
    
    if (modalEditHorario) {
        modalEditHorario.addEventListener('show.bs.modal', function(event) {
            const button = event.relatedTarget;

            const idHorario = button.getAttribute('data-id');
            const idMaestro = button.getAttribute('data-maestro');
            const idMateria = button.getAttribute('data-materia');
            const dia = button.getAttribute('data-dia');
            const inicio = button.getAttribute('data-inicio');
            const fin = button.getAttribute('data-fin');
            const aula = button.getAttribute('data-aula');

            // Inyectar valores en los campos del formulario
            document.getElementById('edit_id_horario').value = idHorario;
            document.getElementById('edit_maestro').value = idMaestro;
            document.getElementById('edit_materia').value = idMateria;
            document.getElementById('edit_dia').value = dia;
            document.getElementById('edit_inicio').value = inicio;
            document.getElementById('edit_fin').value = fin;
            document.getElementById('edit_aula').value = aula;
        });
    }
}

/**
 * Transferencia de datos al modal de eliminación
 */
function initializeDeleteModal() {
    const modalDeleteHorario = document.getElementById('modalDeleteHorario');
    
    if (modalDeleteHorario) {
        modalDeleteHorario.addEventListener('show.bs.modal', function(event) {
            const button = event.relatedTarget;

            const idHorario = button.getAttribute('data-id');
            const materia = button.getAttribute('data-materia');

            document.getElementById('delete_id_horario').value = idHorario;
            document.getElementById('delete_materia').textContent = materia;
        });
    }
}

/**
 * Validación de horarios en tiempo real (opcional)
 */
function validarHorarios() {
    const horaInicio = document.querySelector('input[name="hora_inicio"]');
    const horaFin = document.querySelector('input[name="hora_fin"]');

    if (horaInicio && horaFin) {
        horaFin.addEventListener('change', function() {
            if (this.value <= horaInicio.value) {
                alert('La hora de fin debe ser posterior a la hora de inicio');
                this.value = '';
            }
        });
    }
}

// Ejecutar validación
validarHorarios();

/**
 * Log de eventos para depuración
 */
console.log('✓ Script de Gestión de Horarios cargado correctamente');