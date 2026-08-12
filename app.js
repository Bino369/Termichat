/**
 * TermiChat Web App JavaScript Client
 * Manages WebSocket connectivity, UI state, themes, and sound effects.
 */

document.addEventListener('DOMContentLoaded', () => {
  // DOM Elements
  const messageContainer = document.getElementById('message-container');
  const chatForm = document.getElementById('chat-form');
  const messageInput = document.getElementById('message-input');
  const statusBadge = document.getElementById('status-badge');
  const statusText = document.getElementById('status-text');
  const serverAddressDisplay = document.getElementById('server-address-display');
  const heroIpDisplay = document.getElementById('hero-ip-display');
  
  // Controls & Modals
  const soundBtn = document.getElementById('sound-btn');
  const themeBtn = document.getElementById('theme-btn');
  const settingsBtn = document.getElementById('settings-btn');
  const connectionModal = document.getElementById('connection-modal');
  const closeModalBtn = document.getElementById('close-modal-btn');
  const usernameInput = document.getElementById('username-input');
  const wsUrlInput = document.getElementById('ws-url-input');
  const connectModalBtn = document.getElementById('connect-modal-btn');
  const quickChips = document.querySelectorAll('.quick-chip');

  // Application State
  let socket = null;
  let isSoundEnabled = true;
  let username = localStorage.getItem('termichat_user') || 'User_' + Math.floor(1000 + Math.random() * 9000);
  usernameInput.value = username;

  // Compute default WebSocket URL
  const loc = window.location;
  let defaultWsHost = loc.hostname || 'localhost';
  let defaultWsPort = loc.port || '8000';
  let defaultWsUrl = `${loc.protocol === 'https:' ? 'wss:' : 'ws:'}//${defaultWsHost}:${defaultWsPort}/ws`;
  
  let wsUrl = localStorage.getItem('termichat_ws_url') || defaultWsUrl;
  wsUrlInput.value = wsUrl;

  // Display initial IP info
  const hostIp = loc.hostname || '127.0.0.1';
  serverAddressDisplay.textContent = `Server IP: ${hostIp}:${defaultWsPort}`;
  heroIpDisplay.textContent = `${hostIp}:${defaultWsPort}`;

  // ------------------------------------------------------------------------
  // Web Audio API Sound Chime
  // ------------------------------------------------------------------------
  function playChime() {
    if (!isSoundEnabled) return;
    try {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (!AudioCtx) return;
      const ctx = new AudioCtx();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      osc.type = 'sine';
      osc.frequency.setValueAtTime(587.33, ctx.currentTime); // D5
      osc.frequency.exponentialRampToValueAtTime(880, ctx.currentTime + 0.15); // A5

      gain.gain.setValueAtTime(0.12, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.3);

      osc.connect(gain);
      gain.connect(ctx.destination);

      osc.start();
      osc.stop(ctx.currentTime + 0.3);
    } catch (e) {
      console.warn('Audio playback inhibited:', e);
    }
  }

  // ------------------------------------------------------------------------
  // UI Helper Functions
  // ------------------------------------------------------------------------
  function setStatus(state, text) {
    statusBadge.className = `status-badge status-${state}`;
    statusText.textContent = text;
  }

  function formatTime() {
    const now = new Date();
    return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  function appendSystemNotification(text) {
    const div = document.createElement('div');
    div.className = 'system-notify';
    div.textContent = text;
    messageContainer.appendChild(div);
    scrollToBottom();
  }

  function appendMessage(sender, text, isSelf) {
    const row = document.createElement('div');
    row.className = `message-row ${isSelf ? 'sent' : 'received'}`;

    if (!isSelf) {
      const senderLabel = document.createElement('div');
      senderLabel.className = 'message-sender';
      senderLabel.textContent = sender || 'Them';
      row.appendChild(senderLabel);
    }

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    bubble.textContent = text;

    const timeSpan = document.createElement('span');
    timeSpan.className = 'message-time';
    timeSpan.textContent = formatTime();
    bubble.appendChild(timeSpan);

    row.appendChild(bubble);
    messageContainer.appendChild(row);

    scrollToBottom();

    if (!isSelf) {
      playChime();
    }
  }

  function scrollToBottom() {
    messageContainer.scrollTop = messageContainer.scrollHeight;
  }

  // ------------------------------------------------------------------------
  // WebSocket Manager
  // ------------------------------------------------------------------------
  function connectWebSocket() {
    setStatus('connecting', 'Connecting...');
    wsUrl = wsUrlInput.value.trim() || defaultWsUrl;
    localStorage.setItem('termichat_ws_url', wsUrl);

    try {
      if (socket) {
        socket.close();
      }

      socket = new WebSocket(wsUrl);

      socket.onopen = () => {
        setStatus('connected', 'Connected');
        appendSystemNotification(`Connected to ${wsUrl}`);
      };

      socket.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          if (payload.type === 'message') {
            appendMessage(payload.sender, payload.text, payload.sender === username);
          } else if (payload.type === 'system') {
            appendSystemNotification(payload.text);
          } else {
            // Raw text fallback
            appendMessage('Them', event.data, false);
          }
        } catch (e) {
          // Plain text fallback
          appendMessage('Them', event.data, false);
        }
      };

      socket.onerror = (err) => {
        console.error('WebSocket Error:', err);
        setStatus('disconnected', 'Error');
      };

      socket.onclose = () => {
        setStatus('disconnected', 'Disconnected');
        appendSystemNotification('Disconnected from server.');
      };
    } catch (err) {
      console.error('Failed to create WebSocket:', err);
      setStatus('disconnected', 'Failed');
    }
  }

  // ------------------------------------------------------------------------
  // Event Listeners
  // ------------------------------------------------------------------------
  chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const text = messageInput.value.trim();
    if (!text) return;

    if (socket && socket.readyState === WebSocket.OPEN) {
      const msgObj = {
        type: 'message',
        sender: username,
        text: text
      };
      socket.send(JSON.stringify(msgObj));
      appendMessage(username, text, true);
      messageInput.value = '';
    } else {
      appendSystemNotification('Cannot send message: Not connected to WebSocket server.');
    }
  });

  // Quick Chips
  quickChips.forEach(chip => {
    chip.addEventListener('click', () => {
      messageInput.value = chip.getAttribute('data-msg');
      messageInput.focus();
    });
  });

  // Sound Toggle
  soundBtn.addEventListener('click', () => {
    isSoundEnabled = !isSoundEnabled;
    soundBtn.style.opacity = isSoundEnabled ? '1' : '0.4';
    appendSystemNotification(`Sound effects ${isSoundEnabled ? 'enabled' : 'disabled'}.`);
  });

  // Theme Toggle
  themeBtn.addEventListener('click', () => {
    document.body.classList.toggle('theme-matrix');
    const isMatrix = document.body.classList.contains('theme-matrix');
    appendSystemNotification(`Theme switched to ${isMatrix ? 'Matrix Green' : 'Cyber Dark'}.`);
  });

  // Settings Modal Controls
  settingsBtn.addEventListener('click', () => {
    connectionModal.classList.remove('hidden');
  });

  closeModalBtn.addEventListener('click', () => {
    connectionModal.classList.add('hidden');
  });

  connectModalBtn.addEventListener('click', () => {
    username = usernameInput.value.trim() || 'User';
    localStorage.setItem('termichat_user', username);
    connectionModal.classList.add('hidden');
    connectWebSocket();
  });

  // Auto connect on startup
  connectWebSocket();
});
