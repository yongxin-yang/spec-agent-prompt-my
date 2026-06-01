# check_docus_structure.ps1
# 列出 docus 目录下的文件结构，排除无关目录

$docusPath = Join-Path $PSScriptRoot "..\..\docus"

if (Test-Path $docusPath) {
    $docusPath = Resolve-Path $docusPath | Select-Object -ExpandProperty Path
    Get-ChildItem -Path $docusPath -Recurse | Where-Object {
        $path = $_.FullName
        $path -notmatch '__pycache__' -and
        $path -notmatch '\.git' -and
        $path -notmatch '\.idea' -and
        $path -notmatch '\.vscode' -and
        $path -notmatch 'node_modules'
    } | ForEach-Object {
        $relativePath = $_.FullName.Substring($docusPath.Length)
        $relativePath = $relativePath -replace '^[\\/]', ''

        if ($_.PSIsContainer) {
            Write-Output "[$relativePath]"
        } else {
            Write-Output "  $relativePath"
        }
    }
} else {
    Write-Output "Error: docus directory not found at $docusPath"
}
