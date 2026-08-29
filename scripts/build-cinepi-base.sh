#!/usr/bin/env bash
#
# Builds the cinepi-raw backend and its dependencies from source.
#
# Usage:
#   ./build-cinepi-base.sh              run every stage in order
#   ./build-cinepi-base.sh deps         run a single stage
#   ./build-cinepi-base.sh list         show available stages
#   ./build-cinepi-base.sh preview      HDMI preview, not part of a full run
#
# Stages are idempotent: rerunning one re-checks out the pinned revision and
# rebuilds. Set FORCE_WIPE=1 to discard existing meson build directories.

set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/versions.env"

SRC_DIR="${SRC_DIR:-$HOME/src}"
JOBS="${JOBS:-$(nproc)}"
FORCE_WIPE="${FORCE_WIPE:-0}"

CAM_PORT="${CAM_PORT:-cam0}"
CAM_MODE="${CAM_MODE:-2028:1080:12:P}"
CAM_WIDTH="${CAM_WIDTH:-2028}"
CAM_HEIGHT="${CAM_HEIGHT:-1080}"
LORES_WIDTH="${LORES_WIDTH:-1280}"
LORES_HEIGHT="${LORES_HEIGHT:-720}"
PREVIEW_RECT="${PREVIEW_RECT:-0,30,1920,1020}"
PREVIEW_MS="${PREVIEW_MS:-10000}"

log()  { printf '\n\033[1;34m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[warn]\033[0m %s\n' "$*" >&2; }
die()  { printf '\033[1;31m[error]\033[0m %s\n' "$*" >&2; exit 1; }

# Clone on first run, otherwise fetch; then pin to the recorded revision.
checkout() {
    local repo="$1" ref="$2" dir="$3"
    if [[ -d "$dir/.git" ]]; then
        git -C "$dir" fetch --all --tags --quiet
    else
        git clone --quiet "$repo" "$dir"
    fi
    git -C "$dir" checkout --quiet --detach "$ref"
    printf '    %s @ %s\n' "$(basename "$dir")" "$(git -C "$dir" rev-parse --short HEAD)"
}

meson_setup() {
    local build="$1" src="$2"; shift 2
    if [[ "$FORCE_WIPE" == "1" && -d "$build" ]]; then
        meson setup "$build" "$src" --wipe "$@"
    elif [[ -f "$build/build.ninja" ]]; then
        meson setup "$build" "$src" --reconfigure "$@" \
            || meson setup "$build" "$src" --wipe "$@"
    else
        meson setup "$build" "$src" "$@"
    fi
}

stage_preflight() {
    log "Preflight"
    [[ "$(uname -m)" == "aarch64" ]] || die "expected aarch64, got $(uname -m)"

    local model; model=$(tr -d '\0' < /proc/device-tree/model)
    printf '    board:  %s\n' "$model"
    printf '    kernel: %s\n' "$(uname -r)"
    printf '    jobs:   %s\n' "$JOBS"

    local avail_mb; avail_mb=$(awk '/^MemAvailable:/{print int($2/1024)}' /proc/meminfo)
    printf '    free:   %s MB RAM\n' "$avail_mb"
    [[ "$avail_mb" -gt 1500 ]] || warn "low memory; cinepi_raw.cpp needs ~2 GB at -O3"

    local free_gb; free_gb=$(df -BG --output=avail / | tail -1 | tr -dc '0-9')
    printf '    disk:   %s GB free on /\n' "$free_gb"
    [[ "$free_gb" -ge 5 ]] || die "need at least 5 GB free on /"

    mkdir -p "$SRC_DIR"
}

stage_deps() {
    log "APT dependencies"
    sudo apt-get update
    sudo apt-get install -y \
        build-essential git cmake meson ninja-build pkg-config \
        python3-jinja2 python3-ply python3-yaml python3-pip \
        libboost-dev libboost-program-options-dev \
        libdrm-dev libexif-dev libjpeg-dev libtiff5-dev libpng-dev \
        libcamera-dev libepoxy-dev libglib2.0-dev libyaml-dev \
        libgnutls28-dev openssl pybind11-dev \
        libavcodec-dev libavdevice-dev libavformat-dev libswresample-dev ffmpeg \
        libasound2-dev libjsoncpp-dev libspdlog-dev \
        libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev \
        redis-server libhiredis-dev
}

# Bookworm ships libtiff.so.6; the libcamera apps still link against .so.5.
stage_libtiff_compat() {
    log "libtiff .so.5 compatibility link"
    local target="/usr/lib/aarch64-linux-gnu/libtiff.so.5"
    if [[ -e "$target" ]]; then
        printf '    already present\n'
        return
    fi
    local real; real=$(find /usr/lib -name 'libtiff.so' 2>/dev/null | head -n1)
    [[ -n "$real" ]] || die "libtiff.so not found; is libtiff5-dev installed?"
    sudo ln -sf "$real" "$target"
    sudo ldconfig
    printf '    linked %s -> %s\n' "$target" "$real"
}

stage_redis_pp() {
    log "redis-plus-plus"
    local dir="$SRC_DIR/redis-plus-plus"
    checkout "$REDIS_PP_REPO" "$REDIS_PP_REF" "$dir"
    cmake -S "$dir" -B "$dir/build" -DCMAKE_BUILD_TYPE=Release
    cmake --build "$dir/build" -j "$JOBS"
    sudo cmake --install "$dir/build"
    sudo ldconfig
}

stage_libcamera() {
    log "libcamera (cinemate fork)"
    local dir="$SRC_DIR/libcamera"
    checkout "$LIBCAMERA_REPO" "$LIBCAMERA_REF" "$dir"

    git -C "$dir" config core.fileMode false
    find "$dir" -type f \( -name '*.py' -o -name '*.sh' \) -exec chmod +x {} +

    meson_setup "$dir/build" "$dir" \
        --buildtype=release \
        -Dpipelines=rpi/vc4,rpi/pisp \
        -Dipas=rpi/vc4,rpi/pisp \
        -Dv4l2=true \
        -Dgstreamer=enabled \
        -Dtest=false \
        -Dlc-compliance=disabled \
        -Dcam=disabled \
        -Dqcam=disabled \
        -Ddocumentation=disabled \
        -Dpycamera=disabled
    ninja -C "$dir/build" -j "$JOBS"
    sudo ninja -C "$dir/build" install
    sudo ldconfig
}

stage_mjpeg_streamer() {
    log "cpp-mjpeg-streamer"
    local dir="$SRC_DIR/cpp-mjpeg-streamer"
    checkout "$MJPEG_STREAMER_REPO" "$MJPEG_STREAMER_REF" "$dir"
    cmake -S "$dir" -B "$dir/build" -DCMAKE_BUILD_TYPE=Release
    cmake --build "$dir/build" -j "$JOBS"
    sudo cmake --install "$dir/build"
    sudo ldconfig
}

stage_cinepi_raw() {
    log "cinepi-raw"
    local dir="$SRC_DIR/cinepi-raw"
    checkout "$CINEPI_RAW_REPO" "$CINEPI_RAW_REF" "$dir"

    export PKG_CONFIG_PATH="$SRC_DIR/cpp-mjpeg-streamer/build:${PKG_CONFIG_PATH:-}"
    meson_setup "$dir/build" "$dir" --buildtype=release
    ninja -C "$dir/build" -j "$JOBS"
    sudo env PKG_CONFIG_PATH="$PKG_CONFIG_PATH" meson install -C "$dir/build"
    sudo ldconfig
}

stage_redis_seed() {
    log "Redis white balance defaults"
    sudo systemctl enable --now redis-server
    redis-cli SET cg_rb 3.5,1.5 >/dev/null
    redis-cli PUBLISH cp_controls cg_rb >/dev/null
    printf '    cg_rb = %s\n' "$(redis-cli GET cg_rb)"
}

stage_verify() {
    log "Verify"
    local bin; bin=$(command -v cinepi-raw || true)
    [[ -n "$bin" ]] || die "cinepi-raw not on PATH"
    printf '    cinepi-raw: %s\n' "$bin"

    local rpicam; rpicam=$(command -v rpicam-hello || true)
    if [[ "$rpicam" != /usr/local/bin/* ]]; then
        warn "rpicam-hello resolves to $rpicam, not the freshly built /usr/local/bin one"
    fi

    cinepi-raw --list-cameras
}

# The preview draws from the lores stream; without it the screen stays black.
stage_preview() {
    log "HDMI preview (${PREVIEW_MS} ms)"
    cinepi-raw --cam-port "$CAM_PORT" \
        --mode "$CAM_MODE" --width "$CAM_WIDTH" --height "$CAM_HEIGHT" \
        --lores-width "$LORES_WIDTH" --lores-height "$LORES_HEIGHT" \
        -p "$PREVIEW_RECT" \
        -t "$PREVIEW_MS"
}

STAGES=(
    preflight
    deps
    libtiff_compat
    redis_pp
    libcamera
    mjpeg_streamer
    cinepi_raw
    redis_seed
    verify
)

main() {
    if [[ "${1:-}" == "list" ]]; then
        printf '%s\n' "${STAGES[@]}"
        return
    fi
    if [[ $# -gt 0 ]]; then
        for name in "$@"; do
            declare -F "stage_$name" >/dev/null || die "unknown stage: $name"
        done
        for name in "$@"; do "stage_$name"; done
        return
    fi
    for name in "${STAGES[@]}"; do "stage_$name"; done
    log "Done"
}

main "$@"
