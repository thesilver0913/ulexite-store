"""
アプリのパッケージを配布用の zip にし、カタログ（v1/store.json）のそのアプリの項目を書き換える。
バージョン・URL・SHA-256 に加えて、アプリのマニフェスト（パッケージ直下の ulexite-app.json）から名前・作者・必要な OS と App Services のバージョン・
対応する端末・リリースノート・カテゴリを写す（二重に書かない）。

  python tools/pack.py <パッケージのフォルダ> [--out dist]

zip の中身はパッケージのフォルダの中身そのもの（package.json が zip の直下。VPM と同じ形）。
できた zip は GitHub の Releases に「<パッケージ名>-<バージョン>」のタグで上げる（URL はそれを前提に書く）。
"""
import argparse, hashlib, json, os, re, shutil, sys, zipfile
from collections import OrderedDict

REPO = "thesilver0913/ulexite-store"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG = os.path.join(ROOT, "v1", "store.json")
ICONS = os.path.join(ROOT, "v1", "icons")
ICON_BASE = "https://thesilver0913.github.io/ulexite-store/v1/icons/"


def check_compiled(src):
    """U# のプログラムアセット（.asset）がスクリプト（.cs）より古ければ止める。Unity でコンパイルし直す前に固めると、
    新しいフィールドの一覧が入らず、入れた先でアプリが止まる。"""
    stale = []
    for base, dirs, files in os.walk(src):
        for f in files:
            if f.endswith(".cs") and os.path.exists(os.path.join(base, f[:-3] + ".asset")):
                if os.path.getmtime(os.path.join(base, f)) > os.path.getmtime(os.path.join(base, f[:-3] + ".asset")):
                    stale.append(os.path.relpath(os.path.join(base, f), src))
    if stale:
        sys.exit("U# のプログラムアセットが古いままです（Unity でコンパイルしてから固めてください）：" + ", ".join(stale))


def load_certificate(src, meta):
    """アプリのマニフェストを読み、package.json と食い違っていたら止める（package.json が正）。"""
    path = os.path.join(src, "ulexite-app.json")
    if not os.path.exists(path):
        sys.exit("ulexite-app.json（アプリのマニフェスト）がありません")
    cert = json.load(open(path, encoding="utf-8"))
    if cert.get("version") != meta["version"]:
        sys.exit(f"ulexite-app.json の version（{cert.get('version')}）が package.json（{meta['version']}）と違います")
    if not re.match(r"^[a-z0-9][a-z0-9-]{0,31}$", cert.get("id") or ""):
        sys.exit(f"ulexite-app.json の id の形が違います（{cert.get('id')}）")
    if "tv" not in (cert.get("profiles") or []):
        print("注意：profiles に tv がないので、テレビには組み込まれません")
    return cert


def pack(src, out_dir):
    meta = json.load(open(os.path.join(src, "package.json"), encoding="utf-8"))
    name, version = meta["name"], meta["version"]
    os.makedirs(out_dir, exist_ok=True)
    zip_path = os.path.join(out_dir, f"{name}-{version}.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for base, dirs, files in os.walk(src):
            dirs[:] = sorted(d for d in dirs if not d.startswith("."))
            for f in sorted(files):
                if f.startswith("."):
                    continue
                full = os.path.join(base, f)
                arc = os.path.relpath(full, src).replace(os.sep, "/")
                info = zipfile.ZipInfo(arc, date_time=(2020, 1, 1, 0, 0, 0))  # 同じ中身なら同じ zip（SHA-256）になるように
                info.compress_type = zipfile.ZIP_DEFLATED
                z.writestr(info, open(full, "rb").read())
    sha = hashlib.sha256(open(zip_path, "rb").read()).hexdigest()
    return name, version, zip_path, sha


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("package")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist"))
    a = ap.parse_args()
    check_compiled(a.package)
    cert = load_certificate(a.package, json.load(open(os.path.join(a.package, "package.json"), encoding="utf-8")))
    name, version, zip_path, sha = pack(a.package, a.out)
    catalog = json.load(open(CATALOG, encoding="utf-8"), object_pairs_hook=OrderedDict)
    entry = next((e for e in catalog["apps"] if e["package"] == name), None)
    if entry is None:
        sys.exit(f"カタログに {name} がありません。先に v1/store.json に項目を足してください")
    if entry["id"] != cert["id"]:
        sys.exit(f"カタログの id（{entry['id']}）と ulexite-app.json の id（{cert['id']}）が違います")
    world = (cert.get("runtimes") or {}).get("world") or {}
    entry["name"] = cert["name"]
    if (cert.get("publisher") or {}).get("name"):
        entry["author"] = cert["publisher"]["name"]
    entry["os"] = world.get("os", 1)
    entry["appServices"] = world.get("appServices", 1)
    entry["profiles"] = cert.get("profiles", [])
    if cert.get("releaseNotes"):
        entry["releaseNotes"] = cert["releaseNotes"]
    if cert.get("category"):
        entry["category"] = cert["category"]
    if cert.get("pricing"):
        entry["pricing"] = cert["pricing"]  # 有料アプリ：販売元と購入ページ（Ulexite はお金を扱わない）
    entry["version"] = version
    entry["url"] = f"https://github.com/{REPO}/releases/download/{name}-{version}/{os.path.basename(zip_path)}"
    entry["sha256"] = sha
    # アプリのタイルの絵（白い線画・透明の背景）を v1/icons/<id>.png に置き、カタログに iconUrl を入れる
    # （公式サイトのアプリカタログが Web で出すため。本体のストアは icon の名前を使う）
    icon_src = os.path.join(a.package, "Textures", "icon_512.png")
    if os.path.exists(icon_src):
        os.makedirs(ICONS, exist_ok=True)
        shutil.copyfile(icon_src, os.path.join(ICONS, cert["id"] + ".png"))
        entry["iconUrl"] = ICON_BASE + cert["id"] + ".png"
    else:
        print(f"注意：{icon_src} が無いので、アイコンは書き出していません")
    json.dump(catalog, open(CATALOG, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=2)
    print(zip_path)
    print(sha)
    print(f"gh release create {name}-{version} \"{zip_path}\" --repo {REPO} --title \"{name} {version}\" --notes \"\"")


if __name__ == "__main__":
    main()
