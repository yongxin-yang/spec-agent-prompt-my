# get_env_name.ps1

if ($env:PROJECT_ENV_NAME) {
    Write-Output $env:PROJECT_ENV_NAME
    return
}

$envFilePath = Join-Path $PSScriptRoot "..\..\.env"

if (-not (Test-Path $envFilePath)) {
    Write-Error ".env not found at $envFilePath"
    return
}

$projectEnvName = $null

Get-Content $envFilePath | ForEach-Object {
    if ($_ -match '^\s*PROJECT_ENV_NAME\s*=\s*(.+?)\s*$') {
        $projectEnvName = $matches[1].Trim().Trim('"').Trim("'")
    }
}

if (-not $projectEnvName) {
    Write-Error "PROJECT_ENV_NAME not found in .env (expected key: PROJECT_ENV_NAME=...)"
    return
}

$env:PROJECT_ENV_NAME = $projectEnvName

Write-Output $env:PROJECT_ENV_NAME
