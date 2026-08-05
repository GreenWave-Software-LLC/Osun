$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$OutputEncoding = [System.Text.UTF8Encoding]::new($false)

Add-Type -AssemblyName System.Runtime.WindowsRuntime
$script:DeviceInformationType = [Windows.Devices.Enumeration.DeviceInformation, Windows.Devices.Enumeration, ContentType = WindowsRuntime]
$script:DeviceInformationCollectionType = [Windows.Devices.Enumeration.DeviceInformationCollection, Windows.Devices.Enumeration, ContentType = WindowsRuntime]
$script:MediaDeviceType = [Windows.Media.Devices.MediaDevice, Windows.Media, ContentType = WindowsRuntime]
$script:AsTaskMethod = [System.WindowsRuntimeSystemExtensions].GetMethods() |
    Where-Object { $_.Name -eq 'AsTask' -and $_.IsGenericMethod -and $_.GetParameters().Count -eq 1 } |
    Select-Object -First 1

function Wait-WinRtOperation {
    param($Operation, [Type]$ResultType, [int]$TimeoutMilliseconds = 5000)
    $method = $script:AsTaskMethod.MakeGenericMethod($ResultType)
    $task = $method.Invoke($null, @($Operation))
    if (-not $task.Wait($TimeoutMilliseconds)) { throw 'Windows audio discovery timed out.' }
    return $task.Result
}

function Get-ParentInstanceId {
    param([string]$InstanceId)
    try {
        $property = Get-PnpDeviceProperty -InstanceId $InstanceId -KeyName 'DEVPKEY_Device_Parent' -ErrorAction Stop
        return [string]$property.Data
    } catch {
        return ''
    }
}

function Test-BluetoothAncestry {
    param([string]$InstanceId)
    $current = $InstanceId
    $visited = @{}
    for ($depth = 0; $depth -lt 10 -and $current; $depth++) {
        if ($visited.ContainsKey($current)) { break }
        $visited[$current] = $true
        if ($current -match '^(?i:BTHENUM|BTHLEDEVICE|BTHHFENUM)\\') { return $true }
        $current = Get-ParentInstanceId $current
    }
    return $false
}

function Get-WinRtHeadphoneNames {
    param([string]$NamePattern)
    $selector = $script:MediaDeviceType::GetAudioRenderSelector()
    $operation = $script:DeviceInformationType::FindAllAsync($selector)
    $devices = Wait-WinRtOperation $operation $script:DeviceInformationCollectionType 5000
    return @(
        $devices |
            ForEach-Object { [string]$_.Name } |
            Where-Object { $_ -and $_ -match $NamePattern } |
            Sort-Object -Unique |
            Select-Object -First 8
    )
}

try {
    $namePattern = '(?i)(headphones?|headsets?|earbuds?|earphones?|airpods?|\bbuds?\b|beats|quietcomfort|soundcore|jabra|bose|sony|\bWH-[A-Z0-9]|\bWF-[A-Z0-9])'
    try {
        $names = @(
            Get-PnpDevice -Class 'AudioEndpoint' -PresentOnly -Status 'OK' -ErrorAction Stop |
                Where-Object {
                    $_.FriendlyName -match $namePattern -and (Test-BluetoothAncestry $_.InstanceId)
                } |
                ForEach-Object { [string]$_.FriendlyName } |
                Where-Object { $_ } |
                Sort-Object -Unique |
                Select-Object -First 8
        )
        $evidence = 'windows_present_bluetooth_audio_endpoint'
    } catch {
        # DeviceInformation's render selector returns only currently usable output endpoints.
        # The bounded name match is a least-privilege fallback when PnP ancestry is unavailable.
        $names = @(Get-WinRtHeadphoneNames $namePattern)
        $evidence = 'windows_active_headphone_audio_output'
    }
    [ordered]@{
        success = $true
        connected = $names.Count -gt 0
        names = $names
        evidence = $(if ($names.Count -gt 0) { $evidence } else { '' })
        error = ''
    } | ConvertTo-Json -Compress -Depth 3
} catch {
    [ordered]@{
        success = $false
        connected = $false
        names = @()
        evidence = ''
        error = 'Windows could not inspect Bluetooth audio endpoints.'
    } | ConvertTo-Json -Compress -Depth 3
}
