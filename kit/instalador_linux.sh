#!/usr/bin/env bash
# Instalador DangoHub para Linux / Steam Deck (SteamOS).
# Lê pacote.conf (JOGO, PASTA_STEAM, VERSAO, VERIFICAR, AVISO) e arquivos.lst ("origem<TAB>destino").
# Uso: ./Instalar.sh  |  ./Instalar.sh --install [pasta]  |  ./Instalar.sh --uninstall [pasta]  |  ./Instalar.sh --status [pasta]
set -u
AQUI="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
# shellcheck source=/dev/null
source "$AQUI/pacote.conf"
BACKUP_EXT=".dangohub-backup"
MANIFESTO="DangoHub_PTBR.txt"
TITULO="Tradução PT-BR - $JOGO"

# ---------- interface: zenity > kdialog > terminal ----------
if command -v zenity >/dev/null 2>&1; then UI=zenity
elif command -v kdialog >/dev/null 2>&1; then UI=kdialog
else UI=terminal; fi

info() {
    case $UI in
        zenity) zenity --info --title="$TITULO" --width=420 --text="$1" 2>/dev/null ;;
        kdialog) kdialog --title "$TITULO" --msgbox "$1" ;;
        *) printf '\n%b\n' "$1" ;;
    esac
}
erro() {
    case $UI in
        zenity) zenity --error --title="$TITULO" --width=420 --text="$1" 2>/dev/null ;;
        kdialog) kdialog --title "$TITULO" --error "$1" ;;
        *) printf '\nERRO: %b\n' "$1" >&2 ;;
    esac
}
escolher_acao() {
    local estado="$1"
    case $UI in
        zenity) zenity --list --radiolist --title="$TITULO" --width=460 --height=260 \
                    --text="Pasta do jogo:\n$PASTA\n\nSituação: $estado" \
                    --column="" --column="acao" --column="Ação" --hide-column=2 \
                    TRUE instalar "Instalar / atualizar a tradução" \
                    FALSE desinstalar "Desinstalar (restaurar originais)" 2>/dev/null ;;
        kdialog) kdialog --title "$TITULO" --radiolist "Pasta do jogo:\n$PASTA\n\nSituação: $estado" \
                    instalar "Instalar / atualizar a tradução" on \
                    desinstalar "Desinstalar (restaurar originais)" off ;;
        *) printf '\nPasta do jogo: %s\nSituação: %s\n1) Instalar / atualizar\n2) Desinstalar\nEscolha [1/2]: ' "$PASTA" "$estado" >&2
           read -r r; [ "$r" = 2 ] && echo desinstalar || echo instalar ;;
    esac
}
escolher_pasta() {
    case $UI in
        zenity) zenity --file-selection --directory --title="Selecione a pasta do jogo $JOGO" 2>/dev/null ;;
        kdialog) kdialog --title "Selecione a pasta do jogo $JOGO" --getexistingdirectory "$HOME" ;;
        *) printf 'Caminho da pasta do jogo: ' >&2; read -r r; echo "$r" ;;
    esac
}

# ---------- localizar o jogo ----------
valida() { [ -n "$1" ] && [ -e "$1/$VERIFICAR" ]; }

bibliotecas() {
    local raizes=(
        "$HOME/.local/share/Steam"
        "$HOME/.steam/steam"
        "$HOME/.steam/root"
        "$HOME/.var/app/com.valvesoftware.Steam/.local/share/Steam"
    )
    local r
    for r in "${raizes[@]}"; do
        [ -d "$r/steamapps" ] && echo "$r"
        [ -f "$r/steamapps/libraryfolders.vdf" ] &&
            sed -n 's/^[[:space:]]*"path"[[:space:]]*"\(.*\)"[[:space:]]*$/\1/p' "$r/steamapps/libraryfolders.vdf"
    done
    local m
    for m in /run/media/*/* /run/media/*; do [ -d "$m/steamapps" ] && echo "$m"; done 2>/dev/null
}

achar_jogo() {
    local lib
    while IFS= read -r lib; do
        if valida "$lib/steamapps/common/$PASTA_STEAM"; then
            echo "$lib/steamapps/common/$PASTA_STEAM"
            return
        fi
    done < <(bibliotecas | awk '!visto[$0]++')
}

# ---------- instalar / desinstalar ----------
instalado() { [ -f "$1/$MANIFESTO" ]; }

instalar() {
    local origem destino alvo
    while IFS=$'\t' read -r origem destino; do
        [ -z "$origem" ] && continue
        alvo="$PASTA/$destino"
        mkdir -p "$(dirname "$alvo")" || return 1
        if [ -e "$alvo" ] && [ ! -e "$alvo$BACKUP_EXT" ] && ! instalado "$PASTA"; then
            cp -p "$alvo" "$alvo$BACKUP_EXT" || return 1
        fi
        cp "$AQUI/$origem" "$alvo" || return 1
    done < "$AQUI/arquivos.lst"
    { echo "DangoHub - $TITULO v$VERSAO"; cut -f2 "$AQUI/arquivos.lst"; } > "$PASTA/$MANIFESTO"
}

desinstalar() {
    local origem destino alvo
    while IFS=$'\t' read -r origem destino; do
        [ -z "$origem" ] && continue
        alvo="$PASTA/$destino"
        if [ -e "$alvo$BACKUP_EXT" ]; then mv -f "$alvo$BACKUP_EXT" "$alvo"
        else rm -f "$alvo"; fi
    done < "$AQUI/arquivos.lst"
    rm -f "$PASTA/$MANIFESTO"
}

# ---------- fluxo ----------
ACAO=""
case "${1:-}" in
    --install) ACAO=instalar; PASTA="${2:-}" ;;
    --uninstall) ACAO=desinstalar; PASTA="${2:-}" ;;
    --status) ACAO=status; PASTA="${2:-}" ;;
    *) PASTA="" ;;
esac
[ -n "$ACAO" ] && UI=terminal

valida "$PASTA" || PASTA="$(achar_jogo)"
if ! valida "$PASTA"; then
    [ "$UI" = terminal ] || info "Não encontrei $JOGO automaticamente.\nSelecione a pasta do jogo (a que contém \"$VERIFICAR\")."
    PASTA="$(escolher_pasta)"
    if ! valida "$PASTA"; then
        erro "Pasta inválida: não encontrei \"$VERIFICAR\" em:\n${PASTA:-(nenhuma)}"
        exit 1
    fi
fi

if [ "$ACAO" = status ]; then
    instalado "$PASTA" && echo "instalado: $PASTA" || echo "não instalado: $PASTA"
    exit 0
fi

if [ -z "$ACAO" ]; then
    instalado "$PASTA" && ESTADO="tradução instalada" || ESTADO="tradução não instalada"
    ACAO="$(escolher_acao "$ESTADO")"
    [ -z "$ACAO" ] && exit 0
fi

if [ "$ACAO" = instalar ]; then
    if instalar; then info "Tradução instalada com sucesso!\n\n$AVISO"
    else erro "Falha ao copiar os arquivos para:\n$PASTA"; exit 1; fi
else
    if instalado "$PASTA"; then desinstalar; info "Tradução removida e arquivos originais restaurados."
    else info "A tradução não está instalada nesta pasta."; fi
fi
