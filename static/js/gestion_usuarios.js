// --- TRANSFERENCIA DE DATOS AL MODAL DE EDICIÓN ---
const modalEditUser = document.getElementById('modalEditUser');
if (modalEditUser) {
    modalEditUser.addEventListener('show.bs.modal', function (event) {
        const button = event.relatedTarget;

        const idUsuario = button.getAttribute('data-id');
        const idPersona = button.getAttribute('data-persona');
        const nombrePersona = button.getAttribute('data-nombre-persona'); // Captura el nombre
        const idRol = button.getAttribute('data-rol');
        const username = button.getAttribute('data-username');

        document.getElementById('edit_id_usuario').value = idUsuario;
        document.getElementById('edit_id_role').value = idRol;
        document.getElementById('edit_username').value = username;

        // Pasa el ID al input oculto (para que tu Python no cambie nada)
        document.getElementById('edit_id_persona').value = idPersona;

        // Pasa el Nombre al input visible
        document.getElementById('edit_persona_nombre').value = nombrePersona;
    });
}

// --- TRANSFERENCIA DE DATOS AL MODAL DE ELIMINACIÓN LÓGICA ---
const modalSoftDelete = document.getElementById('modalSoftDelete');
if (modalSoftDelete) {
    modalSoftDelete.addEventListener('show.bs.modal', function (event) {
        const button = event.relatedTarget;

        const idUsuario = button.getAttribute('data-id');
        const username = button.getAttribute('data-username');

        document.getElementById('soft_id_usuario').value = idUsuario;
        document.getElementById('soft_username').textContent = username;
    });
}

// --- TRANSFERENCIA DE DATOS AL MODAL DE ELIMINACIÓN PERMANENTE (DE RAÍZ) ---
const modalHardDelete = document.getElementById('modalHardDelete');
if (modalHardDelete) {
    modalHardDelete.addEventListener('show.bs.modal', function (event) {
        const button = event.relatedTarget;

        // Captura el ID y username del botón rojo/tacho de basura
        const idUsuario = button.getAttribute('data-id');
        const username = button.getAttribute('data-username');

        // Inyecta los valores en los elementos específicos del modal "Hard"
        document.getElementById('hard_id_usuario').value = idUsuario;
        document.getElementById('hard_username').textContent = username;
    });
}