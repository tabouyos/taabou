"""第5弾「真顔しろねこ シュール敬語」40個

リサーチより: シュール系は「白黒・無表情・脱力・シンプルな線」が人気で、
「シュールだけどおしゃれ」なものが求められている。
真顔のねこが、丁寧な敬語のまま変なこと（とける・浮く・増える・食パンになる）をするギャップで笑わせる。
絵柄: 黒い線・白黒で、色は赤いリボンと小物だけ。ほっぺ無し。
"""

STYLE = dict(
    LINE="#222222", SW=4.5, FUR="#ffffff", PATCH="#d6d6d6", INNER="#ececec",
    CHEEK_OP=0, FONT="Zen Kaku Gothic New", TEXT_WEIGHT=700, TEXT_LINE="#222222",
)

INK, RED = "#222222", "#e53935"

MAIN = {"eyes": "tiny", "mouth": "flat", "arms": "down", "item": "bread"}

T = dict(eyes="tiny", mouth="flat", color=INK)   # 基本の真顔


def S(text, **kw):
    return {**T, "text": text, **kw}


STICKERS = [
    # --- 真顔の返事
    S("了解です", arms="down"),
    S("承知しました", arms="together", head_dy=14),
    S("お疲れ様です", eyes="half", arms="down", rot=-90, text_pos="bottom"),
    S("確認します", arms="wave", item="magnifier"),
    S("ご査収ください", arms="hold", item="fish"),
    S("はい", arms="salute"),
    S("いいえ", arms="point"),
    S("検討します", arms="hold", item="memo"),
    S("前向きに\n検討します", arms="hold", item="memo", fx=["sparkles"]),
    S("以上です", arms="salute"),
    # --- シュールな状態報告
    S("食パンです", arms="down", item="bread"),
    S("浮いてます", arms="down", lift=46),
    S("増えました", arms="down", clones=3),
    S("回ってます", arms="banzai", rot=30, fx=["spin"]),
    S("光ってます", arms="banzai", fx=["glow"]),
    S("充電中です", eyes="half", arms="down", fx=["battery"]),
    S("とけました", eyes="half", arms="down", squash=0.35, puddle=True, text_pos="bottom"),
    S("現実逃避中", eyes="closed", arms="down", lift=36, fx=["clouds"]),
    S("宇宙を\n感じています", eyes="stare", mouth="o", arms="down", fx=["space"]),
    S("そっとしておいて\nください", arms="down", item="box"),
    # --- 真顔の気持ち
    S("無", eyes="flat", arms="down"),
    S("え", eyes="stare", mouth="o", arms="down"),
    S("圧", eyes="stare", arms="down", color=RED),
    S("なるほど\n（わかってない）", arms="chin", fx=["dots"]),
    S("考えるのを\nやめました", eyes="half", arms="down", fx=["gloom"]),
    S("見守っています", eyes="stare", arms="together"),
    S("遠くから\n応援しています", arms="wave", lift=20, fx=["sparkles"]),
    S("静かにして\nください", arms="mouth"),
    S("待機しています", arms="down", fx=["clock"]),
    S("様子を見ます", eyes="stare", arms="wave", item="magnifier"),
    # --- 真顔のあいさつ
    S("ありがとう\nございます", arms="together", fx=["confetti"]),
    S("おめでとう\nございます", arms="hold", item="cake", fx=["confetti"]),
    S("すみません", arms="together", head_dy=10, fx=["sweat"]),
    S("よろしく\nお願いします", arms="together", head_dy=14),
    S("帰ります", arms="hold", item="bag", fx=["wind"]),
    S("寝ます", eyes="closed", arms="down", rot=-90, fx=["zzz"], text_pos="bottom"),
    S("布団から\n出られません", arms="down", item="futon"),
    S("本日の営業は\n終了しました", eyes="closed", arms="together", head_dy=12),
    S("失礼します", arms="wave", fx=["wind"]),
    S("また明日", arms="wave", fx=["moon"]),
]
