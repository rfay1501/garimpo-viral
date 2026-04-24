#!/bin/bash
# Roda o garimpador localmente e empurra resultados pro GitHub.
# Chamado pelo launchd a cada 6h (ver com.robsonalves.garimpo-viral.plist).

set -e

PROJECT_DIR="/Users/robsonalves/claude code inicio youtube/garimpo-viral"
cd "$PROJECT_DIR"

echo "=============================================="
echo "Garimpo Viral — iniciando $(date)"
echo "=============================================="

# Sincroniza antes pra evitar conflito se alguém editou no GitHub
git pull --rebase origin main 2>&1 || {
  echo "⚠ git pull falhou, continuando mesmo assim"
}

# Roda o scraper
python3 src/scraper.py

# Checa se achou algo
TOTAL=$(python3 -c "import json; print(json.load(open('data/results.json'))['total'])")
if [ "$TOTAL" -eq 0 ]; then
  echo "⚠ 0 vídeos achados. YouTube pode estar bloqueando (raro em IP residencial)."
  exit 0
fi

# Commit + push
git add data/ docs/results.json
if git diff --cached --quiet; then
  echo "ℹ Nenhuma mudança, pulando commit."
else
  git commit -m "chore: atualiza garimpagem $(date -u +%Y-%m-%dT%H:%MZ)"
  git push origin main || echo "⚠ git push falhou (verificar credenciais)"
fi

echo "✅ Rodada completa: $TOTAL vídeos às $(date)"
