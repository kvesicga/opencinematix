#!/usr/bin/env bash
#
# Starts cinepi-raw with the verified parameters for Pi 4 and IMX477.
# Any argument given here overrides the defaults below.

set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/versions.env" 2>/dev/null || true

CAM_PORT="${CAM_PORT:-cam0}"
CAM_MODE="${CAM_MODE:-2028:1080:12:P}"
CAM_WIDTH="${CAM_WIDTH:-2028}"
CAM_HEIGHT="${CAM_HEIGHT:-1080}"
LORES_WIDTH="${LORES_WIDTH:-1280}"
LORES_HEIGHT="${LORES_HEIGHT:-720}"
PREVIEW_RECT="${PREVIEW_RECT:-0,30,1920,1020}"
TIMEOUT="${TIMEOUT:-0}"

exec cinepi-raw \
    --cam-port "$CAM_PORT" \
    --mode "$CAM_MODE" \
    --width "$CAM_WIDTH" \
    --height "$CAM_HEIGHT" \
    --lores-width "$LORES_WIDTH" \
    --lores-height "$LORES_HEIGHT" \
    -p "$PREVIEW_RECT" \
    -t "$TIMEOUT" \
    "$@"
