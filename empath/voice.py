from gtts import gTTS
import os
import tempfile
import threading
from reachy_mini import ReachyMini # for playback if needed, or system audio

class EmpathVoice:
    def __init__(self):
        # In a real heavy setup, we'd load Parler-TTS or Coqui here.
        # For prototype speed/reliability, we use gTTS (Google TTS) or system.
        pass

    def speak(self, text, emotion="neutral"):
        """
        Synthesizes speech and plays it.
        """
        # Run in thread to not block video loop
        threading.Thread(target=self._speak_thread, args=(text,)).start()

    def _speak_thread(self, text):
        try:
            # Create temp file
            tts = gTTS(text=text, lang='en')
            with tempfile.NamedTemporaryFile(delete=True) as fp:
                temp_filename = f"{fp.name}.mp3"
                tts.save(temp_filename)
                
                # Play audio
                # Mac specific
                os.system(f"afplay {temp_filename}")
                
                # Cleanup handled by tempfile/os
        except Exception as e:
            print(f"Voice Error: {e}")
