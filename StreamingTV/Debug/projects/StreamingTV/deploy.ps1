$tz      = "C:\Users\PedroMelo\.tizen-extension-platform\server\sdktools\data\tools\tizen-core\tz.exe"
$proj    = $PSScriptRoot
$serial  = "192.168.1.101:26101"
$profile = "PedroStreaming"

Write-Host "Building..."
& $tz pack --proj-dir=$proj --sign-profile=$profile
if ($LASTEXITCODE -ne 0) { Write-Host "BUILD FAILED"; exit 1 }

Write-Host "Installing..."
& $tz install-chain --proj-dir=$proj --serial=$serial
if ($LASTEXITCODE -ne 0) { Write-Host "INSTALL FAILED"; exit 1 }

Write-Host "Done. Launching..."
& $tz run --package-id=PedroStrmX --serial=$serial
