document.addEventListener("DOMContentLoaded", function () {
    
    // --- CONTROL DEL MODAL DE EDICIÓN ---
    const modalEditRol = document.getElementById('modalEditRol');
    if (modalEditRol) {
        modalEditRol.addEventListener('show.bs.modal', function (event) {
            // El elemento 'relatedTarget' es el botón exacto que se presionó
            const button = event.relatedTarget;
            
            // Extracción segura de los atributos data- del HTML
            const idRol = button.getAttribute('data-id') || '';
            const nombreRol = button.getAttribute('data-nombre') || '';
            
            // Inyección de los datos dentro de los inputs del modal
            document.getElementById('edit_id_rol').value = idRol;
            document.getElementById('edit_nombre_rol').value = nombreRol;
        });
    }

    // --- CONTROL DEL MODAL DE ELIMINACIÓN ---
    const modalDeleteRol = document.getElementById('modalDeleteRol');
    if (modalDeleteRol) {
        modalDeleteRol.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            
            const idRol = button.getAttribute('data-id') || '';
            const nombreRol = button.getAttribute('data-nombre') || '';
            
            document.getElementById('delete_id_rol').value = idRol;
            document.getElementById('delete_nombre_rol').textContent = nombreRol;
        });
    }
});