Sir James Clark Maxwell
franek1334
Code

Uwe — 31.03.2026 19:24
I think we should do that. I already have the invited talk - let's discuss this further after Easter...
Sir James Clark Maxwell — 31.03.2026 19:26
In which proportion we would split  the lecture and live coding is totally up to you. I will try to make some animations during the breake. Maybe even something what would show some concepts of manim
Critical points, scene, positioning of the mobjects
I hope I have time for this
Sir James Clark Maxwell — 6.04.2026 16:10
Guesz who is back with his programming video
https://youtu.be/HDVl8-cy928
YouTube
Bog
Beginner VS competitive programming
Obraz
Sir James Clark Maxwell — 6.04.2026 16:18
I want to warn you
Your brain will hurt
I've warched it and I need to go to hospital, it is emergency. I don't know what my name is ...
Bog and competitative programing 
What can go wrong ...
Sir James Clark Maxwell — 6.04.2026 18:56
I literally had a short-circuit in my brain when i was watchig it
Sir James Clark Maxwell — 11:19
Do you have a minute right-now?
Sir James Clark Maxwell — 11:36
I have added you to a repo for PTEE-2026 
There I will create a installation instruction, and I will add code examples (with manim slides)
and tbh, I would create a one installation script (without latex) so peoples will not have to deal with instalation process (one for win one for linux) it will detect uv, python, and install all needed things
Sir James Clark Maxwell — 12:52
what do you think about those files?
import timeit
import subprocess

from manim import *
from manim_slides import Slide

manim-test.py
4 KB
# Setup and Test Script for Windows (PowerShell)

param()

$green = 'Green'
$red = 'Red'

setup_and_test.ps1
9 KB
#!/bin/bash
# Setup and Test Script for Unix-like systems (Linux, macOS)
# Checks uv installation, updates project, installs dependencies, and runs tests

set -e

setup_and_test.sh
8 KB
Uwe — 12:53
nice - I was recently thinking about things as well, but unlike my usual lecture period March-May I hardly have any time even to breathe right now. I still have ongoing oral exams and lab-reports to correct, while I also need to get working on an own project and there are tons of pedagogical meetings within different study-programs...
Sir James Clark Maxwell — 12:54
yeah, I know how to be in the eye of storm
Uwe — 12:54
I need to have a look at Manim-slides again and I will have a look at your installation scripts - might have both Linux and Windows platforms to test.
Sir James Clark Maxwell — 12:55
I am involved right now in big project which require a lot of c++ things and building core-systems for profesional GUI application...
Sir James Clark Maxwell — 12:55
I am gonna write some example scenes that would show some manim concepts
(with comments)
and maybe i will write a presentation for us
Uwe — 12:56
The quick scene which I did on Sunday about the radioactive decay might be a nice example as well, which probably most physics teachers can relate to
Sir James Clark Maxwell — 12:57
I will start building examples from manim basics
adding objects, positioning, simple animations, and movement
those would not be related to physics, I guess
We have to decide how we gonna divide material between us in the "lecture" part and coding part
tbh, I have no idea how to draw this line
Uwe — 13:00
I also need to write 3 course reports, answering the course evaluations by the students. In one course I have one student who apparently was extremely critical about the communication of criteria and deadlines for the project part... it's only that I had two seminars and I put everything from the seminars online afterwards, but less than 1/3 of the students showed up for the seminars...
Sir James Clark Maxwell — 13:00
...
no words
I will do what I can, and I will push things into second repo (I have to create it) it will be for our stuff and dev things
﻿
#!/bin/bash
# Setup and Test Script for Unix-like systems (Linux, macOS)
# Checks uv installation, updates project, installs dependencies, and runs tests

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

write_header() {
    echo -e "\n${CYAN}============================================================${NC}"
    echo -e "${CYAN}📋 $1${NC}"
    echo -e "${CYAN}============================================================${NC}"
}

write_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

write_error() {
    echo -e "${RED}❌ $1${NC}"
}

write_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

run_command() {
    local cmd=$1
    local description=$2
    local critical=${3:-true}
    
    if [ -n "$description" ]; then
        echo -e "\n${CYAN}🔧 $description${NC}"
    fi
    
    echo "Running: $cmd"
    
    if eval "$cmd"; then
        write_success "Command completed successfully"
        return 0
    else
        if [ "$critical" = true ]; then
            write_error "Command failed with exit code $?"
            return 1
        else
            write_warning "Command failed (continuing...)"
            return 0
        fi
    fi
}

check_uv_installed() {
    if command -v uv &> /dev/null; then
        local version=$(uv --version)
        write_success "uv is already installed: $version"
        return 0
    else
        write_error "uv is not installed"
        return 1
    fi
}

install_uv() {
    echo -e "\n${CYAN}🔧 Installing uv from official source...${NC}"
    if curl -LsSf https://astral.sh/uv/install.sh | sh; then
        write_success "uv installed successfully"
        return 0
    else
        write_error "Failed to install uv"
        return 1
    fi
}

check_latex_installed() {
    command -v latex >/dev/null 2>&1 && command -v pdflatex >/dev/null 2>&1 && command -v dvisvgm >/dev/null 2>&1
}

install_latex_linux() {
    local distro_id=""

    if [ -f /etc/os-release ]; then
        # shellcheck disable=SC1091
        . /etc/os-release
        distro_id="$ID"
    fi

    case "$distro_id" in
        ubuntu|debian|linuxmint)
            sudo apt-get update
            sudo apt-get install miktex
            ;;
        fedora|rhel|rocky|centos)
            sudo dnf install miktex
            ;;
        opensuse*|sles)
            sudo zypper --non-interactive install miktex
            ;;
        arch)
            sudo pacman -S --needed --noconfirm miktex
        *)
            write_warning "Unsupported Linux distribution for automatic LaTeX installation: ${distro_id:-unknown}"
            write_warning "Install a TeX distribution manually, such as TeX Live, then rerun the script."
            return 1
            ;;
    esac
}

install_latex_macos() {
    if command -v brew >/dev/null 2>&1; then
        brew install --cask mactex-no-gui
        return 0
    fi

    write_warning "Homebrew is not available on macOS. Install MacTeX manually, then rerun the script."
    return 1
}

install_latex_windows() {
    if command -v winget >/dev/null 2>&1; then
        winget install --id MiKTeX.MiKTeX -e --source winget --accept-package-agreements --accept-source-agreements
        return $?
    fi

    write_warning "winget is not available. Install MiKTeX manually from https://miktex.org/download, then rerun the script."
    return 1
}

install_latex() {
    case "$(uname -s)" in
        Linux)
            install_latex_linux
            ;;
        Darwin)
            install_latex_macos
            ;;
        MINGW*|MSYS*|CYGWIN*)
            install_latex_windows
            ;;
        *)
            write_warning "Unsupported platform for automatic LaTeX installation: $(uname -s)"
            write_warning "Install a TeX distribution manually, then rerun the script."
            return 1
            ;;
    esac
}

get_project_root() {
    # scripts/setup_and_test.sh -> go up 1 level to project root
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local project_root="$(dirname "$script_dir")"
    echo "$project_root"
}

main() {
    local project_root=$(get_project_root)
    echo -e "\n${CYAN}🚀 Project root: $project_root${NC}"
    
    # Step 1: Check if uv is installed
    write_header "STEP 1: Checking if uv is installed"
    
    if ! check_uv_installed; then
        echo -e "\n${CYAN}🔧 uv not found. Installing...${NC}"
        if ! install_uv; then
            write_error "Failed to install uv"
            exit 1
        fi
        # Refresh PATH
        export PATH="$HOME/.local/bin:$PATH"
    fi
    
    # Step 2: Ensure Python is installed via uv
    write_header "STEP 2: Ensuring Python is installed via uv"
    
    cd "$project_root"
    if ! run_command "uv python install" "Installing Python via uv" false; then
        write_warning "Python installation via uv had issues, but continuing..."
    fi
    
    # Step 3: Update project with uv
    write_header "STEP 3: Updating project with uv sync"
    
    cd "$project_root"
    if ! run_command "uv sync" "Running 'uv sync' to update dependencies" false; then
        write_warning "uv sync had issues, but continuing..."
    fi
    
    # Step 4: Install dependencies
    write_header "STEP 4: Installing dependencies and manim-physics"
    
    cd "$project_root"
    if ! run_command "uv add manim manim-slides PyQt6 --upgrade" "Installing manim packages and PyQt6" true; then
        write_error "Failed to install packages"
        exit 1
    fi

    if [ ! -d "$project_root/manim-physics" ]; then
        if ! run_command "git clone https://github.com/sjcmdev/manim-physics.git" "Cloning manim-physics" true; then
            write_error "Failed to clone manim-physics"
            exit 1
        fi
    fi

    local physics_pyproject="$project_root/manim-physics/pyproject.toml"
    if [ -f "$physics_pyproject" ]; then
        write_warning "Patching manim-physics compatibility constraints"
        perl -0pi -e 's/python = ">=3\.9,<3\.13"/python = ">=3.9"/g; s/python = ">=3\.9,"/python = ">=3.9"/g; s/manim = "~0\.18\.0"/manim = ">=0.20"/g' "$physics_pyproject"
    fi

    if ! run_command "uv run python -m ensurepip --upgrade" "Ensuring pip in uv environment" true; then
        write_error "Failed to enable pip in uv environment"
        exit 1
    fi

    if ! run_command "uv run python -m pip install -e ./manim-physics" "Installing editable manim-physics" true; then
        write_error "Failed to install editable manim-physics"
        exit 1
    fi
    
    # Step 5: Ensure LaTeX is available
    write_header "STEP 5: Ensuring LaTeX is installed"

    if ! check_latex_installed; then
        if ! install_latex; then
            write_warning "LaTeX is still missing. Manim may fail until a TeX distribution is installed."
        fi
    fi

    # Step 6: Run test script
    write_header "STEP 6: Running test script"
    
    local test_file="$project_root/manim-test.py"
    if [ -f "$test_file" ]; then
        cd "$project_root"
        if ! run_command "uv run python \"$test_file\"" "Running manim-test.py" true; then
            write_warning "Test script completed with warnings"
        fi
    else
        write_warning "Test file not found: $test_file"
    fi
    
    write_header "✅ ALL STEPS COMPLETED SUCCESSFULLY!"
}

# Run main function
main
