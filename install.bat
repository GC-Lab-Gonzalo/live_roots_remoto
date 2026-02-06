@echo off
chcp 65001 > nul
title MIDI Gateway - GC Lab Chile

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║   ███╗   ███╗██╗██████╗ ██╗     ██████╗  █████╗ ████████╗   ║
echo ║   ████╗ ████║██║██╔══██╗██║    ██╔════╝ ██╔══██╗╚══██╔══╝   ║
echo ║   ██╔████╔██║██║██║  ██║██║    ██║  ███╗███████║   ██║      ║
echo ║   ██║╚██╔╝██║██║██║  ██║██║    ██║   ██║██╔══██║   ██║      ║
echo ║   ██║ ╚═╝ ██║██║██████╔╝██║    ╚██████╔╝██║  ██║   ██║      ║
echo ║   ╚═╝     ╚═╝╚═╝╚═════╝ ╚═╝     ╚═════╝ ╚═╝  ╚═╝   ╚═╝      ║
echo ║                                                              ║
echo ║            MIDI Gateway - Instalador                         ║
echo ║            GC Lab Chile                                      ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo [1/4] Verificando Python...
python --version
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Python no esta instalado o no esta en el PATH
    echo Por favor instala Python 3.8+ desde https://python.org
    echo.
    pause
    exit /b 1
)

echo.
echo [2/4] Verificando pip...
pip --version
if %errorlevel% neq 0 (
    echo.
    echo ERROR: pip no esta disponible
    echo.
    pause
    exit /b 1
)

echo.
echo [3/4] Instalando dependencias Python...
pip install mido python-socketio python-engineio

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Fallo la instalacion de dependencias
    echo.
    pause
    exit /b 1
)

echo.
echo [4/4] Verificando Node.js (opcional, solo para servidor)...
node --version 2>nul
if %errorlevel% neq 0 (
    echo Node.js no esta instalado - Solo necesario si vas a ejecutar el servidor localmente
) else (
    echo Node.js encontrado
)

echo.
echo ══════════════════════════════════════════════════════════════
echo.
echo  INSTALACION COMPLETADA
echo.
echo ══════════════════════════════════════════════════════════════
echo.
echo  Proximos pasos:
echo.
echo  PARA EMISOR (PC con Live Roots):
echo    cd emitter
echo    python midi_emitter.py
echo.
echo  PARA RECEPTOR (PC con Ableton/TouchDesigner):
echo    1. Instala loopMIDI: https://www.tobias-erichsen.de/software/loopmidi.html
echo    2. Crea un puerto llamado: GC Lab - Live Roots Remote
echo    3. Ejecuta:
echo       cd receiver
echo       python midi_receiver.py
echo.
echo  PARA SERVIDOR LOCAL (opcional):
echo    cd server
echo    npm install
echo    npm start
echo.
echo ══════════════════════════════════════════════════════════════
echo.
pause
