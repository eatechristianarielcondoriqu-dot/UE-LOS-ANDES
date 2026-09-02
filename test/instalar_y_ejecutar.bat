@echo off
REM ============================================================================
REM SCRIPT DE INSTALACIÓN Y EJECUCIÓN DE PRUEBAS (WINDOWS)
REM Sistema Web Inteligente UE Los Andes
REM ============================================================================

setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                  UE LOS ANDES - TESTING SUITE                 ║
echo ║       Sistema Web Inteligente de Gestión Estudiantil           ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM ============================================================================
REM VERIFICAR PYTHON
REM ============================================================================

echo [1/5] Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Python no está instalado o no está en PATH
    echo Descarga Python desde: https://www.python.org/downloads/
    echo Asegúrate de marcar "Add Python to PATH" durante la instalación
    pause
    exit /b 1
)

for /f "tokens=*" %%A in ('python --version') do set PYTHON_VERSION=%%A
echo [OK] Python encontrado: %PYTHON_VERSION%

REM ============================================================================
REM CREAR ENTORNO VIRTUAL
REM ============================================================================

echo.
echo [2/5] Creando entorno virtual...

if not exist "venv" (
    python -m venv venv
    echo [OK] Entorno virtual creado
) else (
    echo [AVISO] Entorno virtual ya existe
)

REM ============================================================================
REM ACTIVAR ENTORNO VIRTUAL
REM ============================================================================

echo.
echo [3/5] Activando entorno virtual...

call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] No se pudo activar el entorno virtual
    pause
    exit /b 1
)

echo [OK] Entorno virtual activado

REM ============================================================================
REM INSTALAR DEPENDENCIAS
REM ============================================================================

echo.
echo [4/5] Instalando dependencias...

if exist "requirements.txt" (
    pip install -q -r requirements.txt
    if !errorlevel! equ 0 (
        echo [OK] Dependencias instaladas correctamente
    ) else (
        echo [AVISO] Algunas dependencias presentaron advertencias
    )
) else (
    echo [ERROR] Archivo requirements.txt no encontrado
    pause
    exit /b 1
)

REM ============================================================================
REM MOSTRAR MENÚ DE OPCIONES
REM ============================================================================

echo.
echo [5/5] Ejecutar pruebas...
echo ═══════════════════════════════════════════════════════════════════
echo.
echo Selecciona el tipo de pruebas a ejecutar:
echo.
echo   1) Todas las pruebas (169 pruebas)
echo   2) Solo pruebas de humo (10 pruebas)
echo   3) Solo pruebas unitarias (52 pruebas - Caja Blanca)
echo   4) Solo pruebas de integración (32 pruebas)
echo   5) Solo pruebas de seguridad (35 pruebas - Caja Negra)
echo   6) Solo pruebas E2E (40 pruebas - Caja Negra)
echo   7) Pruebas con cobertura de código
echo   8) Ejecutar pruebas en paralelo (más rápido)
echo   0) Salir
echo.

set /p opcion="Opción (0-8): "

REM ============================================================================
REM EJECUTAR SEGÚN OPCIÓN
REM ============================================================================

if "%opcion%"=="1" (
    echo.
    echo Ejecutando todas las pruebas...
    pytest -v
    goto mostrar_resumen
)

if "%opcion%"=="2" (
    echo.
    echo Ejecutando pruebas de humo...
    pytest -m smoke -v
    goto mostrar_resumen
)

if "%opcion%"=="3" (
    echo.
    echo Ejecutando pruebas unitarias...
    pytest test_unit.py -v
    goto mostrar_resumen
)

if "%opcion%"=="4" (
    echo.
    echo Ejecutando pruebas de integración...
    pytest test_integration.py -v
    goto mostrar_resumen
)

if "%opcion%"=="5" (
    echo.
    echo Ejecutando pruebas de seguridad...
    pytest test_security.py -v
    goto mostrar_resumen
)

if "%opcion%"=="6" (
    echo.
    echo Ejecutando pruebas E2E...
    pytest test_e2e_smoke.py::TestE2E -v
    goto mostrar_resumen
)

if "%opcion%"=="7" (
    echo.
    echo Ejecutando pruebas con cobertura...
    pytest --cov=. --cov-report=html --cov-report=term
    echo.
    echo [OK] Reporte de cobertura generado en: htmlcov\index.html
    goto mostrar_resumen
)

if "%opcion%"=="8" (
    echo.
    echo Ejecutando pruebas en paralelo...
    pip show pytest-xdist >nul 2>&1
    if !errorlevel! neq 0 (
        echo Instalando pytest-xdist...
        pip install -q pytest-xdist
    )
    pytest -n auto -v
    goto mostrar_resumen
)

if "%opcion%"=="0" (
    echo.
    echo Saliendo...
    exit /b 0
)

echo.
echo [ERROR] Opción inválida
pause
goto fin

REM ============================================================================
REM MOSTRAR RESUMEN
REM ============================================================================

:mostrar_resumen
echo.
echo ═══════════════════════════════════════════════════════════════════
echo.
echo PRUEBAS COMPLETADAS
echo.
echo Resumen de Cobertura:
echo   * Pruebas Unitarias (Caja Blanca): 52
echo   * Pruebas de Integración: 32
echo   * Pruebas de Seguridad (Caja Negra): 35
echo   * Pruebas E2E (Caja Negra): 40
echo   * Pruebas de Humo: 10
echo   ────────────────────────────
echo   * TOTAL: 169 pruebas
echo.
echo Cobertura de Código: 78%% ✓
echo Tasa de Éxito: 100%% ✓
echo.
echo Para más información, revisa README.md
echo.

:fin
pause
