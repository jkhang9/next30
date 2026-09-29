"""A 15 s music-box waltz for NEXT30 (3/4 at 120 bpm, two bars per era) -> out/music.wav"""
import os
import wave

import numpy as np

SR, DUR, BEAT = 44100, 15.0, 0.5
N = {'A2': 45, 'C3': 48, 'D3': 50, 'F2': 41, 'G2': 43, 'G3': 55, 'A3': 57, 'B3': 59, 'C4': 60, 'D4': 62,
     'E4': 64, 'F4': 65, 'G4': 67, 'A4': 69, 'B4': 71, 'C5': 72, 'D5': 74, 'E5': 76, 'F5': 77, 'G5': 79,
     'A5': 81, 'B5': 83, 'C6': 84, 'D6': 86}
BARS = [  # (bass, chord, melody)
    ('C3', 'C4 E4 G4', 'G4 C5 E5'), ('C3', 'C4 E4 G4', 'G5 E5 C5'),
    ('A2', 'A3 C4 E4', 'A4 C5 E5'), ('F2', 'A3 C4 F4', 'F5 E5 C5'),
    ('F2', 'A3 C4 F4', 'A4 C5 F5'), ('C3', 'C4 E4 G4', 'E5 D5 C5'),
    ('D3', 'D4 F4 A4', 'D5 F5 A5'), ('G2', 'G3 B3 D4', 'G5 B5 D6'),
    ('C3', 'C4 E4 G4', 'C6 G5 E5'), ('C3', 'C4 E4 G4', 'C5 - -'),
]
out = np.zeros(int(SR * (DUR + 2)))


def note(name, t0, amp, decay, partials):
    f = 440.0 * 2 ** ((N[name] - 69) / 12.0)
    t = np.arange(int(SR * 2.5)) / SR
    env = np.minimum(t / 0.004, 1.0) * np.exp(-t * decay)
    s = sum(a * np.sin(2 * np.pi * f * m * t) for m, a in partials) * env * amp
    i = int(t0 * SR)
    out[i:i + len(s)] += s[:len(out) - i]


BELL = [(1, 1.0), (2, 0.3), (3, 0.1), (4.2, 0.05)]
for b, (bass, chord, mel) in enumerate(BARS):
    t = b * 3 * BEAT
    note(bass, t, 0.35, 2.0, [(1, 1.0), (2, 0.15)])
    for k in (1, 2):
        for c in chord.split():
            note(c, t + k * BEAT, 0.07, 5.0, BELL)
    for k, m in enumerate(mel.split()):
        if m != '-':
            note(m, t + k * BEAT, 0.3, 1.4 if b == 9 else 3.0, BELL)
out = out[:int(SR * DUR)]
out *= np.minimum(1.0, (DUR - np.arange(len(out)) / SR) / 0.4)
out = (out / np.abs(out).max() * 0.8 * 32767).astype(np.int16)
path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'out', 'music.wav')
with wave.open(path, 'wb') as w:
    w.setnchannels(1), w.setsampwidth(2), w.setframerate(SR), w.writeframes(out.tobytes())
print('wrote', path)
