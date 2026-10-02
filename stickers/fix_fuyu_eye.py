"""もふもふねこ 冬「またね〜」（元画像7番）の左目を、白目に見えない黒目に描き直す

元のAI画像では左目が白い丸に小さな点だけで、白目をむいているように見えるため、
同じ位置に塗りつぶした黒目＋白いハイライトを描く（右目はウインクのまま）。

    python stickers/fix_fuyu_eye.py
    → stickers/source/mofuneko_fuyu_sheet_fixed.png（これを from_sheet.py に渡す）
"""

from pathlib import Path

import numpy as np
from PIL import Image

SRC = Path(__file__).parent / "source"

# シート上の左目の中心と半径（コマの原点 x935,y7 + コマ内の目 x48-61,y112-123）
CX, CY, RX, RY = 989.5, 124.5, 7.5, 7.8
HX, HY, HR = 991.3, 121.6, 2.4          # 白いハイライト


def blend(a, cx, cy, rx, ry, color):
    """なめらかな縁の楕円を塗る（4x4 のサブピクセルで面積を求める）"""
    y0, y1 = int(cy - ry - 2), int(cy + ry + 3)
    x0, x1 = int(cx - rx - 2), int(cx + rx + 3)
    s = (np.arange(4) + 0.5) / 4
    for y in range(y0, y1):
        for x in range(x0, x1):
            px, py = np.meshgrid(x + s, y + s)
            cov = (((px - cx) / rx) ** 2 + ((py - cy) / ry) ** 2 <= 1).mean()
            if cov:
                a[y, x] = a[y, x] * (1 - cov) + np.array(color) * cov


def main():
    a = np.asarray(Image.open(SRC / "mofuneko_fuyu_sheet.webp").convert("RGB")).astype(float)
    blend(a, CX, CY, RX, RY, (58, 40, 34))      # 黒目（輪郭線と同じこげ茶）
    blend(a, HX, HY, HR, HR, (255, 255, 255))   # ハイライト
    out = SRC / "mofuneko_fuyu_sheet_fixed.png"
    Image.fromarray(a.round().astype(np.uint8)).save(out)
    print(f"saved {out}")


if __name__ == "__main__":
    main()
