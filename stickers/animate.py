"""静止画スタンプから LINE アニメーションスタンプ（APNG）一式を作る

LINE の規格（アニメーションスタンプ）:
    スタンプ画像  最大 320x270（縦横どちらかが 270 以上）/ 5〜20 フレーム / ループ 1〜4 回 /
                 再生時間 4 秒以内 / 1ファイル 300KB 以下 / 1セット 8・16・24 個
    メイン画像    240x240 の APNG / タブ画像 96x74 の PNG
容量を抑えるため、1周約1秒を8コマ（入らなければ6・5コマ）で作り、全コマ共通の色で減色する。
動きは絵を描き直すのではなく、1枚の絵を「はねる・ゆれる・ぽよん」などで動かす簡易アニメ。

    python stickers/animate.py <セット名> 1:bounce 2:shake 21:squash ... [--main 1]
    → stickers/output/<セット名>_anim/01.png〜, main.png, tab.png
"""

import argparse
import math
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).parent
W, H = 320, 270
LOOPS, LOOP_MS = 3, 1000                # 1周 約1秒 を 3回ループ = 約3秒（4秒以内）
MAX_BYTES = 300 * 1024
# 300KB に収まるまで、なめらかさ（コマ数）→ 色数 の順に少しずつ落として試す
TRIES = [(8, 256), (8, 128), (6, 256), (6, 128), (6, 64), (5, 64)]

MOTIONS = ("bounce", "shake", "wiggle", "squash", "zoom", "nod", "dash", "tremble", "beat")


def frame(src, t, motion, w, h):
    """t: 0〜1。motion ごとに位置・角度・大きさを変えた1コマを返す"""
    a = 2 * math.pi * t
    dx = dy = rot = 0.0
    sx = sy = 1.0
    if motion == "bounce":      # ぴょんぴょん跳ねる
        dy = -abs(math.sin(a)) * 18
    elif motion == "shake":     # ぶるぶる（燃えてる・気合い）
        dx = math.sin(a * 3) * 6
        rot = math.sin(a * 3) * 3
    elif motion == "wiggle":    # ゆらゆら（手を振る・ほのぼの）
        rot = math.sin(a) * 7
    elif motion == "squash":    # ぽよん（へたる・のびる）
        sy = 1 + 0.08 * math.sin(a)
        sx = 1 - 0.05 * math.sin(a)
    elif motion == "zoom":      # どーん（びっくり・強調）
        sx = sy = 1 + 0.08 * max(0, math.sin(a))
    elif motion == "nod":       # ぺこり（おじぎ・了解）
        dy = max(0, math.sin(a)) * 10
        rot = -max(0, math.sin(a)) * 5
    elif motion == "dash":      # たったったっ（走る・向かう）
        dx = math.sin(a) * 14
        dy = -abs(math.sin(a * 2)) * 8
    elif motion == "tremble":   # ぷるぷる（泣く・寒い）
        dx = math.sin(a * 5) * 2.5
    elif motion == "beat":      # どきどき（大好き）
        p = max(0, math.sin(a * 2)) if t < 0.5 else 0
        sx = sy = 1 + 0.07 * p
    else:
        raise ValueError(motion)

    im = src.resize((round(src.width * sx), round(src.height * sy)), Image.LANCZOS)
    if rot:
        im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    x = (w - im.width) // 2 + round(dx)
    y = h - im.height - (h - src.height) // 2 + round(dy)   # 足元の高さをそろえる
    canvas.alpha_composite(im, (x, y))
    return canvas


def encode(frames, out_path, colors, ms):
    """全コマ共通のパレットで減色して保存（色がコマごとにちらつかない）"""
    h = frames[0].height
    strip = Image.new("RGBA", (frames[0].width, h * len(frames)))
    for i, f in enumerate(frames):
        strip.paste(f, (0, i * h))
    pal = strip.quantize(colors, method=Image.Quantize.FASTOCTREE)
    q = [pal.crop((0, i * h, f.width, (i + 1) * h)).convert("RGBA") for i, f in enumerate(frames)]
    q[0].save(out_path, save_all=True, append_images=q[1:], duration=ms, loop=LOOPS,
              disposal=1, blend=0, optimize=True)
    return out_path.stat().st_size


def fit(src, w, h, margin):
    src = src.crop(src.getbbox())
    k = min((w - margin * 2) / src.width, (h - margin * 2) / src.height)
    return src.resize((round(src.width * k), round(src.height * k)), Image.LANCZOS)


def make(src_path, out_path, motion, w=W, h=H, margin=20):
    src = fit(Image.open(src_path).convert("RGBA"), w, h, margin)   # 動く分の余白を残す
    for nf, colors in TRIES:
        ms = LOOP_MS // nf
        assert 5 <= nf <= 20 and nf * ms * LOOPS <= 4000
        frames = [frame(src, i / nf, motion, w, h) for i in range(nf)]
        size = encode(frames, out_path, colors, ms)
        if size <= MAX_BYTES:
            return nf, colors, size
    raise SystemExit(f"{out_path.name} が300KBに収まりません（{size // 1024}KB）")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("specs", nargs="+", help="元のスタンプ番号:動き（例 1:bounce）")
    ap.add_argument("--main", default=None, help="メイン画像にする 番号:動き（省略時は1つ目）")
    args = ap.parse_args()
    assert len(args.specs) in (8, 16, 24), f"{len(args.specs)}個（8・16・24個のどれかにする）"

    src_dir = ROOT / "output" / args.name
    out = ROOT / "output" / f"{args.name}_anim"
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.png"):
        old.unlink()
    for n, spec in enumerate(args.specs, 1):
        idx, motion = spec.split(":")
        nf, colors, size = make(src_dir / f"{int(idx):02d}.png", out / f"{n:02d}.png", motion)
        print(f"{n:02d} ← {int(idx):02d} {motion:8s} {nf}コマ {colors}色 {size // 1024}KB")

    idx, motion = (args.main or args.specs[0]).split(":")
    make(src_dir / f"{int(idx):02d}.png", out / "main.png", motion, 240, 240, margin=14)
    Image.open(src_dir / "tab.png").save(out / "tab.png")
    print(f"done: {out}")


if __name__ == "__main__":
    main()
