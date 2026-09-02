// Asegura que el código se ejecute cuando el HTML esté listo
document.addEventListener("DOMContentLoaded", () => {
    
    // Función POO para simular contadores de un Dashboard real
    const animarContador = (id, valorFinal, duracion) => {
        const elemento = document.getElementById(id);
        if (!elemento) return;

        let valorInicial = 0;
        const incremento = Math.ceil(valorFinal / (duracion / 16));
        
        const temporizador = setInterval(() => {
            valorInicial += incremento;
            if (valorInicial >= valorFinal) {
                elemento.textContent = valorFinal;
                clearInterval(temporizador);
            } else {
                elemento.textContent = valorInicial;
            }
        }, 16); // ~60 cuadros por segundo
    };

    // Ejecutar las animaciones con datos simulados del colegio
    animarContador("count-estudiantes", 450, 1500); // 450 alumnos
    animarContador("count-maestros", 32, 1200);      // 32 docentes
    animarContador("count-materias", 18, 1000);      // 18 asignaturas
});