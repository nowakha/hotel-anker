# PI02 rescue watcher (Windows PowerShell 5) — TCP:22 then mask fb-clock + deploy player.
# Probes: LAN .106, Tailscale, mDNS, and IPv4 link-local 169.254.* (direct PC↔Pi, no DHCP).
param(
  [switch]$IncludeLinkLocal = $true,
  [switch]$SkipFixedHosts
)

$ErrorActionPreference = 'Continue'
$FixedHosts = @('192.168.8.106', '100.103.54.63')
$MdnsName = 'AnkerPI02.local'
$SshUser = 'user'
$SshPass = '12345678'
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$WlbRoot = Split-Path -Parent $ScriptDir
$PlayerLocal = Join-Path $WlbRoot 'fb_clock_play.py'
$LogPath = Join-Path $WlbRoot 'docs\_pi02_rescue.log'
$RemotePlayer = '/home/user/WerbeLEDbox-CountDown/fb_clock_play.py'

function Test-SshPort {
  param([string]$Ip, [int]$TimeoutMs = 1200)
  if ([string]::IsNullOrWhiteSpace($Ip)) { return $false }
  try {
    $client = New-Object System.Net.Sockets.TcpClient
    $async = $client.BeginConnect($Ip, 22, $null, $null)
    $ok = $async.AsyncWaitHandle.WaitOne($TimeoutMs, $false)
    if (-not $ok) {
      try { $client.Close() } catch {}
      return $false
    }
    try { $client.EndConnect($async) | Out-Null } catch {
      try { $client.Close() } catch {}
      return $false
    }
    $connected = $client.Connected
    $client.Close()
    return $connected
  } catch {
    return $false
  }
}

function Get-LinkLocalCandidates {
  $found = New-Object System.Collections.Generic.List[string]

  try {
    $neighbors = Get-NetNeighbor -AddressFamily IPv4 -ErrorAction SilentlyContinue |
      Where-Object {
        $_.IPAddress -like '169.254.*' -and
        $_.State -notin @('Unreachable', 'Incomplete', 'Permanent') -and
        $_.IPAddress -notlike '*.255' -and
        $_.IPAddress -ne '169.254.255.255'
      }
    foreach ($n in $neighbors) {
      if (-not $found.Contains($n.IPAddress)) { $found.Add($n.IPAddress) }
    }
  } catch {}

  try {
    $arpOut = & arp -a 2>$null | Out-String
    foreach ($m in [regex]::Matches($arpOut, '169\.254\.\d{1,3}\.\d{1,3}')) {
      $ip = $m.Value
      if ($ip -like '*.255') { continue }
      if (-not $found.Contains($ip)) { $found.Add($ip) }
    }
  } catch {}

  try {
    $llLocal = Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
      Where-Object { $_.IPAddress -like '169.254.*' -and $_.PrefixOrigin -eq 'WellKnown' }
    if ($llLocal) {
      $ping = New-Object System.Net.NetworkInformation.Ping
      try { $null = $ping.Send('169.254.255.255', 200) } catch {}
      $ping.Dispose()
    }
  } catch {}

  return $found
}

function Get-MdnsCandidate {
  try {
    $entries = Resolve-DnsName -Name $MdnsName -Type A -ErrorAction SilentlyContinue |
      Where-Object { $_.IPAddress -and $_.IPAddress -notlike 'fe80:*' }
    foreach ($e in $entries) {
      return [string]$e.IPAddress
    }
  } catch {}
  return $null
}

function Get-HostsToProbe {
  $list = New-Object System.Collections.Generic.List[string]
  if (-not $SkipFixedHosts) {
    foreach ($h in $FixedHosts) {
      if (-not $list.Contains($h)) { $list.Add($h) }
    }
  }
  $mdns = Get-MdnsCandidate
  if ($mdns -and -not $list.Contains($mdns)) { $list.Add($mdns) }
  if ($IncludeLinkLocal) {
    foreach ($ll in (Get-LinkLocalCandidates)) {
      if (-not $list.Contains($ll)) { $list.Add($ll) }
    }
  }
  return $list
}

function Invoke-SshKey {
  param([string]$Ip, [string]$RemoteCmd)
  $args = @(
    '-o', 'StrictHostKeyChecking=no',
    '-o', 'UserKnownHostsFile=NUL',
    '-o', 'ConnectTimeout=5',
    '-o', 'ServerAliveInterval=2',
    '-o', 'ServerAliveCountMax=2',
    '-o', 'BatchMode=yes',
    '-o', 'PreferredAuthentications=publickey',
    ($SshUser + '@' + $Ip),
    $RemoteCmd
  )
  $output = & ssh @args 2>&1 | Out-String
  return @{
    Rc = $LASTEXITCODE
    Out = $output
  }
}

function Invoke-Rescue {
  param([string]$Ip)
  $stamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
  Add-Content -Path $LogPath -Value ($stamp + ' RESCUE ' + $Ip)
  Write-Host ($stamp + ' SSH open on ' + $Ip + ' - masking fb-clock')

  $maskCmd = @'
set +e
echo MASK_START
echo 'PASS' | sudo -S systemctl stop fb-clock
echo 'PASS' | sudo -S systemctl disable fb-clock
echo 'PASS' | sudo -S systemctl mask fb-clock
systemctl is-enabled fb-clock 2>&1
systemctl is-active fb-clock 2>&1
hostname
uptime
echo MASK_DONE
'@
  $maskCmd = $maskCmd.Replace('PASS', $SshPass)

  $result = Invoke-SshKey -Ip $Ip -RemoteCmd $maskCmd
  $line = $stamp + ' MASK rc=' + $result.Rc + ' ' + $result.Out
  Add-Content -Path $LogPath -Value $line
  Write-Host $result.Out

  if (Test-Path $PlayerLocal) {
    Write-Host 'Deploying patched fb_clock_play.py'
    $dest = ($SshUser + '@' + $Ip + ':' + $RemotePlayer)
    & scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=NUL -o ConnectTimeout=5 -o BatchMode=yes $PlayerLocal $dest 2>&1 |
      ForEach-Object { $_ | Tee-Object -FilePath $LogPath -Append }
    $verifyCmd = 'grep -n "Never decode\|ffprobe\|-f null" ' + $RemotePlayer + ' | head -20; echo VERIFY_DONE'
    $verify = Invoke-SshKey -Ip $Ip -RemoteCmd $verifyCmd
    Add-Content -Path $LogPath -Value ($stamp + ' VERIFY ' + $verify.Out)
    Write-Host $verify.Out
    if (($verify.Out -match 'Never decode') -and ($verify.Out -match 'ffprobe') -and ($verify.Out -notmatch '-f null')) {
      Write-Host 'VERIFY_OK: probe uses ffprobe'
    } else {
      Write-Host 'VERIFY_WARN: check probe_size on device'
    }
  }

  if ($result.Out -match 'MASK_DONE') {
    Add-Content -Path $LogPath -Value ($stamp + ' SUCCESS ' + $Ip)
    Write-Host ('RESCUE_OK ' + $Ip)
    return $true
  }
  return $false
}

$startMsg = '=== rescue start ' + (Get-Date -Format o) + ' player=' + $PlayerLocal + ' linklocal=' + $IncludeLinkLocal + ' ==='
$startMsg | Tee-Object -FilePath $LogPath
Write-Host 'Watching fixed (.106 + Tailscale), mDNS, and 169.254.* neighbors for TCP/22 ...'
Write-Host 'Direct PC↔Pi Ethernet (no DHCP): both ends APIPA 169.254.x.x — link in seconds beats late WiFi.'
$round = 0
while ($true) {
  $round++
  $hosts = Get-HostsToProbe
  foreach ($ip in $hosts) {
    if (Test-SshPort -Ip $ip) {
      if (Invoke-Rescue -Ip $ip) {
        exit 0
      }
      Write-Host 'Rescue incomplete; retrying...'
    }
  }
  if (($round % 15) -eq 1) {
    $msg = '[' + (Get-Date -Format 'HH:mm:ss') + '] still offline round=' + $round + ' probing=' + ($hosts -join ', ')
    Write-Host $msg
    Add-Content -Path $LogPath -Value $msg
  }
  Start-Sleep -Seconds 2
}
