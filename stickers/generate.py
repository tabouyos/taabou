"""敬語しろねこ LINEスタンプ生成スクリプト

使い方:
    pip install cairosvg pillow
    python stickers/generate.py

出力 (stickers/output/):
    01.png 〜 40.png  … スタンプ本体 (370x320, 透過PNG)
    main.png         … メイン画像 (240x240)
    tab.png          … トークルームタブ画像 (96x74)
    preview.png      … 一覧プレビュー (確認用・申請不要)
"""

import io
import math
from pathlib import Path

import cairosvg
from PIL import Image, ImageFilter

from phrases import STICKERS

OUT = Path(__file__).parent / "output"
W, H = 370, 320

LINE = "#4b3621"      # 輪郭線
FUR = "#ffffff"       # 体
PATCH = "#f0b87a"     # 片耳のトラ模様（キャラの目印）
INNER = "#ffc2cc"     # 耳の内側・肉球
CHEEK = "#ff9aa8"     # ほっぺ
RIBBON = "#ff6f61"    # リボン（キャラの目印）
SW = 5                # 線の太さ
FONT = "Rounded Mplus 1c"


# ---------------------------------------------------------------- パーツ

def capsule(x1, y1, x2, y2, w=22):
    """輪郭付きのカプセル（腕・しっぽ用）"""
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{LINE}" '
        f'stroke-width="{w + SW * 2}" stroke-linecap="round"/>'
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{FUR}" '
        f'stroke-width="{w}" stroke-linecap="round"/>'
    )


def tail():
    return (
        f'<path d="M 45 70 Q 105 70 100 20 Q 97 -5 115 -15" fill="none" stroke="{LINE}" '
        f'stroke-width="{18 + SW * 2}" stroke-linecap="round"/>'
        f'<path d="M 45 70 Q 105 70 100 20 Q 97 -5 115 -15" fill="none" stroke="{FUR}" '
        f'stroke-width="18" stroke-linecap="round"/>'
    )


def body():
    return (
        f'<ellipse cx="0" cy="50" rx="58" ry="42" fill="{FUR}" stroke="{LINE}" stroke-width="{SW}"/>'
        f'<ellipse cx="-28" cy="90" rx="17" ry="10" fill="{FUR}" stroke="{LINE}" stroke-width="{SW}"/>'
        f'<ellipse cx="28" cy="90" rx="17" ry="10" fill="{FUR}" stroke="{LINE}" stroke-width="{SW}"/>'
    )


def ears():
    left = "M -72 -48 Q -80 -110 -62 -118 Q -40 -105 -20 -88"
    right = "M 72 -48 Q 80 -110 62 -118 Q 40 -105 20 -88"
    return (
        f'<path d="{left} Z" fill="{PATCH}" stroke="{LINE}" stroke-width="{SW}" stroke-linejoin="round"/>'
        f'<path d="M -64 -60 Q -68 -98 -60 -104 Q -46 -96 -36 -86 Z" fill="{INNER}"/>'
        f'<path d="{right} Z" fill="{FUR}" stroke="{LINE}" stroke-width="{SW}" stroke-linejoin="round"/>'
        f'<path d="M 64 -60 Q 68 -98 60 -104 Q 46 -96 36 -86 Z" fill="{INNER}"/>'
    )


def ribbon():
    return (
        '<g transform="translate(52 -92) rotate(20)">'
        f'<path d="M 0 0 L -22 -14 Q -28 0 -22 14 Z" fill="{RIBBON}" stroke="{LINE}" stroke-width="4" stroke-linejoin="round"/>'
        f'<path d="M 0 0 L 22 -14 Q 28 0 22 14 Z" fill="{RIBBON}" stroke="{LINE}" stroke-width="4" stroke-linejoin="round"/>'
        f'<circle r="7" fill="{RIBBON}" stroke="{LINE}" stroke-width="4"/>'
        '</g>'
    )


def head_shape():
    return (
        f'<ellipse cx="0" cy="-30" rx="84" ry="66" fill="{FUR}" stroke="{LINE}" stroke-width="{SW}"/>'
        # 片耳から頭へのトラ模様
        f'<path d="M -62 -80 Q -48 -92 -30 -93 Q -40 -80 -38 -70 Q -52 -72 -62 -80 Z" fill="{PATCH}"/>'
    )


def one_eye(kind, x, y, side):
    s = f'stroke="{LINE}" stroke-width="{SW}" stroke-linecap="round" fill="none"'
    if kind in ("dot", "sad", "determined", "teary", "worried"):
        out = (
            f'<ellipse cx="{x}" cy="{y}" rx="8" ry="10" fill="{LINE}"/>'
            f'<circle cx="{x + 3}" cy="{y - 4}" r="3" fill="#fff"/>'
        )
        if kind in ("sad", "worried"):  # 困り眉: 内側が上がる
            out += f'<path d="M {x + 12 * side} {y - 17} L {x - 10 * side} {y - 26}" {s}/>'
        if kind == "determined":  # キリッと眉: 外側が上がる
            out += f'<path d="M {x + 12 * side} {y - 27} L {x - 10 * side} {y - 18}" {s}/>'
        if kind == "teary":
            out += f'<path d="M {x - 8} {y + 10} Q {x} {y + 16} {x + 8} {y + 10}" stroke="#6ec6ff" stroke-width="5" fill="none" stroke-linecap="round"/>'
        return out
    if kind == "sparkle":
        return (
            f'<ellipse cx="{x}" cy="{y}" rx="11" ry="13" fill="{LINE}"/>'
            f'<circle cx="{x + 4}" cy="{y - 5}" r="4.5" fill="#fff"/>'
            f'<circle cx="{x - 4}" cy="{y + 5}" r="2.2" fill="#fff"/>'
        )
    if kind == "happy":
        return f'<path d="M {x - 11} {y + 4} Q {x} {y - 12} {x + 11} {y + 4}" {s}/>'
    if kind == "closed":
        return f'<path d="M {x - 11} {y} Q {x} {y + 9} {x + 11} {y}" {s}/>'
    if kind == "sorry":  # > <
        d = 10 * side
        return f'<path d="M {x - d} {y - 9} L {x + d} {y} L {x - d} {y + 9}" {s} stroke-linejoin="round"/>'
    if kind == "surprised":
        return (
            f'<circle cx="{x}" cy="{y}" r="12" fill="#fff" stroke="{LINE}" stroke-width="{SW}"/>'
            f'<circle cx="{x}" cy="{y}" r="4" fill="{LINE}"/>'
        )
    if kind == "flat":
        return f'<path d="M {x - 11} {y} L {x + 11} {y}" {s}/>'
    raise ValueError(kind)


def eyes(kind):
    if kind == "wink":
        return one_eye("dot", -30, -30, -1) + one_eye("happy", 30, -30, 1)
    return one_eye(kind, -30, -30, -1) + one_eye(kind, 30, -30, 1)


def mouth(kind):
    s = f'stroke="{LINE}" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round" fill="none"'
    nose = f'<path d="M -6 -12 L 6 -12 L 0 -6 Z" fill="{INNER}" stroke="{LINE}" stroke-width="3" stroke-linejoin="round"/>'
    if kind == "w":
        return nose + f'<path d="M -14 -4 Q -7 4 0 -4 Q 7 4 14 -4" {s}/>'
    if kind == "open":
        return nose + (
            f'<path d="M -14 -3 Q 0 -1 14 -3 Q 12 18 0 18 Q -12 18 -14 -3 Z" fill="#e0475b" stroke="{LINE}" stroke-width="4.5" stroke-linejoin="round"/>'
            f'<ellipse cx="0" cy="12" rx="7" ry="4" fill="#ff9aa8"/>'
        )
    if kind == "o":
        return nose + f'<ellipse cx="0" cy="4" rx="6" ry="8" fill="#e0475b" stroke="{LINE}" stroke-width="4"/>'
    if kind == "flat":
        return nose + f'<path d="M -10 0 L 10 0" {s}/>'
    if kind == "wavy":
        return nose + f'<path d="M -16 2 Q -11 -4 -5 2 Q 0 7 5 2 Q 11 -4 16 2" {s}/>'
    if kind == "small":
        return nose + f'<path d="M -7 -3 Q 0 3 7 -3" {s}/>'
    raise ValueError(kind)


def cheeks(strong=False):
    op = 0.85 if strong else 0.55
    out = (
        f'<ellipse cx="-56" cy="-8" rx="15" ry="9" fill="{CHEEK}" opacity="{op}"/>'
        f'<ellipse cx="56" cy="-8" rx="15" ry="9" fill="{CHEEK}" opacity="{op}"/>'
    )
    if strong:
        for cx in (-56, 56):
            out += "".join(
                f'<path d="M {cx + dx - 3} -12 L {cx + dx + 3} -4" stroke="#e06070" stroke-width="2.5" stroke-linecap="round"/>'
                for dx in (-7, 0, 7)
            )
    return out


def paw(x, y):
    return f'<circle cx="{x}" cy="{y}" r="15" fill="{FUR}" stroke="{LINE}" stroke-width="{SW}"/>'


SHOULDER_L, SHOULDER_R = (-40, 34), (40, 34)

ARMS = {
    "down": ((-52, 62), (52, 62)),
    "wave": ((-52, 62), (88, -28)),
    "banzai": ((-100, -30), (100, -30)),
    "together": ((-9, 26), (9, 26)),
    "cheek": ((-66, 2), (66, 2)),
    "thumb": ((-52, 62), (72, 20)),
    "salute": ((-52, 62), (92, -48)),
    "chin": ((-52, 62), (18, 12)),
    "hold": ((-34, 44), (34, 44)),
    "fist": ((-52, 62), (66, -8)),
    "mouth": ((-14, 4), (14, 4)),
    "point": ((-52, 62), (96, 30)),
}


def arms(pose):
    (lx, ly), (rx, ry) = ARMS[pose]
    out = capsule(*SHOULDER_L, lx, ly) + capsule(*SHOULDER_R, rx, ry)
    out += paw(lx, ly) + paw(rx, ry)
    if pose == "thumb":
        out += capsule(rx + 4, ry - 10, rx + 6, ry - 26, 11)
    if pose == "point":
        out += capsule(rx + 8, ry - 2, rx + 26, ry - 6, 10)
    return out


# ---------------------------------------------------------------- 小物

def item(kind):
    if kind == "heart":
        return (f'<path d="M 0 78 C -60 40 -40 0 0 25 C 40 0 60 40 0 78 Z" fill="#ff6f8a" '
                f'stroke="{LINE}" stroke-width="{SW}" stroke-linejoin="round"/>'
                '<ellipse cx="-18" cy="30" rx="7" ry="4" fill="#fff" opacity=".7" transform="rotate(-30 -18 30)"/>')
    if kind == "cup":
        return (f'<path d="M -26 30 L 26 30 L 20 72 L -20 72 Z" fill="#fff" stroke="{LINE}" stroke-width="{SW}" stroke-linejoin="round"/>'
                f'<path d="M -24 40 L 24 40 L 22 52 L -22 52 Z" fill="#8bc98b"/>'
                '<path d="M -8 20 Q -14 10 -8 2 M 8 20 Q 2 10 8 2" stroke="#bbb" stroke-width="4" fill="none" stroke-linecap="round"/>')
    if kind == "bag":
        return (f'<path d="M -18 40 Q -18 20 0 20 Q 18 20 18 40" fill="none" stroke="{LINE}" stroke-width="{SW}"/>'
                f'<rect x="-34" y="38" width="68" height="44" rx="8" fill="#5b8fd6" stroke="{LINE}" stroke-width="{SW}"/>')
    if kind == "memo":
        return (f'<rect x="-32" y="22" width="64" height="58" rx="5" fill="#fff8d6" stroke="{LINE}" stroke-width="{SW}"/>'
                + "".join(f'<path d="M -20 {y} L 20 {y}" stroke="#c9b27a" stroke-width="4" stroke-linecap="round"/>' for y in (38, 52, 66)))
    if kind == "flower":
        petals = "".join(
            f'<circle cx="{14 * math.cos(a):.1f}" cy="{30 + 14 * math.sin(a):.1f}" r="11" fill="#ff9ec4" stroke="{LINE}" stroke-width="4"/>'
            for a in [i * 2 * math.pi / 5 - math.pi / 2 for i in range(5)])
        return (f'<path d="M 0 40 L 0 85" stroke="#4caf50" stroke-width="7" stroke-linecap="round"/>'
                + petals + f'<circle cx="0" cy="30" r="9" fill="#ffd54f" stroke="{LINE}" stroke-width="4"/>')
    if kind == "cracker":
        return (f'<path d="M -30 80 L -4 30 L 20 56 Z" fill="#ffd54f" stroke="{LINE}" stroke-width="{SW}" stroke-linejoin="round"/>'
                '<path d="M -18 56 L 4 44" stroke="#ff6f61" stroke-width="5"/>')
    if kind == "pillow":
        return (f'<rect x="-50" y="50" width="100" height="44" rx="20" fill="#cfe3ff" stroke="{LINE}" stroke-width="{SW}"/>')
    if kind == "tea":
        return (f'<path d="M -28 34 L 28 34 Q 26 76 0 76 Q -26 76 -28 34 Z" fill="#fff" stroke="{LINE}" stroke-width="{SW}" stroke-linejoin="round"/>'
                '<path d="M -20 44 L 20 44" stroke="#a5d6a7" stroke-width="6" stroke-linecap="round"/>'
                '<path d="M -6 24 Q -12 14 -6 6 M 8 24 Q 2 14 8 6" stroke="#bbb" stroke-width="4" fill="none" stroke-linecap="round"/>')
    if kind == "hanky":
        return f'<path d="M -30 30 L 20 24 L 26 70 L -24 76 Z" fill="#b3e5fc" stroke="{LINE}" stroke-width="{SW}" stroke-linejoin="round"/>'
    raise ValueError(kind)


def hat(kind):
    if kind == "nightcap":
        return (f'<path d="M -60 -80 Q -10 -150 70 -120 Q 30 -110 40 -80 Z" fill="#7e9cf0" stroke="{LINE}" stroke-width="{SW}" stroke-linejoin="round"/>'
                f'<circle cx="74" cy="-120" r="12" fill="#fff" stroke="{LINE}" stroke-width="{SW}"/>'
                f'<rect x="-66" y="-90" width="112" height="18" rx="9" fill="#fff" stroke="{LINE}" stroke-width="{SW}"/>')
    if kind == "headband":
        return (f'<path d="M -82 -58 Q 0 -86 82 -58" stroke="#fff" stroke-width="16" fill="none"/>'
                f'<path d="M -82 -58 Q 0 -86 82 -58" stroke="#ff4d4d" stroke-width="10" fill="none"/>'
                '<circle cx="0" cy="-72" r="6" fill="#ff4d4d"/>')
    return ""


# ---------------------------------------------------------------- 効果

def fx(kind):
    s = 'stroke-linecap="round" stroke-linejoin="round" fill="none"'
    if kind == "sparkles":
        star = lambda x, y, r, c: (f'<path d="M {x} {y - r} Q {x} {y} {x + r} {y} Q {x} {y} {x} {y + r} '
                                   f'Q {x} {y} {x - r} {y} Q {x} {y} {x} {y - r} Z" fill="{c}"/>')
        return star(-115, -80, 16, "#ffd54f") + star(118, -60, 13, "#ffb74d") + star(-100, 30, 10, "#ffd54f") + star(110, 40, 11, "#ffd54f")
    if kind == "hearts":
        h = lambda x, y, k: (f'<path transform="translate({x} {y}) scale({k})" d="M 0 12 C -18 0 -12 -14 0 -5 C 12 -14 18 0 0 12 Z" fill="#ff6f8a"/>')
        return h(-112, -70, 1.3) + h(115, -80, 1.0) + h(118, 10, 0.8)
    if kind == "sweat":
        return '<path d="M 90 -70 Q 80 -52 90 -46 Q 100 -52 90 -70 Z" fill="#8fd3ff" stroke="#4b9fd6" stroke-width="3"/>'
    if kind == "tears":
        return ('<path d="M -34 -18 Q -40 20 -30 40" stroke="#6ec6ff" stroke-width="9" ' + s + '/>'
                '<path d="M 34 -18 Q 40 20 30 40" stroke="#6ec6ff" stroke-width="9" ' + s + '/>')
    if kind == "zzz":
        return (f'<text x="92" y="-78" font-family="{FONT}" font-weight="800" font-size="30" fill="#7e9cf0">Z</text>'
                f'<text x="118" y="-104" font-family="{FONT}" font-weight="800" font-size="22" fill="#7e9cf0">z</text>')
    if kind == "motion":
        return "".join(f'<path d="M {x} -110 Q {x + 10} -95 {x} -80" stroke="#bbb" stroke-width="5" {s}/>' for x in (-110, 110))
    if kind == "exclaim":
        return (f'<path d="M 105 -110 L 100 -70" stroke="#ff6f61" stroke-width="10" {s}/>'
                '<circle cx="98" cy="-52" r="6" fill="#ff6f61"/>')
    if kind == "question":
        return f'<text x="92" y="-68" font-family="{FONT}" font-weight="800" font-size="52" fill="#3d8bd9">?</text>'
    if kind == "bulb":
        return (f'<circle cx="104" cy="-92" r="18" fill="#ffe066" stroke="{LINE}" stroke-width="4"/>'
                + "".join(f'<path d="M {104 + 28 * math.cos(a):.0f} {-92 + 28 * math.sin(a):.0f} L {104 + 38 * math.cos(a):.0f} {-92 + 38 * math.sin(a):.0f}" stroke="#ffc107" stroke-width="4" {s}/>'
                          for a in [math.pi * (1 + i / 4) for i in range(5)]))
    if kind == "gloom":
        return "".join(f'<path d="M {x} -100 L {x} -60" stroke="#9aa7c7" stroke-width="4" {s}/>' for x in (-50, -30, -10, 10, 30, 50))
    if kind == "circle":
        return '<circle cx="0" cy="-10" r="128" fill="none" stroke="#ff6f61" stroke-width="14" opacity=".9"/>'
    if kind == "note":
        return (f'<path d="M 104 -60 L 104 -104 L 124 -110 L 124 -70" stroke="{LINE}" stroke-width="5" {s}/>'
                f'<ellipse cx="98" cy="-60" rx="9" ry="7" fill="{LINE}"/><ellipse cx="118" cy="-70" rx="9" ry="7" fill="{LINE}"/>')
    if kind == "confetti":
        cols = ["#ff6f61", "#ffd54f", "#4fc3f7", "#81c784", "#ba68c8"]
        pts = [(-120, -90), (-95, -120), (-60, -130), (90, -125), (120, -95), (130, -50), (-130, -40), (100, 60), (-110, 60)]
        return "".join(f'<rect x="{x}" y="{y}" width="12" height="7" rx="2" fill="{cols[i % 5]}" transform="rotate({i * 37} {x} {y})"/>'
                       for i, (x, y) in enumerate(pts))
    if kind == "wind":
        return "".join(f'<path d="M {x} {y} L {x - 40} {y}" stroke="#bbb" stroke-width="5" {s}/>' for x, y in ((-100, -20), (-110, 10), (-95, 40)))
    if kind == "clock":
        return (f'<circle cx="104" cy="-90" r="24" fill="#fff" stroke="{LINE}" stroke-width="5"/>'
                f'<path d="M 104 -104 L 104 -90 L 116 -84" stroke="{LINE}" stroke-width="4" {s}/>')
    if kind == "sun":
        return (f'<circle cx="-110" cy="-100" r="18" fill="#ffb74d"/>'
                + "".join(f'<path d="M {-110 + 25 * math.cos(a):.0f} {-100 + 25 * math.sin(a):.0f} L {-110 + 34 * math.cos(a):.0f} {-100 + 34 * math.sin(a):.0f}" stroke="#ffb74d" stroke-width="5" {s}/>'
                          for a in [i * math.pi / 4 for i in range(8)]))
    if kind == "moon":
        return '<path d="M -100 -125 A 24 24 0 1 0 -80 -80 A 20 20 0 1 1 -100 -125 Z" fill="#ffe066"/>'
    return ""


# ---------------------------------------------------------------- 文字

def text_block(lines, color, y_center, max_w=344):
    lines = lines.split("\n")
    longest = max(len(l) for l in lines)
    size = min(54 if len(lines) == 1 else 44, int(max_w / (longest * 1.02)))
    lh = size * 1.12
    top = y_center - lh * (len(lines) - 1) / 2
    out = ""
    for i, l in enumerate(lines):
        y = top + i * lh + size * 0.36
        attrs = (f'x="{W / 2}" y="{y:.1f}" text-anchor="middle" font-family="{FONT}" '
                 f'font-weight="800" font-size="{size}"')
        out += (f'<text {attrs} fill="{LINE}" stroke="{LINE}" stroke-width="{size * 0.34:.1f}" stroke-linejoin="round">{l}</text>'
                f'<text {attrs} fill="#fff" stroke="#fff" stroke-width="{size * 0.2:.1f}" stroke-linejoin="round">{l}</text>'
                f'<text {attrs} fill="{color}">{l}</text>')
    return out, lh * len(lines)


# ---------------------------------------------------------------- 組み立て

def cat_svg(s, scale):
    head_tf = f'translate(0 {s.get("head_dy", 0)}) rotate({s.get("tilt", 0)} 0 20)'
    parts = [fx("circle")] if "circle" in s.get("fx", []) else []
    parts += [tail(), body()]
    if s.get("item") in ("pillow",):
        parts.append(item(s["item"]))
    parts.append(f'<g transform="{head_tf}">' + ears() + head_shape() + ribbon()
                 + cheeks(s.get("blush") == "strong") + eyes(s.get("eyes", "dot"))
                 + mouth(s.get("mouth", "w")) + hat(s.get("hat", "")) + "</g>")
    if s.get("item") and s["item"] != "pillow":
        parts.append(item(s["item"]))
    parts.append(arms(s.get("arms", "down")))
    for f in s.get("fx", []):
        if f != "circle":
            parts.append(fx(f))
    return "".join(parts)


def sticker_svg(s):
    color = s.get("color", "#ff6f61")
    pos = s.get("text_pos", "top")
    txt, th = text_block(s["text"], color, 0)
    th = max(th, 40)
    scale = max(0.82, min(1.0, (H - th - 30) / 250))
    if pos == "top":
        text_y = 14 + th / 2
        cat_cy = text_y + th / 2 + 128 * scale
    else:
        text_y = H - 14 - th / 2
        cat_cy = text_y - th / 2 - 100 * scale
    txt, _ = text_block(s["text"], color, text_y)
    cat = cat_svg(s, scale)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
            f'<g transform="translate({W / 2} {cat_cy:.1f}) scale({scale:.3f})">{cat}</g>{txt}</svg>')


def render(svg, w, h):
    png = cairosvg.svg2png(bytestring=svg.encode("utf-8"), output_width=w, output_height=h)
    return Image.open(io.BytesIO(png)).convert("RGBA")


def add_white_border(im, px=6):
    """スタンプらしい白フチを付ける（どの背景色でも見やすくする）"""
    alpha = im.getchannel("A")
    grown = alpha.point(lambda a: 255 if a > 20 else 0).filter(ImageFilter.MaxFilter(px * 2 + 1))
    grown = grown.filter(ImageFilter.GaussianBlur(0.8))
    base = Image.new("RGBA", im.size, (255, 255, 255, 0))
    base.putalpha(grown)
    base.alpha_composite(im)
    return base


def fit_with_margin(im, w, h, margin=10):
    """透過部分を切り詰め、指定サイズの中央に余白付きで配置"""
    bbox = im.getbbox()
    im = im.crop(bbox)
    k = min((w - margin * 2) / im.width, (h - margin * 2) / im.height)
    im = im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.LANCZOS)
    canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    canvas.alpha_composite(im, ((w - im.width) // 2, (h - im.height) // 2))
    return canvas


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    assert len(STICKERS) == 40, len(STICKERS)
    tiles = []
    for i, s in enumerate(STICKERS, 1):
        # 2倍で描いて縮小するとフチがなめらかになる
        im = render(sticker_svg(s), W * 2, H * 2)
        im = add_white_border(im, 12)
        im = fit_with_margin(im, W, H)
        im.save(OUT / f"{i:02d}.png", optimize=True)
        tiles.append(im)

    # メイン画像・タブ画像（文字なしのキャラ）
    face = {"eyes": "happy", "mouth": "open", "arms": "wave", "fx": ["sparkles"]}
    cat = (f'<svg xmlns="http://www.w3.org/2000/svg" width="600" height="600" viewBox="-150 -150 300 300">'
           f'<g transform="translate(0 20)">{cat_svg(face, 1)}</g></svg>')
    big = add_white_border(render(cat, 600, 600), 14)
    fit_with_margin(big, 240, 240).save(OUT / "main.png", optimize=True)
    fit_with_margin(big, 96, 74, margin=2).save(OUT / "tab.png", optimize=True)

    # プレビュー（LINE風の背景に並べる）
    cols = 5
    pv = Image.new("RGBA", (cols * W, 8 * H), (140, 171, 216, 255))
    for i, t in enumerate(tiles):
        pv.alpha_composite(t, ((i % cols) * W, (i // cols) * H))
    pv.convert("RGB").save(OUT / "preview.png", optimize=True)
    print(f"done: {OUT}")


if __name__ == "__main__":
    main()
