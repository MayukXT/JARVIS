from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import os
import psutil
import threading
import logging
import time
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()
from core.jarvis_engine import JarvisEngine
from core.speech_service import SpeechService

# Initialize Flask and SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='threading')

# Logging Setup
log_buffer = []
class ListHandler(logging.Handler):
    def emit(self, record):
        try:
            log_entry = self.format(record)
            log_buffer.append(log_entry)
            if len(log_buffer) > 500:
                log_buffer.pop(0)
            # Emit logs to client if connected
            socketio.emit('logs_update', {'logs': '\n'.join(log_buffer)})
        except:
            pass

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger()
logger.addHandler(ListHandler())

# Initialize Jarvis Engine and Speech Service
jarvis = JarvisEngine()
speech_service = None  # Will be initialized after socketio

# State
current_model = 'gemini-2.0-flash-lite'
context_history = []
MAX_CONTEXT_TOKENS = 32000
total_tokens_used = 0

# Background Thread for System Stats
thread = None
thread_lock = threading.Lock()

def background_thread():
    """Emit system stats periodically."""
    process = psutil.Process(os.getpid())
    while True:
        try:
            # JARVIS-specific usage
            cpu = process.cpu_percent(interval=0.1)
            ram_bytes = process.memory_info().rss
            ram_mb = ram_bytes / (1024 * 1024) # MB
            
            # Calculate RAM % of system
            total_ram = psutil.virtual_memory().total
            ram_percent = (ram_bytes / total_ram) * 100
            
            socketio.emit('system_stats', {
                'cpu': cpu, 
                'ram': round(ram_percent, 1),
                'ram_mb': round(ram_mb, 1),
                'tokens': total_tokens_used
            })
            socketio.sleep(2)
        except Exception as e:
            logger.error(f"Error in background thread: {e}")
            socketio.sleep(5)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('user_message')
def handle_message(data):
    """Handle incoming text messages from the client."""
    global total_tokens_used
    query = data.get('message')
    mode = data.get('mode', 'ai')
    
    if not query:
        return

    start_time = time.time()
    # --- ROUTING LOGIC ---
    is_task_command = False
    task_keywords = ["open", "close", "turn", "set", "change", "play", "stop", "start"]
    if any(query.lower().startswith(k) for k in task_keywords):
        is_task_command = True

    # Log the effective mode
    log_mode = mode
    if mode == 'ai' and is_task_command:
        log_mode = 'task (auto)'

    logger.info(f"Received message: {query} [Mode: {log_mode}]")
    emit('processing_start') # Notify client processing started

    if mode == 'task':
        if not is_task_command:
            # STRICT TASK MODE: Do not use LLM
            emit('system_message', {'type': 'warning', 'message': f"Command '{query}' not recognized as a task."})
            emit('processing_end')
            return
        else:
            try:
                response = jarvis.process_command(query, mode='task', model_name=current_model)
                emit('bot_response', {'response': response}) 
            except Exception as e:
                logger.error(f"Task Error: {e}")
                emit('system_message', {'type': 'error', 'message': f"Task failed: {str(e)}"})
            emit('processing_end')
            return

    # AI Mode (with Task Override)
    if is_task_command:
        logger.info(f"Routing '{query}' to Task Execution (AI Mode Override)")
        try:
            response = jarvis.process_command(query, mode='task', model_name=current_model)
            emit('bot_response', {'response': f"[Task Executed] {response}"})
        except Exception as e:
            logger.error(f"Task Error: {e}")
            emit('system_message', {'type': 'error', 'message': f"Task failed: {str(e)}"})
        emit('processing_end')
        return

    # AI Conversation
    user_tokens = len(query) // 4
    context_history.append({'role': 'user', 'content': query, 'tokens': user_tokens})
    
    try:
        model_start = time.time()
        
        # Import streaming function
        from core.Gemini import gemini_chat_stream
        
        # Emit streaming start
        emit('bot_response_start')
        
        full_response = ""
        for chunk in gemini_chat_stream(query, model_name=current_model):
            full_response += chunk
            emit('bot_response_chunk', {'chunk': chunk})
            socketio.sleep(0)  # Allow other events to process
        
        response = full_response
        model_end = time.time()
        model_duration = model_end - model_start
    except Exception as e:
        logger.error(f"Error processing command: {e}")
        response = f"I encountered an error: {str(e)}"
        emit('system_message', {'type': 'error', 'message': str(e)})
        emit('processing_end')
        return
    
    
    bot_tokens = len(response) // 4
    context_history.append({'role': 'model', 'content': response, 'tokens': bot_tokens})
    total_tokens_used += (user_tokens + bot_tokens)
    
    current_context_tokens = sum(msg['tokens'] for msg in context_history)
    
    end_time = time.time()
    total_duration = end_time - start_time
    
    # Verbose Logging
    logger.info(f"--- Processing Stats ---")
    logger.info(f"Total Time: {total_duration:.4f}s")
    logger.info(f"Model Gen Time: {model_duration:.4f}s")
    logger.info(f"Output Tokens: {bot_tokens}")
    logger.info(f"------------------------")

    # Emit completion with stats
    emit('bot_response_complete', {
        'context_usage': {
            'current': current_context_tokens,
            'max': MAX_CONTEXT_TOKENS
        },
        'stats': {
            'time': f"{total_duration * 1000:.0f}ms",
            'tokens': bot_tokens
        }
    })
    
    # Clear speech transcript for this session
    if speech_service:
        speech_service.reset_session_transcript(request.sid)
        
    emit('processing_end')

@socketio.on('get_logs')
def handle_get_logs():
    emit('logs_update', {'logs': '\n'.join(log_buffer)})

@socketio.on('get_models')
def handle_get_models():
    # List available models
    models = [
        'gemini-2.0-flash-lite', 
        'gemini-1.5-flash', 
        'gemini-1.5-pro', 
        'gemini-1.0-pro',
        'gemini-pro-vision'
    ]
    emit('models_list', {'models': models, 'current': current_model})

@socketio.on('set_model')
def handle_set_model(data):
    global current_model
    current_model = data.get('model')
    logger.info(f"Model switched to: {current_model}")
    emit('model_changed', {'model': current_model})

@socketio.on('connect')
def test_connect():
    logger.info('Client connected')
    emit('system_status', {'status': 'Online', 'cpu': 'Active', 'model': current_model})
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)

@socketio.on('disconnect')
def test_disconnect():
    logger.info('Client disconnected')
    # Clean up speech session
    if speech_service:
        speech_service.destroy_session(request.sid)

# --- SPEECH RECOGNITION ENDPOINTS ---

@socketio.on('start_speech')
def handle_start_speech(data):
    """Start speech recognition"""
    mode = data.get('mode', 'ai')
    current_text = data.get('current_text', '')
    logger.info(f"Starting speech recognition in {mode} mode with text: '{current_text}'")
    speech_service.start_listening(request.sid, mode, initial_text=current_text)

@socketio.on('stop_speech')
def handle_stop_speech():
    """Stop speech recognition"""
    logger.info("Stopping speech recognition")
    speech_service.stop_listening(request.sid)

@socketio.on('audio_chunk')
def handle_audio_chunk(data):
    """Receive and process audio chunk"""
    audio_data = data.get('audio')
    if audio_data:
        speech_service.process_audio_chunk(request.sid, audio_data)

@socketio.on('voice_mode_changed')
def handle_voice_mode_changed(data):
    """Handle mode toggle"""
    mode = data.get('mode')
    logger.info(f"Voice mode changed to: {mode}")
    speech_service.set_mode(request.sid, mode)

@socketio.on('manual_wake')
def handle_manual_wake():
    """Manually activate task mode"""
    logger.info("Manual wake triggered")
    speech_service.manual_wake(request.sid)

@socketio.on('manual_sleep')
def handle_manual_sleep():
    """Manually deactivate task mode"""
    logger.info("Manual sleep triggered")
    speech_service.manual_sleep(request.sid)

if __name__ == '__main__':
    # Initialize speech service after socketio is ready
    speech_service = SpeechService(socketio)
    
    print("--------------------------------------------------")
    print("JARVIS AI System Starting...")
    print("Access the GUI at: http://127.0.0.1:5000")
    print("Press Ctrl+C to stop.")
    print("--------------------------------------------------")
    socketio.run(app, debug=True, port=5000)

