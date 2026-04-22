#!/usr/bin/env bash
set -Eeuo pipefail

PYTHON_VERSION="3.13"
SKIP_LATEX=0
FORCE_RECREATE_VENV=0
INSTALL_MANIM_PHYSICS=1
MANIM_PHYSICS_REPO="https://github.com/SirJamesClarkMaxwell/manim-physics.git"

STAGE_COUNTER=0
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT=""
LOG_FILE=""

usage() {
    cat <<USAGE
Usage: $(basename "$0") [options]

Options:
  --python-version <version>   Python version to install with uv (default: 3.13)
  --skip-latex                 Skip LaTeX availability checks
  --force-recreate-venv        Remove and recreate .venv
  --skip-manim-physics         Do not clone/install manim-physics
  -h, --help                   Show this help
USAGE
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --python-version)
            [[ $# -ge 2 ]] || { echo "Missing value for --python-version" >&2; exit 1; }
            PYTHON_VERSION="$2"
            shift 2
            ;;
        --skip-latex)
            SKIP_LATEX=1
            shift
            ;;
        --force-recreate-venv)
            FORCE_RECREATE_VENV=1
            shift
            ;;
        --skip-manim-physics)
            INSTALL_MANIM_PHYSICS=0
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown argument: $1" >&2
            usage >&2
            exit 1
            ;;
    esac
done

get_project_root() {
    local candidates=(
        "$(cd "$SCRIPT_DIR/.." 2>/dev/null && pwd || true)"
        "$SCRIPT_DIR"
        "$(pwd)"
    )
    local candidate
    for candidate in "${candidates[@]}"; do
        [[ -n "$candidate" ]] || continue
        [[ -d "$candidate/.git" ]] && { printf '%s\n' "$candidate"; return; }
        [[ -f "$candidate/pyproject.toml" ]] && { printf '%s\n' "$candidate"; return; }
        [[ -f "$candidate/requirements.txt" ]] && { printf '%s\n' "$candidate"; return; }
        [[ -f "$candidate/setup.py" ]] && { printf '%s\n' "$candidate"; return; }
    done
    cd "$SCRIPT_DIR/.." 2>/dev/null && pwd || pwd
}

initialize_logging() {
    local log_dir="$PROJECT_ROOT/logs"
    mkdir -p "$log_dir"
    LOG_FILE="$log_dir/setup_$(date '+%Y-%m-%d_%H-%M-%S').log"
    : > "$LOG_FILE"
}

write_log() {
    local level="$1"
    local color="$2"
    local message="$3"
    local ts line
    ts="$(date '+%Y-%m-%d %H:%M:%S')"
    line="[$ts] [$level] $message"
    printf '%s\n' "$line" >> "$LOG_FILE"
    printf '\033[%sm%s\033[0m\n' "$color" "$line"
}

write_info() { write_log "INFO" "36" "$1"; }
write_ok()   { write_log " OK " "32" "$1"; }
write_warn() { write_log "WARN" "33" "$1"; }
write_fail() { write_log "FAIL" "31" "$1"; }

on_error() {
    local exit_code=$?
    local line_no=${1:-unknown}
    write_fail "Script aborted on line $line_no with exit code $exit_code"
    exit "$exit_code"
}
trap 'on_error $LINENO' ERR

invoke_stage() {
    local name="$1"
    shift
    STAGE_COUNTER=$((STAGE_COUNTER + 1))
    printf '\n'
    write_info '============================================================'
    write_info "STEP $STAGE_COUNTER: $name"
    write_info '============================================================'
    local start end elapsed
    start=$(date +%s)
    "$@"
    end=$(date +%s)
    elapsed=$((end - start))
    write_ok "$name finished in ${elapsed}s"
}

command_available() {
    command -v "$1" >/dev/null 2>&1
}

invoke_logged_command() {
    local description=""
    local allow_failure=0

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --description)
                description="$2"
                shift 2
                ;;
            --allow-failure)
                allow_failure=1
                shift
                ;;
            --)
                shift
                break
                ;;
            *)
                break
                ;;
        esac
    done

    local cmd=("$@")
    [[ ${#cmd[@]} -gt 0 ]] || { write_fail "invoke_logged_command called without command"; return 1; }

    [[ -n "$description" ]] && write_info "$description"
    write_info "> ${cmd[*]}"

    set +e
    "${cmd[@]}" 2>&1 | tee -a "$LOG_FILE"
    local cmd_status=${PIPESTATUS[0]}
    set -e

    if [[ $allow_failure -eq 0 && $cmd_status -ne 0 ]]; then
        write_fail "Command failed with exit code $cmd_status: ${cmd[*]}"
        return "$cmd_status"
    fi
    return 0
}

ensure_xcode_clt() {
    if xcode-select -p >/dev/null 2>&1; then
        write_ok 'Xcode Command Line Tools are available'
        return
    fi

    write_warn 'Xcode Command Line Tools are not installed. Some builds may fail.'
    write_info 'Install them with: xcode-select --install'
}

ensure_homebrew() {
    if command_available brew; then
        write_ok "Homebrew is available: $(brew --version | head -n 1)"
        return
    fi

    write_warn 'Homebrew was not found in PATH. Installing Homebrew from the official installer.'
    invoke_logged_command --description 'Installing Homebrew' -- /bin/bash -c "
NONINTERACTIVE=1 \
$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)
"

    if [[ -x /opt/homebrew/bin/brew ]]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
    elif [[ -x /usr/local/bin/brew ]]; then
        eval "$(/usr/local/bin/brew shellenv)"
    fi

    command_available brew || { write_fail 'Homebrew installation completed, but brew is still unavailable in PATH.'; return 1; }
    write_ok "Homebrew installed successfully: $(brew --version | head -n 1)"
}

ensure_uv_installed() {
    if command_available uv; then
        write_ok "uv is available: $(uv --version)"
        return
    fi

    write_warn 'uv was not found in PATH. Installing uv from the official installer.'
    if command_available curl; then
        invoke_logged_command --description 'Installing uv' -- bash -c 'curl -LsSf https://astral.sh/uv/install.sh | sh'
    else
        ensure_homebrew
        invoke_logged_command --description 'Installing uv via Homebrew' -- brew install uv
    fi

    export PATH="$HOME/.local/bin:$HOME/.cargo/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
    command_available uv || { write_fail 'uv installation completed, but the uv command is still unavailable in PATH.'; return 1; }
    write_ok "uv installed successfully: $(uv --version)"
}

ensure_python_installed() {
    invoke_logged_command --description "Installing Python $PYTHON_VERSION through uv" -- uv python install "$PYTHON_VERSION"
}

ensure_venv() {
    local venv_path="$PROJECT_ROOT/.venv"

    if [[ $FORCE_RECREATE_VENV -eq 1 && -d "$venv_path" ]]; then
        write_warn 'Removing existing .venv because --force-recreate-venv was provided.'
        rm -rf "$venv_path"
    fi

    if [[ ! -d "$venv_path" ]]; then
        if [[ ! -f "$PROJECT_ROOT/pyproject.toml" ]]; then
            invoke_logged_command --description 'Initializing uv project metadata' -- uv init --bare "$PROJECT_ROOT"
        fi
        invoke_logged_command --description 'Creating virtual environment' -- uv venv --python "$PYTHON_VERSION" "$venv_path"
    else
        write_ok "Virtual environment already exists: $venv_path"
    fi
}

sync_dependencies() {
    local py="$PROJECT_ROOT/.venv/bin/python"
    [[ -x "$py" ]] || { write_fail "Virtual environment Python executable was not found: $py"; return 1; }

    invoke_logged_command --description 'Upgrading pip' -- "$py" -m pip install --upgrade pip
    invoke_logged_command --description 'Installing fallback dependencies' -- uv pip install --python "$py" manim manim-slides PySide6 qtpy
}

install_manim_physics() {
    [[ $INSTALL_MANIM_PHYSICS -eq 1 ]] || { write_warn 'Skipping manim-physics installation.'; return; }

    local repo_dir="$PROJECT_ROOT/manim-physics"
    local py="$PROJECT_ROOT/.venv/bin/python"

    if [[ ! -d "$repo_dir/.git" ]]; then
        invoke_logged_command --description 'Cloning manim-physics repository' -- git clone "$MANIM_PHYSICS_REPO" "$repo_dir"
    else
        write_ok "manim-physics repository already exists: $repo_dir"
    fi

    invoke_logged_command --description 'Installing manim-physics in editable mode' -- uv pip install --python "$py" -e "$repo_dir"
}

ensure_latex_installed() {
    if [[ $SKIP_LATEX -eq 1 ]]; then
        write_warn 'Skipping LaTeX checks because --skip-latex was provided.'
        return
    fi

    local found=0
    local cmd
    for cmd in latex pdflatex xelatex; do
        if command_available "$cmd"; then
            found=1
            break
        fi
    done

    if [[ $found -eq 1 ]]; then
        write_ok 'LaTeX commands are available'
        return
    fi

    write_warn 'No LaTeX executable was found in PATH. Manim may fail when rendering LaTeX scenes.'
    if command_available brew; then
        write_info 'Suggested install: brew install --cask mactex-no-gui'
    else
        write_info 'Install MacTeX or BasicTeX, then ensure latex/pdflatex is in PATH.'
    fi
}

test_basic_toolchain() {
    local py="$PROJECT_ROOT/.venv/bin/python"
    [[ -x "$py" ]] || { write_fail "Virtual environment Python executable was not found: $py"; return 1; }

    invoke_logged_command --description 'Checking Python inside virtual environment' -- "$py" --version
    invoke_logged_command --description 'Checking whether Manim is importable' -- "$py" -c 'import manim; import manim_slides; import qtpy; print("qtpy API =", qtpy.API_NAME)' --allow-failure
}

PROJECT_ROOT="$(get_project_root)"
initialize_logging

write_info "Script location : $SCRIPT_DIR"
write_info "Project root    : $PROJECT_ROOT"
write_info "Log file        : $LOG_FILE"
write_info "Target Python   : $PYTHON_VERSION"

invoke_stage 'Checking Xcode Command Line Tools' ensure_xcode_clt
invoke_stage 'Checking Homebrew' ensure_homebrew
invoke_stage 'Checking uv' ensure_uv_installed
invoke_stage 'Installing Python' ensure_python_installed
invoke_stage 'Creating virtual environment' ensure_venv
invoke_stage 'Installing dependencies' sync_dependencies
invoke_stage 'manim-physics installation' install_manim_physics
invoke_stage 'Ensuring LaTeX is installed' ensure_latex_installed
invoke_stage 'Running sanity checks' test_basic_toolchain

printf '\n'
write_ok 'Setup finished successfully.'
write_info 'To activate the environment manually, run:'
printf 'source %q\n' "$PROJECT_ROOT/.venv/bin/activate"
