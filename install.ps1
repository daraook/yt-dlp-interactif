# Installateur tout-en-un de yt-dlp interactif (Windows / PowerShell).
#
#   Lancer :  powershell -ExecutionPolicy Bypass -File install.ps1
#   Sans questions (auto « oui ») :  install.ps1 -Yes
#
# Vérifie Python, yt-dlp et ffmpeg, propose d'installer ce qui manque (via winget),
# puis installe l'outil et le rend lançable avec la commande « ytdlp-interactif ».
param([switch]$Yes)

$ErrorActionPreference = "Stop"
$Repo = "daraook/yt-dlp-interactif"

function Have($name) { return [bool](Get-Command $name -ErrorAction SilentlyContinue) }

function Ask($question) {
    if ($Yes) { return $true }
    $r = Read-Host "$question [O/n]"
    return ($r -eq "" -or $r -match "^[OoYy]")
}

function Winget-Install($id, $label) {
    if (-not (Have "winget")) {
        Write-Host "  winget est indisponible. Installe $label manuellement, puis relance." -ForegroundColor Yellow
        exit 1
    }
    Write-Host "  Installation de $label…" -ForegroundColor Cyan
    winget install --id $id --accept-source-agreements --accept-package-agreements -e
}

# --- Choix de la commande Python (py de préférence, sinon python) ---
$Py = $null
foreach ($c in @("py", "python", "python3")) {
    if (Have $c) { $Py = $c; break }
}

Write-Host "`n=== yt-dlp interactif — installation Windows ===`n"

# --- 1. Python >= 3.11 ---
$pythonOk = $false
if ($Py) {
    try {
        & $Py -c "import sys; sys.exit(0 if sys.version_info[:2] >= (3,11) else 1)"
        if ($LASTEXITCODE -eq 0) { $pythonOk = $true }
    } catch { }
}
if (-not $pythonOk) {
    Write-Host "Python 3.11+ est requis et n'a pas été trouvé." -ForegroundColor Yellow
    if (Ask "Installer Python 3.13 maintenant ?") {
        Winget-Install "Python.Python.3.13" "Python 3.13"
        Write-Host "`n⚠️  Ferme puis rouvre PowerShell, et relance ce script." -ForegroundColor Yellow
        exit 0
    } else { exit 1 }
} else {
    Write-Host "✓ Python présent ($Py)." -ForegroundColor Green
}

# --- 2. yt-dlp ---
if (Have "yt-dlp") {
    Write-Host "✓ yt-dlp présent." -ForegroundColor Green
} else {
    Write-Host "yt-dlp (moteur de téléchargement) est requis." -ForegroundColor Yellow
    if (Ask "Installer yt-dlp maintenant ?") { Winget-Install "yt-dlp.yt-dlp" "yt-dlp" }
    else { Write-Host "  (Requis pour fonctionner.)" -ForegroundColor Yellow }
}

# --- 3. ffmpeg ---
if (Have "ffmpeg") {
    Write-Host "✓ ffmpeg présent." -ForegroundColor Green
} else {
    Write-Host "ffmpeg (audio, fusion, conversion) est requis." -ForegroundColor Yellow
    if (Ask "Installer ffmpeg maintenant ?") { Winget-Install "Gyan.FFmpeg" "ffmpeg" }
    else { Write-Host "  (Requis pour l'audio/la fusion.)" -ForegroundColor Yellow }
}

# --- 4. Récupérer le wheel de la dernière release ---
Write-Host "`nRecherche de la dernière version publiée…" -ForegroundColor Cyan
$api = "https://api.github.com/repos/$Repo/releases/latest"
$rel = Invoke-RestMethod -Uri $api -Headers @{ "User-Agent" = "ytdlp-interactif-installer" }
$wheel = ($rel.assets | Where-Object { $_.name -like "*.whl" } | Select-Object -First 1).browser_download_url
if (-not $wheel) { Write-Host "Aucun wheel trouvé dans la dernière release." -ForegroundColor Red; exit 1 }

# --- 5. Installer l'outil (pipx si dispo/souhaité, sinon pip --user) ---
$havePipx = $false
try { & $Py -m pipx --version *> $null; if ($LASTEXITCODE -eq 0) { $havePipx = $true } } catch { }

if ($havePipx) {
    Write-Host "Installation via pipx…" -ForegroundColor Cyan
    & $Py -m pipx install --force $wheel
} else {
    if (Ask "Installer pipx (recommandé : commande dispo partout) ?") {
        & $Py -m pip install --user --upgrade pipx
        & $Py -m pipx ensurepath
        & $Py -m pipx install --force $wheel
        Write-Host "`n⚠️  Rouvre PowerShell pour que la commande soit reconnue." -ForegroundColor Yellow
    } else {
        Write-Host "Installation via pip (--user)…" -ForegroundColor Cyan
        & $Py -m pip install --user --upgrade $wheel
        Write-Host "`nℹ️  Si « ytdlp-interactif » n'est pas reconnu, lance :  $Py -m ytdlp_interactif" -ForegroundColor Yellow
    }
}

Write-Host "`n✅ Terminé. Lance l'outil avec :  ytdlp-interactif" -ForegroundColor Green
Write-Host "   (ou, en repli :  $Py -m ytdlp_interactif )`n"
