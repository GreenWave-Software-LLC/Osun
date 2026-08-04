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
    [DllImport("user32.dll")] public static extern IntPtr SetActiveWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool ShowWindowAsync(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint processId);
    [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
    [DllImport("user32.dll")] public static extern bool AttachThreadInput(uint sourceThreadId, uint targetThreadId, bool attach);
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
    param([int]$TimeoutMilliseconds = 0)
    $deadline = [DateTime]::UtcNow.AddMilliseconds($TimeoutMilliseconds)
    do {
        $processes = @(Get-Process -Name 'AppleMusic' -ErrorAction SilentlyContinue)
        if ($processes) {
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
        }
        if ([DateTime]::UtcNow -lt $deadline) { Start-Sleep -Milliseconds 200 }
    } while ([DateTime]::UtcNow -lt $deadline)
    return $null
}

function Invoke-AutomationElement {
    param($Element, $Automation)
    $pattern = $null
    if ($Element.TryGetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern, [ref]$pattern)) {
        $pattern.Invoke()
        return $true
    }
    if ($Element.TryGetCurrentPattern([System.Windows.Automation.SelectionItemPattern]::Pattern, [ref]$pattern)) {
        $pattern.Select()
        return $true
    }
    if (-not $Automation -or -not (Set-AppleMusicForeground $Automation)) { return $false }
    try {
        try {
            $point = $Element.GetClickablePoint()
        } catch {
            $rectangle = $Element.Current.BoundingRectangle
            if ($rectangle.Width -le 0 -or $rectangle.Height -le 0) { return $false }
            $point = [System.Windows.Point]::new(
                $rectangle.Left + ($rectangle.Width / 2),
                $rectangle.Top + ($rectangle.Height / 2)
            )
        }
        [OsunAppleMusicNative]::SetCursorPos([int]$point.X, [int]$point.Y) | Out-Null
        [OsunAppleMusicNative]::mouse_event(0x0002, 0, 0, 0, [UIntPtr]::Zero)
        [OsunAppleMusicNative]::mouse_event(0x0004, 0, 0, 0, [UIntPtr]::Zero)
        return $true
    } catch {
        return $false
    }
}

function Invoke-AutomationDoubleClick {
    param($Element, $Automation)
    if (-not (Set-AppleMusicForeground $Automation)) { return $false }
    try {
        try {
            $point = $Element.GetClickablePoint()
        } catch {
            $rectangle = $Element.Current.BoundingRectangle
            if ($rectangle.Width -le 0 -or $rectangle.Height -le 0) { return $false }
            $point = [System.Windows.Point]::new(
                $rectangle.Left + ($rectangle.Width / 2),
                $rectangle.Top + ($rectangle.Height / 2)
            )
        }
        [OsunAppleMusicNative]::SetCursorPos([int]$point.X, [int]$point.Y) | Out-Null
        foreach ($click in 1..2) {
            [OsunAppleMusicNative]::mouse_event(0x0002, 0, 0, 0, [UIntPtr]::Zero)
            [OsunAppleMusicNative]::mouse_event(0x0004, 0, 0, 0, [UIntPtr]::Zero)
            Start-Sleep -Milliseconds 70
        }
        return $true
    } catch {
        return $false
    }
}

function Invoke-AutomationTrack {
    param($Element, $Automation)
    if ($Element.Current.ClassName -eq 'ListViewItem') {
        return Invoke-AutomationDoubleClick $Element $Automation
    }

    # Catalog search exposes result cards as GridViewItem controls. Their native
    # Invoke action opens the album; playback then requires the exact ListViewItem row.
    $invoke = $null
    if ($Element.TryGetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern, [ref]$invoke)) {
        try { $invoke.Invoke() } catch { return $false }
        $albumTrack = Wait-ForAppleAlbumTrack -TimeoutMilliseconds 6000
        if ($albumTrack) {
            return Invoke-AutomationDoubleClick $albumTrack.Element $albumTrack.Automation
        }
    }
    return Invoke-AutomationDoubleClick $Element $Automation
}

function Test-AppleMusicForeground {
    param($Automation)
    $foreground = [OsunAppleMusicNative]::GetForegroundWindow()
    if ($foreground -eq [IntPtr]::Zero) { return $false }
    [uint32]$foregroundProcessId = 0
    [OsunAppleMusicNative]::GetWindowThreadProcessId($foreground, [ref]$foregroundProcessId) | Out-Null
    return $foregroundProcessId -eq [uint32]$Automation.Process.Id
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
    [OsunAppleMusicNative]::SetForegroundWindow($handle) | Out-Null
    Start-Sleep -Milliseconds 150
    if (Test-AppleMusicForeground $Automation) { return $true }

    # Windows may reject foreground activation from a background web request. Attach only
    # to the already-validated Apple Music window long enough to activate that exact window.
    $foreground = [OsunAppleMusicNative]::GetForegroundWindow()
    [uint32]$ignoredProcessId = 0
    $foregroundThread = if ($foreground -ne [IntPtr]::Zero) {
        [OsunAppleMusicNative]::GetWindowThreadProcessId($foreground, [ref]$ignoredProcessId)
    } else { 0 }
    [uint32]$targetProcessId = 0
    $targetThread = [OsunAppleMusicNative]::GetWindowThreadProcessId($handle, [ref]$targetProcessId)
    if ($targetProcessId -ne [uint32]$Automation.Process.Id) { return $false }
    $currentThread = [OsunAppleMusicNative]::GetCurrentThreadId()
    $attachedForeground = $false
    $attachedTarget = $false
    try {
        if ($foregroundThread -and $foregroundThread -ne $currentThread) {
            $attachedForeground = [OsunAppleMusicNative]::AttachThreadInput($currentThread, $foregroundThread, $true)
        }
        if ($targetThread -and $targetThread -ne $currentThread) {
            $attachedTarget = [OsunAppleMusicNative]::AttachThreadInput($currentThread, $targetThread, $true)
        }
        [OsunAppleMusicNative]::BringWindowToTop($handle) | Out-Null
        [OsunAppleMusicNative]::SetActiveWindow($handle) | Out-Null
        [OsunAppleMusicNative]::SetForegroundWindow($handle) | Out-Null
    } finally {
        if ($attachedTarget) {
            [OsunAppleMusicNative]::AttachThreadInput($currentThread, $targetThread, $false) | Out-Null
        }
        if ($attachedForeground) {
            [OsunAppleMusicNative]::AttachThreadInput($currentThread, $foregroundThread, $false) | Out-Null
        }
    }
    Start-Sleep -Milliseconds 200
    return Test-AppleMusicForeground $Automation
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
    return Invoke-AutomationElement $target $automation
}

function Find-AppleSearchField {
    param($Automation)
    $candidates = @()
    for ($index = 0; $index -lt $Automation.Elements.Count; $index++) {
        $element = $Automation.Elements.Item($index)
        $current = $element.Current
        if ($current.ControlType -eq [System.Windows.Automation.ControlType]::Edit -and $current.IsEnabled -and -not $current.IsOffscreen -and
            ($current.Name -match '(?i)search' -or $current.AutomationId -match '(?i)search')) {
            $candidates += $element
        }
    }
    return $candidates | Sort-Object { $_.Current.BoundingRectangle.Top }, { $_.Current.BoundingRectangle.Left } | Select-Object -First 1
}

function Set-AppleSearchQuery {
    param($Automation, $SearchField)
    if (-not $SearchField) { return $false }
    try { $SearchField.SetFocus() } catch { }
    $valuePattern = $null
    if (-not $SearchField.TryGetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern, [ref]$valuePattern)) {
        return $false
    }
    try {
        $valuePattern.SetValue($Query)
        return $true
    } catch {
        return $false
    }
}

function Select-AppleMusicSearchScope {
    param($Automation)
    $scopeTypes = @(
        [System.Windows.Automation.ControlType]::Button,
        [System.Windows.Automation.ControlType]::RadioButton,
        [System.Windows.Automation.ControlType]::TabItem
    )
    $candidates = @()
    for ($index = 0; $index -lt $Automation.Elements.Count; $index++) {
        $element = $Automation.Elements.Item($index)
        $current = $element.Current
        if ($current.IsEnabled -and -not $current.IsOffscreen -and $current.Name -eq 'Apple Music' -and $current.ControlType -in $scopeTypes) {
            $candidates += $element
        }
    }
    $target = $candidates | Sort-Object { $_.Current.BoundingRectangle.Top } | Select-Object -First 1
    if (-not $target) { return $false }
    return Invoke-AutomationElement $target $Automation
}

function Find-AppleTrackResult {
    param($Automation)
    $matches = @()
    $rowTypes = @(
        [System.Windows.Automation.ControlType]::ListItem,
        [System.Windows.Automation.ControlType]::DataItem
    )
    for ($index = 0; $index -lt $Automation.Elements.Count; $index++) {
        $element = $Automation.Elements.Item($index)
        $current = $element.Current
        $name = $current.Name
        if ($current.ControlType -ne [System.Windows.Automation.ControlType]::Edit -and -not $current.IsOffscreen -and $current.IsEnabled -and
            $name -and $name.IndexOf($ExpectedTitle, [StringComparison]::OrdinalIgnoreCase) -ge 0) {
            $isTrackRow = $current.ControlType -in $rowTypes
            $artistMatches = -not $ExpectedArtist -or $name.IndexOf($ExpectedArtist, [StringComparison]::OrdinalIgnoreCase) -ge 0
            $typeRank = if ($isTrackRow -and $artistMatches) { 0 } elseif ($isTrackRow) { 1 } else { 2 }
            $exactRank = [int](-not $name.Equals($ExpectedTitle, [StringComparison]::OrdinalIgnoreCase))
            $matches += [pscustomobject]@{ Element = $element; TypeRank = $typeRank; ExactRank = $exactRank; Top = $current.BoundingRectangle.Top }
        }
    }
    return ($matches | Sort-Object TypeRank, ExactRank, Top | Select-Object -First 1).Element
}

function Wait-ForAppleTrackResult {
    param([int]$TimeoutMilliseconds = 6000)
    $deadline = [DateTime]::UtcNow.AddMilliseconds($TimeoutMilliseconds)
    do {
        $automation = Get-AppleAutomationElements
        if ($automation) {
            $result = Find-AppleTrackResult $automation
            if ($result) { return [pscustomobject]@{ Automation = $automation; Element = $result } }
        }
        Start-Sleep -Milliseconds 200
    } while ([DateTime]::UtcNow -lt $deadline)
    return $null
}

function Wait-ForAppleAlbumTrack {
    param([int]$TimeoutMilliseconds = 6000)
    $deadline = [DateTime]::UtcNow.AddMilliseconds($TimeoutMilliseconds)
    do {
        $automation = Get-AppleAutomationElements
        if ($automation) {
            for ($index = 0; $index -lt $automation.Elements.Count; $index++) {
                $element = $automation.Elements.Item($index)
                $current = $element.Current
                if (-not $current.IsOffscreen -and $current.IsEnabled -and $current.ClassName -eq 'ListViewItem' -and
                    $current.Name -and $current.Name.IndexOf($ExpectedTitle, [StringComparison]::OrdinalIgnoreCase) -ge 0) {
                    return [pscustomobject]@{ Automation = $automation; Element = $element }
                }
            }
        }
        Start-Sleep -Milliseconds 200
    } while ([DateTime]::UtcNow -lt $deadline)
    return $null
}

function Invoke-UiaUrlPlayback {
    $automation = Get-AppleAutomationElements -TimeoutMilliseconds 4000
    if (-not $automation) {
        return [pscustomobject]@{ Invoked = $false; Stage = 'automation_unavailable'; AutomationAvailable = $false; ForegroundAcquired = $false }
    }
    $foregroundAcquired = Set-AppleMusicForeground $automation
    if (-not $foregroundAcquired) {
        return [pscustomobject]@{ Invoked = $false; Stage = 'foreground_blocked'; AutomationAvailable = $true; ForegroundAcquired = $false }
    }
    $match = Wait-ForAppleTrackResult -TimeoutMilliseconds 4000
    if (-not $match) {
        return [pscustomobject]@{ Invoked = $false; Stage = 'url_result_not_found'; AutomationAvailable = $true; ForegroundAcquired = $true }
    }
    if (-not (Invoke-AutomationTrack $match.Element $match.Automation)) {
        return [pscustomobject]@{ Invoked = $false; Stage = 'url_activation_failed'; AutomationAvailable = $true; ForegroundAcquired = $true }
    }
    return [pscustomobject]@{ Invoked = $true; Stage = 'url_track_double_click'; AutomationAvailable = $true; ForegroundAcquired = $true }
}

function Invoke-UiaSearchPlayback {
    if (-not $Query -or -not $ExpectedTitle) {
        return [pscustomobject]@{ Invoked = $false; Stage = 'invalid_search'; AutomationAvailable = $false; ForegroundAcquired = $false }
    }
    $automation = Get-AppleAutomationElements -TimeoutMilliseconds 6000
    if (-not $automation) {
        return [pscustomobject]@{ Invoked = $false; Stage = 'automation_unavailable'; AutomationAvailable = $false; ForegroundAcquired = $false }
    }

    $foregroundAcquired = Set-AppleMusicForeground $automation
    $searchField = Find-AppleSearchField $automation
    if (-not $searchField -and $foregroundAcquired) {
        # Apple documents Alt, then N, F as the Windows access key for catalog search.
        [System.Windows.Forms.SendKeys]::SendWait('%nf')
        Start-Sleep -Milliseconds 350
        $automation = Get-AppleAutomationElements
        $searchField = if ($automation) { Find-AppleSearchField $automation } else { $null }
        if (-not $searchField -and $automation) {
            $focusedSearch = [System.Windows.Automation.AutomationElement]::FocusedElement
            if ($focusedSearch -and $focusedSearch.Current.ProcessId -eq $automation.Process.Id -and
                $focusedSearch.Current.ControlType -eq [System.Windows.Automation.ControlType]::Edit) {
                $searchField = $focusedSearch
            }
        }
    }
    if (-not $searchField) {
        return [pscustomobject]@{ Invoked = $false; Stage = 'search_unavailable'; AutomationAvailable = $true; ForegroundAcquired = $foregroundAcquired }
    }

    if (Select-AppleMusicSearchScope $automation) {
        Start-Sleep -Milliseconds 150
        $automation = Get-AppleAutomationElements
        $searchField = if ($automation) { Find-AppleSearchField $automation } else { $null }
    }
    if (-not (Set-AppleSearchQuery $automation $searchField)) {
        return [pscustomobject]@{ Invoked = $false; Stage = 'search_input_failed'; AutomationAvailable = $true; ForegroundAcquired = $foregroundAcquired }
    }
    if (-not $foregroundAcquired) { $foregroundAcquired = Set-AppleMusicForeground $automation }
    if (-not $foregroundAcquired) {
        return [pscustomobject]@{ Invoked = $false; Stage = 'foreground_blocked'; AutomationAvailable = $true; ForegroundAcquired = $false }
    }
    try { $searchField.SetFocus() } catch { }
    $focused = [System.Windows.Automation.AutomationElement]::FocusedElement
    if (-not $focused -or $focused.Current.ProcessId -ne $automation.Process.Id) {
        return [pscustomobject]@{ Invoked = $false; Stage = 'search_focus_failed'; AutomationAvailable = $true; ForegroundAcquired = $true }
    }
    [System.Windows.Forms.SendKeys]::SendWait('{ENTER}')

    $match = Wait-ForAppleTrackResult -TimeoutMilliseconds 6000
    if (-not $match) {
        return [pscustomobject]@{ Invoked = $false; Stage = 'result_not_found'; AutomationAvailable = $true; ForegroundAcquired = $true }
    }
    if (-not (Invoke-AutomationTrack $match.Element $match.Automation)) {
        return [pscustomobject]@{ Invoked = $false; Stage = 'result_activation_failed'; AutomationAvailable = $true; ForegroundAcquired = $true }
    }
    return [pscustomobject]@{ Invoked = $true; Stage = 'track_double_click'; AutomationAvailable = $true; ForegroundAcquired = $true }
}

$executable = Get-AppleMusicExecutable
if ($Action -eq 'probe') {
    $session = Get-AppleSession
    $snapshot = Get-SessionSnapshot $session
    $automation = Get-AppleAutomationElements
    Write-BridgeResult -Success ([bool]$executable) -Verified ([bool]$session) -PlaybackActive $(if ($snapshot) { $snapshot.Status -eq 'Playing' } else { $null }) -NowPlaying $(if ($snapshot) { $snapshot.Display } else { '' }) -Evidence $(if ($session) { 'windows_media_session' } elseif ($automation) { 'apple_music_ui_automation' } else { 'installation_only' }) -ErrorMessage $(if ($executable) { '' } else { 'The Apple Music app is not installed for this Windows account.' }) -Extra @{ installed = [bool]$executable; running = [bool](Get-Process -Name 'AppleMusic' -ErrorAction SilentlyContinue); session_available = [bool]$session; automation_available = [bool]$automation; automation_element_count = $(if ($automation) { $automation.Elements.Count } else { 0 }) }
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
    # /url is the Apple package's registered, bounded URL command. /play is not a
    # registered Apple Music Windows command and only caused a taskbar attention flash.
    Start-Process -FilePath $executable -ArgumentList @('/url', $MediaUrl) | Out-Null
    $urlResult = Invoke-UiaUrlPlayback
    $confirmed = if ($urlResult.Invoked) {
        Wait-ForSessionState -WantedStatus 'Playing' -TimeoutMilliseconds 5000
    } else { $null }
    $automationResult = $urlResult
    if (-not $confirmed -and $urlResult.AutomationAvailable) {
        $automationResult = Invoke-UiaSearchPlayback
        $confirmed = if ($automationResult.Invoked) {
            Wait-ForSessionState -WantedStatus 'Playing' -TimeoutMilliseconds 7000
        } else { $null }
    }
    if ($confirmed) {
        Write-BridgeResult -Success $true -Verified $true -PlaybackActive $true -NowPlaying $confirmed.Snapshot.Display -Evidence 'windows_media_session'
    } else {
        $failure = switch ($automationResult.Stage) {
            'automation_unavailable' { 'Apple Music is running, but Windows did not expose its controls to Osun. Run Osun and Apple Music as the same Windows user and privilege level; do not run either as Administrator.' }
            'foreground_blocked' { 'Windows blocked Osun from activating Apple Music. Restore the full Apple Music window, then retry; do not run either app as Administrator.' }
            'search_unavailable' { 'Apple Music is open, but its catalog Search control is unavailable. Exit MiniPlayer or full-screen playback, return to the full window, and retry.' }
            'search_input_failed' { 'Apple Music exposed Search but rejected the query. Return to the full Apple Music window and retry.' }
            'search_focus_failed' { 'Apple Music did not accept keyboard focus. Select its full window once, then retry.' }
            'result_not_found' { "Apple Music catalog Search did not expose $ExpectedTitle as a playable result." }
            'result_activation_failed' { "Apple Music found $ExpectedTitle, but Windows blocked the targeted play action." }
            'track_double_click' { "Apple Music received the play action for $ExpectedTitle but did not publish playback read-back. Confirm the app is signed in and the subscription can play the song." }
            'url_result_not_found' { "Apple Music opened the catalog item for $ExpectedTitle but did not expose a playable song row." }
            'url_activation_failed' { "Apple Music opened $ExpectedTitle, but Windows blocked the targeted play action." }
            'url_track_double_click' { "Apple Music received the play action for $ExpectedTitle but did not publish playback read-back. Confirm the app is signed in and the subscription can play the song." }
            default { 'Apple Music could not complete the targeted playback workflow.' }
        }
        Write-BridgeResult -Success $false -Evidence "apple_music_ui:$($automationResult.Stage)" -ErrorMessage $failure -Extra @{ control_stage = $automationResult.Stage; url_stage = $urlResult.Stage; automation_available = $automationResult.AutomationAvailable; foreground_acquired = $automationResult.ForegroundAcquired }
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
