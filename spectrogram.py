from mp3_to_wav import wavFilesPaths
from scipy.io import wavfile
from scipy.signal import spectrogram
from scipy.signal.windows import hann
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import wavio
def get_Sxx(file):
    
    wavData = wavio.read(file)
    sampleRate = 44100; 
    signal = wavData.data; '''returns a 2d array always, even if the audio is mono'''
    if signal.shape[1] == 2:
        mono=signal.mean(axis=1)
    else:
        mono=signal.reshape(-1)
    if mono.dtype==np.uint8:
        mono =(mono-128)/128
    elif mono.dtype==np.int16:
        mono = mono/32768
    elif mono.dtype==np.int32:
        mono = mono/2147483648
        
    window_dur=0.0928
    step_dur = window_dur / 2
    step_samples = int(round(step_dur * sampleRate))
    window_samples = int(round(window_dur * sampleRate))
    window = hann(window_samples, sym=False)
    overlap = window_samples - step_samples
    freq, time, Sxx = spectrogram(mono, fs=sampleRate, window=window, nperseg=window_samples, noverlap=overlap)
    melxx=np.where(Sxx>0, 10*np.log10(Sxx), -100)
        
    return freq, time, melxx

def show_spectrogram(freq, time, melxx):
        
        plt.figure()
        plt.pcolormesh(time[:100], freq, melxx[:, :100], shading='gouraud')
        plt.title('Spectrogram')
        plt.xlabel('Time (s)')
        plt.ylabel('Frequency (Hz)')
        plt.show()
if __name__ == "__main__":
    for file in wavFilesPaths:
        freq, time, melxx = get_Sxx(file)
        show_spectrogram(freq, time, melxx)
