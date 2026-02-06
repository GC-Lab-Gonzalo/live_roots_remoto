#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIDI Gateway - Receptor
GC Lab Chile - Proyecto Live Roots

Este script recibe datos MIDI desde un servidor WebSocket remoto
y los envia a un puerto MIDI virtual para uso en Ableton/TouchDesigner.
"""

import sys
import time
import signal
import platform
import mido
import socketio
from datetime import datetime

# Cliente Socket.io
sio = socketio.Client(reconnection=True, reconnection_attempts=10, reconnection_delay=1)

# Estado global
state = {
    'connected': False,
    'emitter_connected': False,
    'midi_port': None,
    'running': True,
    'notes_received': 0,
    'cc_received': 0,
    'last_ping': None
}

# Nombre del puerto MIDI virtual
VIRTUAL_PORT_NAME = "GC Lab - Live Roots Remote"


def show_banner():
    """Muestra el banner de bienvenida."""
    print("\n")
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                                                              ║")
    print("║   ███╗   ███╗██╗██████╗ ██╗    ██████╗ ███████╗ ██████╗██╗   ║")
    print("║   ████╗ ████║██║██╔══██╗██║    ██╔══██╗██╔════╝██╔════╝██║   ║")
    print("║   ██╔████╔██║██║██║  ██║██║    ██████╔╝█████╗  ██║     ██║   ║")
    print("║   ██║╚██╔╝██║██║██║  ██║██║    ██╔══██╗██╔══╝  ██║     ╚═╝   ║")
    print("║   ██║ ╚═╝ ██║██║██████╔╝██║    ██║  ██║███████╗╚██████╗██╗   ║")
    print("║   ╚═╝     ╚═╝╚═╝╚═════╝ ╚═╝    ╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝   ║")
    print("║                                                              ║")
    print("║              MIDI Gateway - Receptor                         ║")
    print("║              GC Lab Chile                                    ║")
    print("║                                                              ║")
    print("║     Proyecto: Live Roots - Alerce Milenario                  ║")
    print("║                                                              ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print("\n")


def timestamp():
    """Retorna timestamp formateado."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log(emoji, message):
    """Log con emoji y timestamp."""
    print(f"[{timestamp()}] {emoji} {message}")


def get_system_info():
    """Obtiene informacion del sistema operativo."""
    system = platform.system()
    return system


def list_midi_outputs():
    """Lista todos los puertos MIDI de salida disponibles."""
    outputs = mido.get_output_names()

    if not outputs:
        return []

    print("\n📋 Puertos MIDI de salida disponibles:\n")
    print("-" * 50)
    for i, name in enumerate(outputs):
        print(f"   [{i}] {name}")
    print("-" * 50)
    print("")

    return outputs


def select_midi_output(outputs):
    """Permite al usuario seleccionar un puerto MIDI de salida."""
    while True:
        try:
            choice = input("🎹 Selecciona el numero del puerto MIDI: ")
            index = int(choice)
            if 0 <= index < len(outputs):
                return outputs[index]
            else:
                log("⚠️", f"Por favor ingresa un numero entre 0 y {len(outputs)-1}")
        except ValueError:
            log("⚠️", "Por favor ingresa un numero valido")
        except KeyboardInterrupt:
            print("\n")
            log("⚠️", "Cancelado por usuario")
            sys.exit(0)


def setup_midi_port():
    """Configura el puerto MIDI segun el sistema operativo."""
    system = get_system_info()

    if system == 'Windows':
        print("\n")
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║  ⚠️  WINDOWS DETECTADO                                       ║")
        print("║                                                              ║")
        print("║  Para crear puertos MIDI virtuales en Windows necesitas      ║")
        print("║  instalar loopMIDI:                                          ║")
        print("║                                                              ║")
        print("║  1. Descarga loopMIDI desde:                                 ║")
        print("║     https://www.tobias-erichsen.de/software/loopmidi.html    ║")
        print("║                                                              ║")
        print("║  2. Crea un puerto virtual con el nombre:                    ║")
        print("║     'GC Lab - Live Roots Remote'                             ║")
        print("║                                                              ║")
        print("║  3. Vuelve a ejecutar este script                            ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print("\n")

        outputs = list_midi_outputs()

        if not outputs:
            log("✗", "No hay puertos MIDI disponibles.")
            log("⚠️", "Instala loopMIDI y crea el puerto virtual primero.")
            sys.exit(1)

        # Buscar puerto con nombre esperado
        loopmidi_port = None
        for port in outputs:
            if VIRTUAL_PORT_NAME.lower() in port.lower() or 'loopmidi' in port.lower():
                loopmidi_port = port
                break

        if loopmidi_port:
            log("✓", f"Puerto loopMIDI encontrado: {loopmidi_port}")
            try:
                return mido.open_output(loopmidi_port)
            except Exception as e:
                log("✗", f"Error abriendo puerto: {e}")
                sys.exit(1)
        else:
            log("⚠️", f"No se encontro el puerto '{VIRTUAL_PORT_NAME}'")
            selected = select_midi_output(outputs)
            try:
                return mido.open_output(selected)
            except Exception as e:
                log("✗", f"Error abriendo puerto: {e}")
                sys.exit(1)

    else:
        # macOS o Linux - crear puerto virtual
        log("🎹", f"Creando puerto MIDI virtual: {VIRTUAL_PORT_NAME}")
        try:
            port = mido.open_output(VIRTUAL_PORT_NAME, virtual=True)
            log("✓", f"Puerto virtual creado: {VIRTUAL_PORT_NAME}")
            return port
        except Exception as e:
            log("⚠️", f"Error creando puerto virtual: {e}")
            log("⚠️", "Intentando usar puerto existente...")

            outputs = list_midi_outputs()
            if outputs:
                selected = select_midi_output(outputs)
                try:
                    return mido.open_output(selected)
                except Exception as e2:
                    log("✗", f"Error abriendo puerto: {e2}")
                    sys.exit(1)
            else:
                log("✗", "No hay puertos MIDI disponibles")
                sys.exit(1)


def dict_to_midi(data):
    """Convierte un diccionario a mensaje MIDI."""
    msg_type = data.get('type')
    channel = data.get('channel', 0)

    try:
        if msg_type == 'note_on':
            return mido.Message('note_on',
                               note=data.get('note', 60),
                               velocity=data.get('velocity', 64),
                               channel=channel)
        elif msg_type == 'note_off':
            return mido.Message('note_off',
                               note=data.get('note', 60),
                               velocity=data.get('velocity', 0),
                               channel=channel)
        elif msg_type == 'control_change':
            return mido.Message('control_change',
                               control=data.get('control', 0),
                               value=data.get('value', 0),
                               channel=channel)
        elif msg_type == 'program_change':
            return mido.Message('program_change',
                               program=data.get('program', 0),
                               channel=channel)
        elif msg_type == 'pitchwheel':
            return mido.Message('pitchwheel',
                               pitch=data.get('pitch', 0),
                               channel=channel)
        elif msg_type == 'aftertouch':
            return mido.Message('aftertouch',
                               value=data.get('value', 0),
                               channel=channel)
        elif msg_type == 'polytouch':
            return mido.Message('polytouch',
                               note=data.get('note', 60),
                               value=data.get('value', 0),
                               channel=channel)
        else:
            return None
    except Exception as e:
        log("⚠️", f"Error creando mensaje MIDI: {e}")
        return None


# Callbacks de Socket.io
@sio.event
def connect():
    """Callback cuando se conecta al servidor."""
    state['connected'] = True
    log("✓", "Conectado al servidor WebSocket")

    # Identificarse como receptor
    sio.emit('identify', {
        'type': 'receiver',
        'name': 'Santiago - Presentacion Alerce'
    })


@sio.event
def disconnect():
    """Callback cuando se desconecta del servidor."""
    state['connected'] = False
    log("🔌", "Desconectado del servidor")


@sio.on('identify-response')
def on_identify_response(data):
    """Respuesta a la identificacion."""
    if data.get('success'):
        log("✓", "Registrado como receptor exitosamente")
        if data.get('emitterConnected'):
            state['emitter_connected'] = True
            log("🌿", f"Emisor conectado: {data.get('emitterName', 'Desconocido')}")
        else:
            log("⚠️", "Esperando conexion del emisor...")
    else:
        log("✗", f"Error al registrarse: {data.get('message', 'Error desconocido')}")


@sio.on('emitter-status')
def on_emitter_status(data):
    """Estado del emisor."""
    if data.get('connected'):
        state['emitter_connected'] = True
        log("🌿", f"Emisor conectado: {data.get('name', 'Desconocido')}")
        print("\n")
        print("═" * 60)
        print("   ✓ LISTO PARA RECIBIR DATOS MIDI DEL ALERCE")
        print("═" * 60)
        print("\n")
    else:
        state['emitter_connected'] = False
        log("⚠️", f"Emisor desconectado: {data.get('name', 'Desconocido')}")


@sio.on('midi-data')
def on_midi_data(data):
    """Recibe datos MIDI y los envia al puerto virtual."""
    if not state['midi_port']:
        return

    # Convertir a mensaje MIDI
    msg = dict_to_midi(data)
    if not msg:
        return

    # Enviar al puerto MIDI
    try:
        state['midi_port'].send(msg)

        # Log segun tipo
        if data['type'] == 'note_on' and data.get('velocity', 0) > 0:
            state['notes_received'] += 1
            log("🎵", f"Note ON: {data['note']} vel:{data['velocity']} ch:{data.get('channel', 0)}")
        elif data['type'] == 'note_off' or (data['type'] == 'note_on' and data.get('velocity', 0) == 0):
            log("🎵", f"Note OFF: {data['note']} ch:{data.get('channel', 0)}")
        elif data['type'] == 'control_change':
            state['cc_received'] += 1
            log("🎛️", f"CC: {data['control']}={data['value']} ch:{data.get('channel', 0)}")

    except Exception as e:
        log("⚠️", f"Error enviando MIDI: {e}")


@sio.on('system-status')
def on_system_status(data):
    """Estado del sistema."""
    pass  # Status silencioso


@sio.on('pong')
def on_pong(data):
    """Respuesta de heartbeat."""
    state['last_ping'] = time.time()


@sio.on('server-shutdown')
def on_server_shutdown(data):
    """El servidor esta cerrando."""
    log("⚠️", "El servidor esta cerrando...")


def signal_handler(sig, frame):
    """Maneja Ctrl+C para cierre limpio."""
    print("\n")
    log("⚠️", "Cerrando conexiones...")
    state['running'] = False

    if state['midi_port']:
        try:
            state['midi_port'].close()
            log("✓", "Puerto MIDI cerrado")
        except:
            pass

    if sio.connected:
        sio.disconnect()
        log("✓", "Desconectado del servidor")

    print("\n")
    log("✓", f"Sesion finalizada - Notas recibidas: {state['notes_received']} | CC recibidos: {state['cc_received']}")
    print("\n")
    sys.exit(0)


def heartbeat_loop():
    """Envia ping periodico al servidor."""
    while state['running']:
        if sio.connected:
            sio.emit('ping')
        time.sleep(1)


def main():
    """Funcion principal."""
    show_banner()

    # Configurar manejador de senal
    signal.signal(signal.SIGINT, signal_handler)

    # Mostrar sistema detectado
    system = get_system_info()
    log("💻", f"Sistema detectado: {system}")
    print("")

    # Configurar puerto MIDI
    state['midi_port'] = setup_midi_port()
    print("")

    # Solicitar URL del servidor
    print("🌐 Configuracion del servidor")
    print("-" * 50)
    default_url = "http://localhost:3000"
    server_url = input(f"   URL del servidor [{default_url}]: ").strip()
    if not server_url:
        server_url = default_url
    print("")

    # Conectar al servidor WebSocket
    log("🔌", f"Conectando a {server_url}...")
    try:
        sio.connect(server_url, transports=['websocket', 'polling'])
    except Exception as e:
        log("✗", f"Error al conectar: {e}")
        if state['midi_port']:
            state['midi_port'].close()
        sys.exit(1)

    print("\n")
    print("═" * 60)
    print("   🎹 RECEPCION ACTIVA")
    print(f"   Puerto MIDI: {VIRTUAL_PORT_NAME}")
    print("   Presiona Ctrl+C para detener")
    print("═" * 60)
    print("\n")

    if not state['emitter_connected']:
        log("⚠️", "Esperando conexion del emisor (Alerce)...")

    # Loop principal (mantener vivo)
    import threading
    heartbeat_thread = threading.Thread(target=heartbeat_loop, daemon=True)
    heartbeat_thread.start()

    try:
        while state['running']:
            time.sleep(0.1)
    except Exception as e:
        log("✗", f"Error en loop principal: {e}")
    finally:
        signal_handler(None, None)


if __name__ == '__main__':
    main()
