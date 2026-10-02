"""しろねこ LINEスタンプ生成スクリプト

使い方:
    pip install cairosvg pillow
    python stickers/generate.py keigo     # 第1弾 敬語しろねこ
    python stickers/generate.py kisetsu   # 第2弾 季節のごあいさつ

セットの中身は stickers/sets/<名前>.py の STICKERS / MAIN で定義する。

出力 (stickers/output/<名前>/):
    01.png 〜 40.png  … スタンプ本体 (370x320, 透過PNG)
    main.png         … メイン画像 (240x240)
    tab.png          … トークルームタブ画像 (96x74)
    preview.png      … 一覧プレビュー (確認用・申請不要)
"""

import importlib
import io
import math
import sys
from pathlib import Path

import cairosvg
from PIL import Image, ImageFilter, ImageOps

ROOT = Path(__file__).parent
W, H = 370, 320

LINE = "#4b3621"      # 輪郭線
FUR = "#ffffff"       # 体
PATCH = "#f0b87a"     # 片耳のトラ模様（キャラの目印）
INNER = "#ffc2cc"     # 耳の内側・肉球
CHEEK = "#ff9aa8"     # ほっぺ
RIBBON = "#ff6f61"    # リボン（キャラの目印）
SW = 5                # 線の太さ
FONT = "Rounded Mplus 1c"

FLUFFY = False        # True で毛並みのギザギザ輪郭（ふわふわ系）
CHEEK_OP = 1.0        # ほっぺの濃さ（0 で無し）
TEXT_LINE = LINE      # 文字のいちばん外側の線の色
TEXT_WEIGHT = 800

ST = f'stroke="{LINE}" stroke-width="{SW}" stroke-linejoin="round"'
ROUND = 'stroke-linecap="round" stroke-linejoin="round" fill="none"'


def apply_style(style):
    """セットごとの絵柄（線の色・太さ・フォントなど）を切り替える"""
    g = globals()
    g.update(style)
    g.setdefault("TEXT_LINE", g["LINE"])
    if "TEXT_LINE" not in style:
        g["TEXT_LINE"] = g["LINE"]
    g["ST"] = f'stroke="{g["LINE"]}" stroke-width="{g["SW"]}" stroke-linejoin="round"'


def fluffy_ellipse(cx, cy, rx, ry, n, bump):
    """もこもこした毛並みの楕円（外側にふくらむ弧をつなぐ）"""
    pts = [(cx + rx * math.cos(2 * math.pi * i / n), cy + ry * math.sin(2 * math.pi * i / n)) for i in range(n)]
    d = f"M {pts[0][0]:.1f} {pts[0][1]:.1f}"
    for i in range(n):
        a = 2 * math.pi * (i + 0.5) / n
        qx, qy = cx + (rx + bump) * math.cos(a), cy + (ry + bump) * math.sin(a)
        x, y = pts[(i + 1) % n]
        d += f" Q {qx:.1f} {qy:.1f} {x:.1f} {y:.1f}"
    return d + " Z"


def star_path(cx, cy, r_out, r_in, n=5, rot=-90):
    pts = []
    for i in range(n * 2):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot + i * 180 / n)
        pts.append(f"{cx + r * math.cos(a):.1f} {cy + r * math.sin(a):.1f}")
    return "M " + " L ".join(pts) + " Z"


# ---------------------------------------------------------------- 体のパーツ

def tail():
    d = "M 45 70 Q 105 70 100 20 Q 97 -5 115 -15"
    return (f'<path d="{d}" fill="none" stroke="{LINE}" stroke-width="{20 + SW * 2}" stroke-linecap="round"/>'
            f'<path d="{d}" fill="none" stroke="{FUR}" stroke-width="20" stroke-linecap="round"/>')


def body():
    if FLUFFY:
        return (
            f'<path d="{fluffy_ellipse(0, 50, 56, 40, 18, 7)}" fill="{FUR}" {ST}/>'
            f'<ellipse cx="-28" cy="90" rx="18" ry="11" fill="{FUR}" {ST}/>'
            f'<ellipse cx="28" cy="90" rx="18" ry="11" fill="{FUR}" {ST}/>'
        )
    return (
        f'<ellipse cx="0" cy="50" rx="58" ry="42" fill="{FUR}" {ST}/>'
        f'<ellipse cx="-28" cy="90" rx="18" ry="11" fill="{FUR}" {ST}/>'
        f'<ellipse cx="28" cy="90" rx="18" ry="11" fill="{FUR}" {ST}/>'
    )


def ears():
    left = "M -72 -48 Q -80 -110 -62 -118 Q -40 -105 -20 -88"
    right = "M 72 -48 Q 80 -110 62 -118 Q 40 -105 20 -88"
    return (
        f'<path d="{left} Z" fill="{PATCH}" {ST}/>'
        f'<path d="M -64 -60 Q -68 -98 -60 -104 Q -46 -96 -36 -86 Z" fill="{INNER}"/>'
        f'<path d="{right} Z" fill="{FUR}" {ST}/>'
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
    if FLUFFY:
        return (
            f'<path d="{fluffy_ellipse(0, -30, 82, 64, 28, 7)}" fill="{FUR}" {ST}/>'
            f'<path d="M -62 -80 Q -48 -92 -30 -93 Q -40 -80 -38 -70 Q -52 -72 -62 -80 Z" fill="{PATCH}"/>'
        )
    return (
        f'<ellipse cx="0" cy="-30" rx="84" ry="66" fill="{FUR}" {ST}/>'
        f'<path d="M -62 -80 Q -48 -92 -30 -93 Q -40 -80 -38 -70 Q -52 -72 -62 -80 Z" fill="{PATCH}"/>'
    )


def one_eye(kind, x, y, side):
    s = f'stroke="{LINE}" stroke-width="{SW}" stroke-linecap="round" fill="none"'
    if kind in ("dot", "sad", "determined", "teary", "worried"):
        out = (f'<ellipse cx="{x}" cy="{y}" rx="8" ry="10" fill="{LINE}"/>'
               f'<circle cx="{x + 3}" cy="{y - 4}" r="3" fill="#fff"/>')
        if kind in ("sad", "worried"):  # 困り眉: 内側が上がる
            out += f'<path d="M {x + 12 * side} {y - 17} L {x - 10 * side} {y - 26}" {s}/>'
        if kind == "determined":  # キリッと眉: 外側が上がる
            out += f'<path d="M {x + 12 * side} {y - 27} L {x - 10 * side} {y - 18}" {s}/>'
        if kind == "teary":
            out += f'<path d="M {x - 8} {y + 10} Q {x} {y + 16} {x + 8} {y + 10}" stroke="#6ec6ff" stroke-width="5" fill="none" stroke-linecap="round"/>'
        return out
    if kind == "sparkle":
        return (f'<ellipse cx="{x}" cy="{y}" rx="11" ry="13" fill="{LINE}"/>'
                f'<circle cx="{x + 4}" cy="{y - 5}" r="4.5" fill="#fff"/>'
                f'<circle cx="{x - 4}" cy="{y + 5}" r="2.2" fill="#fff"/>')
    if kind == "happy":
        return f'<path d="M {x - 11} {y + 4} Q {x} {y - 12} {x + 11} {y + 4}" {s}/>'
    if kind == "closed":
        return f'<path d="M {x - 11} {y} Q {x} {y + 9} {x + 11} {y}" {s}/>'
    if kind == "sorry":  # > <
        d = 10 * side
        return f'<path d="M {x - d} {y - 9} L {x + d} {y} L {x - d} {y + 9}" {s} stroke-linejoin="round"/>'
    if kind == "surprised":
        return (f'<circle cx="{x}" cy="{y}" r="12" fill="#fff" stroke="{LINE}" stroke-width="{SW}"/>'
                f'<circle cx="{x}" cy="{y}" r="4" fill="{LINE}"/>')
    if kind == "flat":
        return f'<path d="M {x - 11} {y} L {x + 11} {y}" {s}/>'
    if kind == "bead":  # つぶらな目（ふわふわ系）
        return (f'<ellipse cx="{x}" cy="{y + 2}" rx="6" ry="7.5" fill="{LINE}"/>'
                f'<circle cx="{x + 2}" cy="{y - 1}" r="2.2" fill="#fff"/>')
    if kind == "tiny":  # 点の目（シュール系の真顔）
        return f'<circle cx="{x}" cy="{y}" r="4.5" fill="{LINE}"/>'
    if kind == "stare":  # 見開いた真顔
        return (f'<circle cx="{x}" cy="{y}" r="13" fill="#fff" stroke="{LINE}" stroke-width="{SW - 1}"/>'
                f'<circle cx="{x}" cy="{y}" r="3.5" fill="{LINE}"/>')
    if kind == "half":  # 半目
        return (f'<path d="M {x - 12} {y - 2} L {x + 12} {y - 2}" {s}/>'
                f'<path d="M {x - 8} {y - 2} A 8 7 0 0 0 {x + 8} {y - 2} Z" fill="{LINE}"/>')
    raise ValueError(kind)


def eyes(kind):
    if kind == "wink":
        return one_eye("dot", -30, -30, -1) + one_eye("happy", 30, -30, 1)
    return one_eye(kind, -30, -30, -1) + one_eye(kind, 30, -30, 1)


def mouth(kind):
    s = f'stroke="{LINE}" stroke-width="4.5" {ROUND}'
    nose = f'<path d="M -6 -12 L 6 -12 L 0 -6 Z" fill="{INNER}" stroke="{LINE}" stroke-width="3" stroke-linejoin="round"/>'
    if kind == "w":
        return nose + f'<path d="M -14 -4 Q -7 4 0 -4 Q 7 4 14 -4" {s}/>'
    if kind == "open":
        return nose + (
            f'<path d="M -14 -3 Q 0 -1 14 -3 Q 12 18 0 18 Q -12 18 -14 -3 Z" fill="#e0475b" stroke="{LINE}" stroke-width="4.5" stroke-linejoin="round"/>'
            '<ellipse cx="0" cy="12" rx="7" ry="4" fill="#ff9aa8"/>')
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
    op = (0.85 if strong else 0.55) * (1 if strong else CHEEK_OP)
    if op == 0:
        return ""
    out = (f'<ellipse cx="-56" cy="-8" rx="15" ry="9" fill="{CHEEK}" opacity="{op}"/>'
           f'<ellipse cx="56" cy="-8" rx="15" ry="9" fill="{CHEEK}" opacity="{op}"/>')
    if strong:
        for cx in (-56, 56):
            out += "".join(
                f'<path d="M {cx + dx - 3} -12 L {cx + dx + 3} -4" stroke="#e06070" stroke-width="2.5" stroke-linecap="round"/>'
                for dx in (-7, 0, 7))
    return out


# ---------------------------------------------------------------- 腕（ぷっくり丸い手）

SHOULDER_L, SHOULDER_R = (-42, 38), (42, 38)
ARM_W, PAW_R = 30, 18

ARMS = {
    "down": ((-50, 66), (50, 66)),
    "wave": ((-50, 66), (72, -4)),
    "banzai": ((-76, -8), (76, -8)),
    "together": ((-16, 46), (16, 46)),
    "cheek": ((-62, 6), (62, 6)),
    "thumb": ((-50, 66), (64, 26)),
    "salute": ((-50, 66), (76, -26)),
    "chin": ((-50, 66), (18, 16)),
    "hold": ((-40, 56), (40, 56)),
    "fist": ((-50, 66), (64, -2)),
    "mouth": ((-15, 8), (15, 8)),
    "point": ((-50, 66), (80, 34)),
    "umbrella": ((-50, 66), (58, 12)),
}
PADS_SHOWN = {"wave", "banzai", "salute"}   # 肉球を見せるポーズ


def arms(pose):
    """輪郭→中身の2回塗りで、腕と手を継ぎ目のない丸いかたまりにする"""
    hands = ARMS[pose]
    shoulders = (SHOULDER_L, SHOULDER_R)
    outline, fill = "", ""
    for (sx, sy), (hx, hy) in zip(shoulders, hands):
        outline += (f'<line x1="{sx}" y1="{sy}" x2="{hx}" y2="{hy}" stroke="{LINE}" stroke-width="{ARM_W + SW * 2}" stroke-linecap="round"/>'
                    f'<circle cx="{hx}" cy="{hy}" r="{PAW_R + SW}" fill="{LINE}"/>')
        fill += (f'<line x1="{sx}" y1="{sy}" x2="{hx}" y2="{hy}" stroke="{FUR}" stroke-width="{ARM_W}" stroke-linecap="round"/>'
                 f'<circle cx="{hx}" cy="{hy}" r="{PAW_R}" fill="{FUR}"/>')
    out = outline + fill
    for i, (hx, hy) in enumerate(hands):
        side = -1 if i == 0 else 1
        if pose in PADS_SHOWN and side == 1 or pose == "banzai":
            out += (f'<ellipse cx="{hx}" cy="{hy + 4}" rx="7" ry="6" fill="{INNER}"/>'
                    + "".join(f'<circle cx="{hx + dx}" cy="{hy - 8 + abs(dx) // 3}" r="3.2" fill="{INNER}"/>' for dx in (-8, 0, 8)))
        else:  # 指の切れ込み
            out += "".join(f'<path d="M {hx + dx} {hy + 9} L {hx + dx} {hy + 16}" stroke="{LINE}" stroke-width="3" stroke-linecap="round"/>'
                           for dx in (-5, 5))
    if pose == "thumb":
        (hx, hy) = hands[1]
        out += (f'<ellipse cx="{hx + 2}" cy="{hy - 20}" rx="8" ry="12" fill="{FUR}" stroke="{LINE}" stroke-width="{SW}"/>'
                f'<circle cx="{hx}" cy="{hy}" r="{PAW_R - 3}" fill="{FUR}"/>')
    if pose == "point":
        (hx, hy) = hands[1]
        out += f'<ellipse cx="{hx + 20}" cy="{hy - 3}" rx="12" ry="7" fill="{FUR}" stroke="{LINE}" stroke-width="{SW}"/>' \
               f'<circle cx="{hx}" cy="{hy}" r="{PAW_R - 3}" fill="{FUR}"/>'
    return out


# ---------------------------------------------------------------- 小物（手に持つもの）
# (後ろに描く部分, 前に描く部分) を返す

def item(kind):
    if kind == "heart":
        return "", (f'<path d="M 0 78 C -60 40 -40 0 0 25 C 40 0 60 40 0 78 Z" fill="#ff6f8a" {ST}/>'
                    '<ellipse cx="-18" cy="30" rx="7" ry="4" fill="#fff" opacity=".7" transform="rotate(-30 -18 30)"/>')
    if kind == "choco":
        return "", (f'<path d="M 0 80 C -60 42 -40 2 0 27 C 40 2 60 42 0 80 Z" fill="#8a5236" {ST}/>'
                    '<path d="M -34 40 L 34 40 M 0 27 L 0 80" stroke="#ff8fb1" stroke-width="7"/>'
                    '<path d="M 0 40 Q -16 24 -14 40 Q -16 56 0 40 Q 16 24 14 40 Q 16 56 0 40 Z" fill="#ff8fb1" stroke="#e0607f" stroke-width="2"/>')
    if kind == "cup":
        return "", (f'<path d="M -26 30 L 26 30 L 20 72 L -20 72 Z" fill="#fff" {ST}/>'
                    '<path d="M -24 40 L 24 40 L 22 52 L -22 52 Z" fill="#8bc98b"/>'
                    f'<path d="M -8 20 Q -14 10 -8 2 M 8 20 Q 2 10 8 2" stroke="#bbb" stroke-width="4" {ROUND}/>')
    if kind == "bag":
        return "", (f'<path d="M -18 40 Q -18 20 0 20 Q 18 20 18 40" fill="none" stroke="{LINE}" stroke-width="{SW}"/>'
                    f'<rect x="-34" y="38" width="68" height="44" rx="8" fill="#5b8fd6" {ST}/>')
    if kind == "memo":
        return "", (f'<rect x="-32" y="22" width="64" height="58" rx="5" fill="#fff8d6" {ST}/>'
                    + "".join(f'<path d="M -20 {y} L 20 {y}" stroke="#c9b27a" stroke-width="4" stroke-linecap="round"/>' for y in (38, 52, 66)))
    if kind in ("flower", "carnation"):
        color = "#ff9ec4" if kind == "flower" else "#ff4d6d"
        petals = "".join(
            f'<circle cx="{14 * math.cos(a):.1f}" cy="{30 + 14 * math.sin(a):.1f}" r="11" fill="{color}" stroke="{LINE}" stroke-width="4"/>'
            for a in [i * 2 * math.pi / 5 - math.pi / 2 for i in range(5)])
        center = "#ffd54f" if kind == "flower" else "#e0304f"
        return "", ('<path d="M 0 40 L 0 85" stroke="#4caf50" stroke-width="7" stroke-linecap="round"/>'
                    + petals + f'<circle cx="0" cy="30" r="9" fill="{center}" stroke="{LINE}" stroke-width="4"/>')
    if kind == "pillow":
        return f'<rect x="-50" y="50" width="100" height="44" rx="20" fill="#cfe3ff" {ST}/>', ""
    if kind == "tea":
        return "", (f'<path d="M -28 34 L 28 34 Q 26 76 0 76 Q -26 76 -28 34 Z" fill="#fff" {ST}/>'
                    '<path d="M -20 44 L 20 44" stroke="#a5d6a7" stroke-width="6" stroke-linecap="round"/>'
                    f'<path d="M -6 24 Q -12 14 -6 6 M 8 24 Q 2 14 8 6" stroke="#bbb" stroke-width="4" {ROUND}/>')
    if kind == "icedrink":
        return "", (f'<path d="M -24 28 L 24 28 L 19 80 L -19 80 Z" fill="#bfe9ff" {ST}/>'
                    '<rect x="-12" y="36" width="12" height="12" rx="2" fill="#fff" opacity=".9"/>'
                    '<rect x="3" y="44" width="11" height="11" rx="2" fill="#fff" opacity=".9"/>'
                    f'<path d="M 8 28 L 18 2" stroke="#ff6f61" stroke-width="6" stroke-linecap="round"/>')
    if kind == "pumpkin":
        return "", (f'<ellipse cx="0" cy="54" rx="42" ry="32" fill="#ff9a2e" {ST}/>'
                    f'<path d="M -14 24 Q -22 54 -14 84 M 14 24 Q 22 54 14 84" stroke="{LINE}" stroke-width="3.5" fill="none"/>'
                    f'<path d="M -3 24 Q -2 12 6 8" stroke="#4caf50" stroke-width="8" stroke-linecap="round" fill="none"/>'
                    f'<path d="M -26 46 L -16 36 L -8 46 Z M 8 46 L 16 36 L 26 46 Z" fill="{LINE}"/>'
                    f'<path d="M -22 60 Q 0 74 22 60 L 12 64 L 6 58 L 0 66 L -6 58 L -12 64 Z" fill="{LINE}"/>')
    if kind == "gift":
        return "", (f'<rect x="-34" y="32" width="68" height="50" rx="5" fill="#ff5a5f" {ST}/>'
                    '<rect x="-6" y="32" width="12" height="50" fill="#ffd54f"/>'
                    f'<path d="M 0 32 Q -26 8 -20 30 Z M 0 32 Q 26 8 20 30 Z" fill="#ffd54f" stroke="{LINE}" stroke-width="4" stroke-linejoin="round"/>'
                    f'<rect x="-34" y="32" width="68" height="50" rx="5" fill="none" {ST}/>')
    if kind == "cake":
        return "", (f'<rect x="-36" y="40" width="72" height="42" rx="8" fill="#ffe3c2" {ST}/>'
                    f'<path d="M -36 50 Q -27 60 -18 50 Q -9 60 0 50 Q 9 60 18 50 Q 27 60 36 50 L 36 44 Q 36 40 30 40 L -30 40 Q -36 40 -36 44 Z" fill="#fff" stroke="{LINE}" stroke-width="4"/>'
                    '<circle cx="-18" cy="40" r="7" fill="#ff4d6d"/><circle cx="18" cy="40" r="7" fill="#ff4d6d"/>'
                    f'<rect x="-4" y="14" width="8" height="24" rx="3" fill="#8ecbff" stroke="{LINE}" stroke-width="3"/>'
                    '<path d="M 0 2 Q -7 10 0 14 Q 7 10 0 2 Z" fill="#ffb300"/>')
    if kind == "diploma":
        return "", (f'<rect x="-44" y="36" width="88" height="24" rx="12" fill="#fff8e1" {ST} transform="rotate(-15 0 48)"/>'
                    '<rect x="-6" y="34" width="12" height="28" fill="#e53935" transform="rotate(-15 0 48)"/>')
    if kind == "dango":
        balls = "".join(f'<circle cx="0" cy="{y}" r="15" fill="{c}" stroke="{LINE}" stroke-width="4"/>'
                        for y, c in ((8, "#ffb3c6"), (34, "#ffffff"), (60, "#9ccc65")))
        return "", f'<path d="M 0 -12 L 0 92" stroke="#c49a6c" stroke-width="6" stroke-linecap="round"/>' + balls
    if kind == "onigiri":
        return "", (f'<path d="M 0 16 Q 10 16 40 70 Q 44 82 30 82 L -30 82 Q -44 82 -40 70 Q -10 16 0 16 Z" fill="#fff" {ST}/>'
                    '<rect x="-18" y="60" width="36" height="22" fill="#2e4a3a"/>')
    if kind == "maple":
        return "", (f'<path d="M 0 64 L 0 90" stroke="#b5542c" stroke-width="6" stroke-linecap="round"/>'
                    f'<path d="{star_path(0, 44, 36, 16, 5)}" fill="#ff5a36" {ST}/>')
    if kind == "watermelon":
        return "", (f'<path d="M -44 36 A 44 44 0 0 0 44 36 Z" fill="#ff5a6e" stroke="#3aa655" stroke-width="10" stroke-linejoin="round"/>'
                    f'<path d="M -50 36 A 50 50 0 0 0 50 36 Z" fill="none" {ST}/>'
                    + "".join(f'<ellipse cx="{x}" cy="{y}" rx="3" ry="4.5" fill="{LINE}"/>' for x, y in ((-18, 48), (0, 58), (18, 48), (-8, 44), (10, 44))))
    if kind == "uchiwa":  # 右手を上げたポーズ(wave)で持つ
        return (f'<path d="M 72 -4 L 90 -40" stroke="#c49a6c" stroke-width="7" stroke-linecap="round"/>',
                f'<circle cx="96" cy="-66" r="30" fill="#e3f2fd" {ST}/>'
                '<path d="M 82 -66 Q 96 -80 110 -66 Q 96 -52 82 -66 Z" fill="#4fc3f7"/>'
                '<circle cx="96" cy="-66" r="6" fill="#ff6f61"/>')
    if kind == "book":
        return "", (f'<path d="M 0 36 Q -20 26 -44 32 L -44 80 Q -20 74 0 84 Q 20 74 44 80 L 44 32 Q 20 26 0 36 Z" fill="#fff" {ST}/>'
                    f'<path d="M 0 36 L 0 84" stroke="{LINE}" stroke-width="4"/>'
                    + "".join(f'<path d="M {x0} {y} L {x1} {y - 2}" stroke="#c9b27a" stroke-width="3" stroke-linecap="round"/>'
                              for x0, x1 in ((-36, -8), (8, 36)) for y in (48, 58, 68)))
    if kind == "fish":
        return "", (f'<path d="M -56 50 Q -20 18 30 40 L 56 24 L 50 50 L 56 76 L 30 60 Q -20 82 -56 50 Z" fill="#9ec9e8" {ST}/>'
                    f'<circle cx="-36" cy="46" r="4" fill="{LINE}"/>'
                    f'<path d="M -16 40 Q -10 50 -16 60" stroke="{LINE}" stroke-width="3" fill="none"/>')
    if kind == "magnifier":  # 右手を上げたポーズ(wave)で持つ
        return (f'<path d="M 72 -4 L 88 -32" stroke="#8d6e63" stroke-width="9" stroke-linecap="round"/>',
                f'<circle cx="100" cy="-56" r="27" fill="#d6f0ff" fill-opacity=".75" stroke="{LINE}" stroke-width="{SW + 2}"/>'
                '<path d="M 88 -66 Q 94 -74 104 -74" stroke="#fff" stroke-width="5" fill="none" stroke-linecap="round"/>')
    if kind == "box":  # 段ボールに入っている
        return "", (f'<path d="M -86 6 L 86 6 L 80 112 L -80 112 Z" fill="#d7a96b" {ST}/>'
                    f'<path d="M -86 6 L -112 -14 L -60 -14 L -40 6 Z M 86 6 L 112 -14 L 60 -14 L 40 6 Z" fill="#e8c28e" {ST}/>'
                    f'<path d="M -20 40 L 20 40" stroke="{LINE}" stroke-width="4" stroke-linecap="round"/>')
    if kind == "bread":  # 食パンから顔を出す
        crust = ("M -112 60 L -112 -50 Q -140 -140 -60 -146 Q 0 -168 60 -146 Q 140 -140 112 -50 L 112 60 Z")
        inner = ("M -96 48 L -96 -48 Q -118 -124 -54 -128 Q 0 -148 54 -128 Q 118 -124 96 -48 L 96 48 Z")
        return (f'<path d="{crust}" fill="#d68a3c" {ST}/><path d="{inner}" fill="#f8e2b8"/>', "")
    if kind == "futon":  # 布団（rot=-90 などで寝かせて使う）
        return "", (f'<rect x="-104" y="10" width="208" height="104" rx="22" fill="#9fc5ff" {ST}/>'
                    '<path d="M -104 34 L 104 34" stroke="#fff" stroke-width="8"/>'
                    + "".join(f'<circle cx="{x}" cy="{y}" r="6" fill="#fff" opacity=".8"/>' for x, y in ((-60, 70), (0, 86), (60, 66), (-20, 58), (40, 96))))
    if kind == "phone":
        return "", (f'<rect x="-24" y="18" width="48" height="76" rx="9" fill="#37474f" {ST}/>'
                    '<rect x="-17" y="28" width="34" height="52" rx="3" fill="#b3e5fc"/>'
                    '<path d="M -10 44 L 10 44 M -10 54 L 4 54" stroke="#fff" stroke-width="4" stroke-linecap="round"/>')
    if kind == "kagami":
        return "", (f'<rect x="-40" y="72" width="80" height="14" rx="3" fill="#e0a45c" {ST}/>'
                    f'<ellipse cx="0" cy="62" rx="40" ry="16" fill="#fff" {ST}/>'
                    f'<ellipse cx="0" cy="44" rx="30" ry="13" fill="#fff" {ST}/>'
                    f'<circle cx="0" cy="26" r="11" fill="#ffa726" {ST}/>'
                    '<path d="M 0 16 Q 8 8 14 12" stroke="#4caf50" stroke-width="5" fill="none" stroke-linecap="round"/>')
    if kind == "umbrella":  # umbrella ポーズで持つ
        canopy = ("M -60 -118 Q -60 -196 50 -196 Q 160 -196 160 -118 Q 142 -130 124 -118 Q 105 -130 87 -118 "
                  "Q 68 -130 50 -118 Q 31 -130 13 -118 Q -5 -130 -23 -118 Q -42 -130 -60 -118 Z")
        return (f'<path d="M 58 12 L 50 -112" stroke="{LINE}" stroke-width="6" stroke-linecap="round"/>',
                f'<path d="{canopy}" fill="#7fb3ff" {ST}/>'
                f'<path d="M 50 -196 Q 16 -160 13 -118 M 50 -196 Q 84 -160 87 -118" stroke="{LINE}" stroke-width="3.5" fill="none"/>'
                f'<path d="M 58 12 Q 60 30 46 30" stroke="{LINE}" stroke-width="6" fill="none" stroke-linecap="round"/>')
    raise ValueError(kind)


def hat(kind):
    if kind == "":
        return ""
    if kind == "nightcap":
        return (f'<path d="M -60 -80 Q -10 -150 70 -120 Q 30 -110 40 -80 Z" fill="#7e9cf0" {ST}/>'
                f'<circle cx="74" cy="-120" r="12" fill="#fff" {ST}/>'
                f'<rect x="-66" y="-90" width="112" height="18" rx="9" fill="#fff" {ST}/>')
    if kind == "headband":
        return ('<path d="M -82 -58 Q 0 -86 82 -58" stroke="#fff" stroke-width="16" fill="none"/>'
                '<path d="M -82 -58 Q 0 -86 82 -58" stroke="#ff4d4d" stroke-width="10" fill="none"/>'
                '<circle cx="0" cy="-72" r="6" fill="#ff4d4d"/>')
    if kind == "santa":
        return (f'<path d="M -58 -92 Q -20 -170 50 -150 Q 80 -140 92 -108 Q 60 -118 58 -92 Z" fill="#e53935" {ST}/>'
                f'<circle cx="94" cy="-104" r="13" fill="#fff" {ST}/>'
                f'<rect x="-68" y="-102" width="136" height="24" rx="12" fill="#fff" {ST}/>')
    if kind == "witch":
        return (f'<ellipse cx="0" cy="-90" rx="96" ry="18" fill="#5e35b1" {ST}/>'
                f'<path d="M -46 -92 Q -30 -150 10 -186 Q 30 -196 34 -180 Q 24 -176 30 -150 Q 40 -118 46 -92 Z" fill="#5e35b1" {ST}/>'
                '<path d="M -44 -100 Q 0 -112 44 -100 L 45 -92 Q 0 -104 -45 -92 Z" fill="#ff9a2e"/>'
                f'<path d="{star_path(4, -130, 10, 4.5)}" fill="#ffd54f"/>')
    if kind == "straw":
        return (f'<ellipse cx="0" cy="-92" rx="98" ry="20" fill="#f6d77a" {ST}/>'
                f'<path d="M -52 -94 Q -50 -150 0 -150 Q 50 -150 52 -94 Z" fill="#f6d77a" {ST}/>'
                '<path d="M -51 -104 Q 0 -116 51 -104 L 52 -94 Q 0 -106 -52 -94 Z" fill="#e53935"/>')
    raise ValueError(kind)


def accessory(kind):
    if kind == "scarf":
        return (f'<path d="M -56 26 Q 0 46 56 26 L 58 46 Q 0 66 -58 46 Z" fill="#e53935" {ST}/>'
                f'<path d="M 18 46 L 40 46 L 44 88 L 22 88 Z" fill="#e53935" {ST}/>'
                '<path d="M 24 82 L 42 82" stroke="#fff" stroke-width="4"/>'
                '<path d="M -40 38 Q 0 54 40 38" stroke="#fff" stroke-width="4" fill="none"/>')
    if kind == "mask":
        return (f'<path d="M -26 -14 L -70 -26 M 26 -14 L 70 -26" stroke="#ccc" stroke-width="3"/>'
                f'<rect x="-30" y="-20" width="60" height="36" rx="12" fill="#fff" stroke="#9aa7c7" stroke-width="4"/>'
                '<path d="M -20 -8 L 20 -8 M -20 2 L 20 2" stroke="#d5dcea" stroke-width="3"/>')
    return ""


# ---------------------------------------------------------------- 効果

def fx(kind):
    s = ROUND
    if kind == "sparkles":
        star = lambda x, y, r, c: (f'<path d="M {x} {y - r} Q {x} {y} {x + r} {y} Q {x} {y} {x} {y + r} '
                                   f'Q {x} {y} {x - r} {y} Q {x} {y} {x} {y - r} Z" fill="{c}"/>')
        return star(-115, -80, 16, "#ffd54f") + star(118, -60, 13, "#ffb74d") + star(-100, 30, 10, "#ffd54f") + star(110, 40, 11, "#ffd54f")
    if kind == "hearts":
        h = lambda x, y, k: f'<path transform="translate({x} {y}) scale({k})" d="M 0 12 C -18 0 -12 -14 0 -5 C 12 -14 18 0 0 12 Z" fill="#ff6f8a"/>'
        return h(-112, -70, 1.3) + h(115, -80, 1.0) + h(118, 10, 0.8)
    if kind == "sweat":
        return '<path d="M 90 -70 Q 80 -52 90 -46 Q 100 -52 90 -70 Z" fill="#8fd3ff" stroke="#4b9fd6" stroke-width="3"/>'
    if kind == "tears":
        return (f'<path d="M -34 -18 Q -40 20 -30 40" stroke="#6ec6ff" stroke-width="9" {s}/>'
                f'<path d="M 34 -18 Q 40 20 30 40" stroke="#6ec6ff" stroke-width="9" {s}/>')
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
        return ('<circle cx="-110" cy="-100" r="18" fill="#ffb74d"/>'
                + "".join(f'<path d="M {-110 + 25 * math.cos(a):.0f} {-100 + 25 * math.sin(a):.0f} L {-110 + 34 * math.cos(a):.0f} {-100 + 34 * math.sin(a):.0f}" stroke="#ffb74d" stroke-width="5" {s}/>'
                          for a in [i * math.pi / 4 for i in range(8)]))
    if kind == "moon":
        return '<path d="M -100 -125 A 24 24 0 1 0 -80 -80 A 20 20 0 1 1 -100 -125 Z" fill="#ffe066"/>'
    if kind == "sakura":
        def petal(x, y, rot, k=1.0):
            return (f'<g transform="translate({x} {y}) rotate({rot}) scale({k})">'
                    '<path d="M 0 -12 Q 10 -8 8 4 Q 4 12 0 10 Q -4 12 -8 4 Q -10 -8 0 -12 Z" fill="#ffb7cf" stroke="#f08aac" stroke-width="2"/>'
                    '<path d="M -3 -12 L 0 -6 L 3 -12" fill="#fff" stroke="none"/></g>')
        return "".join(petal(x, y, r, k) for x, y, r, k in
                       ((-118, -90, 20, 1.3), (-92, -130, -30, 1.0), (112, -110, 40, 1.2), (126, -40, -10, 0.9),
                        (-128, -20, 60, 0.9), (104, 50, 15, 1.0), (-108, 56, -40, 1.1)))
    if kind == "snow":
        return "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fff" stroke="#9ccaf0" stroke-width="3"/>' for x, y, r in
                       ((-120, -100, 9), (-96, -40, 6), (-126, 30, 8), (110, -120, 7), (128, -60, 10), (104, 20, 6), (-70, -140, 6), (80, -150, 7)))
    if kind == "leaves":
        cols = ["#ff7043", "#ffb300", "#e53935"]

        def leaf(x, y, rot, c):
            return (f'<g transform="translate({x} {y}) rotate({rot})">'
                    f'<path d="M 0 -14 Q 11 -4 0 14 Q -11 -4 0 -14 Z" fill="{c}" stroke="{LINE}" stroke-width="2.5"/>'
                    f'<path d="M 0 -10 L 0 18" stroke="{LINE}" stroke-width="2.5" stroke-linecap="round"/></g>')
        return "".join(leaf(x, y, r, cols[i % 3]) for i, (x, y, r) in enumerate(
            ((-118, -96, -30), (-100, -30, 40), (114, -110, 20), (126, -40, -50), (-124, 40, 70), (108, 44, -20))))
    if kind == "rain":
        return "".join(f'<path d="M {x} {y} L {x - 6} {y + 18}" stroke="#6ec6ff" stroke-width="5" {s}/>' for x, y in
                       ((-120, -60), (-96, -10), (-130, 30), (-104, 60), (130, -50), (112, 0), (138, 40), (116, 70)))
    if kind == "fireworks":
        def burst(cx, cy, r, c):
            return "".join(f'<path d="M {cx + r * 0.45 * math.cos(a):.0f} {cy + r * 0.45 * math.sin(a):.0f} L {cx + r * math.cos(a):.0f} {cy + r * math.sin(a):.0f}" stroke="{c}" stroke-width="5" {s}/>'
                           for a in [i * math.pi / 6 for i in range(12)])
        return burst(-112, -118, 34, "#ff6f61") + burst(116, -104, 28, "#ffd54f") + burst(-128, -40, 18, "#4fc3f7")
    if kind == "shiver":
        return "".join(f'<path d="M {x} -20 L {x + 8 * sgn} -8 L {x} 4 L {x + 8 * sgn} 16" stroke="#9aa7c7" stroke-width="4" {s}/>'
                       for x, sgn in ((-100, -1), (-114, -1), (100, 1), (114, 1)))
    if kind == "xmas_star":
        return (f'<path d="{star_path(-112, -100, 22, 9)}" fill="#ffd54f" stroke="#f5a623" stroke-width="3" stroke-linejoin="round"/>'
                f'<path d="{star_path(118, -60, 14, 6)}" fill="#ffd54f"/>')
    if kind == "glow":  # 後光
        return "".join(f'<path d="M 0 -20 L {165 * math.cos(a - 0.09):.0f} {-20 + 165 * math.sin(a - 0.09):.0f} '
                       f'L {165 * math.cos(a + 0.09):.0f} {-20 + 165 * math.sin(a + 0.09):.0f} Z" fill="#ffe27a" opacity=".55"/>'
                       for a in [i * math.pi / 8 for i in range(16)])
    if kind == "clouds":
        return "".join(f'<path d="{fluffy_ellipse(x, y, rx, ry, 9, 8)}" fill="#fff" stroke="#c9d6e8" stroke-width="4"/>'
                       for x, y, rx, ry in ((-90, 120, 70, 22), (70, 128, 80, 22), (-10, 140, 70, 18)))
    if kind == "battery":
        return (f'<rect x="80" y="-128" width="54" height="28" rx="5" fill="#fff" stroke="{LINE}" stroke-width="4"/>'
                f'<rect x="134" y="-120" width="6" height="12" rx="2" fill="{LINE}"/>'
                '<rect x="85" y="-123" width="14" height="18" rx="2" fill="#ff5252"/>'
                '<path d="M 112 -126 L 104 -112 L 112 -112 L 106 -100" stroke="#ffb300" stroke-width="4" fill="none" stroke-linejoin="round"/>')
    if kind == "space":
        return (f'<circle cx="-112" cy="-110" r="18" fill="#ffcc80" stroke="{LINE}" stroke-width="3"/>'
                '<ellipse cx="-112" cy="-110" rx="30" ry="7" fill="none" stroke="#ff8a65" stroke-width="4" transform="rotate(-20 -112 -110)"/>'
                + "".join(f'<path d="{star_path(x, y, r, r * 0.45)}" fill="#ffd54f"/>' for x, y, r in ((110, -120, 12), (130, -60, 8), (-130, -40, 7), (100, 30, 9), (-96, 40, 6))))
    if kind == "spin":
        return (f'<path d="M -120 -40 A 130 130 0 0 1 -40 -150" stroke="#bbb" stroke-width="6" {s}/>'
                f'<path d="M 120 40 A 130 130 0 0 1 40 150" stroke="#bbb" stroke-width="6" {s}/>'
                '<path d="M -52 -158 L -36 -150 L -50 -138 Z M 52 158 L 36 150 L 50 138 Z" fill="#bbb"/>')
    if kind == "dots":  # 「…」
        return "".join(f'<circle cx="{x}" cy="-118" r="6" fill="{LINE}"/>' for x in (86, 106, 126))
    if kind == "sunrise":
        return ('<path d="M -140 70 A 50 50 0 0 1 -40 70 Z" fill="#ff8a65" opacity=".9"/>'
                + "".join(f'<path d="M {-90 + 58 * math.cos(a):.0f} {70 + 58 * math.sin(a):.0f} L {-90 + 72 * math.cos(a):.0f} {70 + 72 * math.sin(a):.0f}" stroke="#ffb74d" stroke-width="5" {s}/>'
                          for a in [math.pi * (1 + i / 6) for i in range(1, 6)]))
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
                 f'font-weight="{TEXT_WEIGHT}" font-size="{size}"')
        out += (f'<text {attrs} fill="{TEXT_LINE}" stroke="{TEXT_LINE}" stroke-width="{size * 0.34:.1f}" stroke-linejoin="round">{l}</text>'
                f'<text {attrs} fill="#fff" stroke="#fff" stroke-width="{size * 0.2:.1f}" stroke-linejoin="round">{l}</text>'
                f'<text {attrs} fill="{color}">{l}</text>')
    return out, lh * len(lines)


# ---------------------------------------------------------------- 組み立て

BACK_FX = {"circle", "sunrise", "glow", "clouds"}   # 猫の後ろに描く効果


def cat_svg(s):
    head_tf = f'translate(0 {s.get("head_dy", 0)}) rotate({s.get("tilt", 0)} 0 20)'
    back, front = item(s["item"]) if s.get("item") else ("", "")
    fxs = s.get("fx", [])
    parts = [fx(f) for f in fxs if f in BACK_FX]
    parts += [tail(), body(), back]
    parts.append(f'<g transform="{head_tf}">' + ears() + head_shape() + ribbon()
                 + cheeks(s.get("blush") == "strong") + eyes(s.get("eyes", "dot"))
                 + mouth(s.get("mouth", "w")) + accessory("mask" if s.get("mask") else "")
                 + hat(s.get("hat", "")) + "</g>")
    parts.append(accessory(s.get("wear", "")))
    parts.append(arms(s.get("arms", "down")))
    parts.append(front)
    front_fx = "".join(fx(f) for f in fxs if f not in BACK_FX)  # 効果は回転・変形させない
    cat = "".join(parts)

    # 全体の変形: rot=回転, squash=縦につぶす(とける), lift=浮かせる
    tf = f'translate(0 {-s.get("lift", 0)}) rotate({s.get("rot", 0)} 0 60)'
    if s.get("squash"):
        tf += f' translate(0 100) scale({1 + (1 - s["squash"]) * 0.6:.2f} {s["squash"]}) translate(0 -100)'
    cat = f'<g transform="{tf}">{cat}</g>' + front_fx
    if s.get("lift"):  # 浮いている影
        cat = '<ellipse cx="0" cy="104" rx="60" ry="9" fill="#000" opacity=".15"/>' + cat
    if s.get("puddle"):  # とけた水たまり
        cat = f'<path d="{fluffy_ellipse(0, 98, 120, 20, 10, 6)}" fill="{FUR}" {ST}/>' + cat
    if s.get("clones"):  # 分身（増えました）
        n = s["clones"]
        cat = "".join(f'<g transform="translate({(i - (n - 1) / 2) * 150:.0f} {abs(i - (n - 1) / 2) * 30:.0f}) scale(.8)">{cat}</g>'
                      for i in range(n))
    return cat


def cat_image(s, px_per_unit=2):
    """猫だけを大きめのキャンバスに描き、余白を切り取って返す"""
    vb = (-210, -270, 420, 440)
    w, h = vb[2] * px_per_unit, vb[3] * px_per_unit
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
           f'viewBox="{" ".join(map(str, vb))}">{cat_svg(s)}</svg>')
    im = render(svg, w, h)
    return im.crop(im.getbbox())


def sticker_image(s):
    """文字と猫を 2倍サイズのキャンバスに配置する"""
    k = 2
    color = s.get("color", "#ff6f61")
    pos = s.get("text_pos", "top")
    _, th = text_block(s["text"], color, 0)
    text_y = 14 + th / 2 if pos == "top" else H - 14 - th / 2
    txt, _ = text_block(s["text"], color, text_y)
    text_im = render(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{txt}</svg>',
                     W * k, H * k)

    cat = cat_image(s, k)
    overlap = 10  # 文字に少しかぶせて一体感を出す
    if pos == "top":
        top, bottom = 14 + th - overlap, H - 6
    else:
        top, bottom = 6, H - 14 - th + overlap
    box_w, box_h = (W - 20) * k, (bottom - top) * k
    scale = min(box_w / cat.width, box_h / cat.height, 1.1)
    cat = cat.resize((round(cat.width * scale), round(cat.height * scale)), Image.LANCZOS)

    canvas = Image.new("RGBA", (W * k, H * k), (0, 0, 0, 0))
    x = (W * k - cat.width) // 2
    y = bottom * k - cat.height if pos == "top" else top * k
    canvas.alpha_composite(cat, (x, y))
    canvas.alpha_composite(text_im)
    return canvas


def text_width(line):
    """おおよその文字幅（全角=1, 半角=0.62）"""
    return sum(0.62 if ord(c) < 0x2000 else 1.0 for c in line)


def deka_image(s):
    """デカ文字版: 文字をいっぱいに大きく描き、猫は文字と重ならない下の隅に置く"""
    import numpy as np
    k = 2
    color = s.get("color", "#ff6f61")
    side = s.get("cat_side", "right")
    lines = s["text"].split("\n")

    # 文字は上側を横いっぱいに使う（行数が多いほど縦も広く）
    box_w, box_h = W - 44, H * (0.72 if len(lines) == 1 else 0.80)  # 太いフチの分だけ内側に
    size = min(box_w / max(text_width(l) for l in lines), box_h / (len(lines) * 1.06), 150)
    lh = size * 1.06
    top = 18 if len(lines) > 1 else max(18, (H * 0.56 - lh) / 2)
    out = ""
    for i, l in enumerate(lines):
        y = top + i * lh + size * 0.86
        attrs = (f'x="{W / 2}" y="{y:.1f}" text-anchor="middle" font-family="{FONT}" '
                 f'font-weight="800" font-size="{size:.1f}"')
        out += (f'<text {attrs} fill="{LINE}" stroke="{LINE}" stroke-width="{size * 0.26:.1f}" stroke-linejoin="round">{l}</text>'
                f'<text {attrs} fill="#fff" stroke="#fff" stroke-width="{size * 0.13:.1f}" stroke-linejoin="round">{l}</text>'
                f'<text {attrs} fill="{color}">{l}</text>')
    text_im = render(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{out}</svg>',
                     W * k, H * k)
    text_a = np.asarray(text_im.getchannel("A")) > 40

    # 猫: 大きい順に試し、文字とほとんど重ならない位置が見つかったらそこに置く
    cat_full = cat_image(s, k)
    sides = [side, "left" if side == "right" else "right"]
    best = None
    for frac in (0.46, 0.42, 0.38):  # 猫の大きさはほぼ揃える（文字の後ろに少し隠れるのは可）
        sc = min(H * frac * k / cat_full.height, W * 0.5 * k / cat_full.width)
        cat = cat_full.resize((round(cat_full.width * sc), round(cat_full.height * sc)), Image.LANCZOS)
        cat_a = np.asarray(cat.getchannel("A")) > 40
        for sd in sides:
            x = W * k - cat.width - 4 if sd == "right" else 4
            y = H * k - cat.height - 4
            region = text_a[y:y + cat.height, x:x + cat.width]
            ratio = (region & cat_a).sum() / cat_a.sum()
            if best is None or ratio < best[0] - 1e-9:
                best = (ratio, cat, x, y)
            if ratio < 0.12:
                break
        if best[0] < 0.12:
            break

    _, cat, x, y = best
    canvas = Image.new("RGBA", (W * k, H * k), (0, 0, 0, 0))
    canvas.alpha_composite(cat, (x, y))
    canvas.alpha_composite(text_im)
    return canvas


def render(svg, w, h):
    png = cairosvg.svg2png(bytestring=svg.encode("utf-8"), output_width=w, output_height=h)
    return Image.open(io.BytesIO(png)).convert("RGBA")


def add_white_border(im, px=6):
    """スタンプらしい白フチを付ける（どの背景色でも見やすくする）"""
    im = ImageOps.expand(im, border=px * 2, fill=(0, 0, 0, 0))  # フチが端で切れないように余白を足す
    alpha = im.getchannel("A")
    grown = alpha.point(lambda a: 255 if a > 20 else 0).filter(ImageFilter.MaxFilter(px * 2 + 1))
    grown = grown.filter(ImageFilter.GaussianBlur(0.8))
    base = Image.new("RGBA", im.size, (255, 255, 255, 0))
    base.putalpha(grown)
    base.alpha_composite(im)
    return base


def fit_with_margin(im, w, h, margin=10):
    """透過部分を切り詰め、指定サイズの中央に余白付きで配置"""
    im = im.crop(im.getbbox())
    k = min((w - margin * 2) / im.width, (h - margin * 2) / im.height)
    im = im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.LANCZOS)
    canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    canvas.alpha_composite(im, ((w - im.width) // 2, (h - im.height) // 2))
    return canvas


def main(set_name):
    mod = importlib.import_module(f"sets.{set_name}")
    apply_style(getattr(mod, "STYLE", {}))
    stickers = mod.STICKERS
    out = ROOT / "output" / set_name
    out.mkdir(parents=True, exist_ok=True)
    assert len(stickers) in (8, 16, 24, 32, 40), len(stickers)

    tiles = []
    for i, s in enumerate(stickers, 1):
        # 2倍で描いて縮小するとフチがなめらかになる
        im = deka_image(s) if getattr(mod, "LAYOUT", "") == "deka" else sticker_image(s)
        im = fit_with_margin(add_white_border(im, 12), W, H)
        im.save(out / f"{i:02d}.png", optimize=True)
        tiles.append(im)

    # メイン画像・タブ画像（文字なしのキャラ）
    main_pose = getattr(mod, "MAIN", {"eyes": "happy", "mouth": "open", "arms": "wave", "fx": ["sparkles"]})
    cat = (f'<svg xmlns="http://www.w3.org/2000/svg" width="700" height="700" viewBox="-175 -210 350 350">'
           f'{cat_svg(main_pose)}</svg>')
    big = add_white_border(render(cat, 700, 700), 14)
    # MAIN_STICKER を指定したセットは、そのスタンプ（文字入り）をメイン画像にする
    main_src = tiles[mod.MAIN_STICKER - 1] if hasattr(mod, "MAIN_STICKER") else big
    fit_with_margin(main_src, 240, 240).save(out / "main.png", optimize=True)
    fit_with_margin(big, 96, 74, margin=2).save(out / "tab.png", optimize=True)

    # プレビュー（LINE風の背景に並べる）
    cols = 5
    rows = math.ceil(len(tiles) / cols)
    pv = Image.new("RGBA", (cols * W, rows * H), (140, 171, 216, 255))
    for i, t in enumerate(tiles):
        pv.alpha_composite(t, ((i % cols) * W, (i // cols) * H))
    pv.convert("RGB").save(out / "preview.png", optimize=True)
    print(f"done: {out}")


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT))
    main(sys.argv[1] if len(sys.argv) > 1 else "keigo")
