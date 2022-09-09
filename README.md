# Compute Spikes
Compute Spikes for Audio Dropout Analysis and Debugging

## About
Debugging audio drop outs can be challenging- with live mics/instruments it's not clear what are noises/clicks vs. hardware/software drop outs which sound like clicks or pops. By recording a sine wave, we can look for characterstic drop out spikes or other anomolies via FFT spectral analysis in an automated way.

## Installation:
1. Install pip3 python3 if not already installed
2. Run ./install.sh

## Usage:
1. Record audio in your DAW, by sending a sine wave, e.g. 440Hz (A) into line in of your audio interface
2. Run ./cs.sh \<path to your recorded sine wave audio file\>
3. If no errors, PASS will be printed along with some stats
4. If spikes or audio drop outs occured, error data will be printed along with a spectral graph

## Example audio files:

./audio/input_short_clean.aif is an example that should pass with current settings in cs.py. This file had spikes / drop outs removed via spectral edits in Adobe Audition, however there are still some artifacts. Increasing the FFT to 2048 will cause this file to fail. Test with:
 ```   
    ./cs.sh ./audio/input_short_clean.aif

 *** Computing Spikes for: ./audio/input_short_clean.aif *** 

Sample Rate: 48000
Computing Spectrum:
Length (H:M:S):  0:00:03.695979
Time (seconds) of last sample: 3.70
Time (seconds) of last frame:  3.69
Frequency (Hz) of last bin:   24000
Time (samples) : 177408
Number of frames :  347
Number of bins :  513

Computing Approx. Fundamental Frequency:
100% (344 of 344) |####################################################################| Elapsed Time: 0:00:00 Time:  0:00:00
Approx. Fundamental: 421.5, Max Allowed Freq: 1686.0, Energy Error Threshold: 0.2

*** STARTING Spike Analysis ***

100% (344 of 344) |####################################################################| Elapsed Time: 0:00:00 Time:  0:00:00
[PASS]
```
./audio/input_short.aif is an example that should produce 3 errors. Test with:
 ```   
    ./cs.sh ./audio/input_short.aif

 *** Computing Spikes for: ./audio/input_short.aif *** 

Sample Rate: 48000
Computing Spectrum:
Length (H:M:S):  0:00:03.737938
Time (seconds) of last sample: 3.74
Time (seconds) of last frame:  3.73
Frequency (Hz) of last bin:   24000
Time (samples) : 179422
Number of frames :  351
Number of bins :  513

Computing Approx. Fundamental Frequency:
100% (348 of 348) |####################################################################| Elapsed Time: 0:00:00 Time:  0:00:00
Approx. Fundamental: 421.1, Max Allowed Freq: 1684.6, Energy Error Threshold: 0.2

*** STARTING Spike Analysis ***

Error Time 0.245s: AveFreq: 2671.9Hz, MaxFreq: 2718.8Hz, MaxErrorEnergy: 0.5                                                 

Error Time 0.501s: AveFreq: 9937.5Hz, MaxFreq: 9984.4Hz, MaxErrorEnergy: 1.2

Error Time 0.928s: AveFreq: 23953.1Hz, MaxFreq: 24000.0Hz, MaxErrorEnergy: 2.9                                               

100% (348 of 348) |####################################################################| Elapsed Time: 0:00:00 Time:  0:00:00
[FAIL]: Errors: 3
```
![Spectral Image](https://github.com/brightlandco/ComputeSpikes/blob/main/Images/input_short.png)

Note the start and end of audio files can have spectral spikes due to waveform truncation, so the code ignores the first and last FFT frames.