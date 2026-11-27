# Removes the blocker completely (needs administrator rights).
$ErrorActionPreference = 'Stop'
$dir = "$env:ProgramData\YouTubeBlock"
Unregister-ScheduledTask -TaskName 'YouTubeStudyBlock' -Confirm:$false -ErrorAction SilentlyContinue
& (Join-Path $PSScriptRoot 'youtube-block.ps1') -Remove
if ($PSScriptRoot -ne $dir -and (Test-Path $dir)) { Remove-Item $dir -Recurse -Force }
