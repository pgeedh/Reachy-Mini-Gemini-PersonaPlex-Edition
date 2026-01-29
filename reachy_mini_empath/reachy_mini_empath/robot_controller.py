import numpy as np
import time
import threading
import cv2
from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose

class RobotController:
    """
    Advanced physical actuation layer. 
    Manages hardware connection, camera streaming, and physical expressions.
    """
    
    def __init__(self):
        self.mini = None
        self.running = False
        self._is_moving = False
        self.cap = None
        self.use_local_camera = False

    def connect(self, reachy_mini, use_local_camera=True):
        """
        Initializes connection using the provided Reachy Mini instance.
        """
        self.use_local_camera = use_local_camera
        if self.use_local_camera:
            self.cap = cv2.VideoCapture(0)
            if self.cap.isOpened():
                print("📸 [Controller] Vision initialized via local camera.")
            
        self.mini = reachy_mini
        self.running = True
        print("✅ [Controller] Hardware bridge ESTABLISHED (via System).")
        self.trigger_gesture("happy")
        return True

    def disconnect(self):
        if self.cap:
            self.cap.release()
        if self.mini:
            # self.mini.__exit__(None, None, None) # Managed by AppHost
            self.mini = None
        self.running = False

    def get_frame(self):
        if self.use_local_camera and self.cap:
            ret, frame = self.cap.read()
            return frame if ret else None
        
        if self.mini and self.running:
            try:
                return self.mini.media.get_frame()
            except:
                return None
        return None

    def trigger_gesture(self, gesture_name):
        """
        Asynchronous expression trigger. Non-blocking to keep logic loop fluid.
        """
        if self._is_moving:
            return
            
        method = getattr(self, f"_{gesture_name}", None)
        if method:
            threading.Thread(target=method, daemon=True).start()
        else:
            print(f"⚠️ [Controller] Scripted gesture '{gesture_name}' not identified.")

    # --- Scripted Gestures for PersonaPlex Feedback ---

    def _happy(self):
        self._is_moving = True
        try:
            if not self.mini: return
            self.mini.goto_target(
                antennas=np.deg2rad([45, -45]),
                head=create_head_pose(z=10, pitch=-10),
                duration=0.6
            )
            time.sleep(0.6)
            self.mini.goto_target(head=create_head_pose(), antennas=np.deg2rad([0,0]), duration=0.4)
        finally:
            self._is_moving = False

    def _thinking(self):
        self._is_moving = True
        try:
            if not self.mini: return
            self.mini.goto_target(head=create_head_pose(pitch=-15, roll=10), antennas=np.deg2rad([30, 30]), duration=0.8)
            time.sleep(1.0)
            self.mini.goto_target(head=create_head_pose(), antennas=np.deg2rad([0,0]), duration=0.6)
        finally:
            self._is_moving = False

    def _agree(self):
        self._is_moving = True
        try:
            if not self.mini: return
            for _ in range(2):
                self.mini.goto_target(head=create_head_pose(pitch=15), duration=0.3)
                time.sleep(0.3)
                self.mini.goto_target(head=create_head_pose(pitch=-5), duration=0.3)
                time.sleep(0.3)
            self.mini.goto_target(head=create_head_pose(), duration=0.3)
        finally:
            self._is_moving = False

    def _bashful(self):
        self._is_moving = True
        try:
            if not self.mini: return
            self.mini.goto_target(
                head=create_head_pose(pitch=15, roll=-20),
                antennas=np.deg2rad([110, -110]),
                duration=0.8
            )
            time.sleep(1.5)
            self.mini.goto_target(head=create_head_pose(), antennas=np.deg2rad([0,0]), duration=0.8)
        finally:
            self._is_moving = False

    def _giggles(self):
        self._is_moving = True
        try:
            if not self.mini: return
            for _ in range(4):
                phi = 10 if _ % 2 == 0 else -10
                self.mini.goto_target(head=create_head_pose(roll=phi), duration=0.15)
                time.sleep(0.15)
            self.mini.goto_target(head=create_head_pose(), duration=0.2)
        finally:
            self._is_moving = False

    def _sad(self):
        self._is_moving = True
        try:
            if not self.mini: return
            self.mini.goto_target(
                head=create_head_pose(pitch=25), # Look down
                antennas=np.deg2rad([130, -130]), # Droopy antennas
                duration=1.0
            )
            time.sleep(1.5)
            self.mini.goto_target(head=create_head_pose(), antennas=np.deg2rad([0,0]), duration=1.0)
        finally:
            self._is_moving = False

    def _angry(self):
        self._is_moving = True
        try:
            if not self.mini: return
            # Fast, sharp movement
            self.mini.goto_target(
                head=create_head_pose(pitch=10, z=5), 
                antennas=np.deg2rad([-20, 20]), # Forward/aggressive
                duration=0.3
            )
            time.sleep(1.0)
            self.mini.goto_target(head=create_head_pose(), antennas=np.deg2rad([0,0]), duration=0.8)
        finally:
            self._is_moving = False

    def _surprised(self):
        self._is_moving = True
        try:
            if not self.mini: return
            self.mini.goto_target(
                head=create_head_pose(pitch=-15, r=10), # Backwards/Up
                antennas=np.deg2rad([60, -60]), # Wide open
                duration=0.2
            )
            time.sleep(1.0)
            self.mini.goto_target(head=create_head_pose(), antennas=np.deg2rad([0,0]), duration=0.6)
        finally:
            self._is_moving = False

    def _confused(self):
        self._is_moving = True
        try:
            if not self.mini: return
            # Head tilt left then right
            self.mini.goto_target(head=create_head_pose(roll=15, pitch=-5), antennas=np.deg2rad([30, 0]), duration=0.5)
            time.sleep(0.5)
            self.mini.goto_target(head=create_head_pose(roll=-15, pitch=-5), antennas=np.deg2rad([0, -30]), duration=0.5)
            time.sleep(0.5)
            self.mini.goto_target(head=create_head_pose(), antennas=np.deg2rad([0,0]), duration=0.5)
        finally:
            self._is_moving = False
