import cv2
import numpy as np

class EmpathEye:
    """
    Sub-system for visual awareness. 
    Handles face detection and high-level behavioral analysis for context.
    """
    
    def __init__(self):
        # We use a standard pre-trained Haar Cascade for zero-dependency speed.
        # Could be upgraded to MediaPipe or DeepFace for production.
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def analyze_frame(self, frame):
        """
        Processes a single BGR frame for interactive markers.
        Returns analysis dict and annotated display frame.
        """
        if frame is None:
            return {
                "face_detected": False, 
                "dominant_emotion": "neutral",
                "features": {"shirt_color": "unknown", "hair_color": "unknown"}
            }, None
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        
        analysis = {
            "face_detected": len(faces) > 0,
            "dominant_emotion": "neutral",
            "features": {"shirt_color": "unknown", "hair_color": "unknown"},
            "face_count": len(faces)
        }
        
        annotated = frame.copy()
        
        for (x, y, w, h) in faces:
            cv2.rectangle(annotated, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # --- Apparel Analysis (Heuristic) ---
            # 1. Hair: Segment above forehead
            hair_y = max(0, y - int(h * 0.3))
            hair_region = frame[hair_y:y, x:x+w]
            hair_color = self._get_dominant_color_name(hair_region)
            
            # 2. Shirt: Segment below chin
            shirt_y = min(frame.shape[0], y + h + int(h * 0.2))
            shirt_h = min(frame.shape[0], shirt_y + int(h * 0.6)) - shirt_y
            if shirt_h > 0:
                shirt_region = frame[shirt_y:shirt_y+shirt_h, x:x+w]
                shirt_color = self._get_dominant_color_name(shirt_region)
                
                # Draw shirt ROI for debug
                cv2.rectangle(annotated, (x, shirt_y), (x+w, shirt_y+shirt_h), (255, 0, 0), 1)
            else:
                shirt_color = "unknown"
                
            analysis["features"] = {
                "shirt_color": shirt_color,
                "hair_color": hair_color
            }
            
            # Overlay info
            info_text = f"Shirt:{shirt_color} Hair:{hair_color}"
            cv2.putText(annotated, info_text, (x, y+h+20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            if w > frame.shape[1] * 0.4:
                analysis["dominant_emotion"] = "surprised" # Simple proximity heuristic
        
        return analysis, annotated

    def _get_dominant_color_name(self, roi):
        if roi is None or roi.size == 0: return "unknown"
        
        # Calculate average color
        avg_color_per_row = np.average(roi, axis=0)
        avg_color = np.average(avg_color_per_row, axis=0) # BGR
        b, g, r = avg_color
        
        # Simple classification
        if r > 200 and g > 200 and b > 200: return "white"
        if r < 50 and g < 50 and b < 50: return "black"
        if r > 150 and g < 100 and b < 100: return "red"
        if b > 150 and g < 100 and r < 100: return "blue"
        if g > 150 and r < 100 and b < 100: return "green"
        if r > 200 and g > 200 and b < 100: return "yellow"
        if r > 100 and g > 100 and b > 100: return "gray"
        return "neutral"
