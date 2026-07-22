# Wait for clock_24h.mp4, then deploy to AnkerPI02 and measure fps.
$ErrorActionPreference = 'Continue'
$Repo = 'C:\Users\User\Documents\Cursor Projects\Hotel Anker'
$Media = Join-Path $Repo 'WerbeLEDbox-CountDown\media'
$Out = Join-Path $Media 'clock_24h.mp4'
$Log = Join-Path $Media '_deploy_clock_24h.log'
$UnitLocal = Join-Path $Repo 'WerbeLEDbox-CountDown\systemd\fb_clock.service'
$PlayerLocal = Join-Path $Repo 'WerbeLEDbox-CountDown\fb_clock_play.py'
$RemoteSh = Join-Path $Media '_deploy_on_pi02.sh'
$Hosts = @('100.103.54.63', 'ankerpi02', '192.168.8.106')

function Log([string]$m) {
  $line = "$(Get-Date -Format 's') | $m"
  Add-Content -Path $Log -Value $line
  Write-Host $line
}

Log '==== DEPLOY WATCHER START ===='

while (-not (Test-Path $Out)) {
  Log 'waiting for clock_24h.mp4 ...'
  Start-Sleep -Seconds 30
}
$FP = 'C:\Users\User\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.2-full_build\bin\ffprobe.exe'
$probe = & $FP -v error -show_entries stream=width,height,codec_name -show_entries format=duration -of default=noprint_wrappers=1 $Out 2>&1 | Out-String
Log "probe: $($probe.Trim()) size=$((Get-Item $Out).Length)"

@'
#!/bin/bash
set -euo pipefail
sudo mv /tmp/fb-clock.service /etc/systemd/system/fb-clock.service
sudo systemctl daemon-reload
sudo systemctl enable fb-clock.service
sudo systemctl stop fb-clock 2>/dev/null || true
sudo systemctl disable fb_clock_opencv 2>/dev/null || true
pkill -f fb_clock_opencv.py 2>/dev/null || true

# Throughput measure (10s slice only — never full-file null decode)
SEEK=$(python3 -c 'from datetime import datetime; from zoneinfo import ZoneInfo
n=datetime.now(ZoneInfo("Europe/Zurich")); s=n.hour*3600+n.minute*60+n.second+n.microsecond/1e6
print("%02d:%02d:%06.3f" % (int(s)//3600,(int(s)%3600)//60,s%60))')
echo "FPS_SEEK=$SEEK"
timeout 40 ffmpeg -hide_banner -loglevel info -ss "$SEEK" -t 10 -i /home/user/WerbeLEDbox-CountDown/media/clock_24h.mp4 -an \
  -vf "scale=3440:1440:flags=neighbor,rotate=PI:ow=3440:oh=1440,format=rgb565le" \
  -f null - 2>/tmp/fps_throughput.err || true
echo '--- THROUGHPUT ---'
grep -E 'fps=|speed=|frame=' /tmp/fps_throughput.err | tail -5 || tail -15 /tmp/fps_throughput.err

# Live fb push 15s realtime
timeout 25 ffmpeg -hide_banner -loglevel info -ss "$SEEK" -t 15 -re -i /home/user/WerbeLEDbox-CountDown/media/clock_24h.mp4 -an \
  -vf "scale=3440:1440:flags=neighbor,rotate=PI:ow=3440:oh=1440,format=rgb565le" \
  -pix_fmt rgb565le -f fbdev /dev/fb0 2>/tmp/fps_live.err || true
echo '--- LIVE_FB ---'
grep -E 'fps=|speed=|frame=' /tmp/fps_live.err | tail -5 || tail -15 /tmp/fps_live.err

sudo systemctl restart fb-clock.service
sleep 6
systemctl is-active fb-clock
systemctl is-enabled fb-clock
journalctl -u fb-clock -n 25 --no-pager
vcgencmd get_throttled
ls -lh /home/user/WerbeLEDbox-CountDown/media/clock_24h.mp4
echo DEPLOY_OK
'@ | Set-Content -Path $RemoteSh -Encoding utf8

$target = $null
while (-not $target) {
  foreach ($h in $Hosts) {
    $r = ssh -o BatchMode=yes -o ConnectTimeout=5 -o StrictHostKeyChecking=accept-new "user@$h" "hostname" 2>$null
    if ($r -match 'AnkerPI02') { $target = $h; Log "PI02 via $h"; break }
  }
  if (-not $target) { Log 'PI02 offline — retry 20s'; Start-Sleep 20 }
}

Log 'stop old clock + upload'
ssh -o BatchMode=yes "user@$target" "sudo systemctl stop fb-clock 2>/dev/null; sudo systemctl stop fb_clock_opencv 2>/dev/null; sudo systemctl unmask fb-clock 2>/dev/null; pkill -f fb_clock_opencv.py 2>/dev/null; echo OK"
scp -o BatchMode=yes $Out "user@${target}:/home/user/WerbeLEDbox-CountDown/media/clock_24h.mp4"
if ($LASTEXITCODE -ne 0) { Log "SCP mp4 FAILED"; exit 1 }
scp -o BatchMode=yes $PlayerLocal "user@${target}:/home/user/WerbeLEDbox-CountDown/fb_clock_play.py"
scp -o BatchMode=yes $UnitLocal "user@${target}:/tmp/fb-clock.service"
scp -o BatchMode=yes $RemoteSh "user@${target}:/tmp/deploy_on_pi02.sh"
ssh -o BatchMode=yes "user@$target" "sed -i 's/\r$//' /tmp/deploy_on_pi02.sh && bash /tmp/deploy_on_pi02.sh" 2>&1 | Tee-Object -FilePath (Join-Path $Media '_deploy_clock_24h_remote.txt')
Log '==== DEPLOY WATCHER DONE ===='
