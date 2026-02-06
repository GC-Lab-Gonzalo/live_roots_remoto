/**
 * MIDI Gateway Server - GC Lab Chile
 * Servidor WebSocket para transmision MIDI remota
 *
 * Proyecto: Live Roots - Alerce Milenario
 */

const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const cors = require('cors');

const app = express();
const server = http.createServer(app);

// Configuracion de Socket.io con CORS habilitado
const io = new Server(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  },
  pingTimeout: 60000,
  pingInterval: 25000
});

// Middleware
app.use(cors());
app.use(express.json());

// Estado del sistema
const systemState = {
  emitter: null,
  receivers: new Map(),
  startTime: Date.now(),
  stats: {
    totalMidiMessages: 0,
    totalNotesOn: 0,
    totalNotesOff: 0,
    totalControlChanges: 0
  }
};

// Utilidades
const timestamp = () => {
  const now = new Date();
  return now.toISOString().replace('T', ' ').substr(0, 19);
};

const log = (emoji, message) => {
  console.log(`[${timestamp()}] ${emoji} ${message}`);
};

// Banner ASCII
const showBanner = () => {
  console.log('\n');
  console.log('╔══════════════════════════════════════════════════════════════╗');
  console.log('║                                                              ║');
  console.log('║   ███╗   ███╗██╗██████╗ ██╗     ██████╗  █████╗ ████████╗   ║');
  console.log('║   ████╗ ████║██║██╔══██╗██║    ██╔════╝ ██╔══██╗╚══██╔══╝   ║');
  console.log('║   ██╔████╔██║██║██║  ██║██║    ██║  ███╗███████║   ██║      ║');
  console.log('║   ██║╚██╔╝██║██║██║  ██║██║    ██║   ██║██╔══██║   ██║      ║');
  console.log('║   ██║ ╚═╝ ██║██║██████╔╝██║    ╚██████╔╝██║  ██║   ██║      ║');
  console.log('║   ╚═╝     ╚═╝╚═╝╚═════╝ ╚═╝     ╚═════╝ ╚═╝  ╚═╝   ╚═╝      ║');
  console.log('║                                                              ║');
  console.log('║            MIDI Gateway Server - GC Lab Chile                ║');
  console.log('║                                                              ║');
  console.log('║     Proyecto: Live Roots - Alerce Milenario                  ║');
  console.log('║     Conectando la naturaleza con el arte digital             ║');
  console.log('║                                                              ║');
  console.log('╚══════════════════════════════════════════════════════════════╝');
  console.log('\n');
};

// Endpoint de salud
app.get('/health', (req, res) => {
  const uptime = Math.floor((Date.now() - systemState.startTime) / 1000);
  res.json({
    status: 'online',
    server: 'MIDI Gateway - GC Lab Chile',
    version: '1.0.0',
    uptime: uptime,
    uptimeFormatted: formatUptime(uptime),
    emitter: systemState.emitter ? {
      connected: true,
      name: systemState.emitter.name,
      connectedAt: systemState.emitter.connectedAt
    } : { connected: false },
    receivers: {
      count: systemState.receivers.size,
      list: Array.from(systemState.receivers.values()).map(r => ({
        name: r.name,
        connectedAt: r.connectedAt
      }))
    },
    stats: systemState.stats
  });
});

// Endpoint raiz
app.get('/', (req, res) => {
  res.json({
    name: 'MIDI Gateway Server',
    organization: 'GC Lab Chile',
    project: 'Live Roots - Alerce Milenario',
    status: 'running',
    endpoints: {
      health: '/health',
      websocket: 'ws://[host]:[port]'
    }
  });
});

// Formatear uptime
function formatUptime(seconds) {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;
  return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

// Broadcast estado del sistema
function broadcastSystemStatus() {
  const status = {
    emitterConnected: systemState.emitter !== null,
    emitterName: systemState.emitter?.name || null,
    receiversCount: systemState.receivers.size,
    receivers: Array.from(systemState.receivers.values()).map(r => r.name),
    uptime: Math.floor((Date.now() - systemState.startTime) / 1000),
    stats: systemState.stats
  };
  io.emit('system-status', status);
}

// Manejo de conexiones WebSocket
io.on('connection', (socket) => {
  log('🔌', `Nueva conexion: ${socket.id}`);

  // Cliente se identifica
  socket.on('identify', (data) => {
    const { type, name } = data;

    if (type === 'emitter') {
      // Solo permitir un emisor
      if (systemState.emitter && systemState.emitter.id !== socket.id) {
        log('⚠️', `Emisor rechazado (ya hay uno conectado): ${name}`);
        socket.emit('identify-response', {
          success: false,
          message: 'Ya hay un emisor conectado'
        });
        return;
      }

      systemState.emitter = {
        id: socket.id,
        name: name || 'Emisor Anonimo',
        connectedAt: new Date().toISOString()
      };

      log('✓', `Emisor registrado: ${systemState.emitter.name}`);
      socket.emit('identify-response', { success: true, type: 'emitter' });

      // Notificar a receptores
      io.emit('emitter-status', {
        connected: true,
        name: systemState.emitter.name
      });

    } else if (type === 'receiver') {
      const receiverInfo = {
        id: socket.id,
        name: name || 'Receptor Anonimo',
        connectedAt: new Date().toISOString()
      };

      systemState.receivers.set(socket.id, receiverInfo);
      log('✓', `Receptor registrado: ${receiverInfo.name} (Total: ${systemState.receivers.size})`);

      socket.emit('identify-response', {
        success: true,
        type: 'receiver',
        emitterConnected: systemState.emitter !== null,
        emitterName: systemState.emitter?.name || null
      });
    }

    broadcastSystemStatus();
  });

  // Recibir datos MIDI del emisor
  socket.on('midi-data', (data) => {
    // Verificar que es el emisor
    if (!systemState.emitter || systemState.emitter.id !== socket.id) {
      log('⚠️', `Datos MIDI rechazados de no-emisor: ${socket.id}`);
      return;
    }

    // Actualizar estadisticas
    systemState.stats.totalMidiMessages++;
    if (data.type === 'note_on') {
      systemState.stats.totalNotesOn++;
      log('🎵', `Note ON: ${data.note} vel:${data.velocity} ch:${data.channel}`);
    } else if (data.type === 'note_off') {
      systemState.stats.totalNotesOff++;
      log('🎵', `Note OFF: ${data.note} ch:${data.channel}`);
    } else if (data.type === 'control_change') {
      systemState.stats.totalControlChanges++;
      log('🎛️', `CC: ${data.control}=${data.value} ch:${data.channel}`);
    }

    // Retransmitir a todos los receptores
    const receiversCount = systemState.receivers.size;
    systemState.receivers.forEach((receiver, receiverId) => {
      io.to(receiverId).emit('midi-data', {
        ...data,
        timestamp: Date.now(),
        source: systemState.emitter.name
      });
    });

    // Confirmar al emisor
    socket.emit('midi-sent', {
      success: true,
      receiversCount: receiversCount
    });
  });

  // Ping/Pong para heartbeat
  socket.on('ping', () => {
    socket.emit('pong', { timestamp: Date.now() });
  });

  // Desconexion
  socket.on('disconnect', (reason) => {
    log('🔌', `Desconexion: ${socket.id} - Razon: ${reason}`);

    // Verificar si era el emisor
    if (systemState.emitter && systemState.emitter.id === socket.id) {
      const emitterName = systemState.emitter.name;
      systemState.emitter = null;
      log('⚠️', `Emisor desconectado: ${emitterName}`);

      // Notificar a receptores
      io.emit('emitter-status', { connected: false, name: emitterName });
    }

    // Verificar si era un receptor
    if (systemState.receivers.has(socket.id)) {
      const receiver = systemState.receivers.get(socket.id);
      systemState.receivers.delete(socket.id);
      log('⚠️', `Receptor desconectado: ${receiver.name} (Restantes: ${systemState.receivers.size})`);
    }

    broadcastSystemStatus();
  });

  // Error en socket
  socket.on('error', (error) => {
    log('✗', `Error en socket ${socket.id}: ${error.message}`);
  });
});

// Broadcast periodico del estado (cada 30 segundos)
setInterval(() => {
  broadcastSystemStatus();
}, 30000);

// Iniciar servidor
const PORT = process.env.PORT || 3000;

server.listen(PORT, () => {
  showBanner();
  log('✓', `Servidor iniciado en puerto ${PORT}`);
  log('✓', `Health check: http://localhost:${PORT}/health`);
  log('✓', `WebSocket listo para conexiones`);
  console.log('\n');
  log('🌿', 'Esperando conexion del Alerce Milenario...');
  console.log('\n');
});

// Manejo de cierre limpio
process.on('SIGTERM', () => {
  log('⚠️', 'Recibida senal SIGTERM, cerrando servidor...');
  io.emit('server-shutdown', { message: 'Servidor cerrando' });
  server.close(() => {
    log('✓', 'Servidor cerrado correctamente');
    process.exit(0);
  });
});

process.on('SIGINT', () => {
  log('⚠️', 'Recibida senal SIGINT, cerrando servidor...');
  io.emit('server-shutdown', { message: 'Servidor cerrando' });
  server.close(() => {
    log('✓', 'Servidor cerrado correctamente');
    process.exit(0);
  });
});
