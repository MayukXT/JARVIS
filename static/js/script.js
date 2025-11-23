const socket = io();
const chatArea = document.getElementById('chat-area');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const micBtn = document.getElementById('mic-btn');
const voiceVisualizer = document.getElementById('voice-visualizer');
const modeToggle = document.getElementById('mode-toggle');
const errorToast = document.getElementById('error-toast');
const errorMessage = document.getElementById('error-message');

// Navigation
const navItems = document.querySelectorAll('.nav-item');
const views = document.querySelectorAll('.view-section');

navItems.forEach(item => {
    item.addEventListener('click', () => {
        navItems.forEach(nav => nav.classList.remove('active'));
        item.classList.add('active');

        // Hide all views
        views.forEach(view => {
            view.classList.remove('active');
            view.style.display = ''; // Clear inline styles
        });

        const viewId = 'view-' + item.id.replace('nav-', '');
        const viewElement = document.getElementById(viewId);
        if (viewElement) {
            viewElement.classList.add('active');
        }

        if (item.id === 'nav-logs') socket.emit('get_logs');
        if (item.id === 'nav-settings') socket.emit('get_models');
    });
});

// Model Selection
const modelSelect = document.getElementById('model-select');
if (modelSelect) {
    modelSelect.addEventListener('change', (e) => {
        socket.emit('set_model', { model: e.target.value });
    });
}

socket.on('models_list', (data) => {
    if (modelSelect) {
        modelSelect.innerHTML = '';
        data.models.forEach(model => {
            const option = document.createElement('option');
            option.value = model;
            option.textContent = model;
            if (model === data.current) option.selected = true;
            modelSelect.appendChild(option);
        });
    }
});

// --- VOICE LOGIC (Python Speech Recognition via WebSocket) ---

let mediaRecorder;
let audioStream;
let mode = 'ai'; // 'ai' or 'task'
let isManualListening = false; // AI Mode state
let isAwake = false; // Task Mode state
let finalTranscript = ''; // To accumulate text in AI mode
let messageSent = false; // Track if message was sent to clear transcript

const audioConstraints = {
    audio: {
        channelCount: 1,
        sampleRate: 16000
    }
};

// Initialize audio streaming
async function initAudioStreaming() {
    try {
        audioStream = await navigator.mediaDevices.getUserMedia(audioConstraints);
        console.log("Microphone access granted");
        return true;
    } catch (error) {
        console.error("Microphone access denied:", error);
        showError("Microphone access denied. Please allow microphone access.");
        micBtn.style.display = 'none';
        return false;
    }
}

// Start recording and streaming audio
function startRecording() {
    if (!audioStream) {
        showError("Microphone not initialized");
        return;
    }

    // Safety check: In AI mode, only record if manually listening
    if (mode === 'ai' && !isManualListening) {
        return;
    }

    // Reset placeholder to Listening if we are restarting the loop in AI mode
    if (mode === 'ai' && isManualListening) {
        userInput.placeholder = "Listening...";
    }

    const options = { mimeType: 'audio/webm' };
    mediaRecorder = new MediaRecorder(audioStream, options);

    let accumulatedChunks = [];

    mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
            accumulatedChunks.push(event.data);
        }
    };

    mediaRecorder.onstop = () => {
        if (accumulatedChunks.length > 0) {
            // Merge all chunks into a single blob
            const completeBlob = new Blob(accumulatedChunks, { type: 'audio/webm' });

            // Show transcribing indicator ONLY if we are in AI mode and manually listening
            // This prevents it from showing when we stop (toggle off) or in Task Mode
            if (mode === 'ai' && isManualListening) {
                userInput.placeholder = "Transcribing...";
            }

            // Convert blob to base64 and send to server
            const reader = new FileReader();
            reader.onloadend = () => {
                const base64Audio = reader.result.split(',')[1];
                socket.emit('audio_chunk', { audio: base64Audio });
            };
            reader.readAsDataURL(completeBlob);

            accumulatedChunks = [];
        }

        // Restart recording if still listening or in Task Mode (to catch wake word)
        if (isManualListening || mode === 'task') {
            setTimeout(() => {
                if (mediaRecorder && (isManualListening || mode === 'task')) {
                    startRecording();
                }
            }, 100);
        }
    };

    mediaRecorder.onerror = (error) => {
        console.error("MediaRecorder error:", error);
    };

    // Record for 3 seconds then stop (creates complete WebM file)
    mediaRecorder.start();
    setTimeout(() => {
        if (mediaRecorder && mediaRecorder.state === 'recording') {
            mediaRecorder.stop();
        }
    }, 3000);

    console.log("Recording started - will capture 3-second chunks");
}

function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
        console.log("Recording stopped");
    }
}

// Socket event handlers for speech recognition
socket.on('speech_started', (data) => {
    console.log("Speech recognition started. Mode:", data.mode);
    startRecording();

    if (data.mode === 'ai') {
        if (isManualListening) {
            micBtn.classList.add('listening');
            voiceVisualizer.classList.add('active');
            userInput.placeholder = "Listening...";
        }
    } else {
        // Task Mode - always listening, but UI changes based on awake state
        console.log("Task mode listening started. Awake:", isAwake);
        if (isAwake) {
            micBtn.classList.add('listening');
            voiceVisualizer.classList.add('active');
            userInput.placeholder = "Listening for command...";
        } else {
            // Standby mode - listening for wake word
            micBtn.classList.remove('listening');
            micBtn.style.opacity = '0.5';
            voiceVisualizer.classList.remove('active');
            userInput.placeholder = "Say 'Hey JARVIS'...";
        }
    }
});

socket.on('speech_stopped', () => {
    console.log("Speech recognition stopped");
    stopRecording();

    if (mode === 'ai' && !isManualListening) {
        micBtn.classList.remove('listening');
        voiceVisualizer.classList.remove('active');
        userInput.placeholder = "Write or speak...";
    } else if (mode === 'ai' && isManualListening) {
        // Even if manual listening was on, if we get a stop signal that implies we should stop
        // But usually speech_stopped comes from server. 
        // If user toggled off, we handle in click handler.
        // If server stopped it (e.g. error), we should reset.
    }
});

socket.on('speech_interim', (data) => {
    console.log("Interim result:", data.text);
    if (mode === 'ai') {
        userInput.value = data.full_transcript;
        userInput.placeholder = "Listening...";
        updateSendButtonState();
    }
});

socket.on('speech_final', (data) => {
    console.log("Final result:", data.text);

    // Clear transcribing indicator
    if (mode === 'ai') {
        finalTranscript = data.full_transcript || '';
        userInput.value = finalTranscript;
        updateSendButtonState();
        messageSent = false; // Reset message sent flag
        if (isManualListening) {
            userInput.placeholder = "Listening...";
        } else {
            userInput.placeholder = "Write or speak...";
        }
    } else {
        // Task Mode - display command
        if (data.text) {
            // Append text in Task Mode to avoid overwriting with empty strings and handle multiple chunks
            const currentVal = userInput.value.trim();
            userInput.value = currentVal ? (currentVal + ' ' + data.text) : data.text;
            updateSendButtonState();
        }

        // Keep correct placeholder based on state
        if (isAwake) {
            userInput.placeholder = "Listening for command...";
        } else {
            userInput.placeholder = "Say 'Hey JARVIS'...";
        }
    }
});

// Sync transcript with manual edits
userInput.addEventListener('input', () => {
    if (mode === 'ai') {
        finalTranscript = userInput.value;
    }

    // Reset height to auto to get the correct scrollHeight
    userInput.style.height = 'auto';

    // Set height based on scrollHeight (capped by max-height in CSS)
    userInput.style.height = userInput.scrollHeight + 'px';

    // Update send button state
    updateSendButtonState();
});

socket.on('wake_word_detected', () => {
    console.log("Wake word detected!");
    isAwake = true;
    micBtn.classList.add('listening');
    micBtn.style.opacity = '1';
    voiceVisualizer.classList.add('active');
    userInput.placeholder = "Listening for command...";
    userInput.value = '';
    updateSendButtonState();
});

socket.on('task_mode_sleep', () => {
    console.log("Task mode going to sleep");
    isAwake = false;
    micBtn.classList.remove('listening');
    micBtn.style.opacity = '0.5';
    voiceVisualizer.classList.remove('active');
    userInput.placeholder = "Say 'Hey JARVIS'...";
    userInput.value = '';
    updateSendButtonState();

    // Keep recording active but in standby mode
    console.log("Task Mode: Back to standby, listening for wake word...");
});

socket.on('silence_timeout', () => {
    console.log("Silence timeout - auto-sending command");
    if (userInput.value.trim()) {
        sendMessage();
    }
});

socket.on('speech_error', (data) => {
    console.error("Speech error:", data.error);
    showError("Speech recognition error: " + data.error);
});

// Mode Toggle Handler
modeToggle.addEventListener('change', () => {
    mode = modeToggle.checked ? 'ai' : 'task';
    console.log("Mode switched to:", mode);

    // Reset states
    isManualListening = false;
    isAwake = false;
    finalTranscript = '';

    // Stop current recognition
    socket.emit('stop_speech');

    // UI Updates
    userInput.value = '';
    updateSendButtonState();
    updateMicUI();

    // Send mode change to server
    socket.emit('voice_mode_changed', { mode: mode });

    // Task Mode starts automatically
    if (mode === 'task') {
        setTimeout(() => {
            socket.emit('start_speech', { mode: 'task' });
        }, 200);
    }
});

// Mic Button Handler
micBtn.addEventListener('click', () => {
    if (mode === 'ai') {
        if (isManualListening) {
            // Stop (Manual)
            isManualListening = false;
            socket.emit('stop_speech');
            micBtn.classList.remove('listening');
            voiceVisualizer.classList.remove('active');
            userInput.placeholder = "Write or speak...";
        } else {
            // Start (Manual)
            isManualListening = true;
            // Capture current input to preserve it (and handle deletions)
            const currentText = userInput.value;
            finalTranscript = currentText; // Sync local transcript

            userInput.placeholder = "Listening...";
            socket.emit('start_speech', {
                mode: 'ai',
                current_text: currentText
            });
        }
    } else {
        // Task Mode: Manual Wake Up / Sleep
        if (isAwake) {
            socket.emit('manual_sleep');
        } else {
            socket.emit('manual_wake');
        }
    }
});

function updateMicUI() {
    micBtn.classList.remove('listening');
    voiceVisualizer.classList.remove('active');
    micBtn.style.opacity = '1';
    if (mode === 'task') {
        userInput.placeholder = "Say 'Hey JARVIS'...";
        micBtn.style.opacity = '0.5';
    } else {
        userInput.placeholder = "Write or speak...";
    }
}

// Initialize audio on connect
socket.on('connect', () => {
    console.log('Connected');
    initAudioStreaming().then(success => {
        if (success) {
            // Initialize mode
            mode = modeToggle.checked ? 'ai' : 'task';
            if (mode === 'task') {
                socket.emit('start_speech', { mode: 'task' });
            }
        }
    });
});

// --- STANDARD CHAT LOGIC ---

// SocketIO Events
socket.on('connect', () => {
    console.log('Connected');
    // Initialize mode
    mode = modeToggle.checked ? 'ai' : 'task';
    if (mode === 'task') {
        try { recognition.start(); } catch (e) { }
    }
});

socket.on('disconnect', () => {
    console.log('Disconnected');
    document.getElementById('status-system').textContent = 'OFFLINE';
    document.getElementById('status-system').className = 'value';
});

socket.on('system_status', (data) => {
    document.getElementById('status-system').textContent = data.status.toUpperCase();
    document.getElementById('status-system').className = data.status === 'Online' ? 'value online' : 'value';
    if (data.model) {
        document.getElementById('status-model').textContent = data.model;
    }
});

socket.on('model_changed', (data) => {
    document.getElementById('status-model').textContent = data.model;
});

socket.on('system_message', (data) => {
    addSystemMessage(data.message, data.type);
});

socket.on('processing_start', () => {
    showThinking();
});

socket.on('processing_end', () => {
    hideThinking();
});

socket.on('bot_response', (data) => {
    hideThinking();
    addMessage(data.response, 'bot', data.stats);
    speak(data.response);
    if (data.context_usage) updateContextBar(data.context_usage);
});

// Streaming response handlers
let currentStreamingMessage = null;
let currentStreamingContent = null;

socket.on('bot_response_start', () => {
    hideThinking();

    // Create message structure
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', 'bot');

    const avatarDiv = document.createElement('div');
    avatarDiv.classList.add('avatar');
    avatarDiv.innerHTML = '<img src="static/images/jarvis_icon.png" alt="AI">';

    const contentDiv = document.createElement('div');
    contentDiv.classList.add('content');
    const p = document.createElement('p');
    p.textContent = '';

    contentDiv.appendChild(p);
    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(contentDiv);
    chatArea.appendChild(messageDiv);

    currentStreamingMessage = messageDiv;
    currentStreamingContent = p;
    chatArea.scrollTop = chatArea.scrollHeight;
});

socket.on('bot_response_chunk', (data) => {
    if (currentStreamingContent) {
        currentStreamingContent.textContent += data.chunk;
        chatArea.scrollTop = chatArea.scrollHeight; // Auto-scroll
    }
});

socket.on('bot_response_complete', (data) => {
    if (currentStreamingMessage && currentStreamingContent) {
        // Add timestamp and stats
        const timestamp = document.createElement('span');
        timestamp.classList.add('timestamp');
        timestamp.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        currentStreamingContent.parentElement.appendChild(timestamp);

        if (data.stats) {
            const statsDiv = document.createElement('div');
            statsDiv.classList.add('message-stats');
            statsDiv.innerHTML = `<span>${data.stats.tokens} tokens</span> • <span>${data.stats.time}</span>`;
            currentStreamingContent.parentElement.appendChild(statsDiv);
        }

        // Speak the complete message
        speak(currentStreamingContent.textContent);

        if (data.context_usage) updateContextBar(data.context_usage);

        currentStreamingMessage = null;
        currentStreamingContent = null;
    }
});

socket.on('system_stats', (data) => updateDashboard(data));
socket.on('error_message', (data) => showError(data.error));
socket.on('logs_update', (data) => {
    const logsArea = document.getElementById('logs-area');
    if (logsArea) {
        // Highlight errors
        const formattedLogs = data.logs.replace(/ERROR/g, '<span class="log-error">ERROR</span>');
        logsArea.innerHTML = formattedLogs; // Use innerHTML for spans
        logsArea.scrollTop = logsArea.scrollHeight;
    }
});

// TTS
function speak(text) {
    const voiceToggle = document.getElementById('voice-toggle');
    if (voiceToggle && !voiceToggle.checked) return;

    const synth = window.speechSynthesis;
    if (!synth) return;

    synth.cancel();
    const cleanText = text.replace(/[*`#]/g, '');
    const utterance = new SpeechSynthesisUtterance(cleanText);
    synth.speak(utterance);
}

// Chat UI
sendBtn.addEventListener('click', sendMessage);

// Auto-expand textarea
// Auto-expand textarea handled in the input listener above

// Handle Enter key - send on Enter, new line on Shift+Enter
userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

function updateSendButtonState() {
    const hasContent = userInput.value.trim().length > 0;
    if (hasContent) {
        sendBtn.classList.add('active');
    } else {
        sendBtn.classList.remove('active');
    }
}

function sendMessage() {
    const message = userInput.value.trim();
    if (message) {
        addMessage(message, 'user');
        socket.emit('user_message', {
            message: message,
            mode: mode
        });

        // Clear input with smooth transition
        userInput.value = '';
        userInput.style.height = 'auto'; // Reset height
        finalTranscript = ''; // Clear transcript after sending
        messageSent = true; // Mark that message was sent
        updateSendButtonState(); // Update button state
    }
}

function addMessage(text, sender, stats = null) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', sender);

    const avatarDiv = document.createElement('div');
    avatarDiv.classList.add('avatar');
    if (sender === 'bot') {
        avatarDiv.innerHTML = '<img src="static/images/jarvis_icon.png" alt="AI">';
    } else {
        avatarDiv.innerHTML = '<i class="fas fa-user"></i>';
    }

    const contentDiv = document.createElement('div');
    contentDiv.classList.add('content');
    const p = document.createElement('p');
    p.textContent = text;

    const timestamp = document.createElement('span');
    timestamp.classList.add('timestamp');
    timestamp.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    contentDiv.appendChild(p);
    contentDiv.appendChild(timestamp);

    if (stats) {
        const statsDiv = document.createElement('div');
        statsDiv.classList.add('message-stats');
        statsDiv.innerHTML = `<span>${stats.tokens} tokens</span> • <span>${stats.time}</span>`;
        contentDiv.appendChild(statsDiv);
    }

    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(contentDiv);
    chatArea.appendChild(messageDiv);
    chatArea.scrollTop = chatArea.scrollHeight;
}

let thinkingDiv = null;

function showThinking() {
    if (thinkingDiv) return;

    thinkingDiv = document.createElement('div');
    thinkingDiv.classList.add('message', 'bot', 'thinking-message');

    const avatarDiv = document.createElement('div');
    avatarDiv.classList.add('avatar');
    avatarDiv.innerHTML = '<img src="static/images/jarvis_icon.png" alt="AI">';

    const contentDiv = document.createElement('div');
    contentDiv.classList.add('content', 'thinking-bubble');
    contentDiv.innerHTML = '<div class="dot"></div><div class="dot"></div><div class="dot"></div> <span>Processing...</span>';

    thinkingDiv.appendChild(avatarDiv);
    thinkingDiv.appendChild(contentDiv);
    chatArea.appendChild(thinkingDiv);
    chatArea.scrollTop = chatArea.scrollHeight;
}

function hideThinking() {
    if (thinkingDiv) {
        thinkingDiv.remove();
        thinkingDiv = null;
    }
}

function addSystemMessage(text, type) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', 'system');

    const contentDiv = document.createElement('div');
    contentDiv.classList.add('content', 'system-content', type); // type: 'warning' or 'error'

    const icon = type === 'error' ? '<i class="fas fa-exclamation-circle"></i>' : '<i class="fas fa-exclamation-triangle"></i>';

    contentDiv.innerHTML = `${icon} <span>${text}</span>`;

    messageDiv.appendChild(contentDiv);
    chatArea.appendChild(messageDiv);
    chatArea.scrollTop = chatArea.scrollHeight;
}

// Charts
let cpuChart, ramChart;

function initCharts() {
    const cpuCtx = document.getElementById('cpuChart');
    const ramCtx = document.getElementById('ramChart');

    if (cpuCtx && ramCtx) {
        const commonOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, max: 100, grid: { color: 'rgba(255, 255, 255, 0.1)' } },
                x: { display: false }
            },
            elements: {
                line: { tension: 0.4, borderColor: '#00f3ff', borderWidth: 2, fill: true, backgroundColor: 'rgba(0, 243, 255, 0.1)' },
                point: { radius: 0 }
            }
        };

        cpuChart = new Chart(cpuCtx, {
            type: 'line',
            data: { labels: Array(20).fill(''), datasets: [{ data: Array(20).fill(0) }] },
            options: commonOptions
        });

        ramChart = new Chart(ramCtx, {
            type: 'line',
            data: { labels: Array(20).fill(''), datasets: [{ data: Array(20).fill(0) }] },
            options: commonOptions
        });
    }
}

// Initialize charts on load
document.addEventListener('DOMContentLoaded', initCharts);

function updateDashboard(data) {
    document.getElementById('cpu-value').textContent = data.cpu + '%';
    document.getElementById('ram-value').textContent = data.ram + '%';

    const ramMb = document.getElementById('ram-mb');
    if (ramMb && data.ram_mb) {
        ramMb.textContent = data.ram_mb + ' MB';
    }

    if (cpuChart) {
        cpuChart.data.datasets[0].data.push(data.cpu);
        cpuChart.data.datasets[0].data.shift();
        cpuChart.update('none'); // 'none' mode for performance
    }

    if (ramChart) {
        ramChart.data.datasets[0].data.push(data.ram);
        ramChart.data.datasets[0].data.shift();
        ramChart.update('none');
    }
}

function updateContextBar(usage) {
    const fill = document.getElementById('context-fill');
    const stats = document.getElementById('context-stats');
    if (fill && stats) {
        const percentage = Math.min(100, (usage.current / usage.max) * 100);
        fill.style.width = percentage + '%';
        stats.textContent = `${usage.current} / ${usage.max} tokens`;
    }
}

function showError(msg) {
    errorMessage.textContent = msg;
    errorToast.classList.add('show');
    setTimeout(() => errorToast.classList.remove('show'), 5000);
}
