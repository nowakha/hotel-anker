# Wait for BOOTSEL (RPI-RP2), flash matching MicroPython UF2, deploy src via mpremote.
param(
  [int]$BootTimeoutSec = 120,
  [int]$ComTimeoutSec = 60,
  [string]$ForceBoard = ""  # RPI_PICO | RPI_PICO_W
)

$ErrorActionPreference = "Stop"
# scripts/ -> pico/
$picoDir = Split-Path $PSScriptRoot -Parent
$fwDir = Join-Path $picoDir "firmware"
$srcDir = Join-Path $picoDir "src"

function Get-BootDrive {
  Get-CimInstance Win32_LogicalDisk | Where-Object {
    $_.VolumeName -match 'RPI-RP2|RP2350'
  }
}

Write-Host "==> Waiting for BOOTSEL drive (hold BOOTSEL while plugging USB)..."
$deadline = (Get-Date).AddSeconds($BootTimeoutSec)
$boot = $null
while ((Get-Date) -lt $deadline) {
  $boot = Get-BootDrive
  if ($boot) { break }
  Start-Sleep -Milliseconds 500
}
if (-not $boot) { throw "No RPI-RP2 / RP2350 boot drive within ${BootTimeoutSec}s" }

$root = "$($boot.DeviceID)\"
$infoPath = Join-Path $root "INFO_UF2.TXT"
Write-Host "==> Boot drive $root"
if (Test-Path $infoPath) {
  Write-Host "---- INFO_UF2.TXT ----"
  Get-Content $infoPath | Write-Host
  Write-Host "----------------------"
  $info = Get-Content $infoPath -Raw
} else {
  $info = ""
}

$board = $ForceBoard
if (-not $board) {
  if ($info -match 'board_id:\s*(\S+)') { $board = $Matches[1] }
  if ($info -match 'RP2350') {
    if ($info -match 'W') { $board = "RPI_PICO2_W" } else { $board = "RPI_PICO2" }
  }
}
if (-not $board -or $board -eq "RPI-RP2") {
  Write-Host ""
  Write-Host "BOOTSEL does not tell Pico vs Pico W."
  Write-Host "  [1] Raspberry Pi Pico    (no WiFi)  -> RPI_PICO"
  Write-Host "  [2] Raspberry Pi Pico W  (WiFi)     -> RPI_PICO_W"
  $choice = Read-Host "Which board is this? (1/2)"
  if ($choice -eq "2") { $board = "RPI_PICO_W" } else { $board = "RPI_PICO" }
}

# Heuristic: user can pass -ForceBoard RPI_PICO_W
$uf2Map = @{
  "RPI_PICO" = "RPI_PICO-v1.28.0.uf2"
  "RPI_PICO_W" = "RPI_PICO_W-v1.28.0.uf2"
}
if (-not $uf2Map.ContainsKey($board)) {
  Write-Host "Board key '$board' unknown — defaulting to RPI_PICO (pass -ForceBoard RPI_PICO_W if WiFi board)"
  $board = "RPI_PICO"
}
$uf2 = Join-Path $fwDir $uf2Map[$board]
if (-not (Test-Path $uf2)) { throw "Missing firmware $uf2" }

Write-Host "==> Flashing $board <= $(Split-Path $uf2 -Leaf)"
Copy-Item -LiteralPath $uf2 -Destination $root -Force

Write-Host "==> Waiting for USB CDC after reset..."
$deadline = (Get-Date).AddSeconds($ComTimeoutSec)
$port = $null
while ((Get-Date) -lt $deadline) {
  Start-Sleep -Seconds 1
  $ports = py -3 -c "import serial.tools.list_ports as lp
for p in lp.comports():
  if p.vid==0x2E8A: print(p.device)
"
  $line = ($ports | Select-Object -First 1)
  if ($line) { $port = $line.Trim(); break }
}
if (-not $port) { throw "No 2E8A CDC port after flash" }
Write-Host "==> CDC $port"

Write-Host "==> Deploying MicroPython src via mpremote"
$files = @("config.py", "protocol.py", "ws2812_pio.py", "main.py")
if (Test-Path (Join-Path $srcDir "secrets.py")) { $files += "secrets.py" }
foreach ($f in $files) {
  $path = Join-Path $srcDir $f
  Write-Host "  cp $f"
  & mpremote connect $port cp $path :$f
  if ($LASTEXITCODE -ne 0) { throw "mpremote cp failed for $f" }
}
Write-Host "  reset"
& mpremote connect $port reset
Write-Host "==> DONE — board should run main.py (4-line receiver)"
Write-Host "    USB smoke: py -3 WerbeLEDbox-CountDown\scripts\send_pico_stripes.py --port $port"
