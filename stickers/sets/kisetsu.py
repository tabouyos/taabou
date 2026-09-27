"""第2弾「敬語しろねこ 季節のごあいさつ」40個

10月発売を想定し、これから使う順（ハロウィン→秋→冬→年末年始→春→夏）に並べ、
最後に一年中使える季節の気づかいを置いている。
パラメータの意味は sets/keigo.py の説明と同じ。追加分:
    hat : santa / witch / straw / nightcap / headband
    wear: scarf        mask=True でマスク
    item: pumpkin / choco / gift / cake / diploma / dango / onigiri / maple / watermelon /
          uchiwa(arms=wave) / book / kagami / umbrella(arms=umbrella) / icedrink / carnation
    fx  : sakura / snow / leaves / rain / fireworks / shiver / xmas_star / sunrise
"""

CORAL, BLUE, GREEN, ORANGE, PURPLE, PINK, NAVY, RED, BROWN = (
    "#ff6f61", "#3d8bd9", "#2fa36b", "#f28c28", "#8b5cc7", "#ec5b93", "#44548f", "#e53935", "#a0522d")

MAIN = {"eyes": "happy", "mouth": "open", "arms": "wave", "fx": ["sakura", "leaves"]}

STICKERS = [
    # --- 秋・ハロウィン
    dict(text="ハッピーハロウィン", color=PURPLE, eyes="wink", mouth="open", arms="hold", item="pumpkin", hat="witch", fx=["sparkles"]),
    dict(text="秋ですね", color=ORANGE, eyes="happy", mouth="w", arms="cheek", fx=["leaves"]),
    dict(text="紅葉が\nきれいですね", color=RED, eyes="sparkle", mouth="open", arms="hold", item="maple", fx=["leaves"]),
    dict(text="食欲の秋です", color=ORANGE, eyes="happy", mouth="open", arms="hold", item="onigiri", blush="strong", fx=["sparkles"]),
    dict(text="読書の秋です", color=BROWN, eyes="closed", mouth="small", arms="hold", item="book", fx=["leaves"]),
    dict(text="お月見\nしましょう", color=NAVY, eyes="happy", mouth="w", arms="hold", item="dango", fx=["moon"]),
    # --- 冬・年末
    dict(text="寒くなって\nきましたね", color=BLUE, eyes="worried", mouth="wavy", arms="together", wear="scarf", fx=["shiver"]),
    dict(text="あったかくして\nくださいね", color=CORAL, eyes="happy", mouth="w", arms="hold", item="tea", wear="scarf", fx=["hearts"]),
    dict(text="雪ですね！", color=BLUE, eyes="sparkle", mouth="open", arms="banzai", wear="scarf", fx=["snow"]),
    dict(text="メリークリスマス", color=RED, eyes="happy", mouth="open", arms="hold", item="gift", hat="santa", fx=["xmas_star", "snow"]),
    dict(text="大掃除\nがんばります", color=GREEN, eyes="determined", mouth="open", arms="fist", hat="headband", fx=["sparkles"]),
    dict(text="今年も\nお世話になりました", color=NAVY, eyes="closed", mouth="w", arms="together", head_dy=12, fx=["motion"]),
    dict(text="よいお年を", color=RED, eyes="happy", mouth="open", arms="wave", wear="scarf", fx=["snow"]),
    # --- お正月・冬
    dict(text="あけまして\nおめでとうございます", color=RED, eyes="happy", mouth="open", arms="banzai", fx=["sunrise", "confetti"]),
    dict(text="今年もよろしく\nお願いします", color=RED, eyes="closed", mouth="w", arms="together", head_dy=14, fx=["motion", "sparkles"]),
    dict(text="謹賀新年", color=RED, eyes="happy", mouth="w", arms="hold", item="kagami", fx=["sparkles"]),
    dict(text="寒中お見舞い\n申し上げます", color=BLUE, eyes="closed", mouth="small", arms="together", head_dy=10, wear="scarf", fx=["snow"]),
    dict(text="ハッピー\nバレンタイン", color=PINK, eyes="happy", mouth="w", arms="hold", item="choco", blush="strong", fx=["hearts"]),
    # --- 春
    dict(text="春ですね", color=PINK, eyes="happy", mouth="open", arms="wave", fx=["sakura"]),
    dict(text="お花見\nしましょう", color=PINK, eyes="sparkle", mouth="open", arms="hold", item="dango", fx=["sakura"]),
    dict(text="ご卒業\nおめでとうございます", color=CORAL, eyes="happy", mouth="open", arms="hold", item="diploma", fx=["sakura", "confetti"]),
    dict(text="ご入学\nおめでとうございます", color=PINK, eyes="sparkle", mouth="open", arms="banzai", fx=["sakura"]),
    dict(text="新年度もよろしく\nお願いします", color=GREEN, eyes="closed", mouth="w", arms="together", head_dy=12, fx=["sakura"]),
    dict(text="花粉が\nつらいです…", color=GREEN, eyes="teary", arms="down", mask=True, fx=["sweat"]),
    dict(text="いつも\n感謝しています", color=RED, eyes="happy", mouth="w", arms="hold", item="carnation", blush="strong", fx=["hearts"]),
    # --- 梅雨・夏
    dict(text="雨ですね", color=BLUE, eyes="dot", mouth="small", arms="umbrella", item="umbrella", fx=["rain"], text_pos="bottom"),
    dict(text="夏ですね！", color=ORANGE, eyes="sparkle", mouth="open", arms="banzai", hat="straw", fx=["sun"]),
    dict(text="暑いですね…", color=CORAL, eyes="flat", mouth="open", arms="wave", item="uchiwa", fx=["sweat", "sun"]),
    dict(text="暑中お見舞い\n申し上げます", color=BLUE, eyes="happy", mouth="w", arms="hold", item="icedrink", hat="straw"),
    dict(text="熱中症に\nお気をつけて", color=BLUE, eyes="worried", mouth="small", arms="hold", item="icedrink", fx=["sweat"]),
    dict(text="花火が\nきれいですね", color=PURPLE, eyes="sparkle", mouth="open", arms="wave", item="uchiwa", fx=["fireworks"]),
    dict(text="残暑お見舞い\n申し上げます", color=GREEN, eyes="happy", mouth="open", arms="hold", item="watermelon", hat="straw"),
    dict(text="夏休み\n楽しんでください", color=ORANGE, eyes="happy", mouth="open", arms="wave", hat="straw", fx=["sun", "sparkles"]),
    # --- 一年中使える季節の気づかい
    dict(text="お誕生日\nおめでとうございます", color=PINK, eyes="happy", mouth="open", arms="hold", item="cake", fx=["confetti"]),
    dict(text="季節の変わり目\nご自愛ください", color=GREEN, eyes="worried", mouth="small", arms="hold", item="tea", fx=["leaves"]),
    dict(text="風邪ひかないで\nくださいね", color=BLUE, eyes="worried", mouth="small", arms="cheek", wear="scarf", fx=["hearts"]),
    dict(text="連休\n楽しんでください", color=CORAL, eyes="happy", mouth="open", arms="wave", fx=["sparkles"]),
    dict(text="帰省します", color=BLUE, eyes="dot", mouth="w", arms="hold", item="bag", fx=["wind"]),
    dict(text="おみやげです", color=ORANGE, eyes="happy", mouth="open", arms="hold", item="gift", blush="strong", fx=["sparkles"]),
    dict(text="季節のごあいさつ\n失礼します", color=NAVY, eyes="closed", mouth="small", arms="together", head_dy=12, fx=["sakura", "leaves"]),
]
