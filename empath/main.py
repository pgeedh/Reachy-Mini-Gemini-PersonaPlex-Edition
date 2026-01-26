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

def on_hear_text(text):
    print(f"🔄 Processing heard text: {text}")
    if brain:
        # Visual feedback: Look up like we are thinking
        robot.trigger_gesture("thinking")
        
        # Get the latest frame for visual context
        frame = robot.get_frame()
        response = brain.process_query(text, state.current_emotion, frame=frame)
        voice.speak(response)

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
    # Force use of laptop camera for vision as requested
    if robot.connect(use_local_camera=True):
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
            
        # Analyze Emotion
        analysis, annotated_frame = eye.analyze_frame(frame)
        
        state.current_emotion = analysis["dominant_emotion"]
        
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
        "brain_online": brain is not None and not brain.offline
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
    response = brain.process_query(user_text, state.current_emotion, frame=frame)
    voice.speak(response)
    
    return {"response": response}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
