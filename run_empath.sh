#!/bin/bash
echo "❤️ Starting Reachy Empath Setup..."

# Backend Setup
echo "🔹 Setting up Empath Brain (Backend)..."
python3 -m venv venv
source venv/bin/activate
pip install -r empath/requirements.txt

# Start Backend
echo "🧠 Starting Empath Brain..."
export PYTHONPATH=$PYTHONPATH:$(pwd)
nohup python3 -m empath.main > backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend running (PID: $BACKEND_PID)"

# Frontend Setup
echo "🔹 Setting up Empath Interface (Frontend)..."
cd dashboard
npm install

# Start Frontend
echo "💻 Starting Dashboard..."
npm run dev &
FRONTEND_PID=$!

echo "✅ Reachy Empath is Alive!"
echo "Backend logs: backend.log"
echo "Frontend: http://localhost:3000"
echo "Press Ctrl+C to stop everything."

trap "kill $BACKEND_PID $FRONTEND_PID; exit" SIGINT SIGTERM

wait
