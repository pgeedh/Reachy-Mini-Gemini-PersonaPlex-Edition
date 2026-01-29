import threading
import time
import io
import cv2
import numpy as np
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv

from reachy_mini import ReachyMini, ReachyMiniApp

# Relative imports
from .detector import EmpathEye
from .robot_controller import RobotController
from .brain import EmpathBrain
from .voice import EmpathVoice
from .hearing import EmpathEar

load_dotenv()

class EmpathState:
    def __init__(self):
        self.mode = "COMPANION" 
        self.current_emotion = "neutral"
        self.visual_features = {}

class ReachyMiniEmpath(ReachyMiniApp):
    # Host the UI/API on port 8042
    custom_app_url: str | None = "http://0.0.0.0:8042"
    
    def run(self, reachy_mini: ReachyMini, stop_event: threading.Event):
        # 1. State & Modules
        self.state = EmpathState()
        self.robot = RobotController()
        
        # Connect to hardware (passed instance)
        # Note: use_local_camera=False because we rely on Reachy's stream or sim stream
        # If running on robot, reachy_mini handles camera. If sim, same.
        self.robot.connect(reachy_mini, use_local_camera=False) 
        
        self.eye = EmpathEye()
        self.voice = EmpathVoice()
        self.brain = None
        self.ear = None
        
        self.latest_frame_jpeg = None
        self.last_engagement_time = time.time()
        
        # 2. Async Init for Heavy Models
        def init_brain_thread():
            self.brain = EmpathBrain()
            self.ear = EmpathEar(callback=self.on_hear_text)
            self.ear.start_listening()
            print("🧠 [App] Brain & Ear Ready.")
            
        threading.Thread(target=init_brain_thread, daemon=True).start()
        
        # 3. Define Routes (FastAPI)
        
        @self.settings_app.get("/status")
        def get_status():
            return {
                "mode": self.state.mode,
                "emotion": self.state.current_emotion,
                "brain_online": self.brain is not None and not self.brain.offline,
                "features": self.state.visual_features
            }
            
        @self.settings_app.post("/chat")
        async def chat(payload: dict):
            text = payload.get("text", "")
            if not self.brain: return {"response": "Brain loading..."}
            
            # Manual trigger via API
            self.on_hear_text(text) 
            return {"status": "processed"}

        def video_stream_gen():
            while not stop_event.is_set():
                if self.latest_frame_jpeg:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + self.latest_frame_jpeg + b'\r\n')
                time.sleep(0.05)

        @self.settings_app.get("/video_feed")
        def video_feed():
            return StreamingResponse(video_stream_gen(), media_type="multipart/x-mixed-replace; boundary=frame")

        # 4. Main Logic Loop
        print("🚀 [App] Reachy Empath Running...")
        
        while not stop_event.is_set():
            # Vision Loop
            frame = self.robot.get_frame()
            if frame is not None:
                analysis, annotated = self.eye.analyze_frame(frame)
                
                self.state.current_emotion = analysis["dominant_emotion"]
                self.state.visual_features = analysis.get("features", {})
                
                # Update visual mirror
                if analysis["face_detected"]:
                     self._handle_visual_mirroring(self.state.current_emotion)

                # JPEG Encode for Stream
                ret, buffer = cv2.imencode('.jpg', annotated)
                if ret:
                    self.latest_frame_jpeg = buffer.tobytes()
            
            time.sleep(0.05)
            
        # Cleanup
        if self.ear: self.ear.stop_listening()
        self.robot.disconnect()

    def _handle_visual_mirroring(self, emotion):
         # Mirroring Logic
         if emotion == "happy": self.robot.trigger_gesture("happy")
         elif emotion == "sad": self.robot.trigger_gesture("sad")
         elif emotion == "angry": self.robot.trigger_gesture("angry")
         elif emotion == "surprise": self.robot.trigger_gesture("surprised")
         elif emotion == "fear": self.robot.trigger_gesture("bashful")
         elif emotion == "disgust": self.robot.trigger_gesture("confused")

    def on_hear_text(self, text):
        raw_text = text.lower().strip()
        if len(raw_text) < 2: return
        
        wake_words = ["reachy", "hello", "hi", "tadashi", "jarvis"]
        is_active = any(w in raw_text for w in wake_words)
        
        if not is_active:
             if time.time() - self.last_engagement_time < 300:
                 is_active = True
             elif self.state.current_emotion != "neutral":
                 is_active = True
                 
        if is_active:
            print(f"🚀 [App] Activated: {raw_text}")
            self.last_engagement_time = time.time()
            if self.brain:
                self.robot.trigger_gesture("agree")
                threading.Thread(target=self._process_reply, args=(raw_text,), daemon=True).start()
                
    def _process_reply(self, text):
        frame = self.robot.get_frame()
        response = self.brain.process_query(text, self.state.current_emotion, frame, self.state.visual_features)
        
        # Gestures based on response text
        lr = response.lower()
        if any(x in lr for x in ["haha", "lol", "funny"]): self.robot.trigger_gesture("giggles")
        elif any(x in lr for x in ["sad", "sorry"]): self.robot.trigger_gesture("bashful")
        else: self.robot.trigger_gesture("agree")
            
        self.voice.speak(response)

if __name__ == "__main__":
    app = ReachyMiniEmpath()
    try:
        app.wrapped_run()
    except KeyboardInterrupt:
        app.stop()