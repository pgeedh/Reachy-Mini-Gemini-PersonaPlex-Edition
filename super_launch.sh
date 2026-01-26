#!/bin/bash
echo "🚀 Initializing Reachy Empath Super-Launch..."

# 1. Kill everything
echo "🧹 Cleaning up old processes..."
ps aux | grep -E "next dev|empath.main|reachy_mini.daemon" | grep -v grep | awk '{print $2}' | xargs kill -9 2>/dev/null

# 2. Clean Frontend
echo "🧼 Cleaning frontend cache..."
cd dashboard
rm -rf .next
npm install
cd ..

# 3. Start MuJoCo Simulation (Root of Reachy-Mini)
echo "🌍 Starting MuJoCo Simulation..."
nohup ./run_sim.sh > sim.log 2>&1 &
sleep 5

# 4. Start Empath Backend
echo "🧠 Starting Empath Backend..."
source venv/bin/activate
export PYTHONPATH=$PYTHONPATH:$(pwd)
nohup python3 -m empath.main > backend.log 2>&1 &
sleep 5

# 5. Start Empath Frontend
echo "🖥️ Starting Dashboard..."
cd dashboard
npm run dev
