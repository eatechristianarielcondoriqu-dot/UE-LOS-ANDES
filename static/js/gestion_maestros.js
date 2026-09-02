const modalEdit = document.getElementById('modalEditMaestro');

if (modalEdit) {

    modalEdit.addEventListener(
        'show.bs.modal',
        function (event) {

            const btn = event.relatedTarget;

            document.getElementById(
                'edit_id_maestro'
            ).value = btn.dataset.id;

            document.getElementById(
                'edit_dni'
            ).value = btn.dataset.dni;

            document.getElementById(
                'edit_nombres'
            ).value = btn.dataset.nombres;

            document.getElementById(
                'edit_apellidos'
            ).value = btn.dataset.apellidos;

            document.getElementById(
                'edit_genero'
            ).value = btn.dataset.genero;

            document.getElementById(
                'edit_fecha'
            ).value = btn.dataset.fecha;

            document.getElementById(
                'edit_telefono'
            ).value = btn.dataset.telefono;

            document.getElementById(
                'edit_especialidad'
            ).value = btn.dataset.especialidad;
        }
    );
}


const modalDelete =
    document.getElementById('modalDeleteMaestro');

if (modalDelete) {

    modalDelete.addEventListener(
        'show.bs.modal',
        function (event) {

            const btn = event.relatedTarget;

            document.getElementById(
                'delete_id_maestro'
            ).value = btn.dataset.id;

            document.getElementById(
                'delete_nombre_maestro'
            ).innerHTML =
                btn.dataset.nombre;
        }
    );
}