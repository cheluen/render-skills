#!/bin/bash
# Render API CLI - Zero Dependencies
# Config: config.json (mode: json|env, profiles or RENDER_API_KEY/RENDER_API_KEYS)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$(dirname "$SCRIPT_DIR")/config.json"
API_BASE="https://api.render.com/v1"

# Colors
R='\033[0;31m' G='\033[0;32m' Y='\033[1;33m' B='\033[0;34m' N='\033[0m'

API_KEY="" PROFILE=""

# Simple JSON parser
json_val() { echo "$1" | grep -o "\"$2\"[[:space:]]*:[[:space:]]*\"[^\"]*\"" | head -1 | sed 's/.*:[ ]*"\([^"]*\)".*/\1/'; }

load_key() {
    local profile="${1:-}"

    if [[ -f "$CONFIG_FILE" ]]; then
        local cfg=$(cat "$CONFIG_FILE")
        local mode=$(json_val "$cfg" "mode")

        if [[ "$mode" == "json" ]]; then
            [[ -z "$profile" ]] && profile=$(json_val "$cfg" "default_profile")
            profile="${profile:-default}"
            local block=$(grep -A3 "\"$profile\"" "$CONFIG_FILE" | head -4)
            API_KEY=$(json_val "$block" "api_key")
            PROFILE="$profile"
            [[ -n "$API_KEY" && "$API_KEY" != "rnd_YOUR_API_KEY_HERE" ]] && return 0
        fi
    fi

    # Env mode
    if [[ -n "${RENDER_API_KEYS:-}" ]]; then
        IFS=',' read -ra KEYS <<< "$RENDER_API_KEYS"
        API_KEY="${KEYS[0]}"
        PROFILE="env-0"
    elif [[ -n "${RENDER_API_KEY:-}" ]]; then
        API_KEY="$RENDER_API_KEY"
        PROFILE="env"
    else
        echo -e "${R}Error: No API key. Set RENDER_API_KEY or create config.json${N}" >&2
        exit 1
    fi
}

api() {
    local method="$1" endpoint="$2" data="${3:-}"
    local args=(-s -w "\n%{http_code}" -X "$method" "${API_BASE}${endpoint}"
                -H "Authorization: Bearer $API_KEY" -H "Accept: application/json")
    [[ -n "$data" ]] && args+=(-H "Content-Type: application/json" -d "$data")

    local resp=$(curl "${args[@]}")
    local code=$(echo "$resp" | tail -n1)
    local body=$(echo "$resp" | sed '$d')

    case $code in
        2*) echo "$body" ;;
        401) echo -e "${R}Unauthorized${N} (Free plan API keys work fine)" >&2; exit 1 ;;
        403) echo -e "${R}Forbidden${N} - may need paid plan for this feature" >&2; exit 1 ;;
        429) echo -e "${Y}Rate limited${N} - retry later" >&2; exit 1 ;;
        *) echo -e "${R}Error $code${N}" >&2; echo "$body" >&2; exit 1 ;;
    esac
}

cmd_services() {
    case "${1:-list}" in
        list) echo -e "${B}[$PROFILE]${N}"; api GET "/services?limit=20" ;;
        get) api GET "/services/$2" ;;
        suspend) api POST "/services/$2/suspend"; echo -e "${G}Suspended${N}" ;;
        resume) api POST "/services/$2/resume"; echo -e "${G}Resumed${N}" ;;
        restart) api POST "/services/$2/restart"; echo -e "${G}Restarted${N}" ;;
        *) echo "services: list|get|suspend|resume|restart" >&2 ;;
    esac
}

cmd_deploys() {
    case "${1:-list}" in
        list) api GET "/services/$2/deploys?limit=10" ;;
        trigger) api POST "/services/$2/deploys" '{"clearCache":"do_not_clear"}' ;;
        cancel) api POST "/services/$2/deploys/$3/cancel" ;;
        *) echo "deploys: list|trigger|cancel" >&2 ;;
    esac
}

cmd_postgres() {
    case "${1:-list}" in
        list) api GET "/postgres" ;;
        get) api GET "/postgres/$2" ;;
        conn) api GET "/postgres/$2/connection-info" ;;
        *) echo "postgres: list|get|conn" >&2 ;;
    esac
}

cmd_kv() {
    case "${1:-list}" in
        list) api GET "/key-value" ;;
        get) api GET "/key-value/$2" ;;
        conn) api GET "/key-value/$2/connection-info" ;;
        *) echo "kv: list|get|conn" >&2 ;;
    esac
}

cmd_batch() {
    echo -e "${B}Batch: $1${N}"
    if [[ -f "$CONFIG_FILE" ]] && [[ "$(json_val "$(cat "$CONFIG_FILE")" "mode")" == "json" ]]; then
        grep -o '"[^"]*"[[:space:]]*:[[:space:]]*{[^}]*"api_key"' "$CONFIG_FILE" | \
        grep -v "profiles" | sed 's/"\([^"]*\)".*/\1/' | while read -r p; do
            echo -e "\n${Y}--- $p ---${N}"
            load_key "$p"
            case "$1" in
                services) api GET "/services?limit=20" ;;
                workspaces) api GET "/owners" ;;
            esac
        done
    elif [[ -n "${RENDER_API_KEYS:-}" ]]; then
        IFS=',' read -ra KEYS <<< "$RENDER_API_KEYS"
        for i in "${!KEYS[@]}"; do
            echo -e "\n${Y}--- key $i ---${N}"
            API_KEY="${KEYS[$i]}"
            case "$1" in
                services) api GET "/services?limit=20" ;;
                workspaces) api GET "/owners" ;;
            esac
        done
    fi
}

usage() {
    cat << 'EOF'
Render API CLI

Usage: render-api.sh [-p profile] <command> [args]

Commands:
  services list|get|suspend|resume|restart <id>
  deploys list|trigger|cancel <service_id> [deploy_id]
  postgres list|get|conn <id>
  kv list|get|conn <id>
  logs <service_id>
  workspaces
  batch services|workspaces

Config: config.json with mode "json" (profiles) or "env" (RENDER_API_KEY[S])
Free plan API keys work for all core operations.
EOF
    exit 0
}

main() {
    local profile=""
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -p|--profile) profile="$2"; shift 2 ;;
            -h|--help) usage ;;
            *) break ;;
        esac
    done

    [[ $# -eq 0 ]] && usage
    load_key "$profile"

    case "$1" in
        services) shift; cmd_services "$@" ;;
        deploys) shift; cmd_deploys "$@" ;;
        postgres) shift; cmd_postgres "$@" ;;
        kv) shift; cmd_kv "$@" ;;
        logs) api GET "/logs?resource=$2&limit=50" ;;
        workspaces) api GET "/owners" ;;
        batch) shift; cmd_batch "$@" ;;
        *) echo "Unknown: $1" >&2; usage ;;
    esac
}

main "$@"
