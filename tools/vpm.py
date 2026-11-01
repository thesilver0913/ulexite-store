"""パッケージを zip にして、VCC のリスティング（`index.json`）に載せる。

  python tools/vpm.py <パッケージのフォルダ> [--out dist]

`pack.py` と同じ形で zip を作り（同じ中身なら同じ zip）、Releases に上げるコマンドを出して、
`index.json` のそのパッケージの版を書き換える（zip の URL と SHA-256 を含む）。
アプリ（`ulexite-app.json` がある）と、テレビ本体（無い。`package.json` だけ）の両方に使える。
"""
import argparse, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pack import ROOT, REPO, check_compiled, pack  # 同じフォルダの pack.py を使う

INDEX = os.path.join(ROOT, "index.json")
BASE = f"https://github.com/{REPO}/releases/download"

TOP = {
    "name": "Ulexite",
    "id": "io.github.thesilver0913.ulexite",
    "url": "https://thesilver0913.github.io/ulexite-store/index.json",
    "author": "葛城ひなた",
    "description": "VRChat ワールド向けのテレビ「Ulexite TV」と、公式アプリのパッケージです（ベータ版）。",
    "packages": {},
}


def load_index():
    if os.path.exists(INDEX):
        return json.load(open(INDEX, encoding="utf-8"), object_pairs_hook=dict)
    return json.loads(json.dumps(TOP))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("package")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist"))
    a = ap.parse_args()
    meta = json.load(open(os.path.join(a.package, "package.json"), encoding="utf-8"))
    name, version = meta["name"], meta["version"]

    cert = None
    cert_path = os.path.join(a.package, "ulexite-app.json")
    if os.path.exists(cert_path):
        cert = json.load(open(cert_path, encoding="utf-8"))
        if cert.get("version") != version:
            sys.exit(f"ulexite-app.json の version（{cert.get('version')}）が package.json（{version}）と違います")

    check_compiled(a.package)
    name, version, zip_path, sha = pack(a.package, a.out)
    tag = f"{name}-{version}"
    url = f"{BASE}/{tag}/{os.path.basename(zip_path)}"

    index = load_index()
    packages = index.setdefault("packages", {})
    entry = packages.setdefault(name, {"versions": {}})
    entry["versions"][version] = {
        "name": name,
        "displayName": meta.get("displayName") or name,
        "version": version,
        "unity": meta.get("unity", "2022.3"),
        "description": meta.get("description", ""),
        "author": meta.get("author", {"name": "葛城ひなた"}),
        "vpmDependencies": meta.get("vpmDependencies", {}),
        "url": url,
        "zipSHA256": sha,
        "hideInEditor": False,
    }
    json.dump(index, open(INDEX, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=2)
    print(zip_path)
    print(sha)
    print(f'gh release create {tag} "{zip_path}" --repo {REPO} --title "{name} {version}" --notes ""')


if __name__ == "__main__":
    main()
