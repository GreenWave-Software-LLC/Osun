$ErrorActionPreference = 'Stop'
$srcPath = Join-Path $PSScriptRoot 'src'
$env:PYTHONPATH = $srcPath

$expectedModel = 'qwen3.5:9b'
$configuredModelStore = $null
$modelStorePathFile = Join-Path $PSScriptRoot '.osun-local\ollama-models.path'
if (Test-Path -LiteralPath $modelStorePathFile -PathType Leaf) {
    try {
        $candidateModelStore = (Get-Content -LiteralPath $modelStorePathFile -Raw -ErrorAction Stop).Trim()
        if ($candidateModelStore.Length -gt 512 -or -not [System.IO.Path]::IsPathRooted($candidateModelStore)) {
            throw 'The local Ollama model-store path must be a short absolute path.'
        }
        $configuredModelStore = (Resolve-Path -LiteralPath $candidateModelStore -ErrorAction Stop).Path
        $env:OLLAMA_MODELS = $configuredModelStore
    } catch {
        $configuredModelStore = $null
        # A bad local override never prevents Osun from starting with Ollama's normal configuration.
    }
}

$ollamaExe = Join-Path $env:LOCALAPPDATA 'Programs\Ollama\ollama.exe'
if (Test-Path -LiteralPath $ollamaExe) {
    $ollamaReady = $false
    try {
        Invoke-RestMethod -Uri 'http://127.0.0.1:11434/api/version' -TimeoutSec 2 | Out-Null
        $ollamaReady = $true
    } catch {
        # The bounded startup path below handles an unavailable runtime.
    }
    if ($ollamaReady -and $configuredModelStore) {
        try {
            $tags = Invoke-RestMethod -Uri 'http://127.0.0.1:11434/api/tags' -TimeoutSec 3
            $availableModels = @($tags.models | ForEach-Object { $_.name })
            if ($expectedModel -notin $availableModels) {
                Get-Process ollama -ErrorAction SilentlyContinue | Stop-Process -Force
                $ollamaReady = $false
            }
        } catch {
            Get-Process ollama -ErrorAction SilentlyContinue | Stop-Process -Force
            $ollamaReady = $false
        }
    }
    if (-not $ollamaReady) {
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
