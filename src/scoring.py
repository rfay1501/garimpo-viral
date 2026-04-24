"""
Sistema de pontuação dos vídeos garimpados.

Score final (0-100) combina:
  - Velocidade de views (views/dia desde publicação): 40%
  - Qualidade do nicho (RPM + afiliado + escala): 30%
  - Recência do canal (canal novo = mais oportunidade): 15%
  - Bônus faceless confirmado: 15%
"""

from datetime import datetime, timezone


def _velocity_score(views: int, video_age_days: float) -> float:
    """
    Views por dia, normalizado em escala 0-100.
    10k/dia = 50, 50k/dia = 80, 200k+/dia = 100.
    """
    if video_age_days <= 0:
        video_age_days = 0.5
    vpd = views / max(video_age_days, 0.5)
    # Escala log para não deixar blockbusters dominarem 100%
    import math
    # log10(1000)=3 → 0, log10(1M)=6 → 100
    score = (math.log10(max(vpd, 100)) - 3) / 3 * 100
    return max(0, min(100, score))


def _niche_score(niche_cfg: dict) -> float:
    """Média ponderada dos sub-scores do nicho."""
    return (
        niche_cfg["rpm_score"] * 0.4
        + niche_cfg["affiliate_score"] * 0.35
        + niche_cfg["scale_score"] * 0.25
    )


def _channel_freshness_score(channel_age_days: float) -> float:
    """
    Canal mais novo = mais oportunidade de copiar estratégia antes de saturar.
    0d = 100, 30d = 90, 90d = 60, 150d = 10, 180d+ = 0.
    """
    if channel_age_days <= 0:
        return 100
    if channel_age_days >= 180:
        return 0
    return max(0, 100 - (channel_age_days / 180) * 100)


def _faceless_bonus(is_faceless: bool) -> float:
    """Bônus flat se o canal é faceless confirmado."""
    return 100 if is_faceless else 50


def compute_score(video: dict, channel: dict, niche_cfg: dict) -> dict:
    """
    Retorna dict com score final e breakdown.

    video: {view_count, upload_date (YYYYMMDD), ...}
    channel: {age_days, is_faceless}
    niche_cfg: entrada do NICHES
    """
    now = datetime.now(timezone.utc)
    upload = video.get("upload_date")
    if upload and len(upload) == 8:
        up_dt = datetime.strptime(upload, "%Y%m%d").replace(tzinfo=timezone.utc)
        video_age_days = max((now - up_dt).total_seconds() / 86400, 0.1)
    else:
        video_age_days = 1

    v_score = _velocity_score(video.get("view_count") or 0, video_age_days)
    n_score = _niche_score(niche_cfg)
    c_score = _channel_freshness_score(channel.get("age_days", 999))
    f_score = _faceless_bonus(channel.get("is_faceless", False))

    final = v_score * 0.40 + n_score * 0.30 + c_score * 0.15 + f_score * 0.15

    return {
        "score": round(final, 1),
        "velocity": round(v_score, 1),
        "niche_quality": round(n_score, 1),
        "channel_freshness": round(c_score, 1),
        "faceless_bonus": round(f_score, 1),
        "video_age_days": round(video_age_days, 1),
    }


def detect_faceless_heuristic(channel_name: str, channel_description: str = "") -> bool:
    """
    Heurística simples (Fase 1) pra detectar canais faceless.
    Fase 2 vai usar visão computacional nas thumbnails.

    Retorna True se o canal parece faceless.
    """
    if not channel_name:
        return False
    name_lower = channel_name.lower()
    desc_lower = (channel_description or "").lower()

    # Palavras típicas de canais faceless (compiladas, AI-gen, narração etc.)
    faceless_keywords = [
        "facts", "mysteries", "stories", "history", "tales", "legends",
        "top ", "compiled", "documentary", "narrated", "explained",
        "scary", "creepy", "weird", "bizarre", "dark", "secret",
        "hechos", "misterios", "historias", "leyendas", "oscuro",
        "fatos", "mistérios", "historias", "lendas", "obscuro",
        "ai ", " ai", "generated", "tube", "channel", "media",
        "archive", "vault", "chronicle", "legacy", "saga",
    ]

    # Palavras que sugerem canal COM rosto (nomes pessoais, vlogger etc)
    personal_keywords = [
        "vlog", "official", "oficial", "daily", "life with", "my ",
    ]

    has_faceless = any(k in name_lower or k in desc_lower for k in faceless_keywords)
    has_personal = any(k in name_lower for k in personal_keywords)

    return has_faceless and not has_personal
