# ulexite-store

[Ulexite TV](https://thesilver0913.github.io/ulexite-catalog/)（VRChat ワールド向けのテレビ）のアプリストアのカタログと配布物です。

- **カタログ**：https://thesilver0913.github.io/ulexite-store/v1/store.json
- **配布物**：各アプリの zip は [Releases](https://github.com/thesilver0913/ulexite-store/releases)

Unity の「Ulexite 設定」ウィンドウのアプリストアがカタログを読み、掲載されたアプリだけを表示します。インストールするときは zip を落とし、カタログに書かれた SHA-256 と一致したときだけプロジェクトに入れます（審査した版以外は入りません）。

## カタログの形（v1）

| 項目 | 内容 |
| --- | --- |
| `version` | カタログの形の版（今は 1）。読む側は知らない項目を無視する |
| `apps[].id` | アプリ ID（英小文字・数字・ハイフン）。ワールドの中のインストール申請でもこの ID を使う |
| `apps[].package` | VPM のパッケージ名 |
| `apps[].official` | Ulexite 公式なら true |
| `apps[].author` | 作者名 |
| `apps[].name` / `summary` / `description` / `credits` | 言語ごとの文字（`ja`・`en`） |
| `apps[].color` / `icon` | タイルの色と、アイコンの名前 |
| `apps[].quest` | Quest 対応（`yes`・`no`・`check`） |
| `apps[].imageLoading` | 画像の読み込みの量の目安（`none`・`low`・`high`） |
| `apps[].minUlexite` | 必要な Ulexite TV の版 |
| `apps[].version` / `url` / `sha256` | 審査した版と、その zip の場所と SHA-256 |
| `apps[].kind` | 省略＝アプリ。`core` は TV 本体の項目（ストアの一覧には出さない。本体が対応するまで） |
| `apps[].defaultApps` | **TV の既定の組**（`kind: "core"` の項目だけ）。TV と一緒に入れたいアプリの `id` の並び |

### TV の既定の組（`defaultApps`）

- カタログの **TV の項目**（`id: "tv"`・`kind: "core"`・`package: "vrc.ulexite.tv"`）に `defaultApps` を書く。いまは `["clock"]`（天気がカタログに入ったら足す）
- **TV はストアから入れません**（`url`・`sha256` を書かない。VCC のリスティングから入れる）。この項目は既定の組を配るためだけのもの
- 本体は、この項目の `defaultApps` を見て「まだ入っていないアプリ」を入れる（本体の実装待ち。CHANGES 2026-10-22 23時55分）
- `pack.py` はカタログを読み直して該当のアプリの項目だけを書き換えるので、`tv` の項目と `defaultApps` は消えません

## 製品の紹介（v1/products/）

Ulexite Store の製品の横に置く小さな画面（製品紹介アプリ）が読む JSON です。アプリのパッケージ（`vrc.ulexite.app.productintro`）の `Data/products/<id>.json` と同じものを置いています。

- `v1/products/tv.json`：Ulexite（テレビ本体）の紹介。`product` に名前・ひとこと・価格の行・タブ3つ・特長・仕様・くらべる・入手方法（`how.url` と QR コードの元）
- 入手先の URL（BOOTH／VCC）が決まったら、`product.how.url` を書き換えて、アプリの `Textures/qr.png` も差し替える（アプリ側は作り直す）
- 形の版は `version`（今は 1）。読む側は知らない項目を無視する

## 掲載の流れ

1. アプリのパッケージを用意する（Ulexite の `UlexiteAppBuilder` で画面を作る形）
2. `python tools/pack.py <パッケージのフォルダ>` で zip を作り、カタログの版・URL・SHA-256 を書き換える
3. 表示されたコマンドで Releases に zip を上げ、カタログの変更をコミットする

他の作者のアプリは、掲載前にこちらで審査し、審査した版を固定で載せます。更新のたびに審査し直します。
