$ErrorActionPreference = "Continue"
$log = "C:\Users\Public\pi01-sd-mount.log"
function Log($m) { "$(Get-Date -Format o) $m" | Tee-Object -FilePath $log -Append }

Remove-Item $log -Force -ErrorAction SilentlyContinue
Log "prepare disk1 for WSL mount"

# Ensure online
Set-Disk -Number 1 -IsOffline $false -ErrorAction SilentlyContinue
Set-Disk -Number 1 -IsReadOnly $false -ErrorAction SilentlyContinue

# Remove Windows drive letters so WSL can attach
Get-Partition -DiskNumber 1 | ForEach-Object {
    if ($_.DriveLetter) {
        Log "remove letter $($_.DriveLetter) from p$($_.PartitionNumber)"
        try {
            Remove-PartitionAccessPath -DiskNumber 1 -PartitionNumber $_.PartitionNumber -AccessPath "$($_.DriveLetter):\"
        } catch {
            Log "Remove-PartitionAccessPath: $_"
            try { Set-Partition -DiskNumber 1 -PartitionNumber $_.PartitionNumber -NewDriveLetter $null } catch { Log "clear letter: $_" }
        }
    }
}

# Also try mountvol
cmd /c "mountvol D: /P" 2>&1 | ForEach-Object { Log "mountvol: $_" }

Start-Sleep -Seconds 2
Get-Partition -DiskNumber 1 | Format-Table PartitionNumber, DriveLetter, Size | Out-String | ForEach-Object { Log $_ }

wsl --unmount '\\.\PHYSICALDRIVE1' 2>&1 | ForEach-Object { Log "unmount: $_" }
Start-Sleep -Seconds 1

# Prefer partitioned mounts
$m2 = wsl --mount '\\.\PHYSICALDRIVE1' --partition 2 --type ext4 2>&1
Log "mount p2 ext4: $m2 exit=$LASTEXITCODE"
$m1 = wsl --mount '\\.\PHYSICALDRIVE1' --partition 1 --type vfat 2>&1
Log "mount p1 vfat: $m1 exit=$LASTEXITCODE"

if ($LASTEXITCODE -ne 0 -and $m2 -match 'fail|Error|Failed') {
    $mb = wsl --mount '\\.\PHYSICALDRIVE1' --bare 2>&1
    Log "mount bare: $mb exit=$LASTEXITCODE"
}

$ls = wsl -u root -e bash -lc 'lsblk -o NAME,SIZE,FSTYPE,LABEL,MOUNTPOINT; echo ---; find /mnt -maxdepth 3 -type d 2>/dev/null; blkid'
Log "after:"
$ls | ForEach-Object { Log $_ }
