# Setup and Test Script for Windows (PowerShell)

param()

$green = 'Green'
$red = 'Red'
$yellow = 'Yellow'
$cyan = 'Cyan'

function Write-Success([string]$Message) {
    Write-Host "[OK] $Message" -ForegroundColor $green
}

function Write-Error-Custom([string]$Message) {
    Write-Host "[ERROR] $Message" -ForegroundColor $red
}

function Write-Warning-Custom([string]$Message) {
    Write-Host "[WARNING] $Message" -ForegroundColor $yellow
}

function Check-UV-Installed {
    try {
        $version = (& uv --version 2>&1)
        Write-Success "uv is already installed: $version"
        return $true
    }
    catch {
        Write-Error-Custom "uv is not installed"
        return $false
    }
}

function Install-UV {
    Write-Host "`nInstalling uv from official source..." -ForegroundColor $cyan
    try {
        powershell -ExecutionPolicy Bypass -c "irm https://astral.sh/uv/install.ps1 | iex"
        Write-Success "uv installed successfully"
        return $true
    }
    catch {
        Write-Error-Custom "Failed to install uv"
        return $false
    }
}

function Test-LaTeX-Installed {
    foreach ($commandName in @('latex', 'pdflatex', 'dvisvgm')) {
        if (-not (Get-Command $commandName -ErrorAction SilentlyContinue)) {
            return $false
        }
    }

    return $true
}

function Install-LaTeX {
    Write-Host "`nInstalling LaTeX support..." -ForegroundColor $cyan

    if (Get-Command winget -ErrorAction SilentlyContinue) {
        Write-Host "Using winget to install MiKTeX..." -ForegroundColor $yellow
        & winget install --id MiKTeX.MiKTeX -e --source winget --accept-package-agreements --accept-source-agreements 2>&1 | ForEach-Object { Write-Host $_ }
        if ($LASTEXITCODE -eq 0) {
            return $true
        }

        Write-Warning-Custom "winget install failed; please install MiKTeX manually from https://miktex.org/download"
        return $false
    }

    Write-Warning-Custom "winget is not available; please install MiKTeX manually from https://miktex.org/download"
    return $false
}

function Get-ProjectRoot {
    $scriptPath = $PSScriptRoot
    $projectRoot = Split-Path -Parent $scriptPath
    return $projectRoot
}

# Get project root
$projectRoot = Get-ProjectRoot
Write-Host "`nProject root: $projectRoot" -ForegroundColor $cyan
Set-ExecutionPolicy -ExecutionPolicy ByPass -Scope CurrentUser

# Step 1: Check uv
Write-Host "`n============================================================" -ForegroundColor $cyan
Write-Host "STEP 1: Checking if uv is installed" -ForegroundColor $cyan
Write-Host "============================================================" -ForegroundColor $cyan

if (-not (Check-UV-Installed)) {
    Write-Host "`nInstalling uv..." -ForegroundColor $cyan
    if (-not (Install-UV)) {
        Write-Error-Custom "Failed to install uv"
        exit 1
    }
    
    # Refresh PATH after installation
    Write-Host "Refreshing PATH..." -ForegroundColor $yellow
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
}

# Step 2: Update project
Write-Host "`n============================================================" -ForegroundColor $cyan
Write-Host "STEP 2: Ensuring Python is installed via uv" -ForegroundColor $cyan
Write-Host "============================================================" -ForegroundColor $cyan

Push-Location $projectRoot
Write-Host "Running: uv python install" -ForegroundColor Yellow
& uv python install 2>&1 | ForEach-Object { Write-Host $_ }

if ($LASTEXITCODE -ne 0) {
    Write-Warning-Custom "Python installation via uv had issues, but continuing..."
}
Pop-Location

# Step 3: Update project
Write-Host "`n============================================================" -ForegroundColor $cyan
Write-Host "STEP 3: Updating project with uv sync" -ForegroundColor $cyan
Write-Host "============================================================" -ForegroundColor $cyan

Push-Location $projectRoot
Write-Host "Running: uv sync" -ForegroundColor Yellow
& uv sync 2>&1 | ForEach-Object { Write-Host $_ }
Pop-Location

# Step 4: Install dependencies
Write-Host "`n============================================================" -ForegroundColor $cyan
Write-Host "STEP 4: Installing dependencies and manim-physics" -ForegroundColor $cyan
Write-Host "============================================================" -ForegroundColor $cyan

Push-Location $projectRoot
Write-Host "Running: uv add manim manim-slides PyQt6 --upgrade" -ForegroundColor Yellow
& uv add manim manim-slides PyQt6 --upgrade 2>&1 | ForEach-Object { Write-Host $_ }

if ($LASTEXITCODE -ne 0) {
    Write-Error-Custom "Failed to install packages"
    Pop-Location
    exit 1
}

Write-Success "Dependencies installed"

if (-not (Test-Path (Join-Path $projectRoot "manim-physics"))) {
    Write-Host "Running: git clone https://github.com/sjcmdev/manim-physics.git" -ForegroundColor Yellow
    & git clone https://github.com/sjcmdev/manim-physics.git 2>&1 | ForEach-Object { Write-Host $_ }
}

$physicsPyproject = Join-Path $projectRoot "manim-physics\pyproject.toml"
if (Test-Path $physicsPyproject) {
    Write-Host "Patching manim-physics compatibility constraints" -ForegroundColor Yellow
    $content = Get-Content $physicsPyproject -Raw
    $content = $content -replace 'python = ">=3\.9,<3\.13"', 'python = ">=3.9"'
    $content = $content -replace 'python = ">=3\.9,"', 'python = ">=3.9"'
    $content = $content -replace 'manim = "~0\.18\.0"', 'manim = ">=0.20"'
    Set-Content -Path $physicsPyproject -Value $content -NoNewline
}

Write-Host "Running: uv run python -m ensurepip --upgrade" -ForegroundColor Yellow
& uv run python -m ensurepip --upgrade 2>&1 | ForEach-Object { Write-Host $_ }

Write-Host "Running: uv run python -m pip install -e ./manim-physics" -ForegroundColor Yellow
& uv run python -m pip install -e ./manim-physics 2>&1 | ForEach-Object { Write-Host $_ }

if ($LASTEXITCODE -ne 0) {
    Write-Error-Custom "Failed to install editable manim-physics"
    Pop-Location
    exit 1
}

Write-Success "Editable manim-physics installed"
Pop-Location

# Step 5: Ensure LaTeX is available
Write-Host "`n============================================================" -ForegroundColor $cyan
Write-Host "STEP 5: Ensuring LaTeX is installed" -ForegroundColor $cyan
Write-Host "============================================================" -ForegroundColor $cyan

if (-not (Test-LaTeX-Installed)) {
    if (-not (Install-LaTeX)) {
        Write-Warning-Custom "LaTeX is still missing. Manim may fail until a TeX distribution is installed."
    }
    else {
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
    }
}

# Step 6: Run test
Write-Host "`n============================================================" -ForegroundColor $cyan
Write-Host "STEP 6: Running test script" -ForegroundColor $cyan
Write-Host "============================================================" -ForegroundColor $cyan

$testFile = Join-Path $projectRoot "manim-test.py"
if (Test-Path $testFile) {
    Push-Location $projectRoot
    Write-Host "Running: uv run python manim-test.py " -ForegroundColor Yellow
    & uv run python $testFile 2>&1 | ForEach-Object { Write-Host $_ }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Test completed successfully"
    }
    else {
        Write-Warning-Custom "Test completed with exit code: $LASTEXITCODE"
    }
    Pop-Location
}
else {
    Write-Warning-Custom "Test file not found: $testFile"
}

Write-Host "`n============================================================" -ForegroundColor $cyan
Write-Host "ALL STEPS COMPLETED" -ForegroundColor $cyan
Write-Host "============================================================" -ForegroundColor $cyan
