$ErrorActionPreference = 'Stop'
$srcPath = Join-Path $PSScriptRoot 'src'
$env:PYTHONPATH = $srcPath
python -m osun_lights
