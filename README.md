# ComputeSpikes
Compute Spikes for Audio Dropout Analysis and Debugging

## Installation:
1. Install python 3 if not already installed
2. Run ./install.sh

## Usage:
1. Record audio in your DAW, by sending a sine wave, e.g. 440Hz (A) into line in of your audio interface
2. Run ./cs.sh \<path to your audio file\>
3. If no errors, PASS will be printed along with some stats
4. If spikes or audio drop outs occured, error data will be printed along with a spectral graph

## Example audio files:

./audio/input_short_clean.aif is an example that should pass with current settings in cs.py. This file had spikes / drop outs removed via spectral edits in Adobe Audition, however there are still some artifacts. Increasing the FFT to 2048 will cause this file to fail. Test with:
 ```   
    ./cs.sh ./audio/input_short_clean.aif
```
./audio/input_short.aif is an example that should produce 3 errors. Test with:
 ```   
    ./cs.sh ./audio/input_short.aif
```
Note the start and end of audio files can have spectral spikes due to waveform truncation, so the code ignores the first and last FFT frames.