param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('probe', 'play-url', 'pause', 'resume', 'next', 'previous')]
    [string]$Action,
    [ValidateLength(0, 2048)]
    [string]$MediaUrl = '',
    [ValidateLength(0, 200)]
    [string]$Query = '',
    [ValidateLength(0, 200)]
    [string]$ExpectedTitle = '',
    [ValidateLength(0, 200)]
    [string]$ExpectedArtist = ''
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$OutputEncoding = [System.Text.UTF8Encoding]::new($false)

Add-Type -AssemblyName System.Runtime.WindowsRuntime
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Windows.Forms
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class OsunAppleMusicNative {
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool ShowWindowAsync(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint processId);
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")] public static extern void mouse_event(uint flags, uint dx, uint dy, uint data, UIntPtr extraInfo);
}
'@

$script:MediaManagerType = [Windows.Media.Control.GlobalSystemMediaTransportControlsSessionManager, Windows.Media.Control, ContentType = WindowsRuntime]
$script:MediaPropertiesType = [Windows.Media.Control.GlobalSystemMediaTransportControlsSessionMediaProperties, Windows.Media.Control, ContentType = WindowsRuntime]
$script:AsTaskMethod = [System.WindowsRuntimeSystemExtensions].GetMethods() |
    Where-Object { $_.Name -eq 'AsTask' -and $_.IsGenericMethod -and $_.GetParameters().Count -eq 1 } |
    Select-Object -First 1

function Wait-WinRtOperation {
    param($Operation, [Type]$ResultType, [int]$TimeoutMilliseconds = 5000)
    $method = $script:AsTaskMethod.MakeGenericMethod($ResultType)
    $task = $method.Invoke($null, @($Operation))
    if (-not $task.Wait($TimeoutMilliseconds)) {
        throw 'Windows media control timed out.'
    }
    return $task.Result
}

function Write-BridgeResult {
    param(
        [bool]$Success,
        [bool]$Verified = $false,
        [Nullable[bool]]$PlaybackActive = $null,
        [string]$NowPlaying = '',
        [string]$Evidence = '',
        [string]$ErrorMessage = '',
        [hashtable]$Extra = @{}
    )
    $result = [ordered]@{
        success = $Success
        verified = $Verified
        playback_active = $PlaybackActive
        now_playing = $NowPlaying
        evidence = $Evidence
        error = $ErrorMessage
    }
    foreach ($key in $Extra.Keys) { $result[$key] = $Extra[$key] }
    $result | ConvertTo-Json -Compress -Depth 4
}

function Get-AppleMusicExecutable {
    function Test-AppleMusicPath {
        param([string]$Candidate)
        if (-not $Candidate) { return $false }
        try { $fullPath = [IO.Path]::GetFullPath($Candidate) } catch { return $false }
        $registeredAlias = Join-Path $env:LOCALAPPDATA 'Microsoft\WindowsApps\AppleMusic.exe'
        $packageRoot = Join-Path $env:ProgramFiles 'WindowsApps\AppleInc.AppleMusicWin_'
        return $fullPath.Equals($registeredAlias, [StringComparison]::OrdinalIgnoreCase) -or
            ($fullPath.StartsWith($packageRoot, [StringComparison]::OrdinalIgnoreCase) -and
             [IO.Path]::GetFileName($fullPath).Equals('AppleMusic.exe', [StringComparison]::OrdinalIgnoreCase))
    }
    $command = Get-Command 'AppleMusic.exe' -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($command -and (Test-AppleMusicPath $command.Source)) { return $command.Source }
    $alias = Join-Path $env:LOCALAPPDATA 'Microsoft\WindowsApps\AppleMusic.exe'
    try {
        if (Test-Path -LiteralPath $alias -PathType Leaf -ErrorAction Stop -and (Test-AppleMusicPath $alias)) { return $alias }
    } catch {
        # App execution aliases can deny metadata reads in restricted Windows sessions.
    }
    $running = Get-Process -Name 'AppleMusic' -ErrorAction SilentlyContinue | Select-Object -First 1
    try {
        if ($running -and $running.Path -and (Test-AppleMusicPath $running.Path)) { return $running.Path }
    } catch {
        # A process in another Windows session is never used as an executable path.
    }
    return $null
}

function Get-AppleSession {
    try {
        $manager = Wait-WinRtOperation ($script:MediaManagerType::RequestAsync()) $script:MediaManagerType 5000
        $allowedSources = @(
            'AppleInc.AppleMusicWin_nzyj5cx40ttqa!App',
            'AppleInc.AppleMusicWin_nzyj5cx40ttqa',
            'AppleMusic.exe',
            'AppleMusic'
        )
        return $manager.GetSessions() |
            Where-Object { $_.SourceAppUserModelId -in $allowedSources } |
            Select-Object -First 1
    } catch {
        return $null
    }
}

function Get-SessionSnapshot {
    param($Session)
    if (-not $Session) { return $null }
    try {
        $playback = $Session.GetPlaybackInfo().PlaybackStatus.ToString()
        $properties = Wait-WinRtOperation ($Session.TryGetMediaPropertiesAsync()) $script:MediaPropertiesType 5000
        $title = ' ' + $properties.Title
        $artist = ' ' + $properties.Artist
        $title = $title.Trim()
        $artist = $artist.Trim()
        return [pscustomobject]@{
            Status = $playback
            Title = $title
            Artist = $artist
            Display = $(if ($title -and $artist) { "$title by $artist" } else { $title })
        }
    } catch {
        return $null
    }
}

function Test-ExpectedTrack {
    param($Snapshot)
    if (-not $Snapshot -or -not $ExpectedTitle) { return $true }
    $titleMatches = $Snapshot.Title -and (
        $Snapshot.Title.IndexOf($ExpectedTitle, [StringComparison]::OrdinalIgnoreCase) -ge 0 -or
        $ExpectedTitle.IndexOf($Snapshot.Title, [StringComparison]::OrdinalIgnoreCase) -ge 0
    )
    $artistMatches = -not $ExpectedArtist -or ($Snapshot.Artist -and (
        $Snapshot.Artist.IndexOf($ExpectedArtist, [StringComparison]::OrdinalIgnoreCase) -ge 0 -or
        $ExpectedArtist.IndexOf($Snapshot.Artist, [StringComparison]::OrdinalIgnoreCase) -ge 0
    ))
    return $titleMatches -and $artistMatches
}

function Wait-ForSessionState {
    param(
        [string]$WantedStatus = '',
        [string]$PreviousDisplay = '',
        [int]$TimeoutMilliseconds = 12000
    )
    $deadline = [DateTime]::UtcNow.AddMilliseconds($TimeoutMilliseconds)
    do {
        $session = Get-AppleSession
        $snapshot = Get-SessionSnapshot $session
        if ($snapshot) {
            $statusMatches = -not $WantedStatus -or $snapshot.Status -eq $WantedStatus
            $trackMatches = Test-ExpectedTrack $snapshot
            $changed = -not $PreviousDisplay -or $snapshot.Display -ne $PreviousDisplay
            if ($statusMatches -and $trackMatches -and $changed) {
                return [pscustomobject]@{ Session = $session; Snapshot = $snapshot }
            }
        }
        Start-Sleep -Milliseconds 200
    } while ([DateTime]::UtcNow -lt $deadline)
    return $null
}

function Invoke-SessionCommand {
    param($Session, [string]$Command)
    if (-not $Session) { return $false }
    try {
        $operation = switch ($Command) {
            'pause' { $Session.TryPauseAsync() }
            'resume' { $Session.TryPlayAsync() }
            'next' { $Session.TrySkipNextAsync() }
            'previous' { $Session.TrySkipPreviousAsync() }
        }
        return [bool](Wait-WinRtOperation $operation ([bool]) 5000)
    } catch {
        return $false
    }
}

function Get-AppleAutomationElements {
    $processes = @(Get-Process -Name 'AppleMusic' -ErrorAction SilentlyContinue)
    if (-not $processes) { return $null }
    $root = [System.Windows.Automation.AutomationElement]::RootElement
    foreach ($process in $processes) {
        $condition = New-Object System.Windows.Automation.PropertyCondition(
            [System.Windows.Automation.AutomationElement]::ProcessIdProperty,
            $process.Id
        )
        $elements = $root.FindAll([System.Windows.Automation.TreeScope]::Descendants, $condition)
        if ($elements.Count -gt 0) {
            return [pscustomobject]@{ Process = $process; Elements = $elements }
        }
    }
    return $null
}

function Invoke-AutomationElement {
    param($Element)
    $pattern = $null
    if ($Element.TryGetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern, [ref]$pattern)) {
        $pattern.Invoke()
        return $true
    }
    if ($Element.TryGetCurrentPattern([System.Windows.Automation.SelectionItemPattern]::Pattern, [ref]$pattern)) {
        $pattern.Select()
        return $true
    }
    try {
        $point = $Element.GetClickablePoint()
        [OsunAppleMusicNative]::SetCursorPos([int]$point.X, [int]$point.Y) | Out-Null
        [OsunAppleMusicNative]::mouse_event(0x0002, 0, 0, 0, [UIntPtr]::Zero)
        [OsunAppleMusicNative]::mouse_event(0x0004, 0, 0, 0, [UIntPtr]::Zero)
        [OsunAppleMusicNative]::mouse_event(0x0002, 0, 0, 0, [UIntPtr]::Zero)
        [OsunAppleMusicNative]::mouse_event(0x0004, 0, 0, 0, [UIntPtr]::Zero)
        return $true
    } catch {
        return $false
    }
}

function Set-AppleMusicForeground {
    param($Automation)
    $handle = [IntPtr]$Automation.Process.MainWindowHandle
    if ($handle -eq [IntPtr]::Zero) {
        for ($index = 0; $index -lt $Automation.Elements.Count; $index++) {
            $candidate = $Automation.Elements.Item($index)
            if ($candidate.Current.ControlType -eq [System.Windows.Automation.ControlType]::Window -and $candidate.Current.NativeWindowHandle) {
                $handle = [IntPtr]$candidate.Current.NativeWindowHandle
                break
            }
        }
    }
    if ($handle -eq [IntPtr]::Zero) { return $false }
    [OsunAppleMusicNative]::ShowWindowAsync($handle, 9) | Out-Null
    if (-not [OsunAppleMusicNative]::SetForegroundWindow($handle)) { return $false }
    Start-Sleep -Milliseconds 150
    $foreground = [OsunAppleMusicNative]::GetForegroundWindow()
    [uint32]$foregroundProcessId = 0
    [OsunAppleMusicNative]::GetWindowThreadProcessId($foreground, [ref]$foregroundProcessId) | Out-Null
    return $foregroundProcessId -eq [uint32]$Automation.Process.Id
}

function Invoke-UiaTransport {
    param([string]$Command)
    $automation = Get-AppleAutomationElements
    if (-not $automation) { return $false }
    $names = switch ($Command) {
        'pause' { '^(Pause)( button)?$' }
        'resume' { '^(Play|Resume)( button)?$' }
        'next' { '^(Next|Next Song|Skip Forward)( button)?$' }
        'previous' { '^(Previous|Previous Song|Skip Back)( button)?$' }
    }
    $candidates = @()
    for ($index = 0; $index -lt $automation.Elements.Count; $index++) {
        $element = $automation.Elements.Item($index)
        $current = $element.Current
        if ($current.ControlType -eq [System.Windows.Automation.ControlType]::Button -and $current.IsEnabled -and -not $current.IsOffscreen -and $current.Name -match $names) {
            $candidates += $element
        }
    }
    $target = $candidates | Sort-Object { $_.Current.BoundingRectangle.Top } | Select-Object -First 1
    if (-not $target) { return $false }
    return Invoke-AutomationElement $target
}

function Invoke-UiaSearchFallback {
    if (-not $Query -or -not $ExpectedTitle) { return $false }
    $automation = Get-AppleAutomationElements
    if (-not $automation -or -not (Set-AppleMusicForeground $automation)) { return $false }
    [System.Windows.Forms.SendKeys]::SendWait('^f')
    Start-Sleep -Milliseconds 250
    $focused = [System.Windows.Automation.AutomationElement]::FocusedElement
    if (-not $focused -or $focused.Current.ProcessId -ne $automation.Process.Id) { return $false }
    $valuePattern = $null
    if (-not $focused.TryGetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern, [ref]$valuePattern)) { return $false }
    $valuePattern.SetValue($Query)
    [System.Windows.Forms.SendKeys]::SendWait('{ENTER}')
    Start-Sleep -Milliseconds 1500
    $automation = Get-AppleAutomationElements
    if (-not $automation) { return $false }
    $matches = @()
    for ($index = 0; $index -lt $automation.Elements.Count; $index++) {
        $element = $automation.Elements.Item($index)
        $name = $element.Current.Name
        if (-not $element.Current.IsOffscreen -and $name -and $name.IndexOf($ExpectedTitle, [StringComparison]::OrdinalIgnoreCase) -ge 0) {
            $matches += $element
        }
    }
    $target = $matches | Sort-Object { $_.Current.BoundingRectangle.Top } | Select-Object -First 1
    return $target -and (Invoke-AutomationElement $target)
}

$executable = Get-AppleMusicExecutable
if ($Action -eq 'probe') {
    $session = Get-AppleSession
    $snapshot = Get-SessionSnapshot $session
    $automation = Get-AppleAutomationElements
    Write-BridgeResult -Success ([bool]$executable) -Verified ([bool]$session) -PlaybackActive $(if ($snapshot) { $snapshot.Status -eq 'Playing' } else { $null }) -NowPlaying $(if ($snapshot) { $snapshot.Display } else { '' }) -Evidence $(if ($session) { 'windows_media_session' } elseif ($automation) { 'apple_music_ui_automation' } else { 'installation_only' }) -ErrorMessage $(if ($executable) { '' } else { 'The Apple Music app is not installed for this Windows account.' }) -Extra @{ installed = [bool]$executable; running = [bool](Get-Process -Name 'AppleMusic' -ErrorAction SilentlyContinue); session_available = [bool]$session; automation_available = [bool]$automation }
    exit 0
}

if (-not $executable) {
    Write-BridgeResult -Success $false -ErrorMessage 'The Apple Music app is not installed for this Windows account.'
    exit 0
}

if ($Action -eq 'play-url') {
    $uri = $null
    if (-not [Uri]::TryCreate($MediaUrl, [UriKind]::Absolute, [ref]$uri) -or $uri.Scheme -ne 'https' -or $uri.Host -notin @('music.apple.com', 'itunes.apple.com') -or $uri.UserInfo -or $uri.Port -notin @(-1, 443)) {
        Write-BridgeResult -Success $false -ErrorMessage 'Osun rejected an invalid Apple Music catalog link.'
        exit 0
    }
    Start-Process -FilePath $executable -ArgumentList @('/play', $MediaUrl) | Out-Null
    $confirmed = Wait-ForSessionState -WantedStatus 'Playing' -TimeoutMilliseconds 9000
    if (-not $confirmed) {
        Invoke-UiaSearchFallback | Out-Null
        $confirmed = Wait-ForSessionState -WantedStatus 'Playing' -TimeoutMilliseconds 7000
    }
    if ($confirmed) {
        Write-BridgeResult -Success $true -Verified $true -PlaybackActive $true -NowPlaying $confirmed.Snapshot.Display -Evidence 'windows_media_session'
    } else {
        Write-BridgeResult -Success $false -ErrorMessage "Apple Music did not confirm playback of $ExpectedTitle. The app may need you to sign in once."
    }
    exit 0
}

$session = Get-AppleSession
$before = Get-SessionSnapshot $session
$accepted = Invoke-SessionCommand $session $Action
if (-not $accepted) { $accepted = Invoke-UiaTransport $Action }
if (-not $accepted) {
    Write-BridgeResult -Success $false -ErrorMessage 'Apple Music did not expose the requested control. Open the app and confirm you are signed in.'
    exit 0
}
$wanted = if ($Action -eq 'pause') { 'Paused' } else { 'Playing' }
$previous = if ($Action -in @('next', 'previous') -and $before) { $before.Display } else { '' }
$confirmed = Wait-ForSessionState -WantedStatus $wanted -PreviousDisplay $previous -TimeoutMilliseconds 8000
if ($confirmed) {
    Write-BridgeResult -Success $true -Verified $true -PlaybackActive ($wanted -eq 'Playing') -NowPlaying $confirmed.Snapshot.Display -Evidence 'windows_media_session'
} else {
    Write-BridgeResult -Success $true -Verified $false -PlaybackActive $null -Evidence 'targeted_ui_command' -ErrorMessage ''
}
