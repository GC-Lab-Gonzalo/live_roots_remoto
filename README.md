# MIDI Gateway - GC Lab Chile

```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   ███╗   ███╗██╗██████╗ ██╗     ██████╗  █████╗ ████████╗   ║
║   ████╗ ████║██║██╔══██╗██║    ██╔════╝ ██╔══██╗╚══██╔══╝   ║
║   ██╔████╔██║██║██║  ██║██║    ██║  ███╗███████║   ██║      ║
║   ██║╚██╔╝██║██║██║  ██║██║    ██║   ██║██╔══██║   ██║      ║
║   ██║ ╚═╝ ██║██║██████╔╝██║    ╚██████╔╝██║  ██║   ██║      ║
║   ╚═╝     ╚═╝╚═╝╚═════╝ ╚═╝     ╚═════╝ ╚═╝  ╚═╝   ╚═╝      ║
║                                                              ║
║        Sistema de Transmision MIDI Remota por Internet       ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

## Proyecto Live Roots - Alerce Milenario

Este sistema fue desarrollado para el proyecto **Live Roots** de GC Lab Chile, que conecta un **Alerce Milenario** en el sur de Chile con presentaciones artisticas en Santiago y otras ciudades.

Utilizando un dispositivo **MIDI Sprout/Live Roots**, se captura la impedancia electrica del arbol milenario y se convierte en senales MIDI. Este sistema permite transmitir esas senales en tiempo real a traves de Internet para su uso en **Ableton Live**, **TouchDesigner** y otros softwares creativos.

---

## Arquitectura del Sistema

```
┌─────────────────┐     USB      ┌─────────────────┐
│   Live Roots    │─────────────►│  Emisor Python  │
│  (MIDI Sprout)  │              │                 │
└─────────────────┘              └────────┬────────┘
                                          │
                                    WebSocket
                                          │
                                          ▼
                              ┌─────────────────────┐
                              │   Servidor Node.js  │
                              │     (Cloud/Local)   │
                              └──────────┬──────────┘
                                         │
                        ┌────────────────┼────────────────┐
                        │                │                │
                  WebSocket        WebSocket        WebSocket
                        │                │                │
                        ▼                ▼                ▼
              ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
              │  Receptor   │  │  Receptor   │  │  Receptor   │
              │   Python    │  │   Python    │  │   Python    │
              └──────┬──────┘  └──────┬──────┘  └──────┬──────┘
                     │                │                │
               Puerto MIDI      Puerto MIDI      Puerto MIDI
                Virtual           Virtual          Virtual
                     │                │                │
                     ▼                ▼                ▼
              ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
              │   Ableton   │  │TouchDesigner│  │   Otro SW   │
              └─────────────┘  └─────────────┘  └─────────────┘
```

---

## Requisitos Previos

### Software Base
- **Python 3.8+** - [Descargar](https://python.org)
- **Node.js 16+** - [Descargar](https://nodejs.org) (solo para servidor local)

### Windows (Receptor)
- **loopMIDI** - [Descargar](https://www.tobias-erichsen.de/software/loopmidi.html)
  - Necesario para crear puertos MIDI virtuales en Windows

### macOS / Linux
- Los puertos MIDI virtuales se crean automaticamente
- macOS: CoreMIDI incluido en el sistema
- Linux: Puede requerir ALSA (`sudo apt install libasound2-dev`)

---

## Instalacion

### Instalacion Automatica

**Windows:**
```batch
install.bat
```

**macOS/Linux:**
```bash
chmod +x install.sh
./install.sh
```

### Instalacion Manual

```bash
# Dependencias Python
pip install mido python-socketio python-engineio

# Dependencias del servidor (opcional, solo si ejecutas servidor local)
cd server
npm install
```

---

## Configuracion del Servidor

### Opcion 1: Local (Testing)

```bash
cd server
npm install
npm start
```

El servidor estara disponible en `http://localhost:3000`

### Opcion 2: Heroku

```bash
# Instalar Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

heroku login
heroku create midi-gateway-gclab
git push heroku main
```

### Opcion 3: Railway (Recomendado)

1. Ve a [Railway.app](https://railway.app)
2. Crea una cuenta o inicia sesion con GitHub
3. Click en "New Project" > "Deploy from GitHub repo"
4. Selecciona este repositorio
5. Railway detectara automaticamente el `Procfile`
6. Espera el deploy y obtendras una URL como:
   ```
   https://midi-gateway-production-xxxx.up.railway.app
   ```

### Verificar Servidor

```bash
curl https://tu-servidor.railway.app/health
```

Respuesta esperada:
```json
{
  "status": "online",
  "server": "MIDI Gateway - GC Lab Chile",
  "emitter": { "connected": false },
  "receivers": { "count": 0 }
}
```

---

## Configuracion del Emisor

El emisor se ejecuta en la computadora conectada al dispositivo Live Roots/MIDI Sprout.

```bash
cd emitter
python midi_emitter.py
```

### Proceso:
1. Ingresa la URL del servidor (ej: `https://tu-servidor.railway.app`)
2. Selecciona el dispositivo MIDI de la lista
3. El sistema comenzara a transmitir automaticamente

### Output esperado:
```
╔══════════════════════════════════════════════════════════════╗
║              MIDI Gateway - Emisor                           ║
╚══════════════════════════════════════════════════════════════╝

🌐 Configuracion del servidor
--------------------------------------------------
   URL del servidor [http://localhost:3000]: https://tu-servidor.railway.app

📋 Dispositivos MIDI disponibles:
--------------------------------------------------
   [0] Live Roots
   [1] USB MIDI Interface
--------------------------------------------------

🎹 Selecciona el numero del dispositivo MIDI: 0
✓ Dispositivo seleccionado: Live Roots

🔌 Conectando a https://tu-servidor.railway.app...
✓ Conectado al servidor WebSocket
✓ Registrado como emisor exitosamente

════════════════════════════════════════════════════════════════
   🌿 TRANSMISION ACTIVA - Esperando datos MIDI...
════════════════════════════════════════════════════════════════

🎵 Note ON: 60 vel:87 ch:0
🎵 Note OFF: 60 ch:0
🎛️ CC: 1=64 ch:0
```

---

## Configuracion del Receptor

El receptor se ejecuta en la(s) computadora(s) que recibiran los datos MIDI.

### Windows - Paso Previo

1. Descarga e instala [loopMIDI](https://www.tobias-erichsen.de/software/loopmidi.html)
2. Abre loopMIDI
3. En el campo de texto, escribe: `GC Lab - Live Roots Remote`
4. Click en el boton `+` para crear el puerto

### Ejecutar Receptor

```bash
cd receiver
python midi_receiver.py
```

### Proceso:
1. El sistema detecta tu OS (Windows/macOS/Linux)
2. Configura o crea el puerto MIDI virtual
3. Ingresa la URL del servidor
4. Espera la conexion del emisor

### Output esperado:
```
╔══════════════════════════════════════════════════════════════╗
║              MIDI Gateway - Receptor                         ║
╚══════════════════════════════════════════════════════════════╝

💻 Sistema detectado: Darwin

🎹 Creando puerto MIDI virtual: GC Lab - Live Roots Remote
✓ Puerto virtual creado: GC Lab - Live Roots Remote

🌐 Configuracion del servidor
--------------------------------------------------
   URL del servidor [http://localhost:3000]: https://tu-servidor.railway.app

🔌 Conectando a https://tu-servidor.railway.app...
✓ Conectado al servidor WebSocket
✓ Registrado como receptor exitosamente
⚠️ Esperando conexion del emisor (Alerce)...

🌿 Emisor conectado: Live Roots - Alerce Milenario

════════════════════════════════════════════════════════════════
   ✓ LISTO PARA RECIBIR DATOS MIDI DEL ALERCE
════════════════════════════════════════════════════════════════

🎵 Note ON: 60 vel:87 ch:0
🎵 Note OFF: 60 ch:0
🎛️ CC: 1=64 ch:0
```

---

## Configurar Ableton Live

1. Abre **Preferences** (Cmd/Ctrl + ,)
2. Ve a **Link/Tempo/MIDI**
3. En la seccion **MIDI Ports**, busca `GC Lab - Live Roots Remote`
4. Activa:
   - **Track**: On (para recibir notas en pistas)
   - **Remote**: On (opcional, para control de parametros)

```
Input: GC Lab - Live Roots Remote
┌─────────┬───────┬────────┐
│  Track  │ Sync  │ Remote │
├─────────┼───────┼────────┤
│   On    │  Off  │   On   │
└─────────┴───────┴────────┘
```

5. Crea una pista MIDI
6. En **MIDI From**, selecciona `GC Lab - Live Roots Remote`
7. Activa el boton de **Arm** (grabacion) en la pista
8. Los datos MIDI del Alerce llegaran a esta pista

---

## Configurar TouchDesigner

1. Agrega un operador **MIDI In CHOP**
2. En el parametro **Device**, selecciona `GC Lab - Live Roots Remote`
3. Los canales apareceran automaticamente:
   - Notas: `n60`, `n61`, `n62`... (valor = velocity)
   - CC: `ch1c1`, `ch1c2`... (valor = 0-127)

### Ejemplo de Setup

```
MIDI In CHOP ──► Select CHOP ──► Math CHOP ──► [Tu operador]
                 (filtrar        (normalizar
                  canales)        valores)
```

**Select CHOP** para filtrar solo las notas:
```
Channel Names: n*
```

**Math CHOP** para normalizar 0-127 a 0-1:
```
From Range: 0 127
To Range: 0 1
```

---

## Solucion de Problemas

### "No se encontraron dispositivos MIDI"
- Verifica que el dispositivo este conectado por USB
- En Windows, verifica en Administrador de Dispositivos
- Reinicia el script despues de conectar

### "Error al conectar al servidor"
- Verifica que la URL sea correcta (incluir http:// o https://)
- Verifica que el servidor este ejecutandose
- Prueba el endpoint `/health` en el navegador

### "Puerto MIDI no encontrado" (Windows)
- Instala loopMIDI
- Crea un puerto con el nombre exacto: `GC Lab - Live Roots Remote`
- Reinicia el receptor

### "Ya hay un emisor conectado"
- Solo puede haber un emisor activo a la vez
- Cierra el otro emisor o espera a que se desconecte

### "Latencia muy alta"
- La latencia depende de la conexion a Internet
- Latencia tipica en Chile: 50-150ms
- Usa un servidor geograficamente cercano

### "Ableton no recibe MIDI"
- Verifica que Track este activado para el puerto
- Asegurate de que la pista este armada (boton rojo)
- Verifica que el canal MIDI coincida (All o el canal especifico)

---

## Monitoreo y Estadisticas

### Endpoint de Salud
```
GET /health
```

Retorna:
```json
{
  "status": "online",
  "uptime": 3600,
  "uptimeFormatted": "01:00:00",
  "emitter": {
    "connected": true,
    "name": "Live Roots - Alerce Milenario"
  },
  "receivers": {
    "count": 2,
    "list": [
      { "name": "Santiago - Presentacion" },
      { "name": "Valparaiso - Instalacion" }
    ]
  },
  "stats": {
    "totalMidiMessages": 15420,
    "totalNotesOn": 5140,
    "totalNotesOff": 5140,
    "totalControlChanges": 5140
  }
}
```

### Interfaces Web

Tambien puedes usar las interfaces HTML para monitoreo visual:
- `emitter/index.html` - Interfaz del emisor
- `receiver/index.html` - Interfaz del receptor

---

## Estructura del Proyecto

```
midi-gateway/
├── server/
│   ├── server.js          # Servidor WebSocket Node.js
│   └── package.json       # Dependencias del servidor
├── emitter/
│   ├── midi_emitter.py    # Cliente emisor Python
│   └── index.html         # Interfaz web del emisor
├── receiver/
│   ├── midi_receiver.py   # Cliente receptor Python
│   └── index.html         # Interfaz web del receptor
├── requirements.txt       # Dependencias Python
├── README.md              # Esta documentacion
├── QUICKSTART.md          # Guia rapida
├── install.bat            # Instalador Windows
├── install.sh             # Instalador macOS/Linux
├── Procfile               # Configuracion Heroku/Railway
└── .gitignore             # Archivos ignorados por Git
```

---

## Roadmap

- [ ] Interfaz web completa con Socket.io
- [ ] Autenticacion para conexiones
- [ ] Grabacion y reproduccion de sesiones MIDI
- [ ] Visualizacion en tiempo real de datos
- [ ] App movil para monitoreo
- [ ] Soporte para multiples emisores
- [ ] Compresion de datos MIDI
- [ ] Modo offline con cache local

---

## Notas Tecnicas

### Latencia
- Red local: 5-20ms
- Internet (misma ciudad): 20-50ms
- Internet (Chile norte-sur): 50-150ms
- Internacional: 100-300ms

### Protocolo
- WebSocket sobre HTTP/HTTPS
- Mensajes JSON
- Heartbeat cada 30 segundos
- Reconexion automatica

### Puerto MIDI Virtual
- Nombre: `GC Lab - Live Roots Remote`
- Windows: Requiere loopMIDI
- macOS: CoreMIDI (automatico)
- Linux: ALSA (automatico)

### Formato de Mensaje MIDI
```json
{
  "type": "note_on",
  "note": 60,
  "velocity": 100,
  "channel": 0,
  "time": 0.0,
  "timestamp": 1699999999999,
  "source": "Live Roots - Alerce Milenario"
}
```

---

## El Alerce Milenario

> *El Alerce (Fitzroya cupressoides) es una de las especies de arboles mas longevas del mundo, con ejemplares que superan los 3.000 anos de edad. Este proyecto conecta la energia vital de uno de estos gigantes con el arte digital contemporaneo, creando un puente entre la naturaleza ancestral y la tecnologia.*

El dispositivo Live Roots mide las variaciones de impedancia electrica en el arbol, que reflejan su actividad biologica: flujo de savia, respuesta a la luz, temperatura y otros factores ambientales. Estas senales se convierten en datos MIDI que pueden controlar instrumentos, visuales y otros elementos artisticos.

---

## Licencia

MIT License - GC Lab Chile 2025

## Contacto

- **GC Lab Chile**
- Proyecto: Live Roots - Alerce Milenario
- Web: [gclabchile.cl](https://gclabchile.cl)

---

*Conectando la naturaleza con el arte digital*
