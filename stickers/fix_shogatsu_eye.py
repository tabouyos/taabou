"""もふもふねこ お正月「謹賀新年」（元画像4番）の白目に見える目を、にっこり閉じた目に描き直す

元のAI画像では半目で白目が見えていたため、目のまわりを毛の色で塗りつぶし、
こげ茶の「^ ^」（にっこり目）を描く。

    python stickers/fix_shogatsu_eye.py
    → stickers/source/mofuneko_shogatsu_sheet_fixed.png（これを from_sheet.py に渡す）
"""

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

SRC = Path(__file__).parent / "source"
EYES = [(671.5, 99.5), (702.5, 101.5)]      # シート上の両目の中心
RX, RY = 8.5, 6.5                           # 塗りつぶす範囲
LINE = (74, 52, 40)                         # 輪郭線と同じこげ茶
S = 8                                       # なめらかに描くための拡大率


def main():
    sheet = Image.open(SRC / "mofuneko_shogatsu_sheet.webp").convert("RGB")
    a = np.asarray(sheet).astype(float)
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    for cx, cy in EYES:
        d = ((xx - cx) / RX) ** 2 + ((yy - cy) / RY) ** 2
        ring = (d > 1.3) & (d < 2.2)
        fur = np.median(a[ring], axis=0)                      # 目のまわりの毛の色
        w = np.clip((1.25 - d) / 0.35, 0, 1)[..., None]       # ふちはぼかして塗る
        a = a * (1 - w) + fur * w

    img = Image.fromarray(a.round().astype(np.uint8))
    # にっこり目（^）を拡大キャンバスに描いて縮小し、重ねる
    for cx, cy in EYES:
        x0, y0 = int(cx - 10), int(cy - 8)
        patch = Image.new("RGBA", (20 * S, 16 * S), (0, 0, 0, 0))
        dr = ImageDraw.Draw(patch)
        bx = [(cx - 6 - x0) * S, (cy - 3 - y0) * S, (cx + 6 - x0) * S, (cy + 6 - y0) * S]
        dr.arc(bx, start=200, end=340, fill=LINE + (255,), width=int(2.2 * S))
        patch = patch.resize((20, 16), Image.LANCZOS)
        img.paste(patch, (x0, y0), patch)

    out = SRC / "mofuneko_shogatsu_sheet_fixed.png"
    img.save(out)
    print(f"saved {out}")


if __name__ == "__main__":
    main()
