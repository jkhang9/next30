"""Soundtrack for NEXT30 -> out/soundtrack.wav

Every era gets its own little band (same tempo and chord path, so the hand-offs are
smooth), and the things that move get cute, Animal Crossing-style sounds synced to
the frames: bubbly pops while the diorama is rebuilt, babbly blips while captions
type, bloops, plinks, chirps, poofs and sparkles.
"""
import os
import wave

import numpy as np
from scipy.signal import fftconvolve, lfilter

import film

SR = 44100
DUR = film.N_FRAMES / float(film.FPS)
BAR, E8 = 1.5, 0.25            # 3/4 at 120 bpm: two bars per era, eighth note = 3 frames
LEN = int(SR * (DUR + 2))
rng = np.random.default_rng(30)
bus = {'music': np.zeros((2, LEN)), 'sfx': np.zeros((2, LEN))}
PENTA = [0, 2, 4, 7, 9, 12, 14, 16, 19, 21, 24]


def fr(f):
    return f / float(film.FPS)


def hz(name):
    pc = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}[name[0]]
    pc += name[1:-1].count('#') - name[1:-1].count('b')
    return 440.0 * 2 ** ((12 * (int(name[-1]) + 1) + pc - 69) / 12.0)


def tt(dur):
    return np.arange(int(dur * SR)) / SR


def add(which, sig, t0, gain=1.0, pan=0.0):
    i = int(round(t0 * SR))
    if i < 0:
        sig, i = sig[-i:], 0
    sig = sig[:max(0, LEN - i)]
    th = (np.clip(pan, -1, 1) + 1) * np.pi / 4
    bus[which][0, i:i + len(sig)] += sig * gain * np.cos(th)
    bus[which][1, i:i + len(sig)] += sig * gain * np.sin(th)


# ---- instruments -----------------------------------------------------------

EP = ((1, 1.0), (2, 0.22), (3, 0.06), (7, 0.02))
BELL = ((1, 1.0), (2, 0.3), (3, 0.1), (4.2, 0.06))
MARIMBA = ((1, 1.0), (4, 0.22), (9.2, 0.04))
VIBES = ((1, 1.0), (4, 0.12))
GLASS = ((1, 1.0), (2.76, 0.25), (5.4, 0.08))
FLUTE = ((1, 1.0), (2, 0.12), (3, 0.05))
SQUARE = tuple((k, 0.75 ** ((k - 1) // 2) / k) for k in (1, 3, 5, 7))
BASS = ((1, 1.0), (2, 0.25))


def tone(f, dur, partials=((1, 1.0),), decay=3.0, attack=0.004, vib=0.0, trem=0.0, glide=0.0):
    t = tt(dur)
    f_t = f * (1 + vib * np.sin(2 * np.pi * 5.5 * t)) * (1 - glide * np.exp(-t / 0.03))
    ph = 2 * np.pi * np.cumsum(f_t) / SR
    s = sum(a * np.sin(m * ph) for m, a in partials)
    env = np.minimum(t / attack, 1) * np.exp(-t * decay)
    if trem:
        env = env * (1 - trem * (0.5 + 0.5 * np.sin(2 * np.pi * 4.5 * t)))
    return s * env


def noise(dur, lp=None, hp=False):
    n = rng.standard_normal(int(dur * SR))
    if hp:
        n = np.diff(n, prepend=0.0)
    if lp:
        a = np.exp(-2 * np.pi * lp / SR)
        n = lfilter([1 - a], [1, -a], n)
    return n


def held(f, length, partials=FLUTE, vib=0.008, breath=0.03):
    rel = 0.12
    dur = length + rel
    t = tt(dur)
    s = tone(f, dur, partials, decay=0.0, attack=0.05, vib=vib)
    s = s + breath * noise(dur, lp=3000, hp=True) * np.minimum(t / 0.05, 1)
    return s * np.clip((dur - t) / rel, 0, 1)


def pluck(f, dur, decay=0.996):
    """Karplus-Strong string, good enough for a ukulele."""
    N, n = max(2, int(SR / f)), int(dur * SR)
    out = np.zeros(n + N)
    out[:N] = lfilter([0.5, 0.5], [1], rng.uniform(-1, 1, N))
    for i in range(N, n, N):
        prev = out[i - N:i]
        out[i:i + N] = decay * 0.5 * (prev + np.concatenate(([out[i - N - 1]], prev[:-1])))
    return out[:n] * np.exp(-tt(dur) * 1.5)


def pad(f, dur, attack=0.6, release=0.8):
    t = tt(dur)
    s = sum(np.sin(2 * np.pi * f * d * t + p) for d, p in ((1, 0), (1.003, 1.3), (0.997, 2.1))) / 3
    return s * np.minimum(t / attack, 1) * np.clip((dur - t) / release, 0, 1)


def kick():
    t = tt(0.3)
    return np.sin(2 * np.pi * np.cumsum(50 + 70 * np.exp(-t / 0.03)) / SR) * np.exp(-t * 14)


def brush(dur=0.12):
    return noise(dur, lp=7000, hp=True) * np.exp(-tt(dur) * 30)


# ---- motion sounds (cute, short, bubbly) -------------------------------------

def bloop(f0, f1, dur=0.1, decay=25.0):
    t = tt(dur)
    ph = 2 * np.pi * np.cumsum(f0 * (f1 / f0) ** (t / dur)) / SR
    return (np.sin(ph) + 0.2 * np.sin(2 * ph)) * np.minimum(t / 0.003, 1) * np.exp(-t * decay)


def blip(f):
    return tone(f, 0.055, ((1, 1.0), (2, 0.45), (3, 0.2)), decay=40, glide=-0.12)


def chirp(f, n=3, gap=0.065):
    out = np.zeros(int(SR * (gap * n + 0.08)))
    for j in range(n):
        s = blip(f * 2 ** (PENTA[j * 2] / 12.0))
        i = int(j * gap * SR)
        out[i:i + len(s)] += s
    return out


def sparkle(notes=('E7', 'G7', 'C8', 'E8'), gap=0.035, decay=12):
    out = np.zeros(int(SR * (gap * len(notes) + 0.4)))
    for j, n in enumerate(notes):
        s = tone(hz(n), 0.4, ((1, 1.0), (2.7, 0.2)), decay=decay)
        i = int(j * gap * SR)
        out[i:i + len(s)] += s
    return out


def tweet():
    out = np.zeros(int(SR * 0.2))
    for j in range(2):
        t = tt(0.06)
        s = np.sin(2 * np.pi * np.cumsum(4200 - 1600 * t / 0.06) / SR) * np.sin(np.pi * t / 0.06)
        out[int(j * 0.09 * SR):int(j * 0.09 * SR) + len(s)] += s
    return out


def poof(dur=0.3):
    t = tt(dur)
    return noise(dur, lp=900) * np.minimum(t / 0.01, 1) * np.exp(-t * 11) * 3


def whoosh(dur, rising=True):
    t = tt(dur)
    lo, hi = noise(dur, lp=350), noise(dur, lp=2500)
    k = t / dur if rising else 1 - t / dur
    return (lo * (1 - k) * 3 + hi * k) * np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 1.5


def crickets(t0, t1, pan):
    t = t0 + rng.uniform(0, 0.3)
    while t < t1:
        for p in range(3):
            add('sfx', tone(4400, 0.018, decay=0, attack=0.003) * np.hanning(int(0.018 * SR)),
                t + p * 0.035, 0.022, pan)
        t += 0.55 + rng.uniform(-0.08, 0.08)


# ---- the five eras -----------------------------------------------------------

def era_2026(s0):
    for b, (bass, chord) in enumerate((('C3', 'E4 G4 C5'), ('G2', 'D4 G4 B4'))):
        t = s0 + b * BAR
        add('music', tone(hz(bass), 1.6, BASS, decay=2.2), t, 0.28)
        for e in (0, 3):
            for n in chord.split():
                add('music', tone(hz(n), 1.2, EP, decay=2.6, trem=0.25), t + e * E8, 0.065)
    for e, n, l in ((0, 'E5', 2), (2, 'G5', 1), (3, 'E5', 1), (4, 'C5', 2),
                    (6, 'D5', 2), (8, 'B4', 1), (9, 'D5', 1), (10, 'G5', 2)):
        add('music', held(hz(n), l * E8 * 0.9), s0 + e * E8, 0.15, 0.15)


def era_2034(s0):
    for b, (bass, arp) in enumerate((('A2', 'A3 C4 E4 A4 E4 C4'), ('F2', 'F3 A3 C4 F4 C4 A3'))):
        t = s0 + b * BAR
        add('music', tone(hz(bass), 1.4, BASS, decay=3.0), t, 0.26)
        for e, n in enumerate(arp.split()):
            add('music', tone(hz(n), 0.5, MARIMBA, decay=9), t + e * E8, 0.1, -0.25)
    for e, n in ((0, 'E5'), (1, 'A5'), (2, 'C6'), (4, 'B5'), (5, 'A5'),
                 (6, 'A5'), (7, 'F5'), (8, 'C5'), (10, 'E5')):
        add('music', tone(hz(n), 1.2, VIBES, decay=2.2, trem=0.3), s0 + e * E8, 0.12, 0.2)


def era_2041(s0):
    for b, (bass, chord) in enumerate((('F2', 'F3 A3 C4 F4'), ('C3', 'C4 E4 G4 C5'))):
        t = s0 + b * BAR
        add('music', tone(hz(bass), 1.4, BASS, decay=2.6), t, 0.28)
        for e in (0, 2, 3, 5):
            for j, n in enumerate(chord.split()):
                add('music', pluck(hz(n), 0.9), t + e * E8 + j * 0.012, 0.09 if e == 0 else 0.07, -0.3)
        for e in range(6):
            add('music', brush(0.06), t + e * E8, 0.02 if e % 2 == 0 else 0.035, 0.4)
    for e, n, l in ((0, 'A5', 2), (2, 'C6', 1), (3, 'A5', 1), (4, 'F5', 2),
                    (6, 'G5', 2), (8, 'E5', 1), (9, 'G5', 1), (10, 'C6', 2)):
        add('music', held(hz(n), l * E8 * 0.9, vib=0.01, breath=0.05), s0 + e * E8, 0.14, 0.2)


def era_2049(s0):
    for b, (line, chord) in enumerate((('D3 D3 A2 A2 D3 F3', 'D4 F4 A4'), ('G2 G2 D3 D3 G3 B3', 'G4 B4 D5'))):
        t = s0 + b * BAR
        for e, n in enumerate(line.split()):
            add('music', tone(hz(n), 0.4, ((1, 1.0), (2, 0.35), (3, 0.1)), decay=7, glide=0.03), t + e * E8, 0.2)
        add('music', kick(), t, 0.3)
        for e in (2, 4):
            add('music', brush(), t + e * E8, 0.1)
        if b == 0:
            for j in range(6):
                add('music', brush(0.08), t + 4 * E8 + j * E8 / 3, 0.04 + 0.015 * j)
        for n in chord.split():
            add('music', tone(hz(n), 1.4, SQUARE, decay=1.8, attack=0.02), t, 0.03)
    for e, n, l in ((0, 'D5', 1), (1, 'F5', 1), (2, 'A5', 2), (4, 'D6', 2),
                    (6, 'G5', 1), (7, 'B5', 1), (8, 'D6', 1), (9, 'G6', 3)):
        add('music', tone(hz(n), l * E8 + 0.35, SQUARE, decay=2.2, attack=0.01, glide=0.04), s0 + e * E8, 0.06, 0.1)


def era_2056(s0):
    for b in range(2):
        add('music', tone(hz('C3'), 2.2, BASS, decay=1.5), s0 + b * BAR, 0.22)
    for n in ('C4', 'E4', 'G4', 'C5'):
        add('music', pad(hz(n), DUR - s0 + 0.2), s0 - 0.3, 0.03)
    for e, n in ((0, 'E5'), (2, 'G5'), (4, 'C6'), (6, 'B5'), (7, 'D5'), (8, 'C5')):
        add('music', tone(hz(n), 2.6, BELL, decay=1.1 if e == 8 else 2.6), s0 + e * E8, 0.2)
    for e, n in ((1, 'G4'), (3, 'C5'), (5, 'G4'), (9, 'E4'), (10, 'G4')):
        add('music', tone(hz(n), 1.5, BELL, decay=3.0), s0 + e * E8, 0.06)


# ---- motion cues, frame by frame --------------------------------------------

def rebuild_cues():
    for k in range(len(film.SCENES)):
        f0 = k * film.SCENE_LEN
        base = hz('C5') * 2 ** (PENTA[k % 3] / 12.0)
        if k > 0:
            add('sfx', noise(0.45, lp=6000, hp=True) * (tt(0.45) / 0.45) ** 2, fr(f0) - 0.45, 0.03)
            for j in range(8):          # the old set comes down...
                f = base * 2 ** (PENTA[7 - j] / 12.0)
                add('sfx', bloop(f * 1.4, f), fr(f0) + j * 0.042, 0.1, rng.uniform(-0.5, 0.5))
        for j in range(10):             # ...and the new one stacks up
            f = base * 2 ** (PENTA[j] / 12.0)
            add('sfx', bloop(f, f * 1.6, 0.09, 30), fr(f0 + 2) + j * 0.035, 0.11, rng.uniform(-0.5, 0.5))


def caption_cues():
    prev = ''
    for f in range(film.N_FRAMES):
        text, _ = film.caption_at(f)
        if len(text) > len(prev):
            new = text[len(prev):]
            for j, ch in enumerate(new):
                if ch != ' ':
                    p = hz('E5') * 2 ** (PENTA[(ord(ch) * 7) % 8] / 12.0)
                    add('sfx', blip(p), fr(f) + j * fr(1) / len(new), 0.06)
        elif len(text) < len(prev):
            gone = len(prev) - len(text)
            for j in range(gone):
                add('sfx', blip(hz('A4') * 0.97 ** j), fr(f) + j * fr(1) / gone, 0.035)
        prev = text


def scene_cues():
    # 2026: typing, the spark pops out of the laptop, a wave hello
    for f in range(6, 16):
        for _ in range(2):
            add('sfx', noise(0.012, hp=True) * np.exp(-tt(0.012) * 400), fr(f) + rng.uniform(0, fr(1)), 0.05)
    add('sfx', bloop(380, 1150, 0.16, 14), fr(12), 0.22, 0.1)
    add('sfx', sparkle(), fr(14), 0.08, 0.2)
    add('sfx', whoosh(0.3), fr(15), 0.05, 0.3)
    add('sfx', chirp(hz('G5'), 2), fr(20), 0.1, -0.1)
    add('sfx', tone(3100, 0.15, ((1, 1.0), (2.7, 0.2)), decay=30), fr(26), 0.05, 0.3)
    # 2034: the helix plays a rising scale as it grows, then a little celebration
    f0 = film.SCENE_LEN
    notes = 'A4 C5 D5 E5 G5 A5 C6 D6 E6 G6 A6'.split()
    for j, i in enumerate(range(8, 29, 2)):
        add('sfx', tone(hz(notes[j]), 0.35, GLASS, decay=14), fr(f0 + i), 0.1, 0.35)
    add('sfx', sparkle(('A6', 'C7', 'E7', 'A7', 'C8')), fr(f0 + 28), 0.09, 0.35)
    add('sfx', chirp(hz('C6')), fr(f0 + 29), 0.09, -0.2)
    for i in (6, 18, 30):
        add('sfx', tone(1046, 0.07, decay=25), fr(f0 + i), 0.03, -0.4)
    for i in range(9, 36, 5):
        add('sfx', bloop(500, 950, 0.05, 55), fr(f0 + i), 0.035, -0.6)
    # 2041: trees pomf as they grow, flowers plink in, water plips, birds tweet
    f0 = 2 * film.SCENE_LEN
    for j, i in enumerate((10, 14, 18, 22, 26, 30)):
        add('sfx', bloop(170 * 1.1 ** j, 300 * 1.1 ** j, 0.16, 16), fr(f0 + i), 0.16, rng.uniform(-0.4, 0.2))
    r = np.random.default_rng(5)
    per_frame = {}
    for _ in range(46):
        x, _z, appear = r.integers(9, 63), r.integers(9, 63), 8 + r.integers(0, 18)
        per_frame.setdefault(int(appear), []).append(int(x))
    for i, xs in per_frame.items():
        for x in xs[:2]:
            n = hz('C6') * 2 ** (PENTA[rng.integers(0, 8)] / 12.0)
            add('sfx', tone(n, 0.25, GLASS, decay=22), fr(f0 + i) + rng.uniform(0, fr(1)), 0.05, (x - 36) / 40.0)
    for i in range(7, 36, 3):
        add('sfx', bloop(900, 1800, 0.05, 60), fr(f0 + i), 0.04, -0.1)
    for i in (9, 13, 20, 24, 30):
        add('sfx', tweet(), fr(f0 + i), 0.06, np.clip((4 + (i - 6) * 2.2 - 36) / 40.0, -0.8, 0.8))
    # 2049: beacon, ignition rumble and poofs, lift-off whoosh, cheering
    f0 = 3 * film.SCENE_LEN
    for i in range(0, film.LIFTOFF + 1, 6):
        add('sfx', tone(880, 0.08, decay=18), fr(f0 + i), 0.03, 0.5)
    ig, lo = fr(f0 + film.IGNITION), fr(f0 + film.LIFTOFF)
    dur = 2.4
    t = tt(dur)
    add('sfx', noise(dur, lp=140) * np.minimum(t / 0.4, 1) * np.clip((dur - t) / 1.2, 0, 1) * 4, ig, 0.18, 0.2)
    for j in range(4):
        add('sfx', poof(), ig + j * fr(1), 0.1, rng.uniform(-0.3, 0.6))
    add('sfx', whoosh(1.6), lo, 0.16, 0.25)
    add('sfx', chirp(hz('E5')), lo + 0.05, 0.1, -0.4)
    add('sfx', chirp(hz('G5')), lo + fr(4), 0.09, -0.3)
    # 2056: crickets, fireflies, the spark hops, a shooting star, a heart
    f0 = 4 * film.SCENE_LEN
    crickets(fr(f0 + 2), DUR, -0.6)
    crickets(fr(f0 + 5), DUR, 0.6)
    for i in range(8, 36, 4):
        add('sfx', tone(hz('C7') * 2 ** (PENTA[rng.integers(0, 6)] / 12.0), 0.2, GLASS, decay=25),
            fr(f0 + i), 0.02, rng.uniform(-0.7, 0.7))
    for i in (12, 16):
        add('sfx', bloop(320, 640, 0.18, 12), fr(f0 + i), 0.08, 0.1)
    star = 'A7 G7 E7 D7 C7 A6 G6 E6 D6 C6'.split()
    add('sfx', sparkle(star, gap=0.04, decay=10), fr(f0 + 10), 0.07, 0.6)
    add('sfx', noise(0.6, lp=9000, hp=True) * np.exp(-tt(0.6) * 5), fr(f0 + 10), 0.02, 0.6)
    add('sfx', bloop(350, 700, 0.15, 14), fr(f0 + 22), 0.18)
    for n in ('E6', 'G6', 'C7'):
        add('sfx', tone(hz(n), 1.2, BELL, decay=4), fr(f0 + 22) + 0.05, 0.05)
    add('sfx', tone(3100, 0.15, ((1, 1.0), (2.7, 0.2)), decay=30), fr(f0 + 32), 0.04, 0.2)


def main():
    for k, era in enumerate((era_2026, era_2034, era_2041, era_2049, era_2056)):
        era(k * 3.0)
    rebuild_cues()
    caption_cues()
    scene_cues()
    dry = bus['music'] + 0.9 * bus['sfx']
    t = tt(1.6)
    ir = np.stack([lfilter([0.3], [1, -0.7], rng.standard_normal(len(t))) * np.exp(-t / 0.32) for _ in range(2)])
    ir /= np.sqrt((ir ** 2).sum(axis=1, keepdims=True))
    wet = np.stack([fftconvolve(dry[c], ir[c])[:LEN] for c in range(2)])
    out = (dry + 0.22 * wet)[:, :int(SR * DUR)]
    n = out.shape[1]
    out *= np.minimum(1.0, (n - np.arange(n)) / (0.3 * SR))
    out *= np.minimum(1.0, np.arange(n) / (0.01 * SR))
    out = np.tanh(out / np.abs(out).max() * 1.3) / np.tanh(1.3) * 0.89
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'out', 'soundtrack.wav')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with wave.open(path, 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((out.T * 32767).astype(np.int16).tobytes())
    rms = [20 * np.log10(np.sqrt((out[:, i * SR:(i + 1) * SR] ** 2).mean()) + 1e-9) for i in range(int(DUR))]
    print('wrote', path)
    print('loudness per second (dBFS RMS):', ' '.join('%.0f' % r for r in rms))


if __name__ == '__main__':
    main()
