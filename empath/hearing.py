try:
    import speech_recognition as sr
    AUDIO_AVAILABLE = True
except ImportError:
    print("⚠️ SpeechRecognition or PyAudio not found. Voice input disabled.")
    AUDIO_AVAILABLE = False
import threading
import time

class EmpathEar:
    def __init__(self, callback):
        self.callback = callback
        if AUDIO_AVAILABLE:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
        self.listening = False

    def start_listening(self):
        if not AUDIO_AVAILABLE: return
        self.listening = True
        threading.Thread(target=self._listen_loop, daemon=True).start()

    def _listen_loop(self):
        try:
            with self.microphone as source:
                print("👂 Empath Ear is adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print("👂 Empath Ear is listening (STAYING OPEN)...")
                
                while self.listening:
                    try:
                        # Listen for audio with a short timeout to keep loop alive
                        audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                        
                        try:
                            # Uses Google Speech Recognition (free API)
                            text = self.recognizer.recognize_google(audio)
                            print(f"👂 Heard: {text}")
                            if text:
                                self.callback(text)
                        except sr.UnknownValueError:
                            pass # unintelligible
                        except sr.RequestError as e:
                            print(f"Ear Service Error: {e}") 
                            
                    except sr.WaitTimeoutError:
                        continue # Normal timeout, just loop back
                    except Exception as e:
                        if self.listening:
                            print(f"Ear Loop Inner Error: {e}")
        except Exception as e:
            print(f"Ear Critical Error (Mic might be busy): {e}")

    def stop_listening(self):
        self.listening = False
