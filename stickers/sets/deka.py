"""第3弾「しろねこのデカ文字」40個

40〜60代向け。家族・友人との普段のやりとりで使う短い言葉を中心に、
丁寧な言葉も混ぜている。文字をスタンプいっぱいに大きく描き、猫は下の隅に小さく置く。
cat_side="left" で猫を左下に置く（指定なしは右下）。
"""

LAYOUT = "deka"

RED, ORANGE, GREEN, BLUE, NAVY, PINK, PURPLE, BROWN = (
    "#f0463c", "#f58a07", "#1f9e57", "#1e7fd6", "#34469c", "#e8488a", "#8a4fc9", "#9a5a2a")

MAIN = {"eyes": "happy", "mouth": "open", "arms": "wave", "fx": ["sparkles"]}  # タブ画像
MAIN_STICKER = 1  # メイン画像は「了解！」

STICKERS = [
    # --- 返事・あいさつ（いちばん使う）
    dict(text="了解！", color=RED, eyes="dot", mouth="open", arms="salute"),
    dict(text="OK！", color=GREEN, eyes="happy", mouth="open", arms="thumb", cat_side="left"),
    dict(text="ありが\nとう", color=PINK, eyes="happy", mouth="open", arms="hold", item="heart"),
    dict(text="おは\nよう", color=ORANGE, eyes="happy", mouth="open", arms="wave", cat_side="left"),
    dict(text="おや\nすみ", color=PURPLE, eyes="closed", mouth="small", arms="down", item="pillow", hat="nightcap"),
    dict(text="おつかれ\nさま", color=BLUE, eyes="happy", mouth="w", arms="hold", item="cup", cat_side="left"),
    dict(text="よろしく\nお願い\nします", color=GREEN, eyes="closed", mouth="small", arms="together", head_dy=12),
    dict(text="了解\nです", color=NAVY, eyes="dot", mouth="w", arms="salute", cat_side="left"),
    dict(text="ありがとう\nございます", color=PINK, eyes="happy", mouth="w", arms="hold", item="flower", blush="strong"),
    dict(text="ごめんね", color=BLUE, eyes="sorry", mouth="wavy", arms="together", cat_side="left"),
    dict(text="すみ\nません", color=NAVY, eyes="closed", mouth="wavy", arms="together", head_dy=12),
    dict(text="大丈夫！", color=GREEN, eyes="happy", mouth="open", arms="thumb", cat_side="left"),
    dict(text="いいね！", color=ORANGE, eyes="sparkle", mouth="open", arms="thumb"),
    dict(text="すごい！", color=RED, eyes="sparkle", mouth="open", arms="banzai", cat_side="left"),
    dict(text="はーい", color=ORANGE, eyes="happy", mouth="open", arms="wave"),
    dict(text="なるほど", color=BROWN, eyes="dot", mouth="small", arms="chin", cat_side="left"),
    dict(text="わかった", color=BLUE, eyes="sparkle", mouth="open", arms="fist"),
    dict(text="承知\nしました", color=NAVY, eyes="closed", mouth="w", arms="together", head_dy=12, cat_side="left"),
    # --- 家族・友人との連絡
    dict(text="ちょっと\n待ってて", color=ORANGE, eyes="dot", mouth="o", arms="point"),
    dict(text="今から\n帰る", color=BLUE, eyes="dot", mouth="w", arms="hold", item="bag", cat_side="left"),
    dict(text="もうすぐ\n着くよ", color=GREEN, eyes="happy", mouth="open", arms="wave"),
    dict(text="今どこ？", color=PURPLE, eyes="dot", mouth="o", arms="chin", cat_side="left"),
    dict(text="電話\nするね", color=BLUE, eyes="dot", mouth="w", arms="hold", item="phone"),
    dict(text="ごはん\nできたよ", color=ORANGE, eyes="happy", mouth="open", arms="hold", item="onigiri", cat_side="left"),
    dict(text="いってらっ\nしゃい", color=ORANGE, eyes="happy", mouth="open", arms="wave"),
    dict(text="おかえり", color=PINK, eyes="happy", mouth="open", arms="banzai", cat_side="left"),
    dict(text="気をつけ\nてね", color=BLUE, eyes="worried", mouth="small", arms="wave"),
    dict(text="お大事に", color=GREEN, eyes="worried", mouth="small", arms="hold", item="tea", cat_side="left"),
    # --- 気持ち・応援
    dict(text="おめで\nとう！", color=RED, eyes="happy", mouth="open", arms="banzai"),
    dict(text="お誕生日\nおめでとう", color=PINK, eyes="happy", mouth="open", arms="hold", item="cake", cat_side="left"),
    dict(text="がんば\nって！", color=RED, eyes="determined", mouth="open", arms="fist", hat="headband"),
    dict(text="うれ\nしい！", color=PINK, eyes="happy", mouth="open", arms="cheek", blush="strong", cat_side="left"),
    dict(text="楽し\nかった！", color=ORANGE, eyes="happy", mouth="open", arms="banzai"),
    dict(text="助かる！", color=GREEN, eyes="teary", mouth="open", arms="together", blush="strong", cat_side="left"),
    dict(text="お願い！", color=PINK, eyes="teary", mouth="small", arms="together", blush="strong"),
    dict(text="おい\nしい！", color=ORANGE, eyes="happy", mouth="open", arms="hold", item="dango", blush="strong", cat_side="left"),
    dict(text="かわ\nいい！", color=PINK, eyes="sparkle", mouth="open", arms="cheek", blush="strong"),
    dict(text="ドンマイ", color=BLUE, eyes="worried", mouth="w", arms="thumb", cat_side="left"),
    dict(text="感謝", color=RED, eyes="closed", mouth="w", arms="together", head_dy=12),
    dict(text="またね！", color=PURPLE, eyes="happy", mouth="open", arms="wave", cat_side="left"),
]
