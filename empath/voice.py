import os
import tempfile
import threading
from gtts import gTTS

class EmpathVoice:
    """
    Professional Robot Voice module. 
    Handles speech synthesis with persona-consistent delivery.
    """
    
    def __init__(self, use_system_afplay=True):
        self.use_afplay = use_system_afplay
        self._lock = threading.Lock()

    def speak(self, text, emotion="neutral"):
        """
        Thread-safe entry point for speech synthesis.
        """
        if not text:
            return
            
        print(f"🔊 [Voice] Speaking: '{text}'")
        threading.Thread(target=self._synthesize_and_play, args=(text,), daemon=True).start()

    def _synthesize_and_play(self, text):
        # We use a lock to prevent speech overlapping awkwardly
        with self._lock:
            try:
                # 1. Synthesize using high-quality Google TTS (Fallback to local if needed)
                tts = gTTS(text=text, lang='en', tld='co.uk', slow=False) # British accent for professional 'Tadashi' feel
                
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
                    temp_path = tmp.name
                    tts.save(temp_path)
                
                # 2. Playback based on OS
                if self.use_afplay:
                    # macOS high-fidelity playback
                    os.system(f"afplay {temp_path}")
                else:
                    # Generic Linux/Other playback could go here (e.g. mpg123 or play)
                    pass
                
                # 3. Cleanup
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    
            except Exception as e:
                print(f"⚠️ [Voice] Synthesis Error: {e}")
