#! /usr/bin/env python
# -*- coding: utf-8 -*-

import pyaudio
import wave
import sys
import pylab
import numpy
import os

from subprocess import Popen, PIPE
from pylab import *

CHUNK    = 1024
FORMAT   = pyaudio.paInt16
CHANNELS = 1
RATE     = 44100
READ_CNT = 4410 * 3

E5 = 659
A4 = 440
D4 = 294
E4 = 330
G3 = 199
freqs = [G3, D4, A4, E5, E4]
cmds  = ["h", "j", "k", "l", "rr"]

MARGIN = 10

hammingWindow = np.hamming(READ_CNT)

def getFreqIndex(hz):
    for (i, f) in enumerate(freqs):
        if f + MARGIN > hz and f - MARGIN < hz:
            return i
    return -1

def sendKey(hz):
    index = getFreqIndex(hz)
    if index < 0:
        return

    AS = '''
    tell application "MacVim"
        activate
        tell application "System Events"
            keystroke "%s"
        end tell
    end tell
    ''' % cmds[index]

    osa = Popen('osascript', stdin = PIPE)
    osa.stdin.write(AS)
    osa.stdin.close()
    os.waitpid(osa.pid, 0)

def getHz(data):
    data = frombuffer(data, dtype="int16")
    data = hammingWindow * data

    dft      = np.fft.fft(data)
    freqList = np.fft.fftfreq(len(data), d = 1.0 / len(data))
    amp      = [np.sqrt(c.real ** 2 + c.imag ** 2) for c in dft]

    maxValue = 0
    hz       = 0
    for (i, x) in enumerate(amp):
        if x < maxValue or freqList[i] <= 0:
            continue
        maxValue = x
        hz       = freqList[i]

    return int(hz * RATE / READ_CNT)

def loop():
    p      = pyaudio.PyAudio()
    stream = p.open(
                format            = FORMAT,
                channels          = CHANNELS,
                rate              = RATE,
                frames_per_buffer = CHUNK,
                input             = True
            )
    for i in range(1000):
        stream.start_stream()
        data = stream.read(READ_CNT)
        stream.stop_stream()
        hz   = getHz(data)
        print hz
        sendKey(hz)
    stream.close()
    p.terminate()

if __name__ == "__main__":
    loop()

