"""特集の公式フレームをメイン画像に付ける

    python stickers/add_frame.py <セット名> <フレーム画像> [スタンプ番号]
LINE特集のルール（フレーム240x240の場合）: スタンプは194x194以内、フレームとの間は上下左右10px以上あける。
フレームの色・形は変えず、上に重ねたりはみ出したりしない。
"""
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).parent


def main():
    name, frame_path = sys.argv[1], sys.argv[2]
    idx = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    frame = Image.open(frame_path).convert("RGBA")
    assert frame.size == (240, 240), frame.size
    src = Image.open(ROOT / "output" / name / f"{idx:02d}.png").convert("RGBA")
    src = src.crop(src.getbbox())
    k = min(194 / src.width, 194 / src.height)
    src = src.resize((round(src.width * k), round(src.height * k)), Image.LANCZOS)
    out = Image.new("RGBA", (240, 240), (0, 0, 0, 0))
    out.alpha_composite(src, ((240 - src.width) // 2, (240 - src.height) // 2))
    out.alpha_composite(frame)
    out.save(ROOT / "output" / name / "main.png", optimize=True)
    print(f"done: output/{name}/main.png")


if __name__ == "__main__":
    main()
