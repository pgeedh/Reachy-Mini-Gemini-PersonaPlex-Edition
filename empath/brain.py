import os
import io
import cv2
import PIL.Image
from dotenv import load_dotenv
from google import genai
from google.genai import types
from huggingface_hub import InferenceClient, login

load_dotenv()

class EmpathBrain:
    """
    Core intelligence module for Reachy-Mini. 
    Integrates Gemini Robotics VLA (Visual-Language-Action) for physical context 
    and NVIDIA PersonaPlex for empathetic conversation fallback.
    """
    
    def __init__(self, gemini_model="gemini-robotics-er-1.5-preview"):
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.hf_token = os.getenv("HF_TOKEN")
        
        self.vla_online = False
        self.personaplex_client = None
        
        # Explicit HF Login for gated model access
        if self.hf_token:
            try:
                login(token=self.hf_token) # Removed unsupported new_session=False
                self.personaplex_client = InferenceClient(token=self.hf_token)
                print("🧠 [Brain] PersonaPlex Fallback (nvidia/personaplex-7b-v1) is READY.")
            except Exception as e:
                print(f"⚠️ [Brain] PersonaPlex Login/Init Failed: {e}")
                
        # Initialize Gemini VLA
        if self.gemini_key:
            try:
                self.genai_client = genai.Client(api_key=self.gemini_key)
                self.vla_model = gemini_model
                self.vla_online = True
                print("🧠 [Brain] Gemini VLA is ONLINE.")
            except Exception as e:
                print(f"⚠️ [Brain] Gemini VLA Init Failed: {e}")
                self.offline = True # Set offline if VLA fails to initialize

    def process_query(self, text, emotion="neutral", frame=None, visual_notes=None):
        """Generates a response using Gemini VLA or PersonaPlex Fallback."""
        if visual_notes is None: visual_notes = {}
        
        # Inject visual context into text for the fallback models
        context_str = ""
        if visual_notes:
            shirt = visual_notes.get("shirt_color", "unknown")
            hair = visual_notes.get("hair_color", "unknown")
            if shirt != "unknown": context_str += f"[Visual: User is wearing a {shirt} shirt] "
            if hair != "unknown": context_str += f"[Visual: User has {hair} hair] "
        
        # Weather Check (Simple heuristic trigger)
        if "weather" in text.lower():
            try:
                # Approximate location (New York) for demo since we track IPs easily
                w = httpx.get("https://api.open-meteo.com/v1/forecast?latitude=40.71&longitude=-74.00&current=temperature_2m,weather_code").json()
                temp = w['current']['temperature_2m']
                context_str += f"[Context: It is currently {temp}°C outside] "
            except:
                context_str += "[Context: Weather data unavailable] "

        full_text = context_str + text

        # Priority:
        # 1. Gemini VLA (Context-Aware)
        # 2. PersonaPlex (Character-Aware)
        # 3. Local Scripted (Safe-Fallback)

        if self.offline:
            print("🧠 [Brain] Gemini Offline. Using PersonaPlex.")
            # If VLA is offline, directly try PersonaPlex with enhanced text
            if self.personaplex_client:
                try:
                    return self._call_personaplex(full_text, emotion)
                except Exception as e:
                    print(f"⚠️ [Brain] PersonaPlex Error in offline mode: {e}")
            return self._local_intelligence(full_text) # Fallback to local if PersonaPlex also fails or is not ready

        # 1. Attempt VLA if online and frame provided
        if self.vla_online:
            try:
                return self._call_gemini_vla(text, emotion, frame) # VLA uses original text and frame
            except Exception as e:
                print(f"⚠️ [Brain] VLA Error: {e}. Falling back to PersonaPlex...")

        # 2. Attempt PersonaPlex
        if self.personaplex_client:
            try:
                return self._call_personaplex(text, emotion)
            except Exception as e:
                print(f"⚠️ [Brain] PersonaPlex Error: {e}")

        # 3. Final Fallback
        return "I'm listening, and I'm right here with you. Let's take a moment together."

    def _call_gemini_vla(self, text, emotion, frame):
        contents = []
        if frame is not None:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_img = PIL.Image.fromarray(rgb_frame)
            img_byte_arr = io.BytesIO()
            pil_img.save(img_byte_arr, format='PNG')
            contents.append(types.Part.from_bytes(data=img_byte_arr.getvalue(), mime_type='image/png'))
        
        system_prompt = (
            "You are Reachy, a warm and kind AI companion. "
            "Philosophy: PersonaPlex (Empathetic, Brief, Kind). "
            f"User Emotion: {emotion}. "
            f"User input: {text}. "
            "Observe the scene (table, toys, fruits) and respond with warmth."
        )
        contents.append(system_prompt)
        
        response = self.genai_client.models.generate_content(
            model=self.vla_model,
            contents=contents,
            config=types.GenerateContentConfig(
                temperature=0.85,
                top_p=0.95,
                max_output_tokens=150
            )
        )
        return response.text

    def _call_personaplex(self, text, emotion):
        """
        Robust Multi-Layer Fallback Strategy:
        1. Try Authenticated HF Inference (Zephyr)
        2. Try Anonymous HF Inference (Phi-3)
        3. Local Rule-Based Fallback (Math/Greetings)
        """
        # Layer 1: Authenticated
        if self.hf_token:
            try:
                return self._hf_chat_request(self.personaplex_client, "HuggingFaceH4/zephyr-7b-beta", text, emotion)
            except Exception as e:
                print(f"⚠️ [Brain] Auth Layer Failed: {e}")

        # Layer 2: Anonymous (in case token has bad perms)
        try:
            print("🧠 [Brain] Attempting Anonymous Inference...")
            anon_client = InferenceClient() # No token
            return self._hf_chat_request(anon_client, "microsoft/Phi-3-mini-4k-instruct", text, emotion)
        except Exception as e:
             print(f"⚠️ [Brain] Anon Layer Failed: {e}")

        # Layer 3: Local Rule-Based (The "Lobotomy" Mode that still works)
        return self._local_intelligence(text)

    def _hf_chat_request(self, client, model, text, emotion):
        messages = [
            {"role": "system", "content": f"You are Reachy (PersonaPlex). User emotion: {emotion}. Keep it short."},
            {"role": "user", "content": text}
        ]
        response = client.chat_completion(messages=messages, model=model, max_tokens=100)
        return response.choices[0].message.content.strip()

    def _local_intelligence(self, text):
        """Zero-latency local processing for basic tasks."""
        print("🧠 [Brain] Using Local Intelligence.")
        text_lower = text.lower()
        
        # Math capabilities
        import re
        math_match = re.search(r'(\d+)\s*([\+\-\*\/])\s*(\d+)', text)
        if math_match:
            try:
                n1, op, n2 = math_match.groups()
                expr = f"{n1}{op}{n2}"
                result = eval(expr)
                return f"I calculated that simply: it is {result}."
            except:
                pass
                
        # Basic Chit-Chat
        if "hello" in text_lower or "hi" in text_lower:
            return "Hello there! I'm operating on local power."
        if "how are you" in text_lower:
            return "I'm doing well, staying resilient."
            
        return "I can hear you, but my cloud brain is unreachable. Ask me a math question!"
