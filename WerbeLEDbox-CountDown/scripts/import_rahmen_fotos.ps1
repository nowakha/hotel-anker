# Copy lightbox frame photos into Richnerstutz package with canonical names.
param(
  [Parameter(Mandatory = $true)]
  [string]$SourceDir,
  [string]$DestDir = ""
)

$ErrorActionPreference = "Stop"
if (-not $DestDir) {
  $DestDir = Join-Path $PSScriptRoot "..\..\Richnerstutz-Bespannung-Paket\06-fotos-vom-rahmen"
}
$DestDir = Resolve-Path $DestDir
$SourceDir = Resolve-Path $SourceDir

$files = Get-ChildItem $SourceDir -File | Where-Object {
  $_.Extension -match '\.(jpe?g|png|heic)$'
} | Sort-Object Name

if ($files.Count -lt 3) {
  throw "Need at least 3 images in $SourceDir (found $($files.Count))"
}

$names = @(
  "01-gesamtansicht.jpg",
  "02-ecke-keder-nah.jpg",
  "03-kendu-controller-diffuser.jpg"
)

for ($i = 0; $i -lt [Math]::Min(3, $files.Count); $i++) {
  $src = $files[$i].FullName
  $dst = Join-Path $DestDir $names[$i]
  # convert heic/png → jpg via .NET if needed; else copy
  if ($files[$i].Extension -match '\.jpe?g$') {
    Copy-Item $src $dst -Force
  } else {
    # keep original extension if not jpeg
    $dst = [IO.Path]::ChangeExtension($dst, $files[$i].Extension)
    Copy-Item $src $dst -Force
  }
  Write-Host "wrote $dst"
}

Write-Host "Done. Optional 4th/5th files can be copied manually as 05-*.jpg / 06-*.jpg"
