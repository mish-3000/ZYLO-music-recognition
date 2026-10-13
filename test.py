import subprocess
import os
import sounddevice as sd
import soundfile as sf
import numpy as np

from spectrogram import get_Sxx
from peak import get_peaks_for_file

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
pathToffmpeg = os.path.join(BASE_DIR, 'downloaders', 'ffmpeg.exe')
if not os.path.exists(pathToffmpeg):
    pathToffmpeg = 'ffmpeg'
testClipsDir = os.path.join(BASE_DIR, 'database', 'testClips')
os.makedirs(testClipsDir, exist_ok=True)
testclip = os.path.join(testClipsDir, 'recording.flac')
testclipwav = os.path.join(testClipsDir, 'recording.wav')

fs = int(sd.query_devices(kind='input')['default_samplerate']) 
chunks = []
def callback(indata, frames, time_info, status):
    chunks.append(indata.copy())

input("Press Enter to start recording.")
with sd.InputStream(samplerate=fs, channels=2, callback=callback):
    input("Recording. press Enter to stop")
print("Recording finished")
if not chunks:
    print("Error: nothing was recorded.")
    exit()
myrecording = np.concatenate(chunks)
duration = len(myrecording) / fs
if duration < 3:
    print(f"Recording too short ({duration:.1f} s), record at least 3 seconds")
    exit()
loudness_db = 20*np.log10(np.median(np.abs(myrecording)) + 1e-12)
if loudness_db < -60:
    print(f"Recording too quiet ({loudness_db:.1f} dB), move closer / raise mic volume")
    exit()
sf.write(testclip, myrecording, fs)

subprocess.call([pathToffmpeg, '-hide_banner',
    '-loglevel', 'warning', '-y', '-i', testclip, '-ar', '11025', testclipwav])
peaks=[]
for tuple in get_peaks_for_file(testclipwav):
    peaks.append(tuple)
combinationsPerFile=[]
for i in range(len(peaks)):
    timeA, freqA = peaks[i]
    combinationsPerPeak=[]
    if freqA<1000:
        for j in range(i+1, len(peaks)):
            timeT, freqT = peaks[j]
            if freqT<1000 :
                if timeT-timeA>50:
                    break
                if timeT-timeA>0:
                    combinationsPerPeak.append((freqA, freqT, timeA, timeT-timeA, testclipwav))
                    if len(combinationsPerPeak)>10:
                        break
    if len(combinationsPerPeak)>0:
        combinationsPerFile.extend(combinationsPerPeak);
def hashinformation(file):
     hashinfo={}
     hashinfo[file]=[]
     
     for i in range(len(combinationsPerFile)):
        freqA, freqB, timeA, deltaT, file = combinationsPerFile[i]
        
        hash=((int(freqA)& 0x3FF)<< 22) | ((int(freqB) & 0x3FF) << 12) | (int(deltaT) & 0xFFF)

        hashinfo[file].append((hash, timeA))
     return hashinfo
    



allHashes={}
for hash, time in hashinformation(testclipwav)[testclipwav]:
    allHashes[hash] = time* 0.0464 * 1000 

if not allHashes:
    print("Warning: 0 hashes extracted from test clip.")
