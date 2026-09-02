let globalStream = null;
let b64_patron_rostro = "";
let b64_tramite_rostro = "";

function inicializarLienzoFiel(idCanvas) {
    const canvas = document.getElementById(idCanvas);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let trazando = false;

    ctx.lineWidth = 3.5;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.strokeStyle = '#0f172a';
    ctx.shadowBlur = 1;
    ctx.shadowColor = '#0f172a';

    function obtenerPosicion(e) {
        const r = canvas.getBoundingClientRect();
        const clienteX = e.touches ? e.touches[0].clientX : e.clientX;
        const clienteY = e.touches ? e.touches[0].clientY : e.clientY;
        return { x: clienteX - r.left, y: clienteY - r.top };
    }

    function iniciar(e) { trazando = true; ctx.beginPath(); mover(e); }
    function fin() { trazando = false; ctx.beginPath(); }
    function mover(e) {
        if (!trazando) return;
        e.preventDefault();
        const pos = obtenerPosicion(e);
        ctx.lineTo(pos.x, pos.y);
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(pos.x, pos.y);
    }

    canvas.addEventListener('mousedown', iniciar);
    canvas.addEventListener('mouseup', fin);
    canvas.addEventListener('mousemove', mover);

    canvas.addEventListener('touchstart', iniciar, { passive: false });
    canvas.addEventListener('touchend', fin);
    canvas.addEventListener('touchmove', mover, { passive: false });
}

function limpiarCanvas(idCanvas) {
    const canvas = document.getElementById(idCanvas);
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
}

function encenderDispositivo(idVideo) {
    navigator.mediaDevices.getUserMedia({ video: { width: 320, height: 240 } })
        .then(st => { globalStream = st; document.getElementById(idVideo).srcObject = st; })
        .catch(err => alert("Cámara no detectada o denegada. Active los permisos."));
}

function abrirCamaraPatron() { encenderDispositivo('vidPatron'); }
function abrirCamaraTramite() { encenderDispositivo('vidTramite'); }

function cerrarCamaras() {
    if (globalStream) { globalStream.getTracks().forEach(tr => tr.stop()); }
}

function congelarRostro(idVideo, idImgTarget) {
    const vid = document.getElementById(idVideo);
    const canv = document.getElementById('canvasMuestreo');
    const ctx = canv.getContext('2d');
    ctx.drawImage(vid, 0, 0, canv.width, canv.height);
    const dataUrl = canv.toDataURL('image/png');
    document.getElementById(idImgTarget).src = dataUrl;
    return dataUrl;
}

// ── FIX: ahora también se escribe el valor en el input oculto correspondiente,
//         que es lo que realmente lee enviarTramite() en el HTML antes de enviar.
function capturarFotoPatron() {
    b64_patron_rostro = congelarRostro('vidPatron', 'prevPatronFace');
    const inPatronFoto = document.getElementById('in_patron_foto');
    if (inPatronFoto) inPatronFoto.value = b64_patron_rostro;
}

function capturarFotoTramite() {
    b64_tramite_rostro = congelarRostro('vidTramite', 'prevTramiteFace');
    const inCartaFoto = document.getElementById('in_carta_foto');
    if (inCartaFoto) inCartaFoto.value = b64_tramite_rostro;
}

function guardarBiometriaBase() {
    const fData = document.getElementById('canPatronSign').toDataURL('image/png');
    if (!b64_patron_rostro) { alert("Por favor, capture su fotografía facial primero."); return; }

    document.getElementById('in_patron_firma').value = fData;
    document.getElementById('in_patron_foto').value = b64_patron_rostro;
    cerrarCamaras();
    document.getElementById('formBiometriaBase').submit();
}

function enviarFormularioTramite() {
    const fData = document.getElementById('canTramiteSign').toDataURL('image/png');
    if (!b64_tramite_rostro) { alert("Es obligatorio capturar la fotografía facial actual para la auditoría de la IA."); return; }

    document.getElementById('in_carta_firma').value = fData;
    document.getElementById('in_carta_foto').value = b64_tramite_rostro;
    cerrarCamaras();
    document.getElementById('formJustificar').submit();
}

window.onload = function () {
    inicializarLienzoFiel('canPatronSign');
    inicializarLienzoFiel('canTramiteSign');
}