"""もふもふねこ「笑」（元画像33番）の描き忘れた右目を補う

元のAI画像では右目が描かれていなかったので、左目の「^」を左右反転して、
口をはさんで対称の位置に描き足す。線の濃さだけを写すので、周りの毛の色はそのまま残る。

    python stickers/fix_mofuneko_eye.py
    → stickers/source/mofuneko_sheet_fixed.png（これを from_sheet.py に渡す）
"""

from pathlib import Path

import numpy as np
from PIL import Image

import from_sheet as fs

SRC = Path(__file__).parent / "source"


def main():
    sheet = Image.open(SRC / "mofuneko_sheet.webp").convert("RGB")
    a = np.asarray(sheet).astype(float)

    # 「笑」のコマの位置を、切り分けと同じ方法で求める
    nonwhite = a.min(axis=2) < 235
    rows = fs.find_bands(nonwhite.sum(axis=1))
    cols = fs.find_bands(nonwhite.sum(axis=0))
    ox, oy = cols[2][0] - 4, rows[5][0] - 4          # 6行目・3列目 = 33番

    # コマ内の座標: 左目 x57-69, y91-97 / 口の中心 x≈83
    lx0, lx1, ly0, ly1 = 55, 72, 88, 100
    mouth_cx = 83
    left = a[oy + ly0:oy + ly1, ox + lx0:ox + lx1]
    bg = np.median(left.reshape(-1, 3), axis=0)              # 目のまわりの毛の色
    lum = left.mean(axis=2)
    ink = np.clip((bg.mean() - lum) / (bg.mean() - lum.min()), 0, 1)   # 線の濃さ 0〜1
    stroke = left.reshape(-1, 3)[np.argmin(lum)]             # いちばん濃い線の色

    ink = ink[:, ::-1]                                        # 左右反転
    rx0 = ox + 2 * mouth_cx - lx1                             # 口をはさんで対称の位置
    target = a[oy + ly0:oy + ly1, rx0:rx0 + (lx1 - lx0)]
    a[oy + ly0:oy + ly1, rx0:rx0 + (lx1 - lx0)] = target * (1 - ink[..., None]) + stroke * ink[..., None]

    out = SRC / "mofuneko_sheet_fixed.png"
    Image.fromarray(a.round().astype(np.uint8)).save(out)
    print(f"saved {out}")


if __name__ == "__main__":
    main()
