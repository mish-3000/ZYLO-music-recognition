import subprocess
import os
import matplotlib.pyplot as plt
import numpy as np
import wave, sys

mp3Files=r'C:\Users\Hp\OneDrive\Desktop\PROJECTS\zylo\database\mp3Files'
wavFiles=r'C:\Users\Hp\OneDrive\Desktop\PROJECTS\zylo\database\wavFiles'
pathToffmpeg = r"C:\Users\Hp\OneDrive\Desktop\PROJECTS\zylo\ffmpeg.exe"
wavFilesPaths = []

for file in os.listdir(mp3Files):
    subprocess.call([pathToffmpeg, '-hide_banner', 
    '-loglevel', 'warning', '-n', '-i', os.path.join(mp3Files, file),  '-ar', '44100', os.path.join(wavFiles, str(file.split('.')[0]+'.wav'))]) 
    print(f'Converted {file} to wav format')
    wavFilesPaths.append(os.path.join(wavFiles, str(file.split('.')[0]+'.wav')))
"""def visualize(wavFilesPaths):
    for wavFile in wavFilesPaths:
        raw = wave.open(wavFile)
        signal = raw.readframes(-1)
        signal = np.frombuffer(signal, dtype='int16')
        if raw.getnchannels() == 2:
            expanded_signal = signal.reshape(-1, 2)
            mono=expanded_signal.mean(axis=1)
        else:
            mono=signal
        frameRate = raw.getframerate()
        time = np.linspace(0, len(mono) / frameRate, num=len(mono))
        plt.figure()
        plt.title('Waveform')
        plt.xlabel('Time (s)')
        plt.ylabel('Amplitude')
        plt.plot(time, mono)
        plt.show()

visualize(wavFilesPaths)"""
