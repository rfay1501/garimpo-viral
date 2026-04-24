#!/usr/bin/env python3
"""
Garimpador de vídeos virais do YouTube — sem API oficial.

Uso:
    python3 scraper.py                 # roda tudo
    python3 scraper.py --test          # roda 1 nicho em 1 idioma (rápido)
    python3 scraper.py --niche misterios --lang en   # roda 1 combo específico

Saída: data/results.json
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

# Import local
sys.path.insert(0, str(Path(__file__).parent))
from niches import NICHES, LANGUAGE_NAMES, all_queries
from scoring import compute_score, detect_faceless_heuristic

# --- Config ---
MIN_VIEWS = 10_000
MIN_DURATION = 30         # descarta vídeos ultra-curtos
MAX_DURATION = 10_800     # 3h — descarta lives enormes
MAX_VIDEO_AGE_DAYS = 15   # janela de "viral recente"
SEARCH_LIMIT = 15         # top N recentes por query na busca
YTDLP_TIMEOUT = 45        # segundos por chamada
ENRICH_WORKERS = 4        # extrações em paralelo

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

YTDLP = os.path.expanduser("~/Library/Python/3.9/bin/yt-dlp")
if not os.path.exists(YTDLP):
    # CI/Linux fallback — pip instala em ~/.local/bin ou no PATH
    YTDLP = "yt-dlp"


def _run_ytdlp(args: list[str], timeout: int = YTDLP_TIMEOUT) -> str:
    """Roda yt-dlp com args extras. Retorna stdout ou string vazia em erro."""
    cmd = [YTDLP, "--no-warnings", "--ignore-errors"] + args
    try:
        r = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout, check=False
        )
        return r.stdout or ""
    except subprocess.TimeoutExpired:
        print(f"  ⏱  timeout: {' '.join(args[:2])}", file=sys.stderr)
        return ""
    except Exception as e:
        print(f"  ✗ erro: {e}", file=sys.stderr)
        return ""


def search_flat(query: str, limit: int = SEARCH_LIMIT) -> list[dict]:
    """
    Busca rápida via ytsearchdate (ordena por data de upload).
    Muito mais eficiente pra 'virais recentes' do que ytsearch padrão.
    """
    out = _run_ytdlp([
        "--flat-playlist",
        "--dump-json",
        f"ytsearchdate{limit}:{query}",
    ])
    results = []
    for line in out.splitlines():
        if not line.strip():
            continue
        try:
            results.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return results


def extract_full(url: str) -> dict | None:
    """Extração completa de UM vídeo — inclui upload_date, channel_follower_count etc."""
    out = _run_ytdlp(["--dump-json", "--skip-download", url], timeout=30)
    line = out.strip().split("\n")[0] if out.strip() else ""
    if not line:
        return None
    try:
        return json.loads(line)
    except json.JSONDecodeError:
        return None


def video_age_days(upload_date: str) -> float:
    """Converte YYYYMMDD em dias desde então."""
    if not upload_date or len(upload_date) != 8:
        return 9999
    try:
        dt = datetime.strptime(upload_date, "%Y%m%d").replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - dt).total_seconds() / 86400
    except ValueError:
        return 9999


def collect_candidates(niche_filter: str | None, lang_filter: str | None) -> list[dict]:
    """Fase 1: busca plana + pré-filtro por views/duração."""
    seen_ids: set[str] = set()
    candidates: list[dict] = []

    queries = list(all_queries())
    if niche_filter:
        queries = [q for q in queries if q[0] == niche_filter]
    if lang_filter:
        queries = [q for q in queries if q[1] == lang_filter]

    total = len(queries)
    print(f"→ {total} buscas a executar")

    for i, (niche_key, lang, query) in enumerate(queries, 1):
        print(f"  [{i}/{total}] {niche_key}/{lang}: {query!r}")
        hits = search_flat(query)
        kept = 0
        for h in hits:
            vid = h.get("id") or h.get("url", "").split("watch?v=")[-1][:11]
            if not vid or vid in seen_ids:
                continue
            views = h.get("view_count") or 0
            dur = h.get("duration") or 0
            if views < MIN_VIEWS:
                continue
            if dur and (dur < MIN_DURATION or dur > MAX_DURATION):
                continue
            seen_ids.add(vid)
            h["_niche"] = niche_key
            h["_lang"] = lang
            h["_query"] = query
            candidates.append(h)
            kept += 1
        print(f"     → {len(hits)} achados, {kept} passaram no pré-filtro")
    print(f"→ {len(candidates)} candidatos únicos após pré-filtro")
    return candidates


def _enrich_one(c: dict) -> dict | None:
    vid = c.get("id")
    url = c.get("url") or f"https://www.youtube.com/watch?v={vid}"
    full = extract_full(url)
    if not full:
        return None
    age = video_age_days(full.get("upload_date", ""))
    if age > MAX_VIDEO_AGE_DAYS:
        return {"_rejected": "velho", "_age": age}
    return {
        "video_id": full.get("id"),
        "title": full.get("title"),
        "description": (full.get("description") or "")[:400],
        "url": full.get("webpage_url") or url,
        "thumbnail": full.get("thumbnail"),
        "duration": full.get("duration"),
        "view_count": full.get("view_count"),
        "like_count": full.get("like_count"),
        "comment_count": full.get("comment_count"),
        "upload_date": full.get("upload_date"),
        "channel": full.get("channel") or full.get("uploader"),
        "channel_id": full.get("channel_id"),
        "channel_url": full.get("channel_url"),
        "channel_followers": full.get("channel_follower_count"),
        "tags": (full.get("tags") or [])[:10],
        "niche": c["_niche"],
        "lang": c["_lang"],
        "query": c["_query"],
    }


def enrich_candidates(candidates: list[dict]) -> list[dict]:
    """Fase 2: extração completa em paralelo."""
    enriched = []
    total = len(candidates)
    kept = rejected_old = failed = 0
    with ThreadPoolExecutor(max_workers=ENRICH_WORKERS) as pool:
        futures = {pool.submit(_enrich_one, c): c for c in candidates}
        for i, fut in enumerate(as_completed(futures), 1):
            result = fut.result()
            if result is None:
                failed += 1
            elif "_rejected" in result:
                rejected_old += 1
            else:
                enriched.append(result)
                kept += 1
            if i % 10 == 0 or i == total:
                print(f"  enriched {i}/{total}  (kept={kept}, velhos={rejected_old}, falhas={failed})")
    return enriched


def score_all(videos: list[dict]) -> list[dict]:
    for v in videos:
        is_faceless = detect_faceless_heuristic(v.get("channel", ""), v.get("description", ""))
        channel = {
            "age_days": 999,   # Fase 2: calcular idade real do canal
            "is_faceless": is_faceless,
        }
        niche_cfg = NICHES[v["niche"]]
        s = compute_score(v, channel, niche_cfg)
        v["scoring"] = s
        v["is_faceless"] = is_faceless
        v["score"] = s["score"]
    videos.sort(key=lambda x: -x["score"])
    return videos


def save(videos: list[dict], path: Path) -> None:
    now = datetime.now(timezone.utc).isoformat()
    payload = {
        "generated_at": now,
        "total": len(videos),
        "niches": {k: v["name"] for k, v in NICHES.items()},
        "languages": LANGUAGE_NAMES,
        "config": {
            "min_views": MIN_VIEWS,
            "max_video_age_days": MAX_VIDEO_AGE_DAYS,
        },
        "videos": videos,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    # Também grava cópia em docs/ pra GitHub Pages servir
    docs_copy = PROJECT_ROOT / "docs" / "results.json"
    docs_copy.parent.mkdir(exist_ok=True)
    docs_copy.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"💾 {len(videos)} vídeos salvos em {path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--test", action="store_true", help="Rodada rápida (1 nicho, 1 idioma)")
    ap.add_argument("--niche", help="Filtrar por 1 nicho (chave)")
    ap.add_argument("--lang", help="Filtrar por 1 idioma (en/es/pt)")
    args = ap.parse_args()

    niche_filter = args.niche
    lang_filter = args.lang
    if args.test:
        niche_filter = niche_filter or "misterios"
        lang_filter = lang_filter or "en"

    t0 = time.time()
    print(f"🚀 Garimpador iniciado {datetime.now().isoformat()}")

    candidates = collect_candidates(niche_filter, lang_filter)
    if not candidates:
        print("Nenhum candidato após pré-filtro.")
        save([], DATA_DIR / "results.json")
        return

    enriched = enrich_candidates(candidates)
    if not enriched:
        print("Nenhum vídeo recente o suficiente.")
        save([], DATA_DIR / "results.json")
        return

    scored = score_all(enriched)
    save(scored, DATA_DIR / "results.json")
    print(f"✅ Finalizado em {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
