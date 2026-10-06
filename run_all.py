import sys
import glob
import subprocess


venv_python = sys.executable

for file in glob.glob("*.py"):
    if file != "run_all.py":
        print(f"Running {file} using {venv_python}...")
   
        subprocess.run([venv_python, file])
