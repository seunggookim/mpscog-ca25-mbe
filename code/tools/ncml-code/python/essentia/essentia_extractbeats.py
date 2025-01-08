#!/home/sgk/anaconda3/bin/python

from essentia.standard import *
import sys, numpy
from pathlib import Path

fname = sys.argv[1]
print("Input file = %s" % fname)
audio = MonoLoader(filename=fname)()

# Compute beat positions and BPM
rhythm_extractor = RhythmExtractor2013(method="multifeature")
bpm, beats, beats_confidence, _, beats_intervals = rhythm_extractor(audio)
print("BPM:", bpm)
print("Beat positions (sec.):", beats)
print("Beat estimation confidence:", beats_confidence)
numpy.savetxt(Path(fname).stem+"_essentiaBeat.csv", beats, delimiter=",")

# Mark as beeps
marker = AudioOnsetsMarker(onsets=beats, type='beep')
marked_audio = marker(audio)
MonoWriter(filename=Path(fname).stem+"_essentiaBeat.mp4")(marked_audio)
