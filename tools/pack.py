"""
アプリのパッケージを配布用の zip にし、カタログ（v1/store.json）のそのアプリの版・URL・SHA-256 を書き換える。

  python tools/pack.py <パッケージのフォルダ> [--out dist]

zip の中身はパッケージのフォルダの中身そのもの（package.json が zip の直下。VPM と同じ形）。
できた zip は GitHub の Releases に「<パッケージ名>-<版>」のタグで上げる（URL はそれを前提に書く）。
"""
import argparse, hashlib, json, os, sys, zipfile
from collections import OrderedDict

REPO = "thesilver0913/ulexite-store"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG = os.path.join(ROOT, "v1", "store.json")


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
    name, version, zip_path, sha = pack(a.package, a.out)
    catalog = json.load(open(CATALOG, encoding="utf-8"), object_pairs_hook=OrderedDict)
    entry = next((e for e in catalog["apps"] if e["package"] == name), None)
    if entry is None:
        sys.exit(f"カタログに {name} がありません。先に v1/store.json に項目を足してください")
    entry["version"] = version
    entry["url"] = f"https://github.com/{REPO}/releases/download/{name}-{version}/{os.path.basename(zip_path)}"
    entry["sha256"] = sha
    json.dump(catalog, open(CATALOG, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=2)
    print(zip_path)
    print(sha)
    print(f"gh release create {name}-{version} \"{zip_path}\" --repo {REPO} --title \"{name} {version}\" --notes \"\"")


if __name__ == "__main__":
    main()
