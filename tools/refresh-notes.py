"""カタログ（`v1/store.json`）の `releaseNotes` を、アプリのマニフェスト（`ulexite-app.json`）から写し直す。

  python tools/refresh-notes.py [--check]

`pack.py` は zip を作り直す（Release の差し替えが要る）が、リリースノートだけを直すときは
これでよい（版を上げずに、カタログの文だけ新しくする）。`--check` を付けると、書き換えずに
「どれが違うか」だけを出す。
"""
import argparse, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG = os.path.join(ROOT, "v1", "store.json")
PACKAGES = os.path.join(ROOT, "..", "Packages")

TOP = {
    "name": "Ulexite",
    "id": "io.github.thesilver0913.ulexite",
    "url": "https://thesilver0913.github.io/ulexite-store/index.json",
    "author": "葛城ひなた",
    "description": "VRChat ワールド向けのテレビ「Ulexite TV」と、公式アプリのパッケージです（ベータ版）。",
    "packages": {},
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="書き換えずに、違うものだけ出す")
    a = ap.parse_args()
    catalog = json.load(open(CATALOG, encoding="utf-8"), object_pairs_hook=dict) if os.path.exists(CATALOG) else None
    if catalog is None:
        sys.exit("v1/store.json がありません")

    changed = []
    for entry in catalog.get("apps", []):
        package = entry.get("package")
        if not package:
            continue
        path = os.path.join(PACKAGES, package, "ulexite-app.json")
        if not os.path.exists(path):
            continue
        manifest = json.load(open(path, encoding="utf-8"))
        notes = manifest.get("releaseNotes")
        if not notes:
            continue
        if entry.get("releaseNotes") != notes:
            changed.append((entry.get("id", package), notes))
            entry["releaseNotes"] = notes

    if not changed:
        print("変わりません（カタログはマニフェストと同じ）")
        return

    for ident, notes in changed:
        first = (notes.get("ja") or "").split("\n")[0]
        print(f"直す: {ident} … {first[:60]}")

    if a.check:
        print(f"{len(changed)} 件が違います（--check なので書き換えていません）")
        return

    json.dump(catalog, open(CATALOG, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=2)
    print(f"{len(changed)} 件を書き換えました")


if __name__ == "__main__":
    main()
