"""RIAJ ゴールドディスク認定の全作品を取得する (Phase 4)。

日本レコード協会の認定作品検索が内部で使っている JSON API を叩く。
検索ページ (https://www.riaj.or.jp/data/gd/search/) が読み込む
/f/data/js/app/gd_search.js から特定した:

    マスタ  https://www.riaj.or.jp/f/data/api/GdProducts/info.json
    一覧    https://www.riaj.or.jp/f/data/api/GdProducts/index.json?page=N

1 ページ 100 件・全 11,377 件 (1989 年 4 月以降)。
robots.txt は PDF のみ Disallow で、この API は対象外 (2026-08-08 確認)。

    python3 scripts/fetch_riaj_certifications.py

出力: data/raw/riaj_gd.jsonl (1 行 1 作品・git 管理外)
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

UA = "IdolSurvivalResearch/0.1 (academic survival analysis; contact via GitHub repo)"
API = "https://www.riaj.or.jp/f/data/api/GdProducts/index.json"
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
OUT_PATH = os.path.join(OUT_DIR, "riaj_gd.jsonl")


def api_get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
            code = getattr(e, "code", None)
            if (code is not None and code not in (429, 500, 502, 503, 504)) or attempt == 4:
                raise
            time.sleep(5 * (attempt + 1))
    raise RuntimeError("unreachable")


def flatten(rec):
    """API のネストを 1 階層に均す。"""
    p = rec.get("GdProduct", {})
    return {
        "year_month": p.get("year_month"),
        "title": p.get("name"),
        "artist": p.get("artist"),
        "sales_date": p.get("sales_date"),
        "seller": p.get("seller_name"),
        "hoyo": p.get("hoyo"),
        "cert": (rec.get("GdCert") or {}).get("name"),
        "cert_code": (rec.get("GdCert") or {}).get("ryaku_code"),
        "category": (rec.get("GdCategory") or {}).get("name"),
    }


def main():
    first = api_get(f"{API}?page=1")
    total = first["info"]["count"]
    pages = first["info"]["pageCount"]
    print(f"全 {total} 件 / {pages} ページ")

    os.makedirs(OUT_DIR, exist_ok=True)
    seen = set()
    with open(OUT_PATH, "w", encoding="utf-8") as out:
        for page in range(1, pages + 1):
            d = first if page == 1 else api_get(f"{API}?page={page}")
            for rec in d.get("results", []):
                row = flatten(rec)
                # 同一作品が複数認定 (ゴールドとプラチナ) を持つので、
                # 認定段階まで含めて一意判定する
                key = (row["title"], row["artist"], row["cert"], row["year_month"])
                if key in seen:
                    continue
                seen.add(key)
                out.write(json.dumps(row, ensure_ascii=False) + "\n")
            if page % 20 == 0 or page == pages:
                print(f"  {page}/{pages}", flush=True)
            time.sleep(0.4)

    print(f"\n完了: {len(seen)} 件 -> {OUT_PATH}")


if __name__ == "__main__":
    sys.exit(main())
