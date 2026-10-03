"""9-in-1 grid -> music video. A virtual camera flies across the grid (spatially connected transitions),
with beat-synced motion graphics. 1280x720 @30fps, 12.5 s. Raw frames piped to ffmpeg."""
import math, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, DUR = 1280, 720, 30, 12.5
SRC = Image.open('source_grid.webp').convert('RGB')
UP = 2
SRCU = SRC.resize((SRC.width * UP, SRC.height * UP), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 60, 2))
SW, SH = SRC.size
XS = [(0, 553), (558, 1113), (1117, 1672)]
YS = [(0, 308), (312, 621), (625, 941)]
CENT = [((XS[i % 3][0] + XS[i % 3][1]) / 2, (YS[i // 3][0] + YS[i // 3][1]) / 2) for i in range(9)]
YEL = (255, 232, 0)
FJ = '/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf'
FE = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
font = lambda p, s: ImageFont.truetype(p, s)
BEAT = 0.5
T = [1.0 + i for i in range(9)]
TR = 0.25  # transition length (ends on the panel downbeat)

lerp = lambda a, b, p: a + (b - a) * p
clamp = lambda x, a=0.0, b=1.0: max(a, min(b, x))
def ease_io(p):  # strong in-out (expo-like) for whip pans
    p = clamp(p)
    return 0.5 * (1 - math.cos(math.pi * p)) if p in (0, 1) else (
        2 ** (20 * p - 10) / 2 if p < 0.5 else (2 - 2 ** (-20 * p + 10)) / 2)
def ease_out(p):
    p = clamp(p); return 1 - (1 - p) ** 3
def pulse(t, period, decay=0.08):
    return math.exp(-((t % period) / decay))

# ---- per-panel local camera motion: p in [0,1] over hold -> (dx, dy, vw, rot)
def motion(i, p, t):
    e = ease_out(p)
    if i == 0: return (lerp(-20, 10, p), 0, lerp(540, 420, e), lerp(-2, 1, p))
    if i == 1: return (0, 10, lerp(520, 320, 1 - (1 - p) ** 6), 0)
    if i == 2: return (lerp(-60, 60, p), 0, 420, 0)
    if i == 3: return (lerp(30, -20, p), 0, lerp(470, 400, p), lerp(-6, 5, e))
    if i == 4: return (0, lerp(-20, 0, p), lerp(320, 540, e), 0)
    if i == 5: return (40, lerp(40, -40, p), 400, 0)
    if i == 6: return (0, 0, 460 - 50 * pulse(t, 0.25, 0.06), 2.5 * math.sin(t * 2 * math.pi * 2))
    if i == 7: return (0, lerp(0, -30, p), lerp(540, 380, e), 0)
    if i == 8: return (0, 0, lerp(400, 510, e), lerp(5, -1, e))

def state(i, p, t):
    dx, dy, vw, r = motion(i, p, t)
    return (CENT[i][0] + dx, CENT[i][1] + dy, vw, r)

GRID = (SW / 2, SH / 2, SW * 1.06, 0.0)
SPIN = {3: 22, 6: -22}            # roll whips into panel i
ARC = {3: 1.9, 6: 1.9}            # zoom-out arc on row changes (multiplier)

def camera(t):
    if t < 0.55:
        q = t / 0.55
        return (GRID[0], GRID[1], GRID[2] * lerp(1.12, 1.0, ease_out(q)), lerp(-3, 0, ease_out(q))), 0
    if t < T[0]:
        q = ease_io((t - 0.55) / (T[0] - 0.55))
        a, b = GRID, state(0, 0, t)
        return tuple(lerp(a[k], b[k], q) for k in range(4)), 1
    for i in range(9):
        end = T[i] + 1 - TR if i < 8 else T[i] + 0.75
        if T[i] <= t < end:
            return state(i, (t - T[i]) / (end - T[i]), t), 0
        if i < 8 and end <= t < T[i + 1]:
            q = (t - end) / TR; qe = ease_io(q)
            a, b = state(i, 1, t), state(i + 1, 0, t)
            c = [lerp(a[k], b[k], qe) for k in range(4)]
            c[2] *= 1 + (ARC.get(i + 1, 1.0) - 1) * math.sin(math.pi * q)
            c[3] += SPIN.get(i + 1, 0) * math.sin(math.pi * q)
            return tuple(c), 1
    # outro 9.75 -> 10.5 zoom out to grid, then hold
    if t < 10.5:
        q = ease_io((t - 9.75) / 0.75)
        a = state(8, 1, t)
        c = tuple(lerp(a[k], GRID[k], q) for k in range(4))
        return (c[0], c[1], c[2], c[3] + 8 * math.sin(math.pi * q)), 1
    q = clamp((t - 10.5) / 2.0)
    return (GRID[0], GRID[1], GRID[2] * lerp(1.0, 0.93, ease_out(q)), 0), 0

def render_cam(c):
    cx, cy, vw, rot = c
    s = vw / W * UP
    a = math.radians(rot)
    ca, sa = math.cos(a) * s, math.sin(a) * s
    # output (u,v) -> source
    A = (ca, -sa, cx * UP - ca * W / 2 + sa * H / 2,
         sa, ca, cy * UP - sa * W / 2 - ca * H / 2)
    return np.asarray(SRCU.transform((W, H), Image.AFFINE, A, Image.BILINEAR, fillcolor=(10, 10, 10)), dtype=np.float32)

yy, xx = np.mgrid[0:H, 0:W]
VIG = (1 - 0.35 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2))[..., None].astype(np.float32)

def speed(t):
    a, _ = camera(max(0, t - 1 / FPS)); b, _ = camera(t)
    return math.hypot((b[0] - a[0]) / b[2] * W, (b[1] - a[1]) / b[2] * W) + abs(b[3] - a[3]) * 20

def which_panel(t):
    for i in range(8, -1, -1):
        if t >= T[i]: return i
    return -1

def overlay(t, img, spd, moving):
    d = ImageDraw.Draw(img, 'RGBA')
    pi = which_panel(t)
    # --- transition graphics: yellow slash bands + speed lines
    for i in range(1, 9):
        q = (t - (T[i] - TR)) / (TR + 0.12)
        if 0 <= q <= 1:
            dirx = 1 if (i % 3) != 0 else 0
            for k, (w_, off) in enumerate([(140, 0), (60, 0.18), (24, 0.3)]):
                x = lerp(W + 400, -700, clamp(q * 1.3 - off)) if dirx else None
                if dirx:
                    d.polygon([(x, 0), (x + w_, 0), (x + w_ - 260, H), (x - 260, H)], fill=YEL + (200 - k * 50,))
                else:
                    y = lerp(H + 300, -500, clamp(q * 1.3 - off))
                    d.polygon([(0, y), (W, y - 200), (W, y - 200 + w_), (0, y + w_)], fill=YEL + (200 - k * 50,))
    if spd > 25:
        rr = np.random.default_rng(int(t * 1000))
        for _ in range(int(min(40, spd / 4))):
            y = rr.uniform(0, H); x = rr.uniform(-200, W); L = rr.uniform(150, 600)
            d.line([(x, y), (x + L, y)], fill=(255, 255, 255, int(rr.uniform(60, 160))), width=int(rr.uniform(1, 4)))
    # --- per-panel motion graphics
    if pi >= 0:
        lt = t - T[pi]
        if pi == 0:  # expanding rings on each beat
            for bt in (0.0, 0.5):
                q = (lt - bt) / 0.45
                if 0 <= q <= 1:
                    r = 40 + 700 * ease_out(q); a = int(255 * (1 - q))
                    d.ellipse([W * 0.62 - r, H * 0.45 - r, W * 0.62 + r, H * 0.45 + r], outline=YEL + (a,), width=int(18 * (1 - q)) + 2)
        if pi == 1:  # radial burst lines
            q = clamp(lt / 0.6)
            for k in range(36):
                ang = k * math.tau / 36 + 0.05 * math.sin(k * 7)
                r0 = lerp(260, 420, ease_out(q)); r1 = r0 + 300
                d.line([(W / 2 + r0 * math.cos(ang), H / 2 + r0 * math.sin(ang)), (W / 2 + r1 * math.cos(ang), H / 2 + r1 * math.sin(ang))],
                       fill=(255, 255, 255, int(200 * (1 - q))), width=5 if k % 3 else 10)
        if pi == 2:  # ticker band
            y = H - 120
            d.rectangle([0, y, W, y + 64], fill=YEL + (235,))
            f = font(FE, 40); txt = 'SEMINAR  10/3  ▶  ' * 6
            d.text((-((lt * 900) % 560), y + 8), txt, font=f, fill=(0, 0, 0))
        if pi == 3:  # zig-zag energy line drawn on
            q = ease_out(clamp(lt / 0.5))
            pts = [(x, H * 0.82 + (60 if j % 2 else -60) * (1 + 0.5 * pulse(lt, 0.25))) for j, x in enumerate(np.linspace(-20, W + 20, 14))]
            n = max(2, int(len(pts) * q))
            d.line(pts[:n], fill=YEL + (255,), width=14, joint='curve')
        if pi == 4:  # sliding scan bars
            for k in range(6):
                y = (k * 140 + lt * 600) % (H + 140) - 70
                d.rectangle([0, y, W, y + 6], fill=(255, 255, 255, 70))
            f = font(FE, 26)
            for k, w in enumerate(['NURSE', 'HOSPITAL DX', 'AI', 'VIDEO', 'MUSIC']):
                q = clamp((lt - k * 0.06) / 0.2)
                d.text((lerp(-300, 40, ease_out(q)), 220 + k * 40), w, font=f, fill=YEL + (int(255 * q),))
        if pi == 5:  # diagonal hazard stripes slide + big outline text
            q = ease_out(clamp(lt / 0.35))
            off = (lt * 400) % 80
            for k in range(-2, 22):
                x = k * 80 + off
                d.polygon([(x, H - 70), (x + 40, H - 70), (x + 10, H), (x - 30, H)], fill=YEL + (int(220 * q),))
            f = font(FE, 220)
            d.text((lerp(W, 640, q), 30), 'AI', font=f, fill=(0, 0, 0, 0), stroke_width=5, stroke_fill=YEL + (230,))
        if pi == 6:  # equalizer bars
            nb = 28
            for k in range(nb):
                h = 40 + 220 * abs(math.sin(k * 1.7 + lt * 9)) * (0.4 + 0.6 * pulse(lt, 0.25, 0.1))
                x = 30 + k * (W - 60) / nb
                d.rectangle([x, H - 30 - h, x + (W - 60) / nb - 8, H - 30], fill=YEL + (210,))
        if pi == 7:  # concentric squares tunnel
            for k in range(5):
                q = ((lt * 1.6 + k / 5) % 1)
                s_ = lerp(60, 1100, q ** 2)
                d.rectangle([W / 2 - s_, H / 2 - s_ * 0.56, W / 2 + s_, H / 2 + s_ * 0.56], outline=(255, 255, 255, int(160 * (1 - q))), width=4)
        if pi == 8 and lt < 0.9:  # confetti burst (plus signs + triangles)
            rr = np.random.default_rng(8)
            for k in range(46):
                ang = rr.uniform(0, math.tau); sp = rr.uniform(300, 1100)
                q = clamp(lt / 0.9)
                x = W / 2 + math.cos(ang) * sp * ease_out(q); y = H / 2 + math.sin(ang) * sp * ease_out(q) + 300 * q * q
                a = int(255 * (1 - q)); s_ = rr.uniform(10, 26)
                col = YEL if k % 2 else (255, 255, 255)
                if k % 3:
                    d.rectangle([x - s_, y - s_ / 4, x + s_, y + s_ / 4], fill=col + (a,)); d.rectangle([x - s_ / 4, y - s_, x + s_ / 4, y + s_], fill=col + (a,))
                else:
                    d.polygon([(x, y - s_), (x + s_, y + s_), (x - s_, y + s_)], fill=col + (a,))
    # --- intro title
    if t < 1.0:
        f = font(FE, 64); fj = font(FJ, 46)
        q = ease_out(clamp((t - 0.05) / 0.3))
        d.rectangle([0, H / 2 - 70, W * q, H / 2 + 70], fill=(0, 0, 0, 200))
        d.rectangle([0, H / 2 + 60, W * q, H / 2 + 70], fill=YEL + (255,))
        if t > 0.2:
            n = int(clamp((t - 0.2) / 0.4) * 22)
            d.text((60, H / 2 - 62), 'NURSE × HOSPITAL DX × AI'[:n], font=f, fill=YEL)
            d.text((64, H / 2 + 76), 'よくばりナースの日常', font=fj, fill=(255, 255, 255, int(255 * clamp((t - 0.4) / 0.2))))
    # --- outro title
    if t >= 10.5:
        q = ease_out(clamp((t - 10.6) / 0.35))
        d.rectangle([0, H - 190, W * q, H - 60], fill=YEL + (245,))
        d.text((50, H - 182), 'よくばりナースの日常', font=font(FJ, 64), fill=(0, 0, 0, int(255 * q)))
        d.text((W - 430, H - 102), 'AI MUSIC VIDEO', font=font(FE, 34), fill=(0, 0, 0, int(255 * q)))
    # --- HUD: counter, progress bar, corner plus marks
    if 1.0 <= t < 10.5 and pi >= 0:
        d.text((34, 26), f'{pi + 1:02d}', font=font(FE, 54), fill=YEL)
        d.text((112, 50), '/ 09', font=font(FE, 24), fill=(255, 255, 255, 220))
    d.rectangle([0, H - 8, W * t / DUR, H], fill=YEL + (255,))
    r = 14; a = t * 3
    for (cx, cy) in [(W - 40, 40), (40, H - 40)]:
        for k in range(2):
            an = a + k * math.pi / 2
            d.line([(cx - r * math.cos(an), cy - r * math.sin(an)), (cx + r * math.cos(an), cy + r * math.sin(an))], fill=(255, 255, 255, 230), width=4)
    return img

def frame(t):
    c, moving = camera(t)
    spd = speed(t)
    if moving and spd > 6:  # motion blur: average sub-frames
        acc = np.zeros((H, W, 3), np.float32); n = 6
        for k in range(n):
            ts = t - (k / n) * (1 / FPS)
            acc += render_cam(camera(ts)[0])
        a = acc / n
    else:
        a = render_cam(c)
    # punch shake on landing
    for Ti in T + [10.5]:
        if 0 <= t - Ti < 0.15:
            k = 1 - (t - Ti) / 0.15
            a = np.roll(a, (int(14 * k * math.sin(t * 90)), int(10 * k * math.cos(t * 77))), (0, 1))
    # RGB split proportional to speed
    sh = int(min(12, spd / 10))
    if sh > 0:
        a[..., 0] = np.roll(a[..., 0], sh, 1); a[..., 2] = np.roll(a[..., 2], -sh, 1)
    # contrast + vignette
    a = np.clip((a - 128) * 1.08 + 128, 0, 255) * VIG
    # panel 1: invert hit on the off-beat
    if 0 <= t - (T[1] + 0.5) < 0.07:
        a = 255 - a
    # flashes on downbeats
    for Ti in T + [10.5]:
        if 0 <= t - Ti < 0.14:
            f = 0.75 * (1 - (t - Ti) / 0.14)
            a = a * (1 - f) + 255 * f
    # fade in / out
    if t < 0.12: a *= t / 0.12
    if t > DUR - 0.6: a *= max(0, (DUR - t) / 0.6)
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')
    img = overlay(t, img, spd, moving)
    if t > DUR - 0.6:
        img = Image.blend(img, Image.new('RGBA', (W, H), (0, 0, 0, 255)), min(1, (t - (DUR - 0.6)) / 0.6) * 0.0 + (1 - max(0, (DUR - t) / 0.6)))
    return img.convert('RGB')

if __name__ == '__main__':
    if len(sys.argv) > 1:  # preview stills
        for ts in map(float, sys.argv[1:]):
            frame(ts).save(f'prev_{ts:05.2f}.jpg', quality=85)
        sys.exit()
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                          '-i', '-', '-i', 'bgm.wav', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
                          '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', 'nurse_cat_mv.mp4'], stdin=subprocess.PIPE)
    nf = int(DUR * FPS)
    for f in range(nf):
        p.stdin.write(frame(f / FPS).tobytes())
        if f % 60 == 0: print(f, '/', nf, flush=True)
    p.stdin.close(); p.wait()
    print('done', p.returncode)
