# Direct Ethernet rescue helper — PC ↔ AnkerPI02, no DHCP switch/router.
# Wrapper around pi02_rescue_watch.ps1 with link-local (169.254.*) discovery enabled.
# See docs/PI02_DIRECT_ETH_RESCUE.md

$ErrorActionPreference = 'Continue'
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Watcher = Join-Path $ScriptDir 'pi02_rescue_watch.ps1'

Write-Host ''
Write-Host '=== AnkerPI02 Direct-Ethernet Rescue ==='
Write-Host '1. Normal Ethernet cable PC ↔ Pi (auto-MDIX; no crossover needed).'
Write-Host '2. Ethernet adapter enabled on PC; WiFi optional off to avoid confusion.'
Write-Host '3. This watcher stays running, then power-cycle the Pi.'
Write-Host '4. Goal: SSH within first ~2 min (NTP ExecStartPre) → mask fb-clock.'
Write-Host '5. If CPU already hung on full decode: power-cycle again and catch early window.'
Write-Host 'Doc: WerbeLEDbox-CountDown/docs/PI02_DIRECT_ETH_RESCUE.md'
Write-Host ''

try {
  $eth = Get-NetAdapter -Physical -ErrorAction SilentlyContinue |
    Where-Object { $_.Status -eq 'Up' -and ($_.Name -match 'Ethernet|LAN|Realtek|Intel' -or $_.InterfaceDescription -match 'Ethernet') }
  if ($eth) {
    Write-Host ('Up Ethernet adapter(s): ' + (($eth | ForEach-Object { $_.Name }) -join ', '))
  } else {
    Write-Host 'WARN: no obvious Up Ethernet adapter — enable the NIC / check cable.'
  }
  $ll = Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
    Where-Object { $_.IPAddress -like '169.254.*' }
  if ($ll) {
    Write-Host ('PC link-local: ' + (($ll | ForEach-Object { $_.IPAddress }) -join ', '))
  } else {
    Write-Host 'PC has no 169.254.* yet (normal until link; APIPA appears after cable up, no DHCP).'
  }
} catch {}

Write-Host ''
Write-Host 'Starting watcher (LAN .106 + Tailscale + mDNS + 169.254.*) ...'
& $Watcher
