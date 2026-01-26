from fastapi import FastAPI, WebSocket, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import uvicorn
import cv2
import threading
import time
import asyncio
from empath.detector import EmpathEye
from empath.robot_controller import RobotController
from empath.brain import EmpathBrain
from empath.voice import EmpathVoice
from empath.hearing import EmpathEar

app = FastAPI(title="Reachy Empath API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global State
class EmpathState:
    def __init__(self):
        self.mode = "COMPANION" 
        self.is_connected = False
        self.current_emotion = "neutral"
        self.emotion_confidence = 0.0
        self.interaction_log = []

state = EmpathState()

# Initialize Modules
print("🔹 Init Robot...")
robot = RobotController()
print("🔹 Init Eye...")
eye = EmpathEye()

voice = EmpathVoice()
brain = None 

# Engagement timer to allow conversation after initial wake word
# We start with a high value to allow immediate engagement on first run
last_engagement_time = time.time() 

def on_hear_text(text):
    global last_engagement_time
    raw_text = text.lower().strip()
    
    if len(raw_text) < 2: return # Ignore noise
    
    wake_words = [
        "hello reachy", "hey reachy", "hi reachy", "reachy", 
        "jarvis", "tadashi", "hey richie", "hello ritchie",
        "hey ricky", "hey rici", "hey reach", "hey bridgey",
        "hello", "hi", "hey", "talk back", "can you hear", "can you talk"
    ]
    
    # Priority Activation (Wake words)
    is_active = any(w in raw_text for w in wake_words)
    
    # Secondary Activation (Already Engaged or Face Detected)
    if not is_active:
        # Extended conversation window (5 minutes) to allow follow-up questions
        if time.time() - last_engagement_time < 300:
            is_active = True
            print(f"🔄 [Main] Session Active (Time remaining: {300 - (time.time() - last_engagement_time):.0f}s)")
        # If a face is clearly seen (not neutral/passive)
        elif state.current_emotion != "neutral":
            is_active = True

    if is_active:
        print(f"🚀 [Main] ACTIVATED: '{raw_text}'")
        last_engagement_time = time.time() # Update session timer
        
        if brain:
            # Physical acknowledgment
            robot.trigger_gesture("agree") 
            
            def process_and_reply():
                frame = robot.get_frame() # Will be None if camera is off
                response = brain.process_query(raw_text, state.current_emotion, frame=frame)
                
                # Persona expressions
                lr = response.lower()
                if any(x in lr for x in ["haha", "lol", "😊", "funny", "excellent"]):
                    robot.trigger_gesture("giggles")
                elif any(x in lr for x in ["sad", "sorry", "unfortunate", "bad"]):
                    robot.trigger_gesture("bashful")
                else:
                    robot.trigger_gesture("agree")
                
                voice.speak(response)
                
            threading.Thread(target=process_and_reply, daemon=True).start()
    else:
        print(f"👂 [Main] Passive speech ignored (Wait for wake word): '{raw_text}'")

ear = EmpathEar(callback=on_hear_text)

def init_brain():
    global brain
    brain = EmpathBrain() # Downloads model if needed
    # Start listening once brain is ready
    print("👂 Starting Ear...")
    ear.start_listening()

threading.Thread(target=init_brain).start()

# Connection Management
from contextlib import asynccontextmanager

def connect_robot_bg():
    # Camera DISABLED as requested
    if robot.connect(use_local_camera=False):
        state.is_connected = True

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    threading.Thread(target=connect_robot_bg, daemon=True).start()
    yield
    # Shutdown
    robot.disconnect()
    ear.stop_listening()

# Assign lifespan to the existing app
app.router.lifespan_context = lifespan

# Logic Loop
def generate_frames():
    """Video streaming generator function."""
    while True:
        if not state.is_connected:
            time.sleep(1)
            continue
        
        frame = robot.get_frame()
        if frame is None:
            time.sleep(0.1)
            continue
            
        # Analyze Emotion & Features
        analysis, annotated_frame = eye.analyze_frame(frame)
        
        state.current_emotion = analysis["dominant_emotion"]
        # Save features for brain
        state.visual_features = analysis.get("features", {})
        
        # Mirroring Logic (Visual Resonance)
        if analysis["face_detected"]:
            # Automatic reaction in simulation based on what he sees
            if state.current_emotion == "happy":
                robot.trigger_gesture("happy")
            elif state.current_emotion == "sad":
                robot.trigger_gesture("sad")
            elif state.current_emotion == "angry":
                robot.trigger_gesture("angry")
            elif state.current_emotion == "surprise":
                robot.trigger_gesture("surprised")
            elif state.current_emotion == "fear":
                robot.trigger_gesture("bashful")
            elif state.current_emotion == "disgust":
                robot.trigger_gesture("confused")
        
        # Encode
        ret, buffer = cv2.imencode('.jpg', annotated_frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        time.sleep(0.05) 

@app.get("/video_feed")
async def video_feed():
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/status")
def get_status():
    return {
        "mode": state.mode,
        "connected": state.is_connected,
        "emotion": state.current_emotion,
        "brain_online": brain is not None and not brain.offline,
        "features": getattr(state, "visual_features", {})
    }

@app.post("/chat")
async def chat(payload: dict):
    """
    User sends text/voice-transcription here (manual).
    """
    user_text = payload.get("text", "")
    if not brain:
        return {"response": "My brain is still waking up..."}
    
    frame = robot.get_frame()
    # Pass visual features if available
    features = getattr(state, "visual_features", {})
    response = brain.process_query(user_text, state.current_emotion, frame=frame, visual_notes=features)
    voice.speak(response)
    
    return {"response": response}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
