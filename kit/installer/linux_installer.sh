#!/usr/bin/env bash
# Instalador DangoHub para Linux / Steam Deck (SteamOS).
# Lê pacote.conf (JOGO, PASTA_STEAM, VERSAO, VERIFICAR, AVISO) e arquivos.lst ("origem<TAB>destino").
# Com PY_INSTALADOR definido em pacote.conf, delega a instalação ao modo CLI do instalador Python do jogo
# (--install/--uninstall/--status <pasta>), usado quando o patch precisa dos arquivos originais do jogo.
# Uso: ./Instalar.sh  |  ./Instalar.sh --install [pasta]  |  ./Instalar.sh --uninstall [pasta]  |  ./Instalar.sh --status [pasta]
set -u
HERE="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
# shellcheck source=/dev/null
source "$HERE/pacote.conf"
PY_INSTALADOR="${PY_INSTALADOR:-}"
PYTHON="$(command -v python3 || command -v python || true)"
BACKUP_SUFFIX=".dangohub-backup"
MANIFEST="DangoHub_PTBR.txt"
TITLE="Tradução PT-BR - $JOGO"
FILE_LIST="$HERE/arquivos.lst"

# ---------- interface: zenity > kdialog > terminal ----------
if command -v zenity >/dev/null 2>&1; then UI=zenity
elif command -v kdialog >/dev/null 2>&1; then UI=kdialog
else UI=terminal; fi

show_info() {
    case $UI in
        zenity) zenity --info --title="$TITLE" --width=420 --text="$1" 2>/dev/null ;;
        kdialog) kdialog --title "$TITLE" --msgbox "$1" ;;
        *) printf '\n%b\n' "$1" ;;
    esac
}
show_error() {
    case $UI in
        zenity) zenity --error --title="$TITLE" --width=420 --text="$1" 2>/dev/null ;;
        kdialog) kdialog --title "$TITLE" --error "$1" ;;
        *) printf '\nERRO: %b\n' "$1" >&2 ;;
    esac
}
choose_action() {
    local state="$1"
    case $UI in
        zenity) zenity --list --radiolist --title="$TITLE" --width=460 --height=260 \
                    --text="Pasta do jogo:\n$GAME_DIR\n\nSituação: $state" \
                    --column="" --column="action" --column="Ação" --hide-column=2 \
                    TRUE install "Instalar / atualizar a tradução" \
                    FALSE uninstall "Desinstalar (restaurar originais)" 2>/dev/null ;;
        kdialog) kdialog --title "$TITLE" --radiolist "Pasta do jogo:\n$GAME_DIR\n\nSituação: $state" \
                    install "Instalar / atualizar a tradução" on \
                    uninstall "Desinstalar (restaurar originais)" off ;;
        *) printf '\nPasta do jogo: %s\nSituação: %s\n1) Instalar / atualizar\n2) Desinstalar\nEscolha [1/2]: ' "$GAME_DIR" "$state" >&2
           read -r answer; [ "$answer" = 2 ] && echo uninstall || echo install ;;
    esac
}
choose_game_dir() {
    case $UI in
        zenity) zenity --file-selection --directory --title="Selecione a pasta do jogo $JOGO" 2>/dev/null ;;
        kdialog) kdialog --title "Selecione a pasta do jogo $JOGO" --getexistingdirectory "$HOME" ;;
        *) printf 'Caminho da pasta do jogo: ' >&2; read -r answer; echo "$answer" ;;
    esac
}

# ---------- find the game ----------
is_game_dir() { [ -n "$1" ] && [ -e "$1/$VERIFICAR" ]; }

steam_libraries() {
    local roots=(
        "$HOME/.local/share/Steam"
        "$HOME/.steam/steam"
        "$HOME/.steam/root"
        "$HOME/.var/app/com.valvesoftware.Steam/.local/share/Steam"
    )
    local root
    for root in "${roots[@]}"; do
        [ -d "$root/steamapps" ] && echo "$root"
        [ -f "$root/steamapps/libraryfolders.vdf" ] &&
            sed -n 's/^[[:space:]]*"path"[[:space:]]*"\(.*\)"[[:space:]]*$/\1/p' "$root/steamapps/libraryfolders.vdf"
    done
    local media
    for media in /run/media/*/* /run/media/*; do [ -d "$media/steamapps" ] && echo "$media"; done 2>/dev/null
}

find_game() {
    local library
    while IFS= read -r library; do
        if is_game_dir "$library/steamapps/common/$PASTA_STEAM"; then
            echo "$library/steamapps/common/$PASTA_STEAM"
            return
        fi
    done < <(steam_libraries | awk '!seen[$0]++')
}

# ---------- install / uninstall ----------
is_installed() {
    if [ -n "$PY_INSTALADOR" ]; then
        "$PYTHON" "$HERE/$PY_INSTALADOR" --status "$1" 2>/dev/null | grep -q '^instalado'
    else
        [ -f "$1/$MANIFEST" ]
    fi
}

install_translation() {
    if [ -n "$PY_INSTALADOR" ]; then
        "$PYTHON" "$HERE/$PY_INSTALADOR" --install "$GAME_DIR"
        return
    fi
    local source destination target
    while IFS=$'\t' read -r source destination; do
        [ -z "$source" ] && continue
        target="$GAME_DIR/$destination"
        mkdir -p "$(dirname "$target")" || return 1
        if [ -e "$target" ] && [ ! -e "$target$BACKUP_SUFFIX" ] && ! is_installed "$GAME_DIR"; then
            cp -p "$target" "$target$BACKUP_SUFFIX" || return 1
        fi
        cp "$HERE/$source" "$target" || return 1
    done < "$FILE_LIST"
    { echo "DangoHub - $TITLE v$VERSAO"; cut -f2 "$FILE_LIST"; } > "$GAME_DIR/$MANIFEST"
}

uninstall_translation() {
    if [ -n "$PY_INSTALADOR" ]; then
        "$PYTHON" "$HERE/$PY_INSTALADOR" --uninstall "$GAME_DIR"
        return
    fi
    local source destination target
    while IFS=$'\t' read -r source destination; do
        [ -z "$source" ] && continue
        target="$GAME_DIR/$destination"
        if [ -e "$target$BACKUP_SUFFIX" ]; then mv -f "$target$BACKUP_SUFFIX" "$target"
        else rm -f "$target"; fi
    done < "$FILE_LIST"
    rm -f "$GAME_DIR/$MANIFEST"
}

# ---------- flow ----------
ACTION=""
case "${1:-}" in
    --install) ACTION=install; GAME_DIR="${2:-}" ;;
    --uninstall) ACTION=uninstall; GAME_DIR="${2:-}" ;;
    --status) ACTION=status; GAME_DIR="${2:-}" ;;
    *) GAME_DIR="" ;;
esac
[ -n "$ACTION" ] && UI=terminal

if [ -n "$PY_INSTALADOR" ] && [ -z "$PYTHON" ]; then
    show_error "Python 3 não encontrado. No Steam Deck ele já vem instalado; em outras distribuições instale o pacote python3."
    exit 1
fi

is_game_dir "$GAME_DIR" || GAME_DIR="$(find_game)"
if ! is_game_dir "$GAME_DIR"; then
    [ "$UI" = terminal ] || show_info "Não encontrei $JOGO automaticamente.\nSelecione a pasta do jogo (a que contém \"$VERIFICAR\")."
    GAME_DIR="$(choose_game_dir)"
    if ! is_game_dir "$GAME_DIR"; then
        show_error "Pasta inválida: não encontrei \"$VERIFICAR\" em:\n${GAME_DIR:-(nenhuma)}"
        exit 1
    fi
fi

if [ "$ACTION" = status ]; then
    is_installed "$GAME_DIR" && echo "instalado: $GAME_DIR" || echo "não instalado: $GAME_DIR"
    exit 0
fi

if [ -z "$ACTION" ]; then
    is_installed "$GAME_DIR" && STATE="tradução instalada" || STATE="tradução não instalada"
    ACTION="$(choose_action "$STATE")"
    [ -z "$ACTION" ] && exit 0
fi

if [ "$ACTION" = install ]; then
    if install_translation; then show_info "Tradução instalada com sucesso!\n\n$AVISO"
    else show_error "Falha ao instalar em:\n$GAME_DIR\n\nFeche o jogo e tente de novo."; exit 1; fi
else
    if is_installed "$GAME_DIR"; then uninstall_translation; show_info "Tradução removida e arquivos originais restaurados."
    else show_info "A tradução não está instalada nesta pasta."; fi
fi
