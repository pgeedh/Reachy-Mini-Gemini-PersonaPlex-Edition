from google import genai
from google.genai import types
import os
import cv2
import PIL.Image
import io
from dotenv import load_dotenv

load_dotenv()

# Configure API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") 

class EmpathBrain:
    def __init__(self, model_name="gemini-robotics-er-1.5-preview"):
        print(f"🧠 Loading Gemini Robotics Brain ({model_name})...")
        if not GEMINI_API_KEY:
            print("⚠️ GEMINI_API_KEY not found! Please set it in your environment.")
            self.offline = True
            return

        try:
            self.client = genai.Client(api_key=GEMINI_API_KEY)
            self.model_id = model_name
            self.offline = False
            print(f"🧠 Gemini Robotics Brain ({model_name}) is ONLINE.")
        except Exception as e:
            print(f"⚠️ Brain failed to load: {e}. Switching to Lobotomy Mode.")
            self.offline = True

    def process_query(self, user_text, current_emotion="neutral", frame=None):
        """
        Generates a response based on text, emotion, and optional vision frame.
        Uses Gemini Robotics-ER 1.5 Preview.
        """
        if self.offline:
            return self._fallback_response(user_text, current_emotion)

        try:
            contents = []
            
            # Add visual context if frame is available
            if frame is not None:
                # Convert OpenCV BGR to RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Convert to PIL Image
                pil_img = PIL.Image.fromarray(rgb_frame)
                # Save to bytes for the new API
                img_byte_arr = io.BytesIO()
                pil_img.save(img_byte_arr, format='PNG')
                
                contents.append(
                    types.Part.from_bytes(
                        data=img_byte_arr.getvalue(),
                        mime_type='image/png',
                    )
                )
            
            # System instructions and user prompt
            prompt = (
                f"You are Reachy, an AI companion designed with the PersonaPlex philosophy: "
                f"Warm, deeply empathetic, brief, and KIND. You never break character. "
                f"You are sitting at a wooden table. In front of you, there is: "
                f"1. A stylized GREEN T-REX (your favorite toy). "
                f"2. A juicy ORANGE. "
                f"3. A red APPLE. "
                f"4. A delicious CROISSANT. "
                f"5. A rubber DUCK. "
                f"You can see the user through a monitor in front of you. "
                f"Current User Emotion: {current_emotion}. "
                f"User says: {user_text}"
                f"Respond with warmth and personality."
            )
            contents.append(prompt)
            
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=contents,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    thinking_config=types.ThinkingConfig(thinking_budget=0)
                )
            )
            
            return response.text
        except Exception as e:
            err_msg = str(e).lower()
            if "quota" in err_msg or "429" in err_msg or "limit" in err_msg:
                print("⚠️ Gemini API Limit Reached.")
                return "My cloud brain has reached its free limit for now. Please wait a moment or check your API quota."
            
            print(f"Gemini Robotics Error: {e}")
            return "I am having a moment of silence while I process what I see and hear."

    def _fallback_response(self, text, emotion):
        return "My brain is currently resting. I'll be back online in a moment!"
