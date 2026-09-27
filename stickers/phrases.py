"""40枚のセリフ・表情・ポーズ定義

売れる順（使用頻度が高い順）に並べている。LINEでは01番が一覧の先頭に出る。

eyes : dot / sparkle / happy / closed / sorry / surprised / flat / sad / worried / determined / teary / wink
mouth: w / open / o / flat / wavy / small
arms : down / wave / banzai / together / cheek / thumb / salute / chin / hold / fist / mouth / point
item : heart / cup / bag / memo / flower / cracker / pillow / tea / hanky
fx   : sparkles / hearts / sweat / tears / zzz / motion / exclaim / question / bulb / gloom /
       circle / note / confetti / wind / clock / sun / moon
"""

CORAL, BLUE, GREEN, ORANGE, PURPLE, PINK, NAVY = (
    "#ff6f61", "#3d8bd9", "#2fa36b", "#f28c28", "#8b5cc7", "#ec5b93", "#44548f")

STICKERS = [
    # --- 毎日使うあいさつ
    dict(text="おはようございます", color=ORANGE, eyes="happy", mouth="open", arms="wave", fx=["sun"]),
    dict(text="お疲れさまです", color=BLUE, eyes="happy", mouth="w", arms="hold", item="cup", tilt=-6),
    dict(text="ありがとう\nございます", color=PINK, eyes="happy", mouth="open", arms="hold", item="heart", fx=["hearts"]),
    dict(text="了解です", color=CORAL, eyes="dot", mouth="open", arms="salute", fx=["sparkles"]),
    dict(text="承知しました", color=NAVY, eyes="closed", mouth="w", arms="together", head_dy=10, fx=["motion"]),
    dict(text="よろしく\nお願いします", color=GREEN, eyes="closed", mouth="small", arms="together", head_dy=14, tilt=0, fx=["motion"]),
    dict(text="すみません", color=BLUE, eyes="sorry", mouth="wavy", arms="together", fx=["sweat"]),
    dict(text="申し訳\nありません", color=NAVY, eyes="closed", mouth="wavy", arms="together", head_dy=16, fx=["gloom", "sweat"]),
    dict(text="おやすみなさい", color=PURPLE, eyes="closed", mouth="small", arms="down", item="pillow", hat="nightcap", fx=["zzz", "moon"], text_pos="bottom"),
    dict(text="お先に\n失礼します", color=BLUE, eyes="happy", mouth="w", arms="wave", item="bag", tilt=6),
    # --- 返事・リアクション
    dict(text="かしこまりました", color=NAVY, eyes="closed", mouth="w", arms="together", head_dy=12, fx=["motion"]),
    dict(text="大丈夫です", color=GREEN, eyes="happy", mouth="open", arms="thumb", fx=["circle"]),
    dict(text="確認します", color=BLUE, eyes="dot", mouth="small", arms="hold", item="memo"),
    dict(text="少々\nお待ちください", color=ORANGE, eyes="dot", mouth="o", arms="point", fx=["clock", "sweat"]),
    dict(text="助かります", color=PINK, eyes="teary", mouth="open", arms="together", blush="strong", fx=["sparkles"]),
    dict(text="さすがです！", color=CORAL, eyes="sparkle", mouth="open", arms="banzai", fx=["sparkles"]),
    dict(text="いいですね！", color=GREEN, eyes="happy", mouth="open", arms="thumb", fx=["sparkles"], text_pos="bottom"),
    dict(text="なるほど", color=ORANGE, eyes="dot", mouth="small", arms="chin", fx=["bulb"]),
    dict(text="はい！", color=CORAL, eyes="sparkle", mouth="open", arms="salute", fx=["exclaim"]),
    dict(text="お願いします", color=PINK, eyes="teary", mouth="small", arms="together", blush="strong"),
    # --- 気づかい
    dict(text="お気遣い\n感謝です", color=PINK, eyes="happy", mouth="w", arms="hold", item="flower", blush="strong"),
    dict(text="お大事に", color=GREEN, eyes="worried", mouth="small", arms="hold", item="tea"),
    dict(text="ご無理なさらず", color=GREEN, eyes="worried", mouth="small", arms="cheek", fx=["hearts"]),
    dict(text="お気をつけて", color=BLUE, eyes="happy", mouth="open", arms="wave", fx=["sparkles"]),
    dict(text="お疲れさまでした", color=PURPLE, eyes="closed", mouth="w", arms="together", head_dy=12, fx=["sparkles"]),
    dict(text="お手数\nおかけします", color=NAVY, eyes="closed", mouth="wavy", arms="together", head_dy=14, fx=["sweat"]),
    dict(text="恐縮です", color=NAVY, eyes="sorry", mouth="wavy", arms="together", blush="strong", fx=["sweat"]),
    dict(text="どういたしまして", color=ORANGE, eyes="happy", mouth="w", arms="cheek", blush="strong", fx=["note"]),
    dict(text="いえいえ", color=GREEN, eyes="happy", mouth="open", arms="wave", fx=["wind"]),
    dict(text="ごめんなさい", color=BLUE, eyes="teary", mouth="wavy", arms="mouth", fx=["tears"], text_pos="bottom"),
    # --- 予定・気持ち
    dict(text="いってらっしゃい", color=ORANGE, eyes="happy", mouth="open", arms="wave", fx=["hearts"]),
    dict(text="おかえりなさい", color=PINK, eyes="happy", mouth="open", arms="banzai", fx=["hearts"]),
    dict(text="今から帰ります", color=BLUE, eyes="dot", mouth="w", arms="hold", item="bag", fx=["wind"]),
    dict(text="遅れます…", color=NAVY, eyes="sad", mouth="wavy", arms="down", fx=["sweat", "clock"]),
    dict(text="楽しみです", color=CORAL, eyes="sparkle", mouth="open", arms="cheek", blush="strong", fx=["note", "sparkles"]),
    dict(text="おめでとう\nございます", color=CORAL, eyes="happy", mouth="open", arms="banzai", fx=["confetti"]),
    dict(text="がんばります！", color=CORAL, eyes="determined", mouth="open", arms="fist", hat="headband", fx=["exclaim"]),
    dict(text="うれしいです", color=PINK, eyes="happy", mouth="open", arms="cheek", blush="strong", fx=["hearts"]),
    dict(text="ほっとしました", color=GREEN, eyes="closed", mouth="w", arms="hold", item="tea", fx=["sparkles"]),
    dict(text="失礼します", color=NAVY, eyes="closed", mouth="small", arms="together", head_dy=12, fx=["motion"]),
]
