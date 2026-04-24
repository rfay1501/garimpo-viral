# Garimpo Viral

Ferramenta de garimpagem de vídeos virais recentes no YouTube, focada em canais *dark* (faceless) — **sem usar a API oficial do YouTube**.

## Como funciona

1. **Scraper (`src/scraper.py`)** — usa `yt-dlp` pra rodar buscas programáticas no YouTube em 10 nichos × 3 idiomas (EN/ES/PT), ordenadas por data.
2. **Pré-filtro** — descarta vídeos com < 10.000 views ou fora da janela de duração (30s–3h).
3. **Enriquecimento paralelo** — pra cada candidato, extrai metadados completos (upload date, canal, descrição, tags).
4. **Filtro de recência** — mantém só vídeos publicados nos últimos 15 dias.
5. **Score** — cada vídeo recebe nota 0–100 combinando:
   - Velocidade de views (views/dia)
   - Qualidade do nicho (RPM + afiliado + escalabilidade)
   - Ineditismo do canal (heurística faceless)
6. **Saída** — JSON em `data/results.json` + `docs/results.json` (pra GitHub Pages).
7. **Dashboard** — `docs/index.html` com filtros por nicho, idioma, faceless, score, busca textual.

## Rodar localmente

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Rodada rápida (1 nicho, 1 idioma) pra validar
python src/scraper.py --test

# 3. Rodada completa (10 nichos × 3 idiomas)
python src/scraper.py

# 4. Abrir dashboard
open docs/index.html
```

## Automação

GitHub Actions roda o scraper a cada **6 horas** (`.github/workflows/scrape.yml`) e faz commit do `results.json` atualizado no repositório. O dashboard no GitHub Pages lê esse JSON e se atualiza automaticamente.

## Estrutura

```
garimpo-viral/
├── src/
│   ├── niches.py       # 10 nichos × 3 idiomas × queries
│   ├── scoring.py      # sistema de score
│   └── scraper.py      # motor principal
├── data/
│   └── results.json    # saída (gerada)
├── docs/               # GitHub Pages root
│   ├── index.html      # dashboard
│   └── results.json    # espelho do data/
└── .github/workflows/
    └── scrape.yml      # cron 6h
```

## Roadmap

- **Fase 2:** adicionar Alemão e Francês; detecção faceless via visão computacional nas thumbnails; idade real do canal via fetch do `/about`.
- **Fase 3:** Árabe, Japonês; analytics de tendência (qual nicho/idioma está subindo); alertas por e-mail quando score > 85.

## Disclaimer

Esta ferramenta usa `yt-dlp` pra extrair dados **públicos** do YouTube. Respeita os termos de uso: não faz download de vídeos, só lê metadados que qualquer visitante do site pode ver.
