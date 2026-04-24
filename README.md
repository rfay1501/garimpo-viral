# Garimpo Viral

Ferramenta de garimpagem de vídeos virais recentes no YouTube em canais *dark* (faceless) — **sem usar a API oficial do YouTube**.

**Dashboard ao vivo:** https://rfay1501.github.io/garimpo-viral/

## Como funciona

1. **Scraper (`src/scraper.py`)** — usa `yt-dlp` pra rodar buscas programáticas no YouTube em 10 nichos × 3 idiomas (EN/ES/PT), ordenadas por data.
2. **Pré-filtro** — descarta vídeos com < 10.000 views ou fora da janela de duração (30s–3h).
3. **Enriquecimento paralelo** — pra cada candidato, extrai metadados completos (upload date, canal, descrição, tags).
4. **Filtro de recência** — mantém só vídeos publicados nos últimos 15 dias.
5. **Score** — cada vídeo recebe nota 0–100 combinando:
   - Velocidade de views (views/dia)
   - Qualidade do nicho (RPM + afiliado + escalabilidade)
   - Heurística faceless no nome do canal
6. **Saída** — JSON em `data/results.json` + `docs/results.json` (pra GitHub Pages).
7. **Dashboard** — `docs/index.html` com filtros por nicho, idioma, faceless, score, busca textual.

## Automação: **cron local (launchd) no Mac**

⚠ **Importante:** o YouTube bloqueia IPs de data center (GitHub Actions, AWS, etc.), então o scraper roda **localmente no Mac do usuário** via `launchd`. O IP residencial do usuário não é bloqueado.

### Instalar o cron (roda a cada 6h)

```bash
bash scripts/install-cron.sh
```

Depois disso, o scraper roda automaticamente a cada 6h enquanto o Mac estiver ligado, faz commit dos resultados e dá push pro GitHub. O dashboard no GitHub Pages é atualizado automaticamente.

### Comandos úteis

```bash
# Ver execução em tempo real
tail -f /tmp/garimpo-viral.log

# Rodar agora (sem esperar 6h)
bash scripts/run-and-push.sh

# Confirmar que está carregado
launchctl list | grep garimpo

# Desinstalar
bash scripts/install-cron.sh off
```

## Rodar manualmente

```bash
pip install -r requirements.txt

# Rodada rápida (1 nicho, 1 idioma) pra testar
python src/scraper.py --test

# Rodada completa (10 nichos × 3 idiomas, ~30-40 min)
python src/scraper.py

# Abrir dashboard local
open docs/index.html
```

## Estrutura

```
garimpo-viral/
├── src/
│   ├── niches.py       # 10 nichos × 3 idiomas × queries
│   ├── scoring.py      # sistema de score
│   └── scraper.py      # motor principal (yt-dlp)
├── data/
│   └── results.json    # saída canônica
├── docs/               # GitHub Pages root
│   ├── index.html      # dashboard
│   └── results.json    # espelho do data/
├── scripts/
│   ├── install-cron.sh                       # instalador do launchd
│   ├── run-and-push.sh                       # scraper + git push
│   └── com.robsonalves.garimpo-viral.plist   # job launchd (6h)
└── .github/workflows/
    └── scrape.yml      # fallback GH Actions (bloqueado por YT)
```

## Roadmap

- **Fase 2:** Alemão e Francês; detecção faceless via visão computacional nas thumbnails; idade real do canal via `/about` page.
- **Fase 3:** Árabe, Japonês; alertas por e-mail quando score > 85; trend detection por nicho/idioma.

## Disclaimer

Esta ferramenta usa `yt-dlp` pra extrair dados **públicos** do YouTube (só leitura de metadados que qualquer visitante vê). Não faz download de vídeos.
