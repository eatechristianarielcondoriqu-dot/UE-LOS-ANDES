document.addEventListener("DOMContentLoaded", function() {
            const modalDel = new bootstrap.Modal(document.getElementById('modalConfirmarAccion'));
            const inputAction = document.getElementById('inputAction');
            const inputTarget = document.getElementById('inputTarget');
            const textInfo = document.getElementById('textInfo');
            const textLabel = document.getElementById('textLabel');

            // Quitar asignación de la matriz usando la equis (btn-del-malla)
            document.querySelectorAll('.btn-del-malla').forEach(b => {
                b.addEventListener('click', function(e) {
                    e.preventDefault();
                    inputTarget.name = "id_curso_materia"; 
                    inputTarget.value = this.dataset.id;
                    inputAction.value = "eliminar_malla";
                    textLabel.innerText = "¿Está seguro de desvincular esta asignatura de la malla curricular?";
                    textInfo.innerText = this.dataset.info;
                    modalDel.show();
                });
            });

            // Catálogos globales
            document.querySelectorAll('.btn-del-global').forEach(b => {
                b.addEventListener('click', function() {
                    const action = this.dataset.action;
                    if(action === 'eliminar_gestion') inputTarget.name = "id_gestion";
                    if(action === 'eliminar_curso') inputTarget.name = "id_curso";
                    if(action === 'eliminar_materia') inputTarget.name = "id_materia";
                    
                    inputTarget.value = this.dataset.id;
                    inputAction.value = action;
                    textLabel.innerText = "¿Está seguro de eliminar el siguiente registro?";
                    textInfo.innerText = this.dataset.info;
                    modalDel.show();
                });
            });

            // Lógica de edición
            document.querySelectorAll('.btn-edit-gestion').forEach(b => {
                b.addEventListener('click', function() {
                    document.getElementById('edit_g_id').value = this.dataset.id;
                    document.getElementById('edit_g_anio').value = this.dataset.anio;
                    document.getElementById('edit_g_activa').checked = (this.dataset.activa === 'true');
                    new bootstrap.Modal(document.getElementById('modalEditGestion')).show();
                });
            });
            document.querySelectorAll('.btn-edit-curso').forEach(b => {
                b.addEventListener('click', function() {
                    document.getElementById('edit_c_id').value = this.dataset.id;
                    document.getElementById('edit_c_nombre').value = this.dataset.nombre;
                    document.getElementById('edit_c_paralelo').value = this.dataset.paralelo;
                    document.getElementById('edit_c_nivel').value = this.dataset.nivel;
                    new bootstrap.Modal(document.getElementById('modalEditCurso')).show();
                });
            });
            document.querySelectorAll('.btn-edit-materia').forEach(b => {
                b.addEventListener('click', function() {
                    document.getElementById('edit_m_id').value = this.dataset.id;
                    document.getElementById('edit_m_nombre').value = this.dataset.nombre;
                    new bootstrap.Modal(document.getElementById('modalEditMateria')).show();
                });
            });
        });