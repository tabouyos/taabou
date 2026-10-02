"""第4弾「ふわふわしろねこ 全肯定」40個

リサーチより: 癒し系は「ふわふわ・ぽてっと・パステル・つぶらな目」が安定して人気。
「かわいい猫」だけでは埋もれるので、疲れた人をほめる・ねぎらう「全肯定」に絞って差別化する。
絵柄: 毛並みのギザギザ輪郭、やわらかい茶色の細い線、やさしい丸ゴシック。
"""

STYLE = dict(
    LINE="#8c6b5d", SW=4, FUR="#fffaf4", PATCH="#f6d2b0", INNER="#ffc9d3", CHEEK="#ffa9bb",
    FLUFFY=True, CHEEK_OP=1.3, FONT="Zen Maru Gothic", TEXT_WEIGHT=700, TEXT_LINE="#8c6b5d",
)

PINK, BLUE, GREEN, ORANGE, PURPLE, BROWN = (
    "#f07c9b", "#6fa8dc", "#5fb98a", "#f3a35c", "#a58bd6", "#c08a6a")

MAIN = {"eyes": "happy", "mouth": "w", "arms": "hold", "item": "heart", "fx": ["hearts"]}

STICKERS = [
    # --- ねぎらい・全肯定（いちばん売りたいところ）
    dict(text="おつかれさま", color=BROWN, eyes="happy", mouth="w", arms="hold", item="tea", fx=["hearts"]),
    dict(text="えらい！", color=ORANGE, eyes="bead", mouth="open", arms="banzai", fx=["sparkles"]),
    dict(text="がんばったね", color=PINK, eyes="closed", mouth="w", arms="hold", item="heart", blush="strong"),
    dict(text="生きてるだけで\nえらい", color=ORANGE, eyes="happy", mouth="w", arms="down", fx=["glow"]),
    dict(text="むりしないでね", color=BLUE, eyes="worried", mouth="small", arms="cheek", fx=["hearts"]),
    dict(text="よしよし", color=PINK, eyes="happy", mouth="w", arms="wave", fx=["motion", "hearts"]),
    dict(text="ぎゅー", color=PINK, eyes="closed", mouth="w", arms="together", blush="strong", fx=["hearts"]),
    dict(text="だいじょうぶだよ", color=GREEN, eyes="happy", mouth="w", arms="cheek", fx=["sparkles"]),
    dict(text="あなたの\n味方だよ", color=PURPLE, eyes="bead", mouth="open", arms="thumb", fx=["sparkles"]),
    dict(text="ゆっくり\n休んでね", color=BLUE, eyes="closed", mouth="small", arms="hold", item="tea"),
    # --- あいさつ
    dict(text="おはよ", color=ORANGE, eyes="bead", mouth="open", arms="wave", fx=["sun"]),
    dict(text="おやすみ", color=PURPLE, eyes="closed", mouth="small", arms="down", item="pillow", hat="nightcap", fx=["zzz", "moon"]),
    dict(text="ありがと♡", color=PINK, eyes="happy", mouth="open", arms="hold", item="heart"),
    dict(text="いってらっしゃい", color=ORANGE, eyes="happy", mouth="open", arms="wave", fx=["hearts"]),
    dict(text="おかえり〜", color=PINK, eyes="happy", mouth="open", arms="banzai", fx=["hearts"]),
    dict(text="りょうかい〜", color=GREEN, eyes="bead", mouth="w", arms="salute"),
    dict(text="いいよ〜", color=GREEN, eyes="happy", mouth="open", arms="wave", fx=["sparkles"]),
    dict(text="ごめんね", color=BLUE, eyes="sorry", mouth="wavy", arms="together"),
    dict(text="いつも\nありがとう", color=PINK, eyes="happy", mouth="w", arms="hold", item="flower", blush="strong"),
    dict(text="だいすき", color=PINK, eyes="closed", mouth="w", arms="hold", item="heart", blush="strong", fx=["hearts"]),
    # --- ふわふわ・ごろごろ
    dict(text="ふわぁ…", color=PURPLE, eyes="closed", mouth="o", arms="down", fx=["sparkles"]),
    dict(text="ごろーん", color=BROWN, eyes="happy", mouth="w", arms="down", rot=-80, fx=["note"]),
    dict(text="すやぁ", color=PURPLE, eyes="closed", mouth="small", arms="down", item="futon", hat="nightcap", fx=["zzz", "moon"]),
    dict(text="ねむねむ", color=PURPLE, eyes="half", mouth="small", arms="down", item="pillow"),
    dict(text="のんびりいこう", color=GREEN, eyes="closed", mouth="w", arms="down", tilt=-8, fx=["note"]),
    dict(text="まったり", color=BROWN, eyes="closed", mouth="w", arms="hold", item="cup", tilt=6),
    dict(text="ほっ", color=GREEN, eyes="closed", mouth="w", arms="hold", item="tea", fx=["sparkles"]),
    dict(text="あったかいね", color=ORANGE, eyes="happy", mouth="w", arms="hold", item="tea", wear="scarf"),
    # --- 気持ち
    dict(text="うれしいな", color=PINK, eyes="happy", mouth="open", arms="cheek", blush="strong", fx=["hearts"]),
    dict(text="たのしみ〜", color=ORANGE, eyes="sparkle", mouth="open", arms="cheek", fx=["note", "sparkles"]),
    dict(text="あいたいな", color=PINK, eyes="teary", mouth="small", arms="together", blush="strong", fx=["hearts"]),
    dict(text="まってるね", color=BLUE, eyes="bead", mouth="w", arms="down", fx=["hearts"]),
    dict(text="わかるよ〜", color=GREEN, eyes="closed", mouth="w", arms="together", head_dy=8),
    dict(text="すごいね！", color=ORANGE, eyes="sparkle", mouth="open", arms="banzai", fx=["sparkles"]),
    dict(text="てんさい！", color=PURPLE, eyes="sparkle", mouth="open", arms="thumb", fx=["glow"]),
    dict(text="おめでとう", color=PINK, eyes="happy", mouth="open", arms="banzai", fx=["confetti"]),
    dict(text="なでなで", color=PINK, eyes="happy", mouth="w", arms="wave", blush="strong", fx=["motion"]),
    dict(text="いいこいいこ", color=ORANGE, eyes="happy", mouth="w", arms="cheek", fx=["sparkles"]),
    dict(text="おいしいね", color=ORANGE, eyes="happy", mouth="open", arms="hold", item="dango", blush="strong"),
    dict(text="ずっと\n味方だからね", color=PURPLE, eyes="happy", mouth="w", arms="hold", item="heart", fx=["sparkles"]),
]
