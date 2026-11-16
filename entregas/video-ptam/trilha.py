"""Uso: python3 trilha.py [duração] [viradas separadas por vírgula]

Trilha original (sem direitos de terceiros) para o Reels do PTAM.
110 BPM, progressão C – G – Am – F, pad + arpejo + baixo + percussão leve.
Gera trilha-ptam.wav com a duração do vídeo.
"""
import sys
import wave
import numpy as np

SR, BPM = 44100, 110
DUR = float(sys.argv[1]) if len(sys.argv) > 1 else 20.0
WHOOSH = [float(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else [2.95, 5.4, 14.2, 16.8]
beat = 60 / BPM
n = int(SR * DUR)
t = np.arange(n) / SR
mix = np.zeros(n)
rng = np.random.default_rng(7)

def hz(m):
    return 440 * 2 ** ((m - 69) / 12)

def env(length, a=0.01, r=0.25):
    e = np.ones(length)
    na, nr = int(a * SR), int(r * SR)
    e[:na] = np.linspace(0, 1, na)
    e[-nr:] *= np.linspace(1, 0, nr)
    return e

def add(start, sig):
    i = int(start * SR)
    if i >= n:
        return
    j = min(n, i + len(sig))
    mix[i:j] += sig[: j - i]

def lowpass(x, alpha):
    y = np.empty_like(x); acc = 0.0
    for k, v in enumerate(x):
        acc += alpha * (v - acc); y[k] = acc
    return y

# acordes (notas MIDI) – 2 compassos de 4 tempos cada acorde = 1 compasso
CHORDS = [[60, 64, 67], [55, 59, 62], [57, 60, 64], [53, 57, 60]]
BASS = [36, 43, 45, 41]
bar = 4 * beat
nbars = int(np.ceil(DUR / bar))

for b in range(nbars):
    ch = CHORDS[b % 4]; t0 = b * bar
    L = int(bar * SR) + int(0.4 * SR); tt = np.arange(L) / SR
    # pad: soma de senoides levemente desafinadas
    pad = sum(np.sin(2 * np.pi * hz(m) * tt) + 0.5 * np.sin(2 * np.pi * hz(m) * 1.003 * tt) for m in ch)
    add(t0, 0.035 * pad * env(L, 0.25, 0.4))
    # baixo em colcheias
    for k in range(8):
        Lb = int(beat / 2 * SR); tb = np.arange(Lb) / SR
        f = hz(BASS[b % 4] + (12 if k % 4 == 3 else 0))
        s = np.sin(2 * np.pi * f * tb) + 0.3 * np.sin(4 * np.pi * f * tb)
        add(t0 + k * beat / 2, 0.11 * s * env(Lb, 0.005, 0.08))
    # arpejo em semicolcheias (entra após o gancho)
    if t0 >= 2.9:
        notas = ch + [ch[0] + 12]
        for k in range(16):
            La = int(0.18 * SR); ta = np.arange(La) / SR
            f = hz(notas[[0, 1, 2, 3, 2, 1, 2, 3][k % 8]] + 12)
            s = np.sin(2 * np.pi * f * ta) * np.exp(-ta * 18)
            add(t0 + k * beat / 4, 0.05 * s)

# percussão
nbeats = int(DUR / beat) + 1
for k in range(nbeats):
    tb = k * beat
    Lk = int(0.25 * SR); tk = np.arange(Lk) / SR
    kick = np.sin(2 * np.pi * (50 + 90 * np.exp(-tk * 30)) * tk) * np.exp(-tk * 12)
    if tb >= 1.0:
        add(tb, 0.32 * kick)
    if tb >= 2.9 and k % 2 == 1:   # palma/snare leve nos tempos 2 e 4
        Ls = int(0.15 * SR)
        add(tb, 0.06 * rng.standard_normal(Ls) * np.exp(-np.arange(Ls) / SR * 25))
    Lh = int(0.05 * SR)            # chimbal nos contratempos
    hat = rng.standard_normal(Lh) * np.exp(-np.arange(Lh) / SR * 80)
    hat = hat - lowpass(hat, 0.2)
    add(tb + beat / 2, 0.035 * hat)

# "whoosh" nas viradas de cena
for tc in WHOOSH:
    Lw = int(0.5 * SR); w = rng.standard_normal(Lw) * np.sin(np.linspace(0, np.pi, Lw)) ** 2
    add(tc - 0.35, 0.05 * lowpass(w, 0.08) * 6)

# fade in/out e normalização
mix[: int(0.3 * SR)] *= np.linspace(0, 1, int(0.3 * SR))
mix[-int(1.8 * SR):] *= np.linspace(1, 0, int(1.8 * SR))
mix /= np.max(np.abs(mix)) * 1.12
st = np.stack([mix, np.roll(mix, int(0.012 * SR)) * 0.96], axis=1)
with wave.open("trilha-ptam.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st * 32767).astype("<i2").tobytes())
print("ok")
