import subprocess
from spectrogram import get_Sxx
from peak import get_peaks_for_file
subprocess.run(['ffmpeg', '-n', '-i'])
pathToffmpeg = r"C:\ffmpeg-master-latest-win64-gpl-shared\bin\ffmpeg.exe"
testclip = r"C:\Users\Hp\OneDrive\Desktop\reactjs\shazam\database\testClipShapeOfYou.mp3"
testclipwav = r"C:\Users\Hp\OneDrive\Desktop\reactjs\shazam\database\testClipShapeOfYou.wav"
subprocess.call([pathToffmpeg,'-n', '-i', testclip, testclipwav])
peaks=[]
for tuple in get_peaks_for_file(testclipwav):
    peaks.append(tuple)
combinationsPerFile=[]
for i in range(len(peaks)):
    timeA, freqA = peaks[i]
    combinationsPerPeak=[]
    if freqA<1000:
        for j in range(i+1, len(peaks)):
            freqT, timeT = peaks[j]
            if freqT<1000 :
                if timeT-timeA>50:
                    break
                if timeT-timeA>0:
                    combinationsPerPeak.append((freqA, freqT, timeA, timeT-timeA, testclipwav))
                    if len(combinationsPerPeak)>10:
                        break
    if len(combinationsPerPeak)>0:
        combinationsPerFile.extend(combinationsPerPeak)
hashinfo={}

for i in range(len(combinationsPerFile)):
            freqA, freqB, timeA, deltaT, file = combinationsPerFile[i]
            hashinfo[file]=[]
            hash=((int(freqA)& 0x3FF)<< 22) | ((int(freqB) & 0x3FF) << 12) | (int(deltaT*1000) & 0xFFF)

            hashinfo[file].append((hash, timeA))
allHashes=[]
for hash, time in hashinfo[testclipwav]:
    allHashes.append(hash)
