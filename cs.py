#!/usr/bin/env python
# Original code from: https://stackoverflow.com/questions/54612204/trying-to-get-the-frequencies-of-a-wav-file-in-python

# Compute Spikes, created 9/22 jcs
# Usage: capture audio using a pure sine wave, e.g. 440Hz (A), then run this test on the captured file (wav, aif etc.)
# If no drop outs or glitches, it will pass, else error information and a spectrogram will be displayed.

import sys
import datetime
import progressbar as pb
import librosa
import numpy as np
import matplotlib.pyplot as plt
import librosa.display

np.set_printoptions(threshold=sys.maxsize)

try:
    filename = sys.argv[1]
except IndexError:
    raise SystemExit(f'Usage: {sys.argv[0]} <audio file name>')

print(f'\n *** Computing Spikes for: {filename} *** \n')

if True: # Resample to 48kHz
    Fs = 48000
    clip, sample_rate = librosa.load(filename, sr=Fs)
else: # Use file's sample rate
    clip, sample_rate = librosa.load(filename, sr=None)
    Fs = sample_rate
print(f'Sample Rate: {Fs}')

print('Computing Spectrum:')

clip = librosa.util.normalize(clip)

n_fft = 1024  # frame length / FFT size. Larger FFT's can resolve narrower frequencies
              # (FFT phase info can be used to compute more accurate frequency, not needed and not done here)
hop_length = 512
X = librosa.stft(clip, n_fft=n_fft, hop_length=hop_length)
Xdb = librosa.amplitude_to_db(abs(X))

t_samples = np.arange(clip.shape[0]) / Fs
t_frames = np.arange(X.shape[1]) * hop_length / Fs
f_hertz = np.fft.rfftfreq(n_fft, 1 / Fs)

print(f'Length (H:M:S): {datetime.timedelta(seconds=t_samples[-1])}')
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
errors = 0
fundamental = 0
fMaxE = 0 # fundamental max energy

print('\nComputing Approx. Fundamental Frequency:')

SkipFrames = 8

# Find approx. fundamental frequency first (initial tests were at 440Hz). Note FFT size will affect this estimate
for f in pb.progressbar(range(2, len(t_frames)-SkipFrames), redirect_stdout=True):
    for b in range(1, len(f_hertz)):
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
EnergyThresh = 0.15

print(f'Approx. Fundamental: {fundamental:.1f}Hz, Max Allowed Freq: {MaxAllowedFreq:.1f}Hz, Energy Error Threshold: {EnergyThresh:.1f}')

print('\n*** STARTING Spike Analysis ***\n')

NumBins = len(f_hertz)
totalSumE = 0
NumFrames = len(t_frames) - SkipFrames - 1 # Skip 1st and last frames (SkipFrames): can have normal spikes due to waveform cut in/out
sumEFrames = np.tile(0.0,NumFrames)
i = 0
print('Summing frame energies:')
for f in pb.progressbar(range(1, NumFrames), redirect_stdout=True):
    sumE = 0
    for b in range(1, NumBins):
        e = np.abs(X[b, f+1])
        sumE += e
    totalSumE += sumE
    sumEFrames[i] = sumE
    i += 1

AveFrameE = totalSumE / NumFrames
print(f'Ave. Frame Energy: {AveFrameE}')

MaxDeltaFrameESqr = np.square(3.0) # Raise this number to e.g. 10 if not capture a pure sign wave (e.g. running analog sim / effects)
sumDeltaFrameESqr = 0
i = 0
energyErrors = 0
maxErrorSumEFrames = 0
print('Checking frame delta energy from average and computing standard deviation:')
for f in pb.progressbar(range(1, NumFrames), redirect_stdout=True):
    deltaFrameESqr = np.square(sumEFrames[i] - AveFrameE)
    sumDeltaFrameESqr += deltaFrameESqr
    if (deltaFrameESqr > MaxDeltaFrameESqr):
        errorTime = t_frames[f+1]
        errorTimeStr = datetime.timedelta(seconds=errorTime)
        deltaFrameE = np.sqrt(deltaFrameESqr)
        if deltaFrameE > maxErrorSumEFrames:
            maxErrorSumEFrames = deltaFrameE
        print(f'*** DeltaE Error: {errorTimeStr} : {deltaFrameE:.1f}')
        energyErrors += 1
    i += 1

standardDev = np.sqrt(sumDeltaFrameESqr/NumFrames)
print(f'Energy Standard Deviation: {standardDev:.1f}, MaxErrorFrameE/SD: {maxErrorSumEFrames/standardDev:.1f}')

print('Checking for energy / frequency spikes:')
for f in pb.progressbar(range(1, NumFrames), redirect_stdout=True):
    hit = False
    aveFreqError = 0
    for b in range(1, len(f_hertz)):
        e = np.abs(X[b, f+1])
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
        errorTime = t_frames[f+1]
        errorTimeStr = datetime.timedelta(seconds=errorTime)
        print(f'*** Error Time {errorTimeStr}: AveFreq: {aveFreqError:.1f}Hz, MaxFreq: {maxFreq:.1f}Hz, MaxErrorEnergy: {maxE:.3f}')

if errors or energyErrors:
    print(f'[FAIL]: Errors: {errors}, Energy Errors: {energyErrors}')
else:
    print('[PASS]')
print()

plt.figure(figsize=(14, 5))
#librosa.display.specshow(Xdb, sr=Fs, x_axis='time', y_axis='hz') 
librosa.display.specshow(Xdb, sr=Fs, x_axis='time', y_axis='log')
plt.colorbar()
plt.show()
