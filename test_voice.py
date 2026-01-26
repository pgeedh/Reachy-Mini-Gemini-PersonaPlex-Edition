import os
import tempfile
from gtts import gTTS

def test_voice():
    print("Testing Voice Synthesis and Playback...")
    text = "Hello Reachy, I am testing your voice system. Can you hear me?"
    try:
        tts = gTTS(text=text, lang='en', tld='co.uk')
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            temp_path = tmp.name
            tts.save(temp_path)
            print(f"File saved to {temp_path}. Playing now...")
            # Using absolute path for afplay
            os.system(f"afplay {temp_path}")
            os.remove(temp_path)
            print("Playback finished.")
    except Exception as e:
        print(f"Voice Test Failed: {e}")

if __name__ == "__main__":
    test_voice()
