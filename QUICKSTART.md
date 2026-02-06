# MIDI Gateway - Guia Rapida

## 5 Pasos para Comenzar

### Paso 1: Instalar Dependencias

**Windows:**
```batch
install.bat
```

**macOS/Linux:**
```bash
chmod +x install.sh
./install.sh
```

O manualmente:
```bash
pip install mido python-socketio python-engineio
```

---

### Paso 2: Iniciar el Servidor

**Opcion A - Servidor en la nube (recomendado):**

Despliega en Railway.app:
1. Fork este repositorio
2. Conecta Railway con tu GitHub
3. Railway detectara automaticamente el Procfile
4. Obtendras una URL como: `https://tu-app.railway.app`

**Opcion B - Servidor local (testing):**
```bash
cd server
npm install
npm start
```
URL: `http://localhost:3000`

---

### Paso 3: Configurar PC Emisor (con Live Roots)

```bash
cd emitter
python midi_emitter.py
```

1. Ingresa la URL del servidor
2. Selecciona el dispositivo MIDI (Live Roots/MIDI Sprout)
3. Listo - los datos MIDI se transmiten automaticamente

---

### Paso 4: Configurar PC Receptor

**Windows - Requisito previo:**
1. Instala [loopMIDI](https://www.tobias-erichsen.de/software/loopmidi.html)
2. Crea puerto: `GC Lab - Live Roots Remote`

**Todos los sistemas:**
```bash
cd receiver
python midi_receiver.py
```

1. Ingresa la URL del servidor
2. El receptor creara/usara el puerto MIDI virtual
3. Espera la conexion del emisor

---

### Paso 5: Configurar tu DAW

**Ableton Live:**
1. Preferences > Link/Tempo/MIDI
2. Activa Track en `GC Lab - Live Roots Remote`
3. Crea pista MIDI con ese input
4. Arma la pista para grabar

**TouchDesigner:**
1. Agrega `MIDI In CHOP`
2. Selecciona `GC Lab - Live Roots Remote`
3. Los datos apareceran como canales

---

## Verificacion

Todo funciona si ves:

**En el emisor:**
```
✓ Conectado al servidor WebSocket
✓ Registrado como emisor exitosamente
🎵 Note ON: 60 vel:100 ch:0
```

**En el receptor:**
```
✓ Conectado al servidor WebSocket
✓ Registrado como receptor exitosamente
🌿 Emisor conectado: Live Roots - Alerce Milenario
🎵 Note ON: 60 vel:100 ch:0
```

---

## Problemas Comunes

| Problema | Solucion |
|----------|----------|
| "No hay dispositivos MIDI" | Conecta el dispositivo y reinicia el script |
| "Error de conexion" | Verifica la URL del servidor |
| Windows: "Puerto no encontrado" | Instala loopMIDI y crea el puerto |
| "Ya hay un emisor conectado" | Solo puede haber 1 emisor a la vez |

---

**GC Lab Chile** | Proyecto Live Roots - Alerce Milenario
