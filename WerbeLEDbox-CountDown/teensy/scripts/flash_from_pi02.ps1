# Build Teensy hex locally, copy to AnkerPI02, identify board, flash via teensy_loader_cli.
param(
  [string]$HostName = "192.168.8.106",
  [string]$User = "user",
  [ValidateSet("auto", "teensy32", "teensy40", "teensy41")]
  [string]$Board = "auto",
  [switch]$SkipBuild
)

$ErrorActionPreference = "Stop"
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..\..")
$proj = Join-Path $repoRoot "WerbeLEDbox-CountDown\teensy\anker_pixel_pusher"
$remoteDir = "/tmp/anker_teensy_flash"

function Invoke-Pi([string]$cmd) {
  ssh -o ConnectTimeout=12 -o BatchMode=yes "${User}@${HostName}" $cmd
}

Write-Host "=== reachability $HostName ==="
try {
  Invoke-Pi "true" | Out-Null
} catch {
  throw "AnkerPI02 ($HostName) nicht erreichbar. Bitte Pi einschalten / Netz pruefen."
}

if (-not $SkipBuild) {
  Write-Host "=== build teensy32 + teensy40 ==="
  Push-Location $proj
  try {
    pio run -e teensy32
    pio run -e teensy40
  } finally {
    Pop-Location
  }
  New-Item -ItemType Directory -Force -Path (Join-Path $repoRoot "WerbeLEDbox-CountDown\teensy\hex") | Out-Null
  Copy-Item (Join-Path $proj ".pio\build\teensy32\firmware.hex") (Join-Path $repoRoot "WerbeLEDbox-CountDown\teensy\hex\firmware_teensy32.hex") -Force
  Copy-Item (Join-Path $proj ".pio\build\teensy40\firmware.hex") (Join-Path $repoRoot "WerbeLEDbox-CountDown\teensy\hex\firmware_teensy40.hex") -Force
}

$hexDir = Join-Path $repoRoot "WerbeLEDbox-CountDown\teensy\hex"
$hex32 = Join-Path $hexDir "firmware_teensy32.hex"
$hex40 = Join-Path $hexDir "firmware_teensy40.hex"
if (-not (Test-Path $hex32)) {
  $hex32 = Join-Path $proj ".pio\build\teensy32\firmware.hex"
}
if (-not (Test-Path $hex40)) {
  $hex40 = Join-Path $proj ".pio\build\teensy40\firmware.hex"
}
if (-not (Test-Path $hex32)) { throw "missing $hex32" }
if (-not (Test-Path $hex40)) { throw "missing $hex40" }

Write-Host "=== upload files to Pi ==="
Invoke-Pi "mkdir -p $remoteDir"
scp -o ConnectTimeout=12 $hex32 "${User}@${HostName}:${remoteDir}/firmware_teensy32.hex"
scp -o ConnectTimeout=12 $hex40 "${User}@${HostName}:${remoteDir}/firmware_teensy40.hex"
scp -o ConnectTimeout=12 (Join-Path $PSScriptRoot "identify_teensy.sh") "${User}@${HostName}:${remoteDir}/identify_teensy.sh"
scp -o ConnectTimeout=12 (Join-Path $PSScriptRoot "flash_on_pi.sh") "${User}@${HostName}:${remoteDir}/flash_on_pi.sh"

Write-Host "=== identify ==="
Invoke-Pi "bash $remoteDir/identify_teensy.sh"

Write-Host "=== flash on Pi (Board=$Board) ==="
Write-Host "Wenn der Loader wartet: Program-Taste am Teensy kurz druecken."
Invoke-Pi "chmod +x $remoteDir/*.sh; BOARD='$Board' FLASH_DIR='$remoteDir' bash $remoteDir/flash_on_pi.sh"

Write-Host "=== serial banner ==="
Invoke-Pi 'python3 -c "import serial,time; s=serial.Serial(''/dev/ttyACM0'',115200,timeout=0.2); time.sleep(1.5); print(s.read(4096).decode(''utf-8'',''replace'')); s.close()"'
