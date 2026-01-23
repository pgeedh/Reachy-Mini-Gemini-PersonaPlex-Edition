import cv2
from fer import FER
import numpy as np

class EmpathEye:
    def __init__(self):
        # Initialize the FER detector
        # mtcnn=True is more accurate but slower. We'll use default opencv haarcascade for speed in this demo,
        # or switch to mtcnn if installed.
        self.detector = FER(mtcnn=False) 

    def analyze_frame(self, frame):
        """
        Analyzes a frame for emotions.
        Returns:
            dict: {
                "face_detected": bool,
                "dominant_emotion": str,
                "emotions": dict,
                "face_box": tuple (x, y, w, h),
                "annotated_frame": numpy array
            }
        """
        # FER expects RGB
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Detect emotions
        result = self.detector.detect_emotions(image_rgb)
        
        data = {
            "face_detected": False,
            "dominant_emotion": "neutral",
            "emotions": {},
            "face_box": None
        }

        annotated_frame = frame.copy()

        if result:
            # Get largest face
            # result is a list of dicts: [{'box': (x, y, w, h), 'emotions': {'angry': 0.0, ...}}]
            face = max(result, key=lambda x: x['box'][2] * x['box'][3])
            
            data["face_detected"] = True
            data["emotions"] = face['emotions']
            data["face_box"] = face['box']
            
            # Find dominant emotion
            dominant_emotion, score = self.detector.top_emotion(image_rgb)
            data["dominant_emotion"] = dominant_emotion

            # Draw
            x, y, w, h = face['box']
            cv2.rectangle(annotated_frame, (x, y), (x+w, y+h), (0, 255, 255), 2)
            
            label = f"{dominant_emotion}: {score:.2f}"
            cv2.putText(annotated_frame, label, (x, y - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)

            # Draw emotion bars
            y_offset = y + h + 20
            for emo, val in face['emotions'].items():
                if val > 0.1: # Only show significant ones
                    bar_w = int(val * w)
                    cv2.rectangle(annotated_frame, (x, y_offset), (x + bar_w, y_offset + 10), (0, 255, 0), -1)
                    cv2.putText(annotated_frame, emo, (x + w + 5, y_offset + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    y_offset += 15
        
        return data, annotated_frame
