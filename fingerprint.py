from peak import allDicts
from mp3_to_wav import wavFilesPaths
import numpy as np

def combinations():
    allCombinations={}
    for file in wavFilesPaths:
        peaks = allDicts(file)
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
                            combinationsPerPeak.append((freqA, freqT, timeA, timeT-timeA, file))
                            if len(combinationsPerPeak)>10:
                                break
            if len(combinationsPerPeak)>0:
                combinationsPerFile.extend(combinationsPerPeak)            
            
        
        allCombinations[file] = combinationsPerFile
    return allCombinations

def hashes():
    hashinfo={}
    for file in wavFilesPaths:
        hashinfo[file] = []
        combination=combinations()[file]
        for i in range(len(combination)):
            freqA, freqB, timeA, deltaT, file = combination[i]
            hash=((int(freqA)& 0x3FF)<< 22) | ((int(freqB) & 0x3FF) << 12) | (int(deltaT) & 0xFFF)

            hashinfo[file].append((hash, timeA))

    return hashinfo
