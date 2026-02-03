# check_codefile_structure.ps1
# 列出 src 目录下的文件结构，排除无关目录

$srcPath = Resolve-Path (Join-Path $PSScriptRoot "..\..\src") | Select-Object -ExpandProperty Path

if (Test-Path $srcPath) {
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
        if ($relativePath.StartsWith("\") -or $relativePath.StartsWith("/")) {
             $relativePath = $relativePath.Substring(1)
        }

        if ($_.PSIsContainer) {
            Write-Output "[$relativePath]"
        } else {
            Write-Output "  $relativePath"
        }
    }
} else {
    Write-Output "Error: src directory not found at $srcPath"
}
