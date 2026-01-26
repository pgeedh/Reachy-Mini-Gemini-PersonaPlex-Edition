# Reachy Empath ❤️🤖

> **The emotionally intelligent companion for Reachy Mini using Gemini Robotics-ER 1.5 VLA.**

Reachy Empath is a Human-Robot Interaction (HRI) framework that gives the [Reachy Mini](https://www.pollen-robotics.com/reachy-mini/) robot a "soul." By combining computer vision, emotional resonance, and the cutting-edge **Gemini Robotics-ER 1.5 VLA**, Reachy can now see, feel, and respond to you with genuine empathy.

---

## ✨ Key Features

- **🧠 Agentic Brain (Gemini Robotics-ER 1.5):** Uses Google DeepMind's newest Robotics model for advanced reasoning and spatial awareness.
- **👁️ Multimodal Vision:** Reachy "sees" you through his camera and understands context beyond just text.
- **❤️ Emotional Resonance:** Real-time facial expression tracking allows Reachy to mirror your mood.
- **🗣️ Natural Voice interaction:** Seamless STT (Speech-to-Text) and TTS (Text-to-Speech) for fluid conversation.
- **🎭 Expressive Gestures:** Physical movement that matches the conversation's emotional tone (Happy, Sad, Angry, Surprised, Confused, Excited, Bashful).

---

## 🚀 Quick Start

### 1. Requirements
- Python 3.10+
- A Google Gemini API Key in `.env`

### 2. Launch Everything (One Command)
Run the following to start MuJoCo, the AI Backend, and the Dashboard all at once:
```bash
chmod +x super_launch.sh
./super_launch.sh
```

---

## 👁️ Simulation Scene
The MuJoCo simulation now includes:
- **Stylized Green T-Rex** (Reachy's favorite toy).
- **Interactive fruits** (Orange, Apple, Croissant) centered on the table.
- **In-sim Monitor:** A virtual screen that displays your webcam feed directly to Reachy.

---

## 🛠️ Tech Stack

- **Robot Hardware:** Reachy Mini (Pollen Robotics)
- **AI Core:** Google Gemini Robotics-ER 1.5 (VLA)
- **Vision:** OpenCV, FER (Facial Expression Recognition), MediaPipe
- **Audio:** gTTS, SpeechRecognition
- **Framework:** FastAPI (Backend) & Next.js (Dashboard)

---

**Developed with ❤️ by the Neuracore Team.**
