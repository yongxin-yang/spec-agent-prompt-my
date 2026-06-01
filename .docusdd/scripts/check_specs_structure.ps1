# check_specs_structure.ps1
# 列出 specs 目录下的文件结构，排除无关目录

$specsPath = Join-Path $PSScriptRoot "..\..\specs"

if (Test-Path $specsPath) {
    $specsPath = Resolve-Path $specsPath | Select-Object -ExpandProperty Path
    Get-ChildItem -Path $specsPath -Recurse | Where-Object {
        $path = $_.FullName
        $path -notmatch '__pycache__' -and
        $path -notmatch '\.git' -and
        $path -notmatch '\.idea' -and
        $path -notmatch '\.vscode' -and
        $path -notmatch 'node_modules'
    } | ForEach-Object {
        $relativePath = $_.FullName.Substring($specsPath.Length)
        $relativePath = $relativePath -replace '^[\\/]', ''

        if ($_.PSIsContainer) {
            Write-Output "[$relativePath]"
        } else {
            Write-Output "  $relativePath"
        }
    }
} else {
    Write-Output "Error: specs directory not found at $specsPath"
}
