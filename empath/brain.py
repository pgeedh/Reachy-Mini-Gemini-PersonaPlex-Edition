from google import genai
from google.genai import types
import os
import cv2
import PIL.Image
import io
from dotenv import load_dotenv

load_dotenv()

# Configure API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") 
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY") # User to set this for fallback

class EmpathBrain:
    def __init__(self, model_name="gemini-robotics-er-1.5-preview"):
        print(f"🧠 Loading Gemini Robotics Brain ({model_name})...")
        self.offline = False
        
        if not GEMINI_API_KEY:
            print("⚠️ GEMINI_API_KEY not found! Switching to Fallback Mode.")
            self.offline = True
        else:
            try:
                self.client = genai.Client(api_key=GEMINI_API_KEY)
                self.model_id = model_name
                print(f"🧠 Gemini Robotics Brain is ONLINE.")
            except Exception as e:
                print(f"⚠️ Brain failed to load: {e}. Switching to Fallback Mode.")
                self.offline = True

    def process_query(self, user_text, current_emotion="neutral", frame=None):
        """Generates a response using Gemini VLA or NVIDIA Fallback."""
        # Check for wake words in main.py, but here we just process
        
        if self.offline:
            return self._nvidia_fallback(user_text, current_emotion)

        try:
            contents = []
            if frame is not None:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_img = PIL.Image.fromarray(rgb_frame)
                img_byte_arr = io.BytesIO()
                pil_img.save(img_byte_arr, format='PNG')
                contents.append(types.Part.from_bytes(data=img_byte_arr.getvalue(), mime_type='image/png'))
            
            prompt = (
                f"You are Reachy, an AI companion designed with the PersonaPlex philosophy: "
                f"Warm, deeply empathetic, brief, and KIND. You never break character. "
                f"Context: You are sitting at a wooden table with your favorite T-Rex toy and some fruit. "
                f"Current User Emotion: {current_emotion}. "
                f"User says: {user_text}"
                f"Respond with warmth and personality. Mention your T-Rex toy if appropriate."
            )
            contents.append(prompt)
            
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=contents,
                config=types.GenerateContentConfig(
                    temperature=0.8,
                    thinking_config=types.ThinkingConfig(thinking_budget=0)
                )
            )
            return response.text
        except Exception as e:
            err_msg = str(e).lower()
            if "quota" in err_msg or "429" in err_msg or "limit" in err_msg:
                print("⚠️ Gemini Limit Reached. Activating NVIDIA Talking Model...")
                return self._nvidia_fallback(user_text, current_emotion)
            
            print(f"Brain Error: {e}")
            return "I am taking a moment to process my thoughts. I'm still here with you."

    def _nvidia_fallback(self, user_text, current_emotion):
        """Fallback to NVIDIA NIM or similar text-only talking model."""
        if not NVIDIA_API_KEY:
            return "My cloud brain is resting, but I'm still right here with you. (Fallback active)"
            
        try:
            # Using NVIDIA NIM (Mistral-7B or similar via OpenAI compatible API)
            from openai import OpenAI
            client = OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=NVIDIA_API_KEY)
            
            completion = client.chat.completions.create(
                model="meta/llama3-70b-instruct",
                messages=[{"role": "system", "content": "You are Reachy, a warm, brief, and kind AI companion. You love your T-Rex toy."},
                          {"role": "user", "content": f"User is feeling {current_emotion}. User said: {user_text}"}],
                temperature=0.7,
                max_tokens=100
            )
            return completion.choices[0].message.content
        except:
            return "I can't reach my cloud thoughts right now, but I can still see you're here. Let's just spend a moment in quiet together."

    def _fallback_response(self, text, emotion):
        return "I'm having a quiet moment. I'll be back fully in just a second!"
