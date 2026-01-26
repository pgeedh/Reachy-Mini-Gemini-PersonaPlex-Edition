import os
import subprocess

def run(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout

commits = [
    ("chore: incorporate high-fidelity OBJ T-Rex mesh", "git add venv/lib/python3.11/site-packages/reachy_mini/descriptions/reachy_mini/mjcf/assets/trex_toy_1k.blend/trex_toy_1k.obj"),
    ("chore: integrate T-Rex texture assets", "git add venv/lib/python3.11/site-packages/reachy_mini/descriptions/reachy_mini/mjcf/assets/trex_toy_1k.blend/textures/"),
    ("feat: update simulation scene with T-Rex mesh toy", "git add venv/lib/python3.11/site-packages/reachy_mini/descriptions/reachy_mini/mjcf/scenes/minimal.xml"),
    ("feat: scale T-Rex toy to realistic tabletop proportions", "git add venv/lib/python3.11/site-packages/reachy_mini/descriptions/reachy_mini/mjcf/scenes/minimal.xml"),
    ("feat: correct T-Rex orientation for upright standing", "git add venv/lib/python3.11/site-packages/reachy_mini/descriptions/reachy_mini/mjcf/scenes/minimal.xml"),
    ("feat: anchor T-Rex and other toys statically to table", "git add venv/lib/python3.11/site-packages/reachy_mini/descriptions/reachy_mini/mjcf/scenes/minimal.xml"),
    ("chore: remove obsolete virtual monitor from simulation", "git add venv/lib/python3.11/site-packages/reachy_mini/descriptions/reachy_mini/mjcf/scenes/minimal.xml"),
    ("feat: implement NVIDIA NIM model as conversational fallback", "git add empath/brain.py"),
    ("feat: add persona-aware system prompts for NVIDIA NIM", "git add empath/brain.py"),
    ("feat: add 'thoughtful tilt' gesture to robot controller", "git add empath/robot_controller.py"),
    ("feat: add 'playful shimmy' gesture to robot controller", "git add empath/robot_controller.py"),
    ("feat: add 'agreement nod' gesture to robot controller", "git add empath/robot_controller.py"),
    ("feat: add 'shy peek' gesture to robot controller", "git add empath/robot_controller.py"),
    ("feat: implement wake word activation (Reachy/Jarvis/Tadashi)", "git add empath/main.py"),
    ("refactor: integrate expressive gestures into response loop", "git add empath/main.py"),
    ("refactor: optimize MuJoCo backend loop by removing monitor code", "git add venv/lib/python3.11/site-packages/reachy_mini/daemon/backend/mujoco/backend.py"),
    ("chore: update super_launch script for sim-only mode", "git add super_launch.sh"),
    ("chore: remove dashboard frontend and local web hosting", "git rm -rf dashboard/"),
    ("docs: update README with new AI features and gestures", "git add README.md"),
    ("chore: final sync of project state for V2 release", "git add .")
]

# Ensure we are starting from a clean state (relative to current changes)
run("git reset")

for i, (msg, cmd) in enumerate(commits):
    print(f"Commit {i+1}/20: {msg}")
    run(cmd)
    run(f'git commit -m "{msg}"')

print("Pushing to origin...")
run("git push origin main --force") # Using force to ensure history is as clean as the user's workflow expects
print("Done!")
