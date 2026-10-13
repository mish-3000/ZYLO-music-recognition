import subprocess
import os
import matplotlib.pyplot as plt
import numpy as np
import wave, sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
mp3Files = os.path.join(BASE_DIR, 'database', 'orgFiles')
wavFiles = os.path.join(BASE_DIR, 'database', 'wavFiles')
pathToffmpeg = os.path.join(BASE_DIR, 'downloaders', 'ffmpeg.exe')
if not os.path.exists(pathToffmpeg):
    pathToffmpeg = 'ffmpeg'  
wavFilesPaths = []

if not os.path.exists(mp3Files):
    print(f" Error: mp3Files directory not found: {mp3Files}")
    exit()
if not os.path.exists(wavFiles):
    os.makedirs(wavFiles)
    

for file in os.listdir(mp3Files):
    filename_without_ext = os.path.splitext(file)[0]
    wavPath = os.path.join(wavFiles, filename_without_ext+'.wav')
    if not os.path.exists(wavPath):
        subprocess.call([pathToffmpeg, '-hide_banner',
        '-loglevel', 'warning', '-n', '-i', os.path.join(mp3Files, file),  '-ar', '11025', wavPath])
        print(f'Converted {file} to wav format')
    wavFilesPaths.append(wavPath)
