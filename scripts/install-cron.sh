#!/bin/bash
# Instala o cron local (launchd) que roda o garimpador a cada 6h.
# Uso:
#   bash scripts/install-cron.sh        # instala
#   bash scripts/install-cron.sh off    # desinstala

PLIST_SRC="/Users/robsonalves/claude code inicio youtube/garimpo-viral/scripts/com.robsonalves.garimpo-viral.plist"
PLIST_DEST="$HOME/Library/LaunchAgents/com.robsonalves.garimpo-viral.plist"
RUNNER="/Users/robsonalves/claude code inicio youtube/garimpo-viral/scripts/run-and-push.sh"

if [ "$1" = "off" ]; then
  echo "→ Desinstalando cron do garimpador..."
  launchctl unload "$PLIST_DEST" 2>/dev/null
  rm -f "$PLIST_DEST"
  echo "✅ Desinstalado."
  exit 0
fi

echo "→ Instalando cron do garimpador..."
chmod +x "$RUNNER"
mkdir -p "$HOME/Library/LaunchAgents"
cp "$PLIST_SRC" "$PLIST_DEST"

# Unload se já estava carregado, pra reaplicar qualquer mudança
launchctl unload "$PLIST_DEST" 2>/dev/null
launchctl load "$PLIST_DEST"

echo "✅ Cron instalado — vai rodar a cada 6 horas enquanto teu Mac estiver ligado."
echo ""
echo "Comandos úteis:"
echo "  tail -f /tmp/garimpo-viral.log          # ver execução em tempo real"
echo "  launchctl list | grep garimpo           # confirmar que está carregado"
echo "  bash $RUNNER                             # rodar agora manualmente"
echo "  bash $0 off                              # desinstalar"
