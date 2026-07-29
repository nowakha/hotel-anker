$ErrorActionPreference = "Continue"
$log = "C:\Users\Public\pi01-sd-fix.log"
function Log($m) { "$(Get-Date -Format o) $m" | Tee-Object -FilePath $log -Append }
Remove-Item $log -Force -ErrorAction SilentlyContinue

$usbipd = "$env:ProgramFiles\usbipd-win\usbipd.exe"
if (-not (Test-Path $usbipd)) { $usbipd = (Get-Command usbipd -ErrorAction SilentlyContinue).Source }
Log "usbipd=$usbipd"

# Unmount Windows letters so Linux can claim the disk
try {
    Get-Partition -DiskNumber 1 -ErrorAction SilentlyContinue | ForEach-Object {
        if ($_.DriveLetter) {
            Log "remove letter $($_.DriveLetter)"
            Remove-PartitionAccessPath -DiskNumber 1 -PartitionNumber $_.PartitionNumber -AccessPath "$($_.DriveLetter):\" -ErrorAction SilentlyContinue
        }
    }
} catch { Log "partition letter: $_" }

& $usbipd list 2>&1 | ForEach-Object { Log $_ }

# Find mass storage busid
$list = & $usbipd list 2>&1 | Out-String
$busid = $null
foreach ($line in ($list -split "`n")) {
    if ($line -match '^\s*(\d+-\d+)\s+\S+\s+.*Mass Storage') { $busid = $Matches[1]; break }
    if ($line -match '^\s*(\d+-\d+)\s+\S+\s+.*STORAGE') { $busid = $Matches[1]; break }
}
if (-not $busid) {
    # fallback known from earlier probe
    $busid = "6-2"
}
Log "busid=$busid"

& $usbipd bind --busid $busid 2>&1 | ForEach-Object { Log "bind: $_" }
& $usbipd attach --wsl --busid $busid 2>&1 | ForEach-Object { Log "attach: $_" }
Start-Sleep -Seconds 3

$ls = wsl -u root -e bash -lc 'lsblk -o NAME,SIZE,FSTYPE,LABEL,MOUNTPOINT,MODEL; blkid'
Log "lsblk after attach:"
$ls | ForEach-Object { Log $_ }
