# check_codefile_structure.ps1
# 列出 src 目录下的文件结构，排除无关目录

$srcPath = Join-Path $PSScriptRoot "..\..\src"

if (Test-Path $srcPath) {
    $srcPath = Resolve-Path $srcPath | Select-Object -ExpandProperty Path
    Get-ChildItem -Path $srcPath -Recurse | Where-Object {
        $path = $_.FullName
        $path -notmatch '__pycache__' -and 
        $path -notmatch '\.git' -and 
        $path -notmatch '\.idea' -and 
        $path -notmatch '\.vscode' -and
        $path -notmatch 'node_modules'
    } | ForEach-Object {
        # Calculate relative path
        # $srcPath might not have a trailing slash, so we add 1 for the separator if needed
        # But Substring is safer if we ensure $srcPath length handles it.
        
        # A robust way to get relative path:
           $relativePath = $_.FullName.Substring($srcPath.Length)
           $relativePath = $relativePath -replace '^[\\/]', ''

        if ($_.PSIsContainer) {
            Write-Output "[$relativePath]"
        } else {
            Write-Output "  $relativePath"
        }
    }
} else {
    Write-Output "Error: src directory not found at $srcPath"
}
