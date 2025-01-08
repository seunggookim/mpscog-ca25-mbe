#!/home/sgk/anaconda3/bin/python3

from essentia.standard import *
import sys, librosa, numpy
from pathlib import Path

fname = sys.argv[1]
print("Input file = %s" % fname)
audio = MonoLoader(filename=fname)()
y, sr = librosa.load(fname)

# Compute beat
tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
beats_sec = numpy.single(librosa.frames_to_time(beats, sr=sr))
numpy.savetxt(Path(fname).stem+"_librosaBeat.csv", beats_sec, delimiter=",")

# Mark as beeps
marker = AudioOnsetsMarker(onsets=beats_sec, type='beep')
marked_audio = marker(audio)
MonoWriter(filename=Path(fname).stem+"_librosaBeat.mp4")(marked_audio)
