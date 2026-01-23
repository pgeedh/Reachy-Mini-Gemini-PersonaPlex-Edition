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
# Note: Brain loading is heavy, might block startup a bit.
print("🔹 Init Robot...")
robot = RobotController()
print("🔹 Init Eye...")
eye = EmpathEye()

# Lazy load brain to allow fast server start? No, let's load it.
# Warning: This requires user to have ample RAM.
brain = None 
voice = EmpathVoice()

def init_brain():
    global brain
    brain = EmpathBrain() # Downloads model if needed

threading.Thread(target=init_brain).start()

# Connection Management
@app.on_event("startup")
async def startup_event():
    threading.Thread(target=connect_robot_bg, daemon=True).start()

def connect_robot_bg():
    if robot.connect():
        state.is_connected = True

@app.on_event("shutdown")
def shutdown_event():
    robot.disconnect()

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
        # Convert emotion confidence if needed, simplified here
        
        # Mirroring Logic (Simple)
        if analysis["face_detected"]:
            # If sad, look sad. If happy, look happy. (Head pose)
            # We debounce this so it doesn't spasm
            pass 
        
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
    User sends text/voice-transcription here.
    """
    user_text = payload.get("text", "")
    if not brain:
        return {"response": "My brain is still waking up..."}
    
    response = brain.process_query(user_text, state.current_emotion)
    voice.speak(response)
    
    # Robot gesture based on text sentiment?
    # robot.gesture_talk() 
    
    return {"response": response}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
