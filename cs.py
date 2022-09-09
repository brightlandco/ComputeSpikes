#!/usr/bin/env python
# Original code from: https://stackoverflow.com/questions/54612204/trying-to-get-the-frequencies-of-a-wav-file-in-python

# Compute Spikes, created 9/22 jcs
# Usage: capture audio using a pure sine wave, e.g. 440Hz (A), then run this test on the captured file (wav, aif etc.)
# If no drop outs or glitches, it will pass, else error information and a spectrogram will be displayed.

import sys
import datetime
import progressbar as pb
import librosa
import sys
import numpy as np
import matplotlib.pyplot as plt
import librosa.display

np.set_printoptions(threshold=sys.maxsize)

try:
    filename = sys.argv[1]
except IndexError:
    raise SystemExit(f"Usage: {sys.argv[0]} <audio file name>")

print(f'\n *** Computing Spikes for: {filename} *** \n')

if True: # Resample to 48kHz
    Fs = 48000
    clip, sample_rate = librosa.load(filename, sr=Fs)
else: # Use file's sample rate
    clip, sample_rate = librosa.load(filename, sr=None)
    Fs = sample_rate
print(f'Sample Rate: {Fs}')

print("Computing Spectrum:")

n_fft = 1024  # frame length / FFT size. Larger FFT's can resolve narrower frequencies
              # (FFT phase info can be used to compute more accurate frequency, not needed and not done here)
hop_length = 512
X = librosa.stft(clip, n_fft=n_fft, hop_length=hop_length)
Xdb = librosa.amplitude_to_db(abs(X))

t_samples = np.arange(clip.shape[0]) / Fs
t_frames = np.arange(X.shape[1]) * hop_length / Fs
f_hertz = np.fft.rfftfreq(n_fft, 1 / Fs)

print("Length (H:M:S): ", str(datetime.timedelta(seconds=t_samples[-1])))
print('Time (seconds) of last sample: %.2f' % t_samples[-1])
print('Time (seconds) of last frame:  %.2f' %t_frames[-1])
print('Frequency (Hz) of last bin:   %d' % f_hertz[-1])
print('Time (samples) :', len(t_samples))

print('Number of frames : ', len(t_frames))
print('Number of bins : ', len(f_hertz))

if False:
    curLine = 'Frequency Bins:\n'
    for b in range(1, len(f_hertz)):
        curLine += f'{f_hertz[b]:>9.1f}\t'
    print(curLine)

maxFreq = 0
maxE_Freq = 0
maxE = 0
curLine = ''
errors = 0
fundamental = 0
fMaxE = 0 # fundamental max energy

print("\nComputing Approx. Fundamental Frequency:")

# Find approx. fundamental frequency first (initial tests were at 440Hz). Note FFT size will affect this estimate
for f in pb.progressbar(range(2, len(t_frames)-1), redirect_stdout=True): # Skip 1st and last frames: can have normal spikes due to waveform cut in/out
#for f in range(2, len(t_frames)-1): # Skip 1st and last frames: can have normal spikes due to waveform cut in/out
    for b in range(1, len(f_hertz)): #for each frame, we get list of bin values printed
        e = np.abs(X[b, f])
        fr = f_hertz[b]
        if e > fMaxE:
            fMaxE = e
            if fundamental == 0:
                fundamental = fr
            else:
                fundamental = (fr + fundamental)*0.5
fMaxE = 0
MaxAllowedFreq = fundamental*4
EnergyThresh = 0.2

print(f'Approx. Fundamental: {fundamental:.1f}Hz, Max Allowed Freq: {MaxAllowedFreq:.1f}Hz, Energy Error Threshold: {EnergyThresh:.1f}\n')

print('\n*** STARTING Spike Analysis ***\n')

#for f in range(1, len(t_frames)):
for f in pb.progressbar(range(2, len(t_frames)-1), redirect_stdout=True): # Skip 1st and last frames: can have normal spikes due to waveform cut in/out
#for f in range(2, len(t_frames)-1): # Skip 1st and last frames: can have normal spikes due to waveform cut in/out
    hit = False
    aveFreqError = 0
    for b in range(1, len(f_hertz)): #for each frame, we get list of bin values printed
        e = np.abs(X[b, f])
        fr = f_hertz[b]
        if e > EnergyThresh and fr > MaxAllowedFreq:
            if aveFreqError == 0:
                aveFreqError = fr
            else:
                aveFreqError = (aveFreqError + fr)*0.5
            if e > maxE:
                maxE = e
                if fr > maxE_Freq:
                    maxE_Freq = fr
            if fr > maxFreq:
                maxFreq = fr
            hit = True 
    if hit:
        errors += 1
        print(f'Error Time {t_frames[f]:4.3f}s: AveFreq: {aveFreqError:.1f}Hz, MaxFreq: {maxFreq:.1f}Hz, MaxErrorEnergy: {maxE:.1f}')

if errors:
    print(f'[FAIL]: Errors: {errors}')
    plt.figure(figsize=(14, 5))
    librosa.display.specshow(Xdb, sr=Fs, x_axis='time', y_axis='hz') 
    librosa.display.specshow(Xdb, sr=Fs, x_axis='time', y_axis='log')
    plt.colorbar()
    plt.show()
else:
    print('[PASS]')
print()