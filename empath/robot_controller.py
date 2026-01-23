from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose
import numpy as np
import time
import threading

class RobotController:
    def __init__(self):
        self.mini = None
        self.running = False

    def connect(self):
        try:
            self.mini = ReachyMini()
            self.mini.__enter__() 
            self.running = True
            print("Connected to Reachy Mini")
            self.gesture_happy()
            return True
        except Exception as e:
            print(f"Failed to connect: {e}")
            self.mini = None
            return False

    def disconnect(self):
        if self.mini:
            self.mini.__exit__(None, None, None)
            self.mini = None
            self.running = False

    def get_frame(self):
        if self.mini and self.running:
            try:
                return self.mini.media.get_frame()
            except:
                return None
        return None

    # --- Gestures ---
    def gesture_happy(self):
        if not self.mini: return
        self.mini.goto_target(
            antennas=np.deg2rad([45, -45]), # Wiggle
            head=create_head_pose(z=10, pitch=-10, degrees=True, mm=True),
            duration=0.5
        )
        time.sleep(0.5)
        self.mini.goto_target(
            antennas=np.deg2rad([0, 0]),
            head=create_head_pose(pitch=0, degrees=True, mm=True),
            duration=0.5
        )

    def gesture_sad(self):
        if not self.mini: return
        self.mini.goto_target(
            antennas=np.deg2rad([130, -130]), # Droopy
            head=create_head_pose(z=-10, pitch=20, degrees=True, mm=True), # Look down
            duration=1.0
        )

    def gesture_curious(self):
        if not self.mini: return
        self.mini.goto_target(
            head=create_head_pose(roll=20, degrees=True, mm=True), # Tilt
            duration=0.5
        )
