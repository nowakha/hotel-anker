# PI02 rescue watcher (Windows PowerShell 5) — TCP:22 then mask fb-clock + deploy player.
$ErrorActionPreference = 'Continue'
$HostsToTry = @('192.168.8.106', '100.103.54.63')
$SshUser = 'user'
$SshPass = '12345678'
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$WlbRoot = Split-Path -Parent $ScriptDir
$PlayerLocal = Join-Path $WlbRoot 'fb_clock_play.py'
$LogPath = Join-Path $WlbRoot 'docs\_pi02_rescue.log'
$RemotePlayer = '/home/user/WerbeLEDbox-CountDown/fb_clock_play.py'

function Test-SshPort {
  param([string]$Ip, [int]$TimeoutMs = 1200)
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

function Invoke-SshKey {
  param([string]$Ip, [string]$RemoteCmd)
  $args = @(
    '-o', 'StrictHostKeyChecking=no',
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
    & scp -o StrictHostKeyChecking=no -o ConnectTimeout=5 -o BatchMode=yes $PlayerLocal ($SshUser + '@' + $Ip + ':' + $RemotePlayer) 2>&1 |
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

$startMsg = '=== rescue start ' + (Get-Date -Format o) + ' player=' + $PlayerLocal + ' ==='
$startMsg | Tee-Object -FilePath $LogPath
Write-Host ('Watching ' + ($HostsToTry -join ', ') + ' for TCP/22 ...')
$round = 0
while ($true) {
  $round++
  foreach ($ip in $HostsToTry) {
    if (Test-SshPort -Ip $ip) {
      if (Invoke-Rescue -Ip $ip) {
        exit 0
      }
      Write-Host 'Rescue incomplete; retrying...'
    }
  }
  if (($round % 15) -eq 1) {
    $msg = '[' + (Get-Date -Format 'HH:mm:ss') + '] still offline round=' + $round
    Write-Host $msg
  }
  Start-Sleep -Seconds 2
}
