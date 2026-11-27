# Installs the blocker (needs administrator rights).
$ErrorActionPreference = 'Stop'
$dir = "$env:ProgramData\YouTubeBlock"
$log = Join-Path $PSScriptRoot 'install.log'
try {
    New-Item -ItemType Directory -Force $dir | Out-Null
    # Only administrators and SYSTEM may change files that run as SYSTEM
    icacls $dir /setowner '*S-1-5-32-544' | Out-Null
    icacls $dir /inheritance:r /grant:r '*S-1-5-32-544:(OI)(CI)F' '*S-1-5-18:(OI)(CI)F' '*S-1-5-32-545:(OI)(CI)RX' | Out-Null
    if ($LASTEXITCODE -ne 0) { throw 'icacls failed' }
    Copy-Item (Join-Path $PSScriptRoot 'youtube-block.ps1'), (Join-Path $PSScriptRoot 'uninstall.ps1') $dir -Force
    $hosts = "$env:SystemRoot\System32\drivers\etc\hosts"
    if (-not (Test-Path "$dir\hosts.backup")) { Copy-Item $hosts "$dir\hosts.backup" }

    $action = New-ScheduledTaskAction -Execute "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe" `
        -Argument "-NoProfile -NonInteractive -ExecutionPolicy Bypass -File `"$dir\youtube-block.ps1`""
    $triggers = @(New-ScheduledTaskTrigger -AtStartup)
    $triggers += New-ScheduledTaskTrigger -AtLogOn
    foreach ($t in '00:00', '01:00', '07:00', '18:00', '20:40') { $triggers += New-ScheduledTaskTrigger -Daily -At $t }
    # safety net every 5 minutes (covers sleep / wake)
    $triggers += New-ScheduledTaskTrigger -Once -At (Get-Date).Date -RepetitionInterval (New-TimeSpan -Minutes 5)
    $principal = New-ScheduledTaskPrincipal -UserId 'S-1-5-18' -LogonType ServiceAccount -RunLevel Highest
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable `
        -ExecutionTimeLimit (New-TimeSpan -Minutes 2) -MultipleInstances IgnoreNew
    Register-ScheduledTask -TaskName 'YouTubeStudyBlock' -Action $action -Trigger $triggers -Principal $principal -Settings $settings -Force | Out-Null
    Start-ScheduledTask -TaskName 'YouTubeStudyBlock'
    'OK' | Set-Content $log
} catch {
    "ERROR: $_" | Set-Content $log
    exit 1
}
