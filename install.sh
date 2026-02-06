#!/bin/bash

# Colores ANSI
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                              ║${NC}"
echo -e "${BLUE}║   ███╗   ███╗██╗██████╗ ██╗     ██████╗  █████╗ ████████╗   ║${NC}"
echo -e "${BLUE}║   ████╗ ████║██║██╔══██╗██║    ██╔════╝ ██╔══██╗╚══██╔══╝   ║${NC}"
echo -e "${BLUE}║   ██╔████╔██║██║██║  ██║██║    ██║  ███╗███████║   ██║      ║${NC}"
echo -e "${BLUE}║   ██║╚██╔╝██║██║██║  ██║██║    ██║   ██║██╔══██║   ██║      ║${NC}"
echo -e "${BLUE}║   ██║ ╚═╝ ██║██║██████╔╝██║    ╚██████╔╝██║  ██║   ██║      ║${NC}"
echo -e "${BLUE}║   ╚═╝     ╚═╝╚═╝╚═════╝ ╚═╝     ╚═════╝ ╚═╝  ╚═╝   ╚═╝      ║${NC}"
echo -e "${BLUE}║                                                              ║${NC}"
echo -e "${BLUE}║            MIDI Gateway - Instalador                         ║${NC}"
echo -e "${BLUE}║            GC Lab Chile                                      ║${NC}"
echo -e "${BLUE}║                                                              ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Detectar sistema operativo
OS=$(uname -s)
echo -e "${YELLOW}[INFO]${NC} Sistema detectado: $OS"
echo ""

# Verificar Python3
echo -e "${BLUE}[1/4]${NC} Verificando Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓${NC} $PYTHON_VERSION"
else
    echo -e "${RED}✗${NC} Python3 no encontrado"
    echo ""
    echo "Por favor instala Python 3.8+ primero:"
    if [ "$OS" = "Darwin" ]; then
        echo "  brew install python3"
    else
        echo "  sudo apt install python3 python3-pip"
    fi
    exit 1
fi

# Verificar pip
echo ""
echo -e "${BLUE}[2/4]${NC} Verificando pip..."
if command -v pip3 &> /dev/null; then
    PIP_VERSION=$(pip3 --version)
    echo -e "${GREEN}✓${NC} pip3 disponible"
else
    echo -e "${RED}✗${NC} pip3 no encontrado"
    exit 1
fi

# Instalar dependencias Python
echo ""
echo -e "${BLUE}[3/4]${NC} Instalando dependencias Python..."
pip3 install mido python-socketio python-engineio

if [ $? -ne 0 ]; then
    echo -e "${RED}✗${NC} Error instalando dependencias"
    exit 1
fi
echo -e "${GREEN}✓${NC} Dependencias Python instaladas"

# Verificar Node.js (opcional)
echo ""
echo -e "${BLUE}[4/4]${NC} Verificando Node.js (opcional)..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓${NC} Node.js $NODE_VERSION"
else
    echo -e "${YELLOW}!${NC} Node.js no instalado (solo necesario para servidor local)"
fi

echo ""
echo -e "${GREEN}══════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}  INSTALACION COMPLETADA${NC}"
echo ""
echo -e "${GREEN}══════════════════════════════════════════════════════════════${NC}"
echo ""
echo "  Proximos pasos:"
echo ""
echo -e "  ${BLUE}PARA EMISOR${NC} (PC con Live Roots):"
echo "    cd emitter"
echo "    python3 midi_emitter.py"
echo ""
echo -e "  ${BLUE}PARA RECEPTOR${NC} (PC con Ableton/TouchDesigner):"
echo "    cd receiver"
echo "    python3 midi_receiver.py"
echo ""
if [ "$OS" = "Darwin" ]; then
    echo -e "  ${YELLOW}NOTA macOS:${NC} El puerto MIDI virtual se crea automaticamente"
else
    echo -e "  ${YELLOW}NOTA Linux:${NC} Puede que necesites instalar ALSA:"
    echo "    sudo apt install libasound2-dev"
fi
echo ""
echo -e "  ${BLUE}PARA SERVIDOR LOCAL${NC} (opcional):"
echo "    cd server"
echo "    npm install"
echo "    npm start"
echo ""
echo -e "${GREEN}══════════════════════════════════════════════════════════════${NC}"
echo ""
