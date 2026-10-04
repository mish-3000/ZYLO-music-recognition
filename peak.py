from spectrogram import get_Sxx
from scipy import ndimage
import matplotlib.pyplot as plt
from mp3_to_wav import wavFilesPaths
import numpy as np

minFreqBin=23 ;'''approx 250Hz'''
maxPeaksPerTimeframe=3
minDB=-50
def get_peaks_for_file(file):
            freq, time, melxx = get_Sxx(file)
            input_melxx=np.where(melxx[minFreqBin:,:]>minDB, melxx[minFreqBin:,:], -np.inf); 

            Pxx=ndimage.maximum_filter(input_melxx, size=5, mode='reflect'); 

            PxxFinalIndices=np.where(Pxx==input_melxx);  

        
            for i in range(Pxx.shape[1]):
                if i in PxxFinalIndices[1]:
                    ValueIndices=np.where(PxxFinalIndices[1]==i)[0]; 
                    Values=Pxx[PxxFinalIndices[0][ValueIndices], PxxFinalIndices[1][ValueIndices]]
                    if np.all(Values == -np.inf):
                        continue; '''if all peaks are -infinity skip this iteration'''
                    if len(Values)>maxPeaksPerTimeframe:
                        sortedIndices=np.argsort(Values)[-maxPeaksPerTimeframe:][::-1]
                        ValuesSorted=Values[sortedIndices]

                    else:
                        sortedIndices=np.argsort(Values)[::-1]
                        ValuesSorted=Values[sortedIndices]
                    
                    freqTimeArr=[]; 
                    for j in sortedIndices:
                        freqTimeTuple1=(time,freq[PxxFinalIndices[0][ValueIndices[j]]+minFreqBin])
                        freqTimeArr.append(freqTimeTuple1)
                
                
                    if -np.inf in ValuesSorted:
                        indicesWithoutNegInf=np.where(ValuesSorted!=-np.inf)[0]; 
                        ValuesSorted=ValuesSorted[indicesWithoutNegInf]
                    
                        freqTimeArr=[]
                        for j in indicesWithoutNegInf:
                            freqTimeTuple2=(time,freq[PxxFinalIndices[0][ValueIndices[sortedIndices][j]]+minFreqBin])
                            freqTimeArr.append(freqTimeTuple2)
                    for j in range(len(ValuesSorted)):  
                        Tuple=freqTimeArr[j] ; 
                        yield Tuple
def get_peaks(minFreqBin, maxPeaksPerTimeframe, minDB): 
    allPeaks={}
    for file in wavFilesPaths:
        get_peaks_for_file(file) 
        peaks=[]; 
        for Tuple in get_peaks_for_file(file):
            peaks.append(Tuple)
            
        allPeaks[file]=peaks ;           
    return allPeaks

def allDicts(file):
    return get_peaks(minFreqBin, maxPeaksPerTimeframe, minDB)[file]
        

