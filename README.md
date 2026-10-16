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

## 掲載の流れ

1. アプリのパッケージを用意する（Ulexite の `UlexiteAppBuilder` で画面を作る形）
2. `python tools/pack.py <パッケージのフォルダ>` で zip を作り、カタログの版・URL・SHA-256 を書き換える
3. 表示されたコマンドで Releases に zip を上げ、カタログの変更をコミットする

他の作者のアプリは、掲載前にこちらで審査し、審査した版を固定で載せます。更新のたびに審査し直します。
