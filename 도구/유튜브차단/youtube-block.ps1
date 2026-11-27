# YouTube study-time blocker: adds/removes a marked section in the Windows hosts file.
# Blocked: Mon-Fri 07:00-18:00 and 20:40-01:00 (Friday night runs until Sat 01:00).
param(
    [string]$HostsPath = "$env:SystemRoot\System32\drivers\etc\hosts",
    [datetime]$Now = (Get-Date),
    [switch]$Remove
)

function Test-BlockTime([datetime]$t) {
    $m = $t.Hour * 60 + $t.Minute
    $day = [int]$t.DayOfWeek          # Sunday = 0
    $prev = [int]$t.AddDays(-1).DayOfWeek
    $weekday = ($day -ge 1 -and $day -le 5)
    if ($weekday -and $m -ge 420 -and $m -lt 1080) { return $true }   # 07:00-18:00
    if ($weekday -and $m -ge 1240) { return $true }                   # 20:40-24:00
    if ($prev -ge 1 -and $prev -le 5 -and $m -lt 60) { return $true } # 00:00-01:00
    return $false
}

$begin = '# BEGIN YouTubeStudyBlock'
$end = '# END YouTubeStudyBlock'
$domains = 'youtube.com', 'www.youtube.com', 'm.youtube.com', 'music.youtube.com', 'studio.youtube.com',
    'youtu.be', 'www.youtu.be', 'youtube-nocookie.com', 'www.youtube-nocookie.com',
    'youtubei.googleapis.com', 'youtube.googleapis.com'

# Latin-1 keeps every existing byte unchanged
$enc = [Text.Encoding]::GetEncoding(28591)
$old = [IO.File]::ReadAllText($HostsPath, $enc)
$pattern = '(?s)(\r?\n)?' + [regex]::Escape($begin) + '.*?' + [regex]::Escape($end) + '(\r?\n)?'
$new = [regex]::Replace($old, $pattern, "`r`n").TrimEnd("`r", "`n") + "`r`n"

if (-not $Remove -and (Test-BlockTime $Now)) {
    $lines = @($begin)
    foreach ($d in $domains) { $lines += "0.0.0.0 $d"; $lines += ":: $d" }
    $lines += $end
    $new += ($lines -join "`r`n") + "`r`n"
}

if ($new -ne $old) {
    [IO.File]::WriteAllText($HostsPath, $new, $enc)
    ipconfig /flushdns | Out-Null
}
