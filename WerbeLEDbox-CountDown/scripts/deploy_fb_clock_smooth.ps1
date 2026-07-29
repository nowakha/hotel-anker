# Deploy optimized fb_clock_play.py + unit to AnkerPI02 when SSH is up.
# Usage: pwsh scripts/deploy_fb_clock_smooth.ps1
# Optional: -Watch to poll until online, then deploy.

param(
    [switch]$Watch,
    [int]$PollSeconds = 15,
    [string[]]$Hosts = @("100.103.54.63", "192.168.1.222", "192.168.8.106", "AnkerPI02.local")
)

$ErrorActionPreference = "Stop"
$Local = Split-Path $PSScriptRoot -Parent
$Player = Join-Path $Local "fb_clock_play.py"
$Unit = Join-Path $Local "systemd\fb_clock.service"
$User = "user"

function Test-Ssh([string]$h) {
    try {
        $r = Test-NetConnection -ComputerName $h -Port 22 -WarningAction SilentlyContinue -ErrorAction SilentlyContinue
        return [bool]$r.TcpTestSucceeded
    } catch { return $false }
}

function Invoke-SshPass([string]$h, [string]$remoteCmd) {
    # Prefer key-based; fall back to plink/sshpass-less echo pipe is unreliable on Win.
    $sshArgs = @(
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=NUL",
        "-o", "ConnectTimeout=8",
        "-o", "BatchMode=yes",
        "${User}@${h}",
        $remoteCmd
    )
    & ssh @sshArgs
    return $LASTEXITCODE
}

function Deploy-To([string]$h) {
    Write-Host "deploy → $h"
    $scp = @(
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=NUL",
        "-o", "ConnectTimeout=8",
        "-o", "BatchMode=yes"
    )
    & scp @scp $Player "${User}@${h}:/home/user/WerbeLEDbox-CountDown/fb_clock_play.py"
    if ($LASTEXITCODE -ne 0) { throw "scp player failed" }
    & scp @scp $Unit "${User}@${h}:/tmp/fb-clock.service"
    if ($LASTEXITCODE -ne 0) { throw "scp unit failed" }

    $remote = @'
set -e
sudo cp /tmp/fb-clock.service /etc/systemd/system/fb-clock.service
sudo systemctl daemon-reload
sudo systemctl restart fb-clock
sleep 2
systemctl is-active fb-clock
systemctl show fb-clock -p ActiveEnterTimestamp -p NRestarts --no-pager
vcgencmd get_throttled || true
journalctl -u fb-clock -n 15 --no-pager
'@ -replace "`r", ""

    $b64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($remote))
    $rc = Invoke-SshPass $h "echo $b64 | base64 -d | bash"
    if ($rc -ne 0) { throw "remote apply failed rc=$rc" }
    Write-Host "OK deployed on $h"
}

$target = $null
while ($true) {
    foreach ($h in $Hosts) {
        Write-Host "probe $h ..."
        if (Test-Ssh $h) {
            $target = $h
            break
        }
    }
    if ($target) { break }
    if (-not $Watch) {
        Write-Host "PI02 SSH not reachable. Re-run with -Watch or when online."
        exit 2
    }
    Write-Host "offline — retry in ${PollSeconds}s"
    Start-Sleep -Seconds $PollSeconds
}

Deploy-To $target
