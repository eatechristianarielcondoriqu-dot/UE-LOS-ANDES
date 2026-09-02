document.addEventListener('DOMContentLoaded', function() {
    // Capturar todos los botones/tarjetas del menú
    const menuItems = document.querySelectorAll('.menu-item');

    menuItems.forEach(item => {
        item.addEventListener('click', function(e) {
            // Obtener el identificador único de la opción seleccionada
            const section = this.getAttribute('data-section');
            
            if (section) {
                console.log(`Abriendo sección: ${section}`);
                // Aquí podrás añadir efectos visuales o redirecciones dinámicas más adelante.
            }
        });
    });
});