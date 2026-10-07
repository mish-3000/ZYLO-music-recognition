import subprocess
import os

from spectrogram import get_Sxx
from peak import get_peaks_for_file

pathToffmpeg = r"C:\Users\Hp\OneDrive\Desktop\PROJECTS\zylo\ffmpeg.exe"
testclip = r"C:\Users\Hp\OneDrive\Desktop\PROJECTS\zylo\database\testClips\three.OGG"
testclipwav = r"C:\Users\Hp\OneDrive\Desktop\PROJECTS\zylo\database\testClips\three.wav"
subprocess.call([pathToffmpeg, '-hide_banner', 
    '-loglevel', 'warning', '-n', '-i', testclip, '-ar', '44100', testclipwav])
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
