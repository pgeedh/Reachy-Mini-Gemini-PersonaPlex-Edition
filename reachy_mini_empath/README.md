---
title: Reachy Mini Empath
emoji: 👋
colorFrom: indigo
colorTo: purple
sdk: static
pinned: false
short_description: Empathetic companion with Gemini VLA & PersonaPlex
tags:
 - reachy_mini
 - reachy_mini_python_app
---


# 🦖 Reachy-Mini: PersonaPlex Edition

Reachy-Mini is an interactive AI companion system built on the **PersonaPlex** philosophy of warm, empathetic, and kind robot-human interaction. This repository provides a full-stack integration of **Gemini 1.5 Robotics VLA** for physical-visual reasoning and **NVIDIA PersonaPlex-7B** for high-fidelity conversational empathy.

---

## 🌟 Key Features

*   **Dual-Tier Intelligence**:
    *   **Primary (Gemini VLA)**: Real-time visual context awareness (detects tabletop items like T-Rex toys, fruits, etc.) and sophisticated reasoning.
    *   **Fallback (NVIDIA PersonaPlex)**: High-empathy conversation engine that maintains a persistent "kind" character even when global APIs are limited.
*   **PersonaPlex Physicality**: 15+ scripted physical expressions (Thinking tilts, Playful shimmies, Shy peeks) that mirror conversational sentiment.
*   **Zero-Lag Interaction**: High-speed processing loops for vision, hearing, and actuation.
*   **Voice-First Interface**: Multi-variant wake-word activation ("Hello Reachy", "Jarvis", "Tadashi").

---

## 🛠 Prerequisites

*   **Hardware**: Reachy-Mini Robot (or MuJoCo Simulation instance).
*   **OS**: macOS (recommended for high-fidelity `afplay` voice) or Linux.
*   **Python**: 3.11+
*   **API Keys**:
    *   `GEMINI_API_KEY`: Google AI Studio.
    *   `HF_TOKEN`: Hugging Face token with access to `nvidia/personaplex-7b-v1`.

---

## 🚀 Quick Start

### 1. Installation
Clone the repository and install dependencies:

```bash
git clone https://github.com/pgeedh/Reachy-Mini.git
cd Reachy-Mini
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configuration
Create a `.env` file in the root directory:

```env
GEMINI_API_KEY=your_gemini_key
HF_TOKEN=your_huggingface_token
```

### 3. Launching the System
Use the professional Super-Launch script to start both the simulation and the AI brain:

```bash
./super_launch.sh
```

---

## 🧠 Brain Architecture (PersonaPlex)

Reachy's brain is designed to never break character. 

1.  **Vision Phase**: Reachy captures a frame from his eyes and analyzes face proximity.
2.  **Listening Phase**: Reachy uses Google Speech-to-Text with phonetic wake-word matching to catch commands even in noisy environments.
3.  **Synthesis Phase**: Reachy merges visual descriptors ("I see your green T-Rex!") with user text.
4.  **Fallback Phase**: If the Gemini API hits a quota limit, the `InferenceClient` immediately switches to **nvidia/personaplex-7b-v1** to ensure the conversation stays warm and fluid.

---

## 📜 Licenses

*   **Software**: MIT License
*   **AI Model (PersonaPlex)**: [NVIDIA Open Model License](NVIDIA_LICENSE.md)

---

## 🤖 Manual Control & API

The system exposes a FastAPI backend at `http://localhost:8080`:

*   `GET /status`: Check connection and brain health.
*   `GET /video_feed`: Real-time annotated stream of what Reachy sees.
*   `POST /chat`: Manually send text inputs to the brain.

---

*“Hello Reachy. I am Tadashi Hamada.”*
Designed for connection, one nod at a time.
