param(
    [string]$PythonVersion = '3.13',
    [switch]$SkipLaTeX,
    [switch]$ForceRecreateVenv
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$script:StageCounter = 0
$script:ProjectRoot = $null
$script:LogFile = $null

function Refresh-Path {
    $machinePath = [Environment]::GetEnvironmentVariable('Path', 'Machine')
    $userPath = [Environment]::GetEnvironmentVariable('Path', 'User')

    if ([string]::IsNullOrWhiteSpace($machinePath) -and [string]::IsNullOrWhiteSpace($userPath)) {
        return
    }

    if ([string]::IsNullOrWhiteSpace($userPath)) {
        $env:Path = $machinePath
    }
    elseif ([string]::IsNullOrWhiteSpace($machinePath)) {
        $env:Path = $userPath
    }
    else {
        $env:Path = "$machinePath;$userPath"
    }
}

function Get-ProjectRoot {
    $candidates = @(
        (Split-Path -Parent $PSScriptRoot),
        $PSScriptRoot,
        (Get-Location).Path
    ) | Select-Object -Unique

    foreach ($candidate in $candidates) {
        if (-not $candidate) { continue }
        if (Test-Path (Join-Path $candidate '.git')) { return $candidate }
        if (Test-Path (Join-Path $candidate 'pyproject.toml')) { return $candidate }
        if (Test-Path (Join-Path $candidate 'requirements.txt')) { return $candidate }
        if (Test-Path (Join-Path $candidate 'setup.py')) { return $candidate }
    }

    return (Split-Path -Parent $PSScriptRoot)
}

function Initialize-Logging {
    $logDir = Join-Path $script:ProjectRoot 'logs'
    if (-not (Test-Path $logDir)) {
        New-Item -ItemType Directory -Path $logDir | Out-Null
    }

    $timestamp = Get-Date -Format 'yyyy-MM-dd_HH-mm-ss'
    $script:LogFile = Join-Path $logDir "setup_$timestamp.log"
    New-Item -ItemType File -Path $script:LogFile -Force | Out-Null
}

function Write-Log {
    param(
        [string]$Level,
        [string]$Message,
        [ConsoleColor]$Color = [ConsoleColor]::White
    )

    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    $line = "[$timestamp] [$Level] $Message"

    if ($script:LogFile) {
        Add-Content -Path $script:LogFile -Value $line
    }

    Write-Host $line -ForegroundColor $Color
}

function Write-Info([string]$Message) { Write-Log -Level 'INFO' -Message $Message -Color Cyan }
function Write-Ok([string]$Message) { Write-Log -Level ' OK ' -Message $Message -Color Green }
function Write-Warn([string]$Message) { Write-Log -Level 'WARN' -Message $Message -Color Yellow }
function Write-Fail([string]$Message) { Write-Log -Level 'FAIL' -Message $Message -Color Red }

function Invoke-Stage {
    param(
        [string]$Name,
        [scriptblock]$Action
    )

    $script:StageCounter++
    Write-Host ''
    Write-Info '============================================================'
    Write-Info ('STEP {0}: {1}' -f $script:StageCounter, $Name)
    Write-Info '============================================================'

    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    try {
        & $Action
        $sw.Stop()
        Write-Ok ('{0} finished in {1:N1}s' -f $Name, $sw.Elapsed.TotalSeconds)
    }
    catch {
        $sw.Stop()
        Write-Fail ('{0} failed after {1:N1}s' -f $Name, $sw.Elapsed.TotalSeconds)
        Write-Fail $_.Exception.Message
        throw
    }
}

function Test-CommandAvailable([string]$CommandName) {
    return $null -ne (Get-Command $CommandName -ErrorAction SilentlyContinue)
}

function Invoke-LoggedCommand {
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [string[]]$Arguments = @(),
        [string]$Description = $null,
        [switch]$AllowFailure
    )

    $quotedArgs = if ($Arguments.Count -gt 0) {
        ($Arguments | ForEach-Object {
            if ($_ -match '\s') { '"{0}"' -f $_ } else { $_ }
        }) -join ' '
    }
    else {
        ''
    }

    if ($Description) {
        Write-Info $Description
    }
    Write-Info ('> {0} {1}' -f $FilePath, $quotedArgs)

    $oldNativePref = $null
    $hadNativePref = $false
    if (Get-Variable -Name PSNativeCommandUseErrorActionPreference -Scope Global -ErrorAction SilentlyContinue) {
        $hadNativePref = $true
        $oldNativePref = $global:PSNativeCommandUseErrorActionPreference
        $global:PSNativeCommandUseErrorActionPreference = $false
    }

    $oldErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'

    try {
        & $FilePath @Arguments 2>&1 | ForEach-Object {
            $text = $_.ToString()
            if ($script:LogFile) {
                Add-Content -Path $script:LogFile -Value $text
            }
            Write-Host $text
        }

        if (-not $AllowFailure -and $LASTEXITCODE -ne 0) {
            throw ("Command failed with exit code {0}: {1} {2}" -f $LASTEXITCODE, $FilePath, $quotedArgs)
        }
    }
    finally {
        $ErrorActionPreference = $oldErrorActionPreference
        if ($hadNativePref) {
            $global:PSNativeCommandUseErrorActionPreference = $oldNativePref
        }
    }
}

function Ensure-UVInstalled {
    Refresh-Path

    if (Test-CommandAvailable 'uv') {
        $version = & uv --version
        Write-Ok "uv is available: $version"
        return
    }

    Write-Warn 'uv was not found in PATH. Installing uv from the official installer.'
    Invoke-LoggedCommand -FilePath 'powershell' -Arguments @(
        '-NoProfile',
        '-ExecutionPolicy', 'Bypass',
        '-Command',
        'irm https://astral.sh/uv/install.ps1 | iex'
    ) -Description 'Installing uv'

    Refresh-Path
    if (-not (Test-CommandAvailable 'uv')) {
        throw 'uv installation completed, but the uv command is still unavailable in PATH.'
    }

    $version = & uv --version
    Write-Ok "uv installed successfully: $version"
}

function Ensure-PythonInstalled {
    Invoke-LoggedCommand -FilePath 'uv' -Arguments @('python', 'install', $PythonVersion) -Description "Installing Python $PythonVersion through uv"
}

function Ensure-Venv {
    $venvPath = Join-Path $script:ProjectRoot '.venv'

    if ($ForceRecreateVenv -and (Test-Path $venvPath)) {
        Write-Warn 'Removing existing .venv because -ForceRecreateVenv was provided.'
        Remove-Item -Recurse -Force $venvPath
    }

    if (-not (Test-Path $venvPath)) {
        Invoke-LoggedCommand -FilePath 'uv' -Arguments @('init') -Description 'Initializing uv environment'
        # Invoke-LoggedCommand -FilePath 'uv' -Arguments @('venv') -Description 'Ensuring virtual environment is set up for uv'
        Invoke-LoggedCommand -FilePath 'uv' -Arguments @('venv', '--python', $PythonVersion, $venvPath) -Description 'Creating virtual environment'
        Invoke-LoggedCommand -FilePath './.venv/Scripts/activate' -Description 'Activating virtual environment for dependency installation'
    }
    else {
        Write-Ok "Virtual environment already exists: $venvPath"
    }
}

function Test-PyProjectIsPackageProject {
    $pyprojectPath = Join-Path $script:ProjectRoot 'pyproject.toml'
    if (-not (Test-Path $pyprojectPath)) {
        return $false
    }

    $content = Get-Content -Path $pyprojectPath -Raw
    return $content -match '(?m)^\[project\]'
}

function Sync-Dependencies {
    Invoke-LoggedCommand -FilePath 'uv' -Arguments @('pip', 'install', 'manim', 'manim-slides', 'pyqt6', 'pyside6') -Description 'Installing fallback dependencies'

}

function Ensure-LaTeXInstalled {
    if ($SkipLaTeX) {
        Write-Warn 'Skipping LaTeX checks because -SkipLaTeX was provided.'
        return
    }

    $latexCommands = @('latex', 'pdflatex', 'xelatex')
    $found = $false
    foreach ($cmd in $latexCommands) {
        if (Test-CommandAvailable $cmd) {
            $found = $true
            break
        }
    }

    if ($found) {
        Write-Ok 'LaTeX commands are available'
    }
    else {
        Write-Warn 'No LaTeX executable was found in PATH. Manim may fail when rendering LaTeX scenes.'
    }
}

function Test-BasicToolchain {
    $pythonExe = Join-Path $script:ProjectRoot '.venv\Scripts\python.exe'
    if (-not (Test-Path $pythonExe)) {
        throw "Virtual environment Python executable was not found: $pythonExe"
    }

    Invoke-LoggedCommand -FilePath $pythonExe -Arguments @('--version') -Description 'Checking Python inside virtual environment'

    $manimCheck = @('uv run manim-text.py')
    Invoke-LoggedCommand -FilePath $pythonExe -Arguments $manimCheck -Description 'Checking whether Manim is importable' -AllowFailure
}
function Install-ManimPhysics {
    $manimPhysicsRepo = 'https://github.com/SirJamesClarkMaxwell/manim-physics.git' 
    git clone $manimPhysicsRepo 
    cd .\manim-physics
    uv pip install -e .
    cd ..
}
$script:ProjectRoot = Get-ProjectRoot
Initialize-Logging

Write-Info "Script location : $PSScriptRoot"
Write-Info "Project root    : $script:ProjectRoot"
Write-Info "Log file        : $script:LogFile"
Write-Info "Target Python   : $PythonVersion"

Invoke-Stage -Name 'Checking uv' -Action { Ensure-UVInstalled }
Invoke-Stage -Name 'Installing Python' -Action { Ensure-PythonInstalled }
Invoke-Stage -Name 'Creating virtual environment' -Action { Ensure-Venv }
Invoke-Stage -Name 'Installing dependencies' -Action { Sync-Dependencies }
Invoke-Stage -Name 'manim-physics installation' -Action {Install-ManimPhysics}
Invoke-Stage -Name 'Ensuring LaTeX is installed' -Action { Ensure-LaTeXInstalled }
Invoke-Stage -Name 'Running sanity checks' -Action { Test-BasicToolchain }

Write-Host ''
Write-Ok 'Setup finished successfully.'
Write-Info 'To activate the environment manually, run:'
Write-Host (Join-Path $script:ProjectRoot '.venv\Scripts\activate') -ForegroundColor White
