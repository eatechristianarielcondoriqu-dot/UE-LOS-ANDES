// static/js/maestro_dashboard.js
document.addEventListener('DOMContentLoaded', function() {
    console.log("Panel del Maestro de la UE Los Andes cargado correctamente.");
    
    // Animación suave de entrada para las tarjetas de estadísticas
    const cards = document.querySelectorAll('.stat-card, .menu-item');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(15px)';
        card.style.transition = 'all 0.4s ease';
        
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 50);
    });
});