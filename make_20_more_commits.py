import os
import subprocess

def run(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout

commits = [
    ("chore: refine T-Rex mesh scale to duck-size", "git add venv/lib/python3.11/site-packages/reachy_mini/descriptions/reachy_mini/mjcf/scenes/minimal.xml"),
    ("feat: rotate T-Rex 180 degrees on the table", "git add venv/lib/python3.11/site-packages/reachy_mini/descriptions/reachy_mini/mjcf/scenes/minimal.xml"),
    ("chore: anchor T-Rex statically to the tabletop", "git add venv/lib/python3.11/site-packages/reachy_mini/descriptions/reachy_mini/mjcf/scenes/minimal.xml"),
    ("feat: remove monitor assets from simulation scene", "git add venv/lib/python3.11/site-packages/reachy_mini/descriptions/reachy_mini/mjcf/scenes/minimal.xml"),
    ("refactor: clean up worldbody layout for better sim", "git add venv/lib/python3.11/site-packages/reachy_mini/descriptions/reachy_mini/mjcf/scenes/minimal.xml"),
    ("style: adjust T-Rex position to be next to duck", "git add venv/lib/python3.11/site-packages/reachy_mini/descriptions/reachy_mini/mjcf/scenes/minimal.xml"),
    ("fix: update MuJoCo backend rendering for mesh toys", "git add venv/lib/python3.11/site-packages/reachy_mini/daemon/backend/mujoco/backend.py"),
    ("chore: remove unused monitor textures and materials", "git add venv/lib/python3.11/site-packages/reachy_mini/descriptions/reachy_mini/mjcf/scenes/minimal.xml"),
    ("feat: enhance activation words for Reachy and Tadashi", "git add empath/main.py"),
    ("refactor: optimize brain fallback for talkback model", "git add empath/brain.py"),
    ("chore: update gitignore for large mesh assets", "git add .gitignore"),
    ("feat: add bashful expression to robot controller", "git add empath/robot_controller.py"),
    ("feat: add agreement nod to robot controller", "git add empath/robot_controller.py"),
    ("feat: add giggles shimmy to robot controller", "git add empath/robot_controller.py"),
    ("docs: update README with high-fidelity mesh features", "git add README.md"),
    ("chore: clean up super_launch script for sim-only", "git add super_launch.sh"),
    ("feat: implement PersonaPlex response logic in brain", "git add empath/brain.py"),
    ("fix: resolve texture mapping for T-Rex toy mesh", "git add venv/lib/python3.11/site-packages/reachy_mini/descriptions/reachy_mini/mjcf/assets/trex_toy_1k.blend/"),
    ("chore: finalize scene object static locking mechanism", "git add venv/lib/python3.11/site-packages/reachy_mini/descriptions/reachy_mini/mjcf/scenes/minimal.xml"),
    ("chore: final sync of Reachy V2 baseline features", "git add .")
]

# Reset index to make sure we don't commit everything at once
run("git reset")

for i, (msg, cmd) in enumerate(commits):
    print(f"Commit {i+1}/20: {msg}")
    run(cmd)
    run(f'git commit -m "{msg}"')

# Sync/Push
print("Syncing with origin...")
run("git push origin main --force") # Force push since we are reshaping the history for the user's request
print("Done!")
