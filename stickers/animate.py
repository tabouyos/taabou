"""静止画スタンプから LINE アニメーションスタンプ（APNG）を作る

LINE の規格: 最大 320x270 / 5〜20 フレーム / 再生時間 1〜4 秒 / ループ 1〜4 回 / 1ファイル 1MB 以下
動きは絵を描き直すのではなく、1枚の絵を「はねる・ゆれる・ぷるぷる・ぽよん」と動かす簡易アニメ。

    python stickers/animate.py <セット名> 1:bounce 2:shake 21:squash ...
    → stickers/output/<セット名>_anim/01.png〜（APNG）
"""

import math
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).parent
W, H = 320, 270
FRAMES, MS, LOOPS = 12, 90, 4          # 12コマ x 90ms ≒ 1.1秒 を 4回ループ


def frame(src, t, motion):
    """t: 0〜1。motion ごとに位置・角度・大きさを変える"""
    a = 2 * math.pi * t
    dx = dy = rot = 0.0
    sx = sy = 1.0
    if motion == "bounce":      # ぴょんぴょん跳ねる
        dy = -abs(math.sin(a)) * 18
        sy = 1 - 0.06 * max(0, math.cos(2 * a))
    elif motion == "shake":     # ぶるぶる（燃えてる・怒ってる）
        dx = math.sin(a * 3) * 6
        rot = math.sin(a * 3) * 3
    elif motion == "wiggle":    # ゆらゆら
        rot = math.sin(a) * 7
    elif motion == "squash":    # ぽよん（へたる・のびる）
        sy = 1 + 0.08 * math.sin(a)
        sx = 1 - 0.05 * math.sin(a)
    elif motion == "zoom":      # どーん（びっくり・強調）
        sx = sy = 1 + 0.08 * max(0, math.sin(a))
    elif motion == "nod":       # ぺこり
        dy = max(0, math.sin(a)) * 10
        rot = -max(0, math.sin(a)) * 5

    im = src.resize((round(src.width * sx), round(src.height * sy)), Image.LANCZOS)
    im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    x = (W - im.width) // 2 + round(dx)
    y = H - im.height - 4 + round(dy) + round((src.height * (sy - 1)) / 2 if sy < 1 else 0)
    canvas.alpha_composite(im, (x, max(y, -im.height // 2)))
    return canvas


def make(src_path, out_path, motion):
    src = Image.open(src_path).convert("RGBA")
    src = src.crop(src.getbbox())
    k = min((W - 40) / src.width, (H - 40) / src.height)  # 動く分の余白を残す
    src = src.resize((round(src.width * k), round(src.height * k)), Image.LANCZOS)
    # 256色に減色して容量を小さくする（透明も保つ）
    frames = [frame(src, i / FRAMES, motion).quantize(256, method=Image.Quantize.FASTOCTREE).convert("RGBA")
              for i in range(FRAMES)]
    frames[0].save(out_path, save_all=True, append_images=frames[1:], duration=MS, loop=LOOPS,
                   disposal=1, blend=0, optimize=True)
    assert out_path.stat().st_size <= 1_000_000, f"{out_path.name} が1MBを超えています"


def main():
    name, specs = sys.argv[1], sys.argv[2:]
    out = ROOT / "output" / f"{name}_anim"
    out.mkdir(parents=True, exist_ok=True)
    for n, spec in enumerate(specs, 1):
        idx, motion = spec.split(":")
        make(ROOT / "output" / name / f"{int(idx):02d}.png", out / f"{n:02d}.png", motion)
    print(f"done: {out} ({len(specs)}個)")


if __name__ == "__main__":
    main()
