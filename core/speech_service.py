"""
Speech Recognition Service for JARVIS
Handles server-side speech recognition using Python's speech_recognition library
"""
import speech_recognition as sr
import io
import threading
import time
import base64
import wave
import tempfile
import os
import glob
from pydub import AudioSegment
from pydub.utils import which
from flask_socketio import emit
import logging

logger = logging.getLogger(__name__)

# Configure FFmpeg path for pydub
def find_ffmpeg():
    """Find FFmpeg in winget installation directory"""
    winget_patterns = [
        os.path.expandvars(r"$LOCALAPPDATA\Microsoft\WinGet\Packages\Gyan.FFmpeg*\**\bin\ffmpeg.exe"),
        r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
        r"C:\ffmpeg\bin\ffmpeg.exe",
    ]
    
    for pattern in winget_patterns:
        matches = glob.glob(pattern, recursive=True)
        if matches:
            return matches[0]
    
    # Fall back to system PATH
    return which("ffmpeg")

ffmpeg_path = find_ffmpeg()
if ffmpeg_path:
    # Set the paths for pydub
    AudioSegment.converter = ffmpeg_path
    AudioSegment.ffmpeg = ffmpeg_path
    AudioSegment.ffprobe = ffmpeg_path.replace("ffmpeg.exe", "ffprobe.exe")
    
    # CRITICAL: Add ffmpeg directory to PATH so subprocess can find it
    ffmpeg_dir = os.path.dirname(ffmpeg_path)
    if ffmpeg_dir not in os.environ['PATH']:
        os.environ['PATH'] = ffmpeg_dir + os.pathsep + os.environ['PATH']
    
    logger.info(f"FFmpeg configured at: {ffmpeg_path}")
    logger.info(f"FFmpeg directory added to PATH: {ffmpeg_dir}")
else:
    logger.warning("FFmpeg not found. Audio conversion may fail.")


class SpeechService:
    """Manages speech recognition for voice input"""
    
    def __init__(self, socketio):
        self.socketio = socketio
        self.recognizer = sr.Recognizer()
        # Adjust for ambient noise
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        
        # Session states (per client)
        self.sessions = {}
        
        # Audio processing configuration
        self.ACCUMULATION_DURATION = 3.0  # seconds to accumulate before processing
        
    def create_session(self, sid):
        """Create a new speech session for a client"""
        self.sessions[sid] = {
            'mode': 'ai',  # 'ai' or 'task'
            'is_listening': False,
            'is_awake': False,  # Task mode state
            'final_transcript': '',  # AI mode accumulated text
            'silence_timer': None,
            'no_input_timer': None,
            'last_speech_time': None,
            'audio_buffer': [],  # Accumulate audio chunks
            'last_process_time': time.time(),  # Track processing intervals
            'process_timer': None  # Timer for periodic processing
        }
        logger.info(f"Created speech session for {sid}")
        
    def destroy_session(self, sid):
        """Clean up session"""
        if sid in self.sessions:
            session = self.sessions[sid]
            # Cancel any active timers
            if session['silence_timer']:
                session['silence_timer'].cancel()
            if session['no_input_timer']:
                session['no_input_timer'].cancel()
            if session['process_timer']:
                session['process_timer'].cancel()
            del self.sessions[sid]
            logger.info(f"Destroyed speech session for {sid}")
    
    def set_mode(self, sid, mode):
        """Set voice mode (ai or task)"""
        if sid in self.sessions:
            self.sessions[sid]['mode'] = mode
            self.sessions[sid]['is_listening'] = False
            self.sessions[sid]['is_awake'] = False
            self.sessions[sid]['final_transcript'] = ''
            logger.info(f"Session {sid} mode changed to: {mode}")
    
    def start_listening(self, sid, mode='ai', initial_text=''):
        """Start listening for speech"""
        if sid not in self.sessions:
            self.create_session(sid)
        
        session = self.sessions[sid]
        session['mode'] = mode
        session['is_listening'] = True
        session['last_speech_time'] = time.time()
        
        # Initialize transcript with current text (handles deletions/edits)
        if mode == 'ai':
            session['final_transcript'] = initial_text
            logger.info(f"Initialized transcript with: '{initial_text}'")
        
        logger.info(f"Started listening for {sid} in {mode} mode")
        
        # Emit event to client
        self.socketio.emit('speech_started', {'mode': mode}, room=sid)

    def reset_session_transcript(self, sid):
        """Reset the session transcript"""
        if sid in self.sessions:
            self.sessions[sid]['final_transcript'] = ''
            logger.info(f"Reset transcript for {sid}")
    
    def stop_listening(self, sid):
        """Stop listening"""
        if sid in self.sessions:
            session = self.sessions[sid]
            session['is_listening'] = False
            
            # Cancel timers
            if session['silence_timer']:
                session['silence_timer'].cancel()
                session['silence_timer'] = None
            if session['no_input_timer']:
                session['no_input_timer'].cancel()
                session['no_input_timer'] = None
            if session['process_timer']:
                session['process_timer'].cancel()
                session['process_timer'] = None
            
            # Process any remaining audio in buffer
            if session['audio_buffer']:
                self._process_accumulated_audio(sid)
            
            logger.info(f"Stopped listening for {sid}")
            self.socketio.emit('speech_stopped', room=sid)
    
    def process_audio_chunk(self, sid, audio_data):
        """Accumulate incoming audio chunk"""
        if sid not in self.sessions:
            logger.warning(f"No session found for {sid}")
            return
        
        session = self.sessions[sid]
        if not session['is_listening']:
            return
        
        try:
            # Decode base64 audio
            audio_bytes = base64.b64decode(audio_data)
            
            # Skip empty or very small chunks
            if len(audio_bytes) < 100:
                logger.debug(f"Skipping small audio chunk: {len(audio_bytes)} bytes")
                return
            
            logger.debug(f"Received audio chunk: {len(audio_bytes)} bytes")
            
            # Add to buffer
            session['audio_buffer'].append(audio_bytes)
            
            # Check if we should process accumulated audio
            time_since_last_process = time.time() - session['last_process_time']
            
            if time_since_last_process >= self.ACCUMULATION_DURATION:
                # Process accumulated audio
                self._process_accumulated_audio(sid)
            elif not session['process_timer']:
                # Start timer for periodic processing
                def process_callback():
                    self._process_accumulated_audio(sid)
                
                session['process_timer'] = threading.Timer(self.ACCUMULATION_DURATION, process_callback)
                session['process_timer'].start()
                    
        except Exception as e:
            logger.error(f"Error processing audio chunk: {e}", exc_info=True)
    
    def _process_accumulated_audio(self, sid):
        """Process accumulated audio chunks"""
        if sid not in self.sessions:
            return
        
        session = self.sessions[sid]
        
        # Cancel process timer if active
        if session['process_timer']:
            session['process_timer'].cancel()
            session['process_timer'] = None
        
        # Check if we have audio to process
        if not session['audio_buffer']:
            logger.debug(f"No audio in buffer for {sid}")
            return
        
        try:
            # Merge all accumulated chunks
            merged_audio = b''.join(session['audio_buffer'])
            total_size = len(merged_audio)
            chunk_count = len(session['audio_buffer'])
            
            logger.info(f"Processing {chunk_count} audio chunks, total {total_size} bytes")
            
            # Clear buffer and update process time
            session['audio_buffer'] = []
            session['last_process_time'] = time.time()
            
            # Skip if audio is too small
            if total_size < 1000:
                logger.debug(f"Skipping processing: audio too small ({total_size} bytes)")
                return
            
            # Create temp files for conversion
            webm_path = None
            wav_path = None
            
            try:
                with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as webm_file:
                    webm_file.write(merged_audio)
                    webm_path = webm_file.name
                logger.debug(f"Created WebM temp file: {webm_path}")
            except Exception as e:
                logger.error(f"Failed to create WebM temp file: {e}")
                return
            
            try:
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as wav_file:
                    wav_path = wav_file.name
                logger.debug(f"Created WAV temp file: {wav_path}")
            except Exception as e:
                logger.error(f"Failed to create WAV temp file: {e}")
                if webm_path and os.path.exists(webm_path):
                    os.unlink(webm_path)
                return
            
            try:
                # Convert WebM to WAV using pydub
                logger.debug(f"Converting {webm_path} to WAV...")
                audio = AudioSegment.from_file(webm_path, format="webm")
                audio = audio.set_channels(1).set_frame_rate(16000)
                audio.export(wav_path, format="wav")
                logger.debug("Conversion successful")
                
                # Now use speech_recognition
                logger.debug(f"Reading WAV file for recognition...")
                with sr.AudioFile(wav_path) as source:
                    audio_data = self.recognizer.record(source)
                
                # Recognize speech using Google (free, no API key)
                try:
                    text = self.recognizer.recognize_google(audio_data)
                    
                    if text:
                        session['last_speech_time'] = time.time()
                        self._handle_recognition_result(sid, text, is_final=True)
                        logger.info(f"Successfully recognized: {text}")
                        
                except sr.UnknownValueError:
                    # No speech detected in this chunk
                    logger.debug("No speech detected in audio")
                    # Emit empty final speech to reset UI "Transcribing..." state
                    self.socketio.emit('speech_final', {'text': '', 'full_transcript': session['final_transcript']}, room=sid)
                    pass
                except sr.RequestError as e:
                    logger.error(f"Speech recognition error: {e}")
                    self.socketio.emit('speech_error', {'error': str(e)}, room=sid)
            
            except Exception as e:
                logger.error(f"Conversion/Recognition error: {e}", exc_info=True)
            
            finally:
                # Clean up temp files
                try:
                    if webm_path and os.path.exists(webm_path):
                        os.unlink(webm_path)
                        logger.debug(f"Deleted temp file: {webm_path}")
                except Exception as e:
                    logger.warning(f"Failed to delete WebM temp file: {e}")
                
                try:
                    if wav_path and os.path.exists(wav_path):
                        os.unlink(wav_path)
                        logger.debug(f"Deleted temp file: {wav_path}")
                except Exception as e:
                    logger.warning(f"Failed to delete WAV temp file: {e}")
                    
        except Exception as e:
            logger.error(f"Error in _process_accumulated_audio: {e}", exc_info=True)
    
    def _handle_recognition_result(self, sid, text, is_final=False):
        """Handle recognized text"""
        session = self.sessions[sid]
        mode = session['mode']
        
        logger.info(f"Recognition result [{mode}]: {text} (final={is_final})")
        
        if mode == 'ai':
            # AI Mode: Append to transcript
            if is_final:
                session['final_transcript'] += text + ' '
                self.socketio.emit('speech_final', {
                    'text': text,
                    'full_transcript': session['final_transcript']
                }, room=sid)
            else:
                self.socketio.emit('speech_interim', {
                    'text': text,
                    'full_transcript': session['final_transcript'] + text
                }, room=sid)
                
        else:
            # Task Mode
            if not session['is_awake']:
                # Check for wake word
                lower_text = text.lower()
                wake_word_found = False
                command_part = ""
                
                if 'hey jarvis' in lower_text:
                    wake_word_found = True
                    parts = lower_text.split('hey jarvis', 1)
                    if len(parts) > 1:
                        command_part = parts[1].strip()
                elif 'hello jarvis' in lower_text:
                    wake_word_found = True
                    parts = lower_text.split('hello jarvis', 1)
                    if len(parts) > 1:
                        command_part = parts[1].strip()
                
                if wake_word_found:
                    logger.info(f"Wake word detected! Command part: '{command_part}'")
                    self._activate_task_mode(sid)
                    
                    # If there's a command part immediately, process it
                    if command_part:
                        # We need to send the original case text if possible, but we split lower.
                        # For now, sending the lower case command is fine, or we can try to preserve case.
                        # Simple approach: just send the command_part (it's lower, but JARVIS should handle it)
                        self.socketio.emit('speech_final', {'text': command_part}, room=sid)
                        self._reset_silence_timer(sid)
                        self._reset_no_input_timer(sid)
                        
            else:
                # Process command
                self.socketio.emit('speech_final', {'text': text}, room=sid)
                
                # Reset silence timer
                self._reset_silence_timer(sid)
                # Reset no input timer
                self._reset_no_input_timer(sid)
    
    def _activate_task_mode(self, sid):
        """Activate task mode (awake state)"""
        if sid not in self.sessions:
            return
        
        session = self.sessions[sid]
        session['is_awake'] = True
        
        self.socketio.emit('wake_word_detected', room=sid)
        
        # Start no input timer (5s)
        self._reset_no_input_timer(sid)
    
    def _deactivate_task_mode(self, sid):
        """Deactivate task mode (sleep)"""
        if sid not in self.sessions:
            return
        
        session = self.sessions[sid]
        session['is_awake'] = False
        
        # Cancel timers
        if session['silence_timer']:
            session['silence_timer'].cancel()
            session['silence_timer'] = None
        if session['no_input_timer']:
            session['no_input_timer'].cancel()
            session['no_input_timer'] = None
        
        self.socketio.emit('task_mode_sleep', room=sid)
    
    def _reset_silence_timer(self, sid):
        """Reset auto-send timer (3s in Task Mode)"""
        if sid not in self.sessions:
            return
        
        session = self.sessions[sid]
        
        # Cancel existing timer
        if session['silence_timer']:
            session['silence_timer'].cancel()
        
        # Start new timer
        def on_silence():
            logger.info(f"Silence timeout for {sid}")
            self.socketio.emit('silence_timeout', room=sid)
            self._deactivate_task_mode(sid)
        
        session['silence_timer'] = threading.Timer(3.0, on_silence)
        session['silence_timer'].start()
    
    def _reset_no_input_timer(self, sid):
        """Reset no-input timer (5s in Task Mode)"""
        if sid not in self.sessions:
            return
        
        session = self.sessions[sid]
        
        # Cancel existing timer
        if session['no_input_timer']:
            session['no_input_timer'].cancel()
        
        # Start new timer
        def on_no_input():
            logger.info(f"No input timeout for {sid}")
            self._deactivate_task_mode(sid)
        
        session['no_input_timer'] = threading.Timer(5.0, on_no_input)
        session['no_input_timer'].start()
    
    def manual_wake(self, sid):
        """Manually wake up task mode (mic button click)"""
        self._activate_task_mode(sid)
    
    def manual_sleep(self, sid):
        """Manually sleep task mode (mic button click)"""
        self._deactivate_task_mode(sid)
