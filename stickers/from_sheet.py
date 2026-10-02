"""1枚の一覧画像（白背景にスタンプが格子状に並んだもの）から LINE スタンプ一式を作る

使い方:
    pip install pillow numpy scipy
    python stickers/from_sheet.py <一覧画像> <セット名> [--drop 29,40] [--main 2] [--tab 2]

処理:
    1. 白い余白の行・列を探して、格子を自動で切り分ける
    2. 外周から白い背景を塗りつぶして透明にする（猫の毛のハイライトは残す）
    3. 小さなゴミ（はぐれた点）を消す
    4. 370x320 に収まるよう拡大し、白フチを付ける
出力: stickers/output/<セット名>/01.png〜, main.png, tab.png, preview.png
"""

import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter, ImageOps
from scipy import ndimage

ROOT = Path(__file__).parent
W, H = 370, 320


def find_bands(nonwhite_counts, min_gap=3):
    """白い帯（隙間）で区切られた中身の範囲を返す"""
    filled = nonwhite_counts > 1
    bands, start = [], None
    for i, f in enumerate(filled):
        if f and start is None:
            start = i
        if not f and start is not None:
            bands.append([start, i])
            start = None
    if start is not None:
        bands.append([start, len(filled)])
    # 隙間が細すぎるものは同じセルとしてつなぐ
    merged = [bands[0]]
    for b in bands[1:]:
        if b[0] - merged[-1][1] < min_gap:
            merged[-1][1] = b[1]
        else:
            merged.append(b)
    return merged


def row_cuts(ink, ncols, min_gap=2):
    """1行の縦の白い隙間から ncols 個に切る位置を決める。
    隙間が足りないときは、いちばん幅の広いコマを中ほどの線が少ない所で切る。"""
    width = len(ink)
    gaps, st = [], None
    for i, v in enumerate(ink):
        if v <= 1 and st is None:
            st = i
        if v > 1 and st is not None:
            if i - st >= min_gap and st > 5 and i < width - 5:
                gaps.append((st + i - 1) // 2)
            st = None
    cuts = sorted(gaps)
    while len(cuts) < ncols - 1:
        edges = [0] + cuts + [width]
        k = int(np.argmax(np.diff(edges)))
        lo, hi = edges[k], edges[k + 1]
        m0, m1 = lo + (hi - lo) * 3 // 10, lo + (hi - lo) * 7 // 10
        cuts = sorted(cuts + [m0 + int(np.argmin(ink[m0:m1]))])
    while len(cuts) > ncols - 1:  # 多すぎるときは、いちばん狭いコマをつなぐ
        edges = [0] + cuts + [width]
        k = int(np.argmin(np.diff(edges)))
        cuts.pop(max(0, min(k, len(cuts) - 1)))
    return [0] + cuts + [width]


def split_row(a, nonwhite, y0, y1, ncols):
    """1行を ncols 個に切る。境目をまたぐ絵・文字は、多く入っている側のコマに入れる"""
    ink = nonwhite[y0:y1]
    edges = row_cuts(ink.sum(axis=0), ncols)
    labels, n = ndimage.label(ink, structure=np.ones((3, 3)))
    # 上のほう（セリフの行）では、近くに並んだ文字を1つのかたまりにまとめる。
    # こうすると、境目で切れたセリフも丸ごと多く入っている側のコマに入る
    top = int(ink.shape[0] * 0.32)
    text_groups, _ = ndimage.label(ndimage.binary_dilation(ink[:top], structure=np.ones((3, 13))))
    objs = ndimage.find_objects(labels)
    for i, sl in enumerate(objs, 1):
        if sl is not None and sl[0].stop <= top:
            g = text_groups[sl][labels[sl] == i]
            g = g[g > 0]
            if len(g):
                labels[labels == i] = n + int(g[0])
    cells = []
    for k in range(ncols):
        x0, x1 = edges[k], edges[k + 1]
        lab = labels[:, x0:x1]
        ids = np.unique(lab[lab > 0])
        own = []
        for i in ids:
            comp = labels == i
            inside = comp[:, x0:x1].sum()
            if inside * 2 >= comp.sum():
                own.append(i)
        mask = np.isin(labels, own)
        # 自分のかたまりが境目の外にはみ出していれば、その分も含める
        xs = np.where(mask.any(axis=0))[0]
        bx0, bx1 = (min(x0, xs.min()), max(x1, xs.max() + 1)) if len(xs) else (x0, x1)
        crop = a[y0:y1, bx0:bx1].copy()
        other = ink[:, bx0:bx1] & ~mask[:, bx0:bx1]
        # 白っぽい毛の内側は ink に入らないので、他人のかたまりの中だけ白で消す
        other = ndimage.binary_fill_holes(ndimage.binary_closing(other, structure=np.ones((5, 5))))
        # 消した絵のまわりの薄いふち（色のにじみ）も残らないよう、少し広げて消す
        other = ndimage.binary_dilation(other, structure=np.ones((5, 5))) & ~mask[:, bx0:bx1]
        crop[other] = 255
        cells.append(ImageOps.expand(Image.fromarray(crop.astype(np.uint8)), border=4, fill=(255, 255, 255)))
    return cells


def split_sheet(sheet, ncols=None):
    """格子を切り分ける。ncols を指定すると、行ごとに縦の隙間を探して ncols 個に分ける
    （コマの幅が行ごとにバラバラな画像向け）"""
    a = np.asarray(sheet.convert("RGB")).astype(int)
    nonwhite = a.min(axis=2) < 235
    rows = find_bands(nonwhite.sum(axis=1))
    if not ncols:  # 縦の白い隙間が全行を通っているきれいな格子
        cols = find_bands(nonwhite.sum(axis=0))
        cells = [sheet.crop((max(0, x0 - 4), max(0, y0 - 4), x1 + 4, y1 + 4)) for y0, y1 in rows for x0, x1 in cols]
        return cells, len(rows), len(cols)
    cells = []
    for y0, y1 in rows:
        cells += split_row(a, nonwhite, max(0, y0 - 4), min(a.shape[0], y1 + 4), ncols)
    return cells, len(rows), ncols


def remove_background(cell, white_min=245, neutral=14, seal=4):
    """白い背景を透明にする。
    毛が真っ白な猫は背景と色で区別できないので、輪郭線のすき間をいったんふさぎ、
    輪郭で囲まれた内側（白い毛を含む）はすべて残す。"""
    pad = seal * 3
    a = np.asarray(ImageOps.expand(cell.convert("RGB"), border=pad, fill=(255, 255, 255))).astype(int)
    mn, mx = a.min(axis=2), a.max(axis=2)
    ink = (mn < white_min) | ((mx - mn) > neutral)          # 線・色のある部分
    yy, xx = np.mgrid[-seal:seal + 1, -seal:seal + 1]
    disk = (xx ** 2 + yy ** 2) <= seal ** 2
    closed = ndimage.binary_closing(ink, structure=disk)      # 線のすき間をふさぐ
    fg = ndimage.binary_fill_holes(closed)                    # 囲まれた内側を残す

    # 境目をなめらかに
    dist = ndimage.distance_transform_edt(fg)
    alpha = np.clip(dist / 1.5, 0, 1)

    # はぐれた小さな点（AI画像のゴミ）と、コマの左右の端に残った隣のコマの細い切れ端を消す
    labels, n = ndimage.label(alpha > 0.5)
    if n > 1:
        sizes = ndimage.sum(alpha > 0.5, labels, range(1, n + 1))
        width = alpha.shape[1]
        drop = []
        for i, sl in enumerate(ndimage.find_objects(labels)):
            w = sl[1].stop - sl[1].start
            at_edge = sl[1].start <= pad + 6 or sl[1].stop >= width - pad - 6
            if sizes[i] < 25 or (at_edge and (w <= 6 or sizes[i] < 60)):
                drop.append(i + 1)
        alpha[np.isin(labels, drop)] = 0

    rgba = np.dstack([a, (alpha * 255).astype(int)]).astype(np.uint8)
    im = Image.fromarray(rgba, "RGBA")
    return im.crop(im.getbbox())


def add_white_border(im, px):
    im = ImageOps.expand(im, border=px * 2, fill=(0, 0, 0, 0))
    grown = im.getchannel("A").point(lambda v: 255 if v > 40 else 0).filter(ImageFilter.MaxFilter(px * 2 + 1))
    grown = grown.filter(ImageFilter.GaussianBlur(0.8))
    base = Image.new("RGBA", im.size, (255, 255, 255, 0))
    base.putalpha(grown)
    base.alpha_composite(im)
    return base


def fit(im, w, h, margin=10):
    im = im.crop(im.getbbox())
    k = min((w - margin * 2) / im.width, (h - margin * 2) / im.height)
    im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    if k > 1:  # 拡大したときは少しだけシャープに
        im = im.filter(ImageFilter.UnsharpMask(radius=1.2, percent=60, threshold=2))
    canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    canvas.alpha_composite(im, ((w - im.width) // 2, (h - im.height) // 2))
    return canvas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sheet")
    ap.add_argument("name")
    ap.add_argument("--drop", default="", help="使わないセル番号（左上から1,2,3…）をカンマ区切りで")
    ap.add_argument("--main", type=int, default=1, help="メイン画像にするセル番号")
    ap.add_argument("--tab", type=int, default=None, help="タブ画像にするセル番号（省略時はメインと同じ）")
    ap.add_argument("--cols", type=int, default=None, help="列の数（白い隙間で切れない画像のときに指定）")
    ap.add_argument("--tab-cut", type=float, default=0.27, help="タブ画像で上から切り落とす割合（文字の部分）")
    args = ap.parse_args()

    sheet = Image.open(args.sheet).convert("RGB")
    cells, nr, nc = split_sheet(sheet, args.cols)
    print(f"{nr}行 x {nc}列 = {len(cells)}セル")
    drop = {int(x) for x in args.drop.split(",") if x}
    keep = [i for i in range(1, len(cells) + 1) if i not in drop]
    assert len(keep) in (8, 16, 24, 32, 40), f"{len(keep)}個になる（8/16/24/32/40のどれかにする）"

    out = ROOT / "output" / args.name
    out.mkdir(parents=True, exist_ok=True)
    cut = {i: remove_background(cells[i - 1]) for i in set(keep) | {args.main, args.tab or args.main}}

    tiles = []
    for n, i in enumerate(keep, 1):
        # 先に拡大してからフチを付けると、フチの太さがどのスタンプでも同じになる
        big = fit(cut[i], W - 24, H - 24, margin=0)
        tile = fit(add_white_border(big.crop(big.getbbox()), 5), W, H)
        tile.save(out / f"{n:02d}.png", optimize=True)
        tiles.append(tile)

    for idx, (fname, size, margin) in {args.main: ("main.png", (240, 240), 6)}.items():
        src = fit(cut[idx], size[0] - 16, size[1] - 16, margin=0)
        fit(add_white_border(src.crop(src.getbbox()), 4), *size, margin=margin).save(out / fname, optimize=True)
    # タブ画像は小さいので、上の文字を除いて猫だけにする
    t = cut[args.tab or args.main]
    t = t.crop((0, int(t.height * args.tab_cut), t.width, t.height))
    tab_src = fit(t.crop(t.getbbox()), 92, 70, margin=0)
    fit(add_white_border(tab_src.crop(tab_src.getbbox()), 2), 96, 74, margin=2).save(out / "tab.png", optimize=True)

    cols = 5
    pv = Image.new("RGBA", (cols * W, -(-len(tiles) // cols) * H), (140, 171, 216, 255))
    for n, t in enumerate(tiles):
        pv.alpha_composite(t, ((n % cols) * W, (n // cols) * H))
    pv.convert("RGB").save(out / "preview.png", optimize=True)
    print(f"done: {out} ({len(tiles)}個)")


if __name__ == "__main__":
    main()
