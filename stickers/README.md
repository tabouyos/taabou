# しろねこ LINEスタンプ

| セット | 内容 | 状態 |
|---|---|---|
| 第1弾 `keigo` | 敬語しろねこ 40個 | 審査待ち（申請済み） |
| 第2弾 `kisetsu` | 敬語しろねこ 季節のごあいさつ 40個（手がぷっくり丸い新デザイン） | 申請準備中 |
| 第3弾 `deka` | しろねこのデカ文字 40個（40〜60代向け・普段使い） | 申請準備中 |
| 第4弾 `fuwafuwa` | ふわふわしろねこ 全肯定 40個（癒し系） | 申請準備中 |
| 第5弾 `shuru` | 真顔しろねこ シュール敬語 40個 | 申請準備中 |
| 別シリーズ `mofuneko` | もふもふねこ 毎日のきもち 40個（持ち込みの一覧画像から作成） | 申請準備中 |

![第1弾](output/keigo/preview.png)
![第2弾](output/kisetsu/preview.png)
![第3弾](output/deka/preview.png)
![第4弾](output/fuwafuwa/preview.png)
![第5弾](output/shuru/preview.png)
![もふもふねこ](output/mofuneko/preview.png)

> `output/keigo/` は申請した時点の画像をそのまま残している。今の generate.py で作り直すと、腕が第2弾と同じ丸い手になる。

## キャラクター
- **白くてぽっちゃりしたねこ**に、**赤いリボン**と**片耳のトラ模様**の2つの目印を付けた
- 一覧の小さなサムネイルでも「あのねこ」と分かるようにしている

## 売れるための設計
| ポイント | 内容 |
|---|---|
| ターゲット | 30〜50代。職場・目上の人・ママ友など、敬語を使う相手とのやりとり |
| セリフ | 使う頻度が高い順に並べた（01〜10が毎日使うあいさつ）。LINEでは先頭のスタンプが目立つ |
| 文字 | 太い丸ゴシック＋2重フチで、スマホの小さい画面やダークモードでも読める |
| 枚数 | 40個。「これ1つで足りる」と思ってもらえる |
| 絵柄 | 全40個でキャラの形を統一。LINEの審査でも、キャラがブレていないことが求められる |

## 販売ページ用の文案
- **タイトル（候補）**
  1. ていねい敬語しろねこ【毎日使える】
  2. 敬語でやさしく♪しろねこスタンプ
  3. 大人のための丁寧しろねこ
- **説明文**：リボンがチャームポイントのしろねこが、ていねいな敬語であいさつ。職場でも目上の方にも使いやすい、毎日使える40種類です。
- **価格**：¥190（日本での最低価格）

## LINE Creators Market への申請手順
1. https://creator.line.me/ja/ に登録する（無料・個人でも可）
2. 「新規登録」→「スタンプ」を選び、タイトル・説明文・販売価格を入力する
3. `output/` 内の次のファイルをZIPにまとめてアップロードする
   - `01.png`〜`40.png`（370×320px、透過PNG）
   - `main.png`（240×240px）
   - `tab.png`（96×74px）
   - ※ `preview.png` は確認用なので含めない
4. 「リクエスト」を送信すると審査が始まる（数日〜）
5. 承認されたら「リリース」を押して販売開始

## 作り直し方
```bash
pip install cairosvg pillow
# fonts/ のフォント（M PLUS Rounded 1c / Zen Maru Gothic / Zen Kaku Gothic New, すべて SIL OFL）をOSにインストールしておく
python stickers/generate.py keigo     # 第1弾
python stickers/generate.py kisetsu   # 第2弾
python stickers/generate.py deka      # 第3弾（LAYOUT="deka" で文字を大きく配置）
python stickers/generate.py fuwafuwa  # 第4弾（STYLE で毛並み・やわらかい線に切り替え）
python stickers/generate.py shuru     # 第5弾（STYLE で白黒・真顔に切り替え）
```
- セリフ・表情・ポーズを変えたいときは `sets/<セット名>.py` を編集する。新しいセットも同じ形でファイルを足せば作れる
- 絵はすべてコード（SVG）で描いている。ただし描画プログラムとデザインはAI（Claude）が作ったので、LINEの申請では「AIを使用しています」を選ぶ
- フォントはすべてSIL Open Font Licenseのため、商用スタンプに利用できる

## 第2弾 販売ページ用の文案
- **タイトル（日本語）**：ていねい敬語しろねこ 季節のごあいさつ
- **タイトル（英語）**：Polite White Cat: Seasonal Greetings
- **説明文（日本語）**：リボンのしろねこが、季節のごあいさつを丁寧な敬語で。ハロウィン・クリスマス・お正月から春夏まで、一年中使える40種類です。
- **説明文（英語）**：A chubby white cat with a red ribbon sends polite seasonal greetings in Japanese, from Halloween and New Year to spring and summer. 40 stickers for all year.

## 第3弾 販売ページ用の文案
- **タイトル（日本語）**：しろねこのデカ文字【毎日使える】
- **タイトル（英語）**：Big Text White Cat: Everyday Words
- **説明文（日本語）**：大きな文字で読みやすい！リボンのしろねこが、家族や友だちとの毎日のやりとりにぴったりな40種類。了解・ありがとう・今から帰るなど。
- **説明文（英語）**：Big, easy-to-read words with a chubby white cat. 40 everyday stickers for family and friends: OK, thank you, on my way home and more.
- メイン画像は「了解！」のスタンプ（デカ文字だと一目で分かるように）

## 第4弾・第5弾のリサーチ結果（2026年10月）
- 「かわいい猫」「ゆるい犬」だけでは飽和していて埋もれる → 使う場面やテーマを絞って差別化する
- 癒し系は「ふわふわ・ぽてっと・パステル」が安定して人気（シマエナガ・うさぎ・こぐま など）
- シュール系は「白黒・無表情・脱力・シンプルな線」が人気。「シュールだけどおしゃれ」が求められている
- シンプルなデザインが男女とも選ばれやすく、毎日使える定番の言葉が結局いちばん使われる
- 人気キャラのシリーズ2弾・3弾は既存ファンが買ってくれる

## 第4弾 販売ページ用の文案
- **タイトル（日本語）**：ふわふわしろねこ 全肯定
- **タイトル（英語）**：Fluffy White Cat: You're Doing Great
- **説明文（日本語）**：もふもふのしろねこが、がんばるあなたをやさしく全肯定。おつかれさま・えらい・むりしないでね。毎日に癒しを届ける40種類です。
- **説明文（英語）**：A fluffy white cat gently cheers you on: good job, you're amazing, take it easy. 40 soothing stickers for every day.

## 第5弾 販売ページ用の文案
- **タイトル（日本語）**：真顔しろねこ シュール敬語
- **タイトル（英語）**：Deadpan White Cat: Polite and Surreal
- **説明文（日本語）**：真顔のしろねこが、丁寧な敬語のままとけたり浮いたり食パンになったり。職場でも使えるシュールな40種類です。
- **説明文（英語）**：A deadpan white cat speaks polite Japanese while melting, floating or turning into toast. 40 surreal stickers you can even use at work.

## もふもふねこ（一覧画像から作るセット）
1枚の一覧画像（白背景にスタンプが格子状に並んだもの）から、そのまま申請できる一式を作る。

```bash
pip install pillow numpy scipy
python stickers/from_sheet.py stickers/source/mofuneko_sheet.webp mofuneko --drop 29,40 --main 2
```
- 白い余白から格子を自動で切り分け、外周の白い背景を透明にする。毛が真っ白でも欠けないよう、輪郭のすき間をふさいでから内側を残している
- `--drop 29,40`：元画像の29「お疲れさまです」（カップのロゴが実在チェーン店に似ていて商標リスク）と、40「また連絡するね！」（24「あとで連絡するね！」と重複）を外して40個にしている
- タブ画像は文字を除いて猫だけにしている
- 元画像は1枚1254px（1コマ約190px）なので約1.8倍に拡大している。より大きい元画像があれば、同じコマンドでくっきり作り直せる
- **販売ページ用の文案**
  - タイトル（日本語）：もふもふねこ 毎日のきもち ／（英語）：Fluffy Kitty: Everyday Feelings
  - 説明文（日本語）：もふもふのねこが毎日のきもちを届けます。ありがとう・了解・おつかれさま・大好きなど、家族や友だちと使いやすい40種類。
  - 説明文（英語）：A super fluffy kitty shares everyday feelings: thank you, OK, good job, love you and more. 40 stickers for family and friends.

## 次の展開案（シリーズ化すると売上が伸びる）
- 動くスタンプ版（単価が上がる）
- ナース・医療職版（職場ネタ、競合が少ない）
