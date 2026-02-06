#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIDI Gateway - Emisor
GC Lab Chile - Proyecto Live Roots

Este script lee datos MIDI de un dispositivo (como Live Roots/MIDI Sprout)
y los transmite a un servidor WebSocket remoto.
"""

import sys
import time
import signal
import mido
import socketio
from datetime import datetime

# Cliente Socket.io
sio = socketio.Client(reconnection=True, reconnection_attempts=10, reconnection_delay=1)

# Estado global
state = {
    'connected': False,
    'midi_port': None,
    'running': True,
    'notes_sent': 0,
    'cc_sent': 0
}


def show_banner():
    """Muestra el banner de bienvenida."""
    print("\n")
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                                                              ║")
    print("║   ███╗   ███╗██╗██████╗ ██╗    ███████╗███╗   ███╗██╗████████╗║")
    print("║   ████╗ ████║██║██╔══██╗██║    ██╔════╝████╗ ████║██║╚══██╔══╝║")
    print("║   ██╔████╔██║██║██║  ██║██║    █████╗  ██╔████╔██║██║   ██║   ║")
    print("║   ██║╚██╔╝██║██║██║  ██║██║    ██╔══╝  ██║╚██╔╝██║██║   ██║   ║")
    print("║   ██║ ╚═╝ ██║██║██████╔╝██║    ███████╗██║ ╚═╝ ██║██║   ██║   ║")
    print("║   ╚═╝     ╚═╝╚═╝╚═════╝ ╚═╝    ╚══════╝╚═╝     ╚═╝╚═╝   ╚═╝   ║")
    print("║                                                              ║")
    print("║              MIDI Gateway - Emisor                           ║")
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


def list_midi_devices():
    """Lista todos los dispositivos MIDI disponibles."""
    inputs = mido.get_input_names()

    if not inputs:
        log("⚠️", "No se encontraron dispositivos MIDI de entrada")
        return []

    print("\n📋 Dispositivos MIDI disponibles:\n")
    print("-" * 50)
    for i, name in enumerate(inputs):
        print(f"   [{i}] {name}")
    print("-" * 50)
    print("")

    return inputs


def select_midi_device(devices):
    """Permite al usuario seleccionar un dispositivo MIDI."""
    while True:
        try:
            choice = input("🎹 Selecciona el numero del dispositivo MIDI: ")
            index = int(choice)
            if 0 <= index < len(devices):
                return devices[index]
            else:
                log("⚠️", f"Por favor ingresa un numero entre 0 y {len(devices)-1}")
        except ValueError:
            log("⚠️", "Por favor ingresa un numero valido")
        except KeyboardInterrupt:
            print("\n")
            log("⚠️", "Cancelado por usuario")
            sys.exit(0)


def midi_to_dict(msg):
    """Convierte un mensaje MIDI a diccionario."""
    data = {
        'type': msg.type,
        'channel': msg.channel if hasattr(msg, 'channel') else 0,
        'time': msg.time if hasattr(msg, 'time') else 0
    }

    if msg.type in ['note_on', 'note_off']:
        data['note'] = msg.note
        data['velocity'] = msg.velocity
    elif msg.type == 'control_change':
        data['control'] = msg.control
        data['value'] = msg.value
    elif msg.type == 'program_change':
        data['program'] = msg.program
    elif msg.type == 'pitchwheel':
        data['pitch'] = msg.pitch
    elif msg.type == 'aftertouch':
        data['value'] = msg.value
    elif msg.type == 'polytouch':
        data['note'] = msg.note
        data['value'] = msg.value

    return data


# Callbacks de Socket.io
@sio.event
def connect():
    """Callback cuando se conecta al servidor."""
    state['connected'] = True
    log("✓", "Conectado al servidor WebSocket")

    # Identificarse como emisor
    sio.emit('identify', {
        'type': 'emitter',
        'name': 'Live Roots - Alerce Milenario'
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
        log("✓", "Registrado como emisor exitosamente")
    else:
        log("✗", f"Error al registrarse: {data.get('message', 'Error desconocido')}")


@sio.on('midi-sent')
def on_midi_sent(data):
    """Confirmacion de envio MIDI."""
    receivers = data.get('receiversCount', 0)
    if receivers > 0:
        pass  # Confirmacion silenciosa para no saturar la consola


@sio.on('system-status')
def on_system_status(data):
    """Estado del sistema."""
    receivers = data.get('receiversCount', 0)
    if receivers > 0:
        log("📡", f"Receptores conectados: {receivers}")


@sio.on('pong')
def on_pong(data):
    """Respuesta de heartbeat."""
    pass  # Heartbeat silencioso


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
    log("✓", f"Sesion finalizada - Notas enviadas: {state['notes_sent']} | CC enviados: {state['cc_sent']}")
    print("\n")
    sys.exit(0)


def main():
    """Funcion principal."""
    show_banner()

    # Configurar manejador de senal
    signal.signal(signal.SIGINT, signal_handler)

    # Solicitar URL del servidor
    print("🌐 Configuracion del servidor")
    print("-" * 50)
    default_url = "http://localhost:3000"
    server_url = input(f"   URL del servidor [{default_url}]: ").strip()
    if not server_url:
        server_url = default_url
    print("")

    # Listar y seleccionar dispositivo MIDI
    devices = list_midi_devices()
    if not devices:
        log("✗", "No hay dispositivos MIDI disponibles. Conecta tu dispositivo e intenta de nuevo.")
        sys.exit(1)

    selected_device = select_midi_device(devices)
    log("✓", f"Dispositivo seleccionado: {selected_device}")
    print("")

    # Conectar al servidor WebSocket
    log("🔌", f"Conectando a {server_url}...")
    try:
        sio.connect(server_url, transports=['websocket', 'polling'])
    except Exception as e:
        log("✗", f"Error al conectar: {e}")
        sys.exit(1)

    # Abrir puerto MIDI
    try:
        state['midi_port'] = mido.open_input(selected_device)
        log("✓", f"Puerto MIDI abierto: {selected_device}")
    except Exception as e:
        log("✗", f"Error al abrir puerto MIDI: {e}")
        sio.disconnect()
        sys.exit(1)

    print("\n")
    print("═" * 60)
    print("   🌿 TRANSMISION ACTIVA - Esperando datos MIDI...")
    print("   Presiona Ctrl+C para detener")
    print("═" * 60)
    print("\n")

    # Loop principal de lectura MIDI
    try:
        while state['running']:
            for msg in state['midi_port'].iter_pending():
                if not state['connected']:
                    continue

                # Convertir mensaje a diccionario
                midi_data = midi_to_dict(msg)

                # Enviar al servidor
                try:
                    sio.emit('midi-data', midi_data)

                    # Log segun tipo
                    if msg.type == 'note_on' and msg.velocity > 0:
                        state['notes_sent'] += 1
                        log("🎵", f"Note ON: {msg.note} vel:{msg.velocity} ch:{msg.channel}")
                    elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                        log("🎵", f"Note OFF: {msg.note} ch:{msg.channel}")
                    elif msg.type == 'control_change':
                        state['cc_sent'] += 1
                        log("🎛️", f"CC: {msg.control}={msg.value} ch:{msg.channel}")

                except Exception as e:
                    log("⚠️", f"Error enviando MIDI: {e}")

            # Pequena pausa para no saturar CPU
            time.sleep(0.001)

    except Exception as e:
        log("✗", f"Error en loop principal: {e}")
    finally:
        signal_handler(None, None)


if __name__ == '__main__':
    main()
