"""BGM synth: 120 BPM, A minor, 12.5 s. Beat grid aligned with video (panel i starts at 1+i sec)."""
import numpy as np, wave

SR = 44100
DUR = 12.5
N = int(SR * DUR)
rng = np.random.default_rng(7)
out = np.zeros((N, 2))
BEAT = 0.5


def add(sig, t0, gain=1.0, pan=0.0):
    i = int(t0 * SR)
    if i >= N:
        return
    sig = sig[: N - i]
    l = gain * np.sqrt(0.5 * (1 - pan))
    r = gain * np.sqrt(0.5 * (1 + pan))
    out[i:i + len(sig), 0] += sig * l
    out[i:i + len(sig), 1] += sig * r


def env(n, a, d):
    t = np.arange(n) / SR
    e = np.exp(-t / d)
    na = max(1, int(a * SR))
    e[:na] *= np.linspace(0, 1, na)
    return e


def lp(x, a):
    # one-pole lowpass, a in (0,1): higher = brighter
    y = np.empty_like(x)
    s = 0.0
    for i, v in enumerate(x):
        s += a * (v - s)
        y[i] = s
    return y


def kick(big=False):
    n = int(SR * (0.6 if big else 0.35))
    t = np.arange(n) / SR
    f = 45 + 110 * np.exp(-t / 0.035)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * env(n, 0.001, 0.22 if big else 0.12)
    s += 0.3 * rng.standard_normal(n) * env(n, 0.0005, 0.004)
    return np.tanh(s * 1.8)


def clap():
    n = int(SR * 0.25)
    nz = rng.standard_normal(n)
    nz = nz - lp(nz, 0.15)
    e = env(n, 0.001, 0.06)
    for k in (0.008, 0.016):
        e += 0.6 * np.roll(env(n, 0.001, 0.01), int(k * SR))
    return nz * e * 0.6


def hat(open_=False):
    n = int(SR * (0.18 if open_ else 0.05))
    nz = rng.standard_normal(n)
    nz = np.diff(np.diff(nz, prepend=0), prepend=0)
    return nz * env(n, 0.0005, 0.06 if open_ else 0.012) * 0.25


def saw(freq, dur, bright=0.3):
    n = int(SR * dur)
    t = np.arange(n) / SR
    s = 0
    for det in (-0.006, 0, 0.007):
        s = s + 2 * ((t * freq * (1 + det)) % 1) - 1
    return lp(s / 3, bright)


def note(m):
    return 440 * 2 ** ((m - 69) / 12)


def whoosh(dur=0.32, up=True):
    n = int(SR * dur)
    nz = rng.standard_normal(n)
    a = np.linspace(0.02, 0.5, n) if up else np.linspace(0.5, 0.02, n)
    y = np.empty(n); s = 0.0
    for i in range(n):
        s += a[i] * (nz[i] - s)
        y[i] = s
    e = np.linspace(0, 1, n) ** 2 if up else np.linspace(1, 0, n) ** 2
    return y * e * 1.2


def impact():
    n = int(SR * 1.2)
    nz = rng.standard_normal(n)
    return lp(nz, 0.25) * env(n, 0.001, 0.35) * 0.9


# chord progression per 2 seconds: Am, F, C, G
CHORDS = [(57, [57, 60, 64]), (53, [53, 57, 60]), (48, [55, 60, 64]), (55, [55, 59, 62])]

# --- intro riser 0..1
add(whoosh(1.0), 0.0, 0.5)
n = SR
t = np.arange(n) / SR
f = 200 * 2 ** (t * 2.5)
add(np.sin(2 * np.pi * np.cumsum(f) / SR) * t ** 2 * 0.12, 0.0)
for k in range(8):  # snare roll building
    add(clap(), 0.5 + k * 0.0625, 0.25 + k * 0.08)

# --- groove 1.0 .. 10.5
sidechain = np.ones(N)
for b in range(19):  # beats from 1.0 to 10.0
    tb = 1.0 + b * BEAT
    big = abs((tb - 1.0) % 1.0) < 1e-6
    add(kick(big), tb, 0.9)
    i = int(tb * SR)
    m = min(N - i, int(0.3 * SR))
    sidechain[i:i + m] = np.minimum(sidechain[i:i + m], 1 - 0.7 * np.exp(-np.arange(m) / SR / 0.08))
    if b % 2 == 1:
        add(clap(), tb, 0.8)
    for s in range(4):
        add(hat(open_=(s == 2)), tb + s * BEAT / 4, 0.9 if s == 2 else 0.5, pan=0.3 if s % 2 else -0.3)

pad = np.zeros(N)
bass = np.zeros(N)
lead = np.zeros((N,))
for seg in range(5):
    t0 = 1.0 + seg * 2.0
    root, ch = CHORDS[seg % 4]
    d = 2.0
    p = sum(saw(note(m), d, 0.12) for m in ch) / 3
    p *= np.minimum(1, np.arange(len(p)) / (0.05 * SR))
    i = int(t0 * SR); pad[i:i + len(p)] += p[: N - i]
    for e8 in range(8):  # 8th-note bass
        tb = t0 + e8 * 0.25
        nb = saw(note(root - 12), 0.22, 0.25) * env(int(0.22 * SR), 0.003, 0.12)
        i = int(tb * SR); bass[i:i + len(nb)] += nb[: N - i]
    arp = ch + [ch[0] + 12]
    for s16 in range(16):  # 16th arpeggio pluck
        tb = t0 + s16 * 0.125
        m = arp[(s16 * 3) % 4] + 12
        nn = int(0.12 * SR)
        tt = np.arange(nn) / SR
        pl = np.sign(np.sin(2 * np.pi * note(m) * tt)) * 0.5 + np.sin(2 * np.pi * note(m) * 2 * tt) * 0.3
        pl = lp(pl, 0.35) * env(nn, 0.001, 0.05)
        i = int(tb * SR); lead[i:i + nn] += pl[: N - i]

out[:, 0] += pad * sidechain * 0.35 + bass * 0.5 + lead * 0.16
out[:, 1] += pad * sidechain * 0.35 + bass * 0.5 + np.roll(lead, int(0.09 * SR)) * 0.16

# transitions: whoosh before each panel change, impact at landing
for i in range(1, 9):
    T = 1.0 + i
    add(whoosh(0.3), T - 0.3, 0.45, pan=(-0.5 if i % 2 else 0.5))
add(impact(), 1.0, 0.7)

# --- outro: riser 9.75->10.5, final hit chord + ringout
add(whoosh(0.75), 9.75, 0.6)
add(impact(), 10.5, 0.9)
add(kick(True), 10.5, 1.0)
fin = sum(saw(note(m), 2.0, 0.18) for m in [45, 57, 60, 64, 69]) / 5 * env(int(2.0 * SR), 0.005, 0.7)
add(fin, 10.5, 0.8)
for k in range(6):  # sparse hats in outro
    add(hat(True), 10.5 + 0.25 * k, 0.4 * (1 - k / 6))

# master
fade = np.ones(N); fs = int(11.8 * SR); fade[fs:] = np.linspace(1, 0, N - fs)
out *= fade[:, None]
out = np.tanh(out * 1.3)
out /= np.abs(out).max() / 0.92
pcm = (out * 32767).astype(np.int16)
with wave.open('bgm.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print('bgm ok')
