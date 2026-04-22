#!/usr/bin/env bash
set -Eeuo pipefail

PYTHON_VERSION="3.13"
SKIP_LATEX=0
FORCE_RECREATE_VENV=0
SKIP_MANIM_PHYSICS=0

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT=""
LOG_FILE=""
STAGE_COUNTER=0

usage() {
  cat <<USAGE
Usage: $(basename "$0") [options]

Options:
  --python-version <ver>     Python version to install with uv (default: 3.13)
  --skip-latex               Skip LaTeX checks
  --force-recreate-venv      Remove and recreate .venv
  --skip-manim-physics       Do not install manim-physics editable package
  -h, --help                 Show this help
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --python-version)
      PYTHON_VERSION="${2:?Missing value for --python-version}"
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
      SKIP_MANIM_PHYSICS=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

write_log() {
  local level="$1" color="$2" msg="$3"
  local ts line
  ts="$(date '+%Y-%m-%d %H:%M:%S')"
  line="[$ts] [$level] $msg"
  [[ -n "$LOG_FILE" ]] && printf '%s\n' "$line" >> "$LOG_FILE"
  printf '\033[%sm%s\033[0m\n' "$color" "$line"
}
write_info() { write_log "INFO" "36" "$1"; }
write_ok()   { write_log " OK " "32" "$1"; }
write_warn() { write_log "WARN" "33" "$1"; }
write_fail() { write_log "FAIL" "31" "$1"; }

on_error() {
  local exit_code=$?
  write_fail "Script aborted on line $1 with exit code $exit_code"
  exit "$exit_code"
}
trap 'on_error $LINENO' ERR

get_project_root() {
  # Match setup.ps1 resolution order: parent of script dir, script dir, then current dir.
  local candidates=("$(dirname "$SCRIPT_DIR")" "$SCRIPT_DIR" "$PWD")
  local c
  for c in "${candidates[@]}"; do
    [[ -z "$c" ]] && continue
    if [[ -d "$c/.git" || -f "$c/pyproject.toml" || -f "$c/requirements.txt" || -f "$c/setup.py" ]]; then
      printf '%s\n' "$c"
      return 0
    fi
  done
  # If no markers are found, prefer the parent of the script directory.
  printf '%s\n' "$(dirname "$SCRIPT_DIR")"
}

initialize_logging() {
  local log_dir
  log_dir="$PROJECT_ROOT/logs"
  mkdir -p "$log_dir"
  LOG_FILE="$log_dir/setup_$(date '+%Y-%m-%d_%H-%M-%S').log"
  : > "$LOG_FILE"
}

invoke_stage() {
  local name="$1"
  STAGE_COUNTER=$((STAGE_COUNTER + 1))
  echo
  write_info '============================================================'
  write_info "STEP $STAGE_COUNTER: $name"
  write_info '============================================================'
  local start end dur
  start=$(date +%s)
  "$@" >/dev/null 2>&1 && : || true
}

run_stage() {
  local name="$1"; shift
  STAGE_COUNTER=$((STAGE_COUNTER + 1))
  echo
  write_info '============================================================'
  write_info "STEP $STAGE_COUNTER: $name"
  write_info '============================================================'
  local start end dur
  start=$(date +%s)
  "$@"
  end=$(date +%s)
  dur=$((end - start))
  write_ok "$name finished in ${dur}s"
}

command_available() {
  command -v "$1" >/dev/null 2>&1
}

run_logged() {
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

  [[ -n "$description" ]] && write_info "$description"
  write_info "> $*"

  set +e
  "$@" 2>&1 | tee -a "$LOG_FILE"
  local cmd_status=${PIPESTATUS[0]}
  set -e

  if [[ $allow_failure -eq 0 && $cmd_status -ne 0 ]]; then
    write_fail "Command failed with exit code $cmd_status: $*"
    return "$cmd_status"
  fi
  return 0
}

ensure_uv_installed() {
  if command_available uv; then
    write_ok "uv is available: $(uv --version)"
    return 0
  fi

  write_warn 'uv was not found in PATH. Installing uv from the official installer.'
  if command_available curl; then
    run_logged --description 'Installing uv' -- sh -c 'curl -LsSf https://astral.sh/uv/install.sh | sh'
  elif command_available wget; then
    run_logged --description 'Installing uv' -- sh -c 'wget -qO- https://astral.sh/uv/install.sh | sh'
  else
    write_fail 'Neither curl nor wget is available, cannot install uv automatically.'
    return 1
  fi

  export PATH="$HOME/.local/bin:$PATH"
  command_available uv || { write_fail 'uv installation completed, but uv is still unavailable in PATH.'; return 1; }
  write_ok "uv installed successfully: $(uv --version)"
}

ensure_python_installed() {
  run_logged --description "Installing Python $PYTHON_VERSION through uv" -- uv python install "$PYTHON_VERSION"
}

ensure_project_metadata() {
  if [[ ! -f "$PROJECT_ROOT/pyproject.toml" ]]; then
    run_logged --description 'Initializing uv project metadata' -- uv init --bare "$PROJECT_ROOT"
  else
    write_ok 'pyproject.toml already exists; skipping uv init.'
  fi

  if [[ ! -f "$PROJECT_ROOT/uv.lock" ]]; then
    run_logged --description 'Creating uv lockfile' -- uv lock --project "$PROJECT_ROOT"
  else
    write_ok 'uv.lock already exists; skipping uv lock.'
  fi
}

ensure_system_dependencies() {
  local packages=()
  local -a elevate=()

  if [[ ${EUID:-$(id -u)} -ne 0 ]]; then
    if command_available sudo; then
      elevate=(sudo)
    else
      write_fail 'sudo is required to install Linux system dependencies automatically.'
      return 1
    fi
  fi

  if command_available apt-get; then
    packages=(pkg-config libcairo2-dev libpango1.0-dev ffmpeg)
    run_logged --description 'Installing Linux system dependencies (apt-get update)' -- \
      "${elevate[@]}" apt-get update
    run_logged --description 'Installing Linux system dependencies for manim (apt-get install)' -- \
      "${elevate[@]}" apt-get install -y "${packages[@]}"
    return 0
  fi

  if command_available dnf; then
    packages=(pkgconf-pkg-config cairo-devel pango-devel ffmpeg)
    run_logged --description 'Installing Linux system dependencies for manim (dnf install)' -- \
      "${elevate[@]}" dnf install -y "${packages[@]}"
    return 0
  fi

  if command_available pacman; then
    packages=(pkgconf cairo pango ffmpeg)
    run_logged --description 'Installing Linux system dependencies for manim (pacman -S)' -- \
      "${elevate[@]}" pacman -S --noconfirm --needed "${packages[@]}"
    return 0
  fi

  if command_available zypper; then
    packages=(pkg-config cairo-devel pango-devel ffmpeg)
    run_logged --description 'Installing Linux system dependencies for manim (zypper install)' -- \
      "${elevate[@]}" zypper install -y "${packages[@]}"
    return 0
  fi

  write_warn 'No supported package manager found for automatic Linux dependency install.'
  write_warn 'Please install these packages manually: pkg-config, cairo dev libs, pango dev libs, ffmpeg'
}

ensure_venv() {
  local venv_path="$PROJECT_ROOT/.venv"

  if [[ $FORCE_RECREATE_VENV -eq 1 && -d "$venv_path" ]]; then
    write_warn 'Removing existing .venv because --force-recreate-venv was provided.'
    rm -rf "$venv_path"
  fi

  if [[ ! -d "$venv_path" ]]; then
    run_logged --description 'Creating virtual environment' -- uv venv --python "$PYTHON_VERSION" "$venv_path"
  else
    write_ok "Virtual environment already exists: $venv_path"
  fi
}

sync_dependencies() {
  local venv_python="$PROJECT_ROOT/.venv/bin/python"
  [[ -x "$venv_python" ]] || { write_fail "Virtual environment Python executable not found: $venv_python"; return 1; }

  run_logged --description 'Installing dependencies with uv' -- \
    uv pip install --python "$venv_python" manim manim-slides PySide6
}

install_manim_physics() {
  if [[ $SKIP_MANIM_PHYSICS -eq 1 ]]; then
    write_warn 'Skipping manim-physics installation because --skip-manim-physics was provided.'
    return 0
  fi

  local repo_dir="$PROJECT_ROOT/manim-physics"
  local venv_python="$PROJECT_ROOT/.venv/bin/python"

  if [[ ! -d "$repo_dir/.git" ]]; then
    run_logged --description 'Cloning manim-physics repository' -- \
      git clone https://github.com/SirJamesClarkMaxwell/manim-physics.git "$repo_dir"
  else
    write_ok "manim-physics repository already exists: $repo_dir"
  fi

  run_logged --description 'Installing manim-physics in editable mode' -- \
    uv pip install --python "$venv_python" -e "$repo_dir"
}

ensure_latex_installed() {
  if [[ $SKIP_LATEX -eq 1 ]]; then
    write_warn 'Skipping LaTeX checks because --skip-latex was provided.'
    return 0
  fi

  if command_available latex || command_available pdflatex || command_available xelatex; then
    write_ok 'LaTeX commands are available'
    return 0
  fi

  write_warn 'No LaTeX executable was found in PATH. Manim may fail when rendering LaTeX scenes.'
  if command_available apt; then
    write_warn 'Ubuntu/Debian suggestion: sudo apt install texlive-full'
  elif command_available dnf; then
    write_warn 'Fedora suggestion: sudo dnf install texlive-scheme-full'
  elif command_available pacman; then
    write_warn 'Arch suggestion: sudo pacman -S texlive-most'
  elif command_available zypper; then
    write_warn 'openSUSE suggestion: sudo zypper install texlive-scheme-full'
  fi
}

test_basic_toolchain() {
  local venv_python="$PROJECT_ROOT/.venv/bin/python"
  [[ -x "$venv_python" ]] || { write_fail "Virtual environment Python executable not found: $venv_python"; return 1; }

  run_logged --description 'Checking Python inside virtual environment' -- "$venv_python" --version
  run_logged --description 'Checking whether Manim is importable' -- "$venv_python" -c 'import manim, manim_slides; print("Manim and manim-slides imports OK")'
}

PROJECT_ROOT="$(get_project_root)"
initialize_logging

write_info "Script location : $SCRIPT_DIR"
write_info "Project root    : $PROJECT_ROOT"
write_info "Log file        : $LOG_FILE"
write_info "Target Python   : $PYTHON_VERSION"

run_stage 'Checking uv' ensure_uv_installed
run_stage 'Installing Python' ensure_python_installed
run_stage 'Ensuring project metadata' ensure_project_metadata
run_stage 'Installing Linux system dependencies' ensure_system_dependencies
run_stage 'Creating virtual environment' ensure_venv
run_stage 'Installing dependencies' sync_dependencies
run_stage 'manim-physics installation' install_manim_physics
run_stage 'Ensuring LaTeX is installed' ensure_latex_installed
run_stage 'Running sanity checks' test_basic_toolchain

echo
write_ok 'Setup finished successfully.'
write_info 'To activate the environment manually, run:'
printf '%s\n' "source \"$PROJECT_ROOT/.venv/bin/activate\""
