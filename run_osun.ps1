$ErrorActionPreference = 'Stop'
$srcPath = Join-Path $PSScriptRoot 'src'
$env:PYTHONPATH = $srcPath

$ollamaExe = Join-Path $env:LOCALAPPDATA 'Programs\Ollama\ollama.exe'
if (Test-Path -LiteralPath $ollamaExe) {
    $ollamaReady = $false
    try {
        Invoke-RestMethod -Uri 'http://127.0.0.1:11434/api/version' -TimeoutSec 2 | Out-Null
        $ollamaReady = $true
    } catch {
        try {
            Start-Process -FilePath $ollamaExe -ArgumentList 'serve' -WindowStyle Hidden
            for ($attempt = 0; $attempt -lt 40; $attempt++) {
                Start-Sleep -Milliseconds 250
                try {
                    Invoke-RestMethod -Uri 'http://127.0.0.1:11434/api/version' -TimeoutSec 1 | Out-Null
                    $ollamaReady = $true
                    break
                } catch {
                    # Continue the bounded local readiness check.
                }
            }
        } catch {
            # Osun still starts with deterministic agent fallbacks when Ollama cannot start.
        }
    }
}

python -m osun
