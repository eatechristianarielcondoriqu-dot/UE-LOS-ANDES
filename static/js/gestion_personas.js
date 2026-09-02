document.addEventListener("DOMContentLoaded", function () {
    // --- MANEJO DE MODAL DE EDICIÓN ---
    const modalEditPersona = document.getElementById('modalEditPersona');
    if (modalEditPersona) {
        modalEditPersona.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            
            // Atributos base comunes
            document.getElementById('edit_id_persona').value = button.getAttribute('data-id-persona') || '';
            document.getElementById('edit_id_entidad').value = button.getAttribute('data-id-entidad') || '';
            document.getElementById('edit_dni_cedula').value = button.getAttribute('data-dni') || '';
            document.getElementById('edit_nombres').value = button.getAttribute('data-nombres') || '';
            document.getElementById('edit_apellidos').value = button.getAttribute('data-apellidos') || '';
            document.getElementById('edit_genero').value = button.getAttribute('data-genero') || 'M';
            document.getElementById('edit_fecha_nacimiento').value = button.getAttribute('data-fecha-nac') || '';
            document.getElementById('edit_telefono').value = button.getAttribute('data-telefono') || '';

            // Campo dinámico específico del rol
            const extraField = document.getElementById('edit_campo_extra');
            if (extraField) {
                extraField.value = button.getAttribute('data-extra-val') || '';
            }

            // Gestión de Sub-relaciones Complejas (Estudiante -> Padres)
            const jsonPadresRaw = button.getAttribute('data-json-padres');
            const wrapperPadres = document.getElementById('edit_relaciones_padres_wrapper');
            
            if (wrapperPadres && jsonPadresRaw) {
                wrapperPadres.innerHTML = '';
                try {
                    const padresAsignados = JSON.parse(jsonPadresRaw);
                    padresAsignados.forEach(p => {
                        agregarFilaPadreAEditar(p.id_padre, p.parentesco, p.es_tutor);
                    });
                } catch (e) {
                    console.error("Error parseando parientes asignados: ", e);
                }
            }
        });
    }

    // --- MANEJO DE MODAL DE ELIMINACIÓN ---
    const modalDeletePersona = document.getElementById('modalDeletePersona');
    if (modalDeletePersona) {
        modalDeletePersona.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            document.getElementById('delete_id_entidad').value = button.getAttribute('data-id-entidad') || '';
            document.getElementById('delete_nombre_completo').textContent = 
                `${button.getAttribute('data-nombres')} ${button.getAttribute('data-apellidos')}`;
        });
    }
});

// --- FUNCIONES INTERNAS PARA AGREGAR FILAS DINÁMICAS (FORMULARIO ALUMNOS) ---
function agregarFilaPadreACrear() {
    const selectorOriginal = document.getElementById('selector_padres_base');
    if (!selectorOriginal) return;
    
    const wrapper = document.getElementById('crear_relaciones_padres_wrapper');
    const index = wrapper.children.length;
    
    const div = document.createElement('div');
    div.className = "row g-2 align-items-center mb-2 dynamic-parent-row";
    div.innerHTML = `
        <div class="col-md-5">
            <select name="padres_ids" class="form-select" required>
                ${selectorOriginal.innerHTML}
            </select>
        </div>
        <div class="col-md-4">
            <select name="padres_parentescos" class="form-select" required>
                <option value="PADRE">PADRE</option>
                <option value="MADRE">MADRE</option>
                <option value="TUTOR">TUTOR</option>
                <option value="ABUELO">ABUELO</option>
                <option value="ABUELA">ABUELA</option>
                <option value="TIO">TIO</option>
                <option value="TIA">TIA</option>
                <option value="APODERADO">APODERADO</option>
            </select>
        </div>
        <div class="col-md-2 text-center">
            <div class="form-check d-inline-block">
                <input class="form-check-input" type="checkbox" name="padres_tutores_indices" value="${index}">
                <label class="form-check-label small">¿Tutor?</label>
            </div>
        </div>
        <div class="col-md-1">
            <button type="button" class="btn btn-outline-danger btn-sm w-100" onclick="this.closest('.dynamic-parent-row').remove()">
                <i class="bi bi-trash"></i>
            </button>
        </div>
    `;
    wrapper.appendChild(div);
}

function agregarFilaPadreAEditar(idPadre = null, parentesco = '', esTutor = false) {
    const selectorOriginal = document.getElementById('selector_padres_base');
    if (!selectorOriginal) return;
    
    const wrapper = document.getElementById('edit_relaciones_padres_wrapper');
    const index = wrapper.children.length;
    
    const div = document.createElement('div');
    div.className = "row g-2 align-items-center mb-2 dynamic-parent-row";
    
    // Clonar opciones del selector base y marcar la correspondiente
    let selectPadreHTML = `<select name="edit_padres_ids" class="form-select" required>`;
    Array.from(selectorOriginal.options).forEach(opt => {
        const selected = (idPadre && opt.value == idPadre) ? 'selected' : '';
        selectPadreHTML += `<option value="${opt.value}" ${selected}>${opt.text}</option>`;
    });
    selectPadreHTML += `</select>`;

    // Listado manual de opciones del Enum de parentesco postgres
    const parentescos = ['PADRE', 'MADRE', 'TUTOR', 'ABUELO', 'ABUELA', 'TIO', 'TIA', 'APODERADO'];
    let selectParentescoHTML = `<select name="edit_padres_parentescos" class="form-select" required>`;
    parentescos.forEach(par => {
        const selected = (parentesco === par) ? 'selected' : '';
        selectParentescoHTML += `<option value="${par}" ${selected}>${par}</option>`;
    });
    selectParentescoHTML += `</select>`;

    div.innerHTML = `
        <div class="col-md-5">${selectPadreHTML}</div>
        <div class="col-md-4">${selectParentescoHTML}</div>
        <div class="col-md-2 text-center">
            <div class="form-check d-inline-block">
                <input class="form-check-input" type="checkbox" name="edit_padres_tutores_indices" value="${index}" ${esTutor ? 'checked' : ''}>
                <label class="form-check-label small">¿Tutor?</label>
            </div>
        </div>
        <div class="col-md-1">
            <button type="button" class="btn btn-outline-danger btn-sm w-100" onclick="this.closest('.dynamic-parent-row').remove()">
                <i class="bi bi-trash"></i>
            </button>
        </div>
    `;
    wrapper.appendChild(div);
}