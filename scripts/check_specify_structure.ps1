# check_specify_structure.ps1
# 列出 SpecMd 目录下的文件结构

$specPath = Resolve-Path (Join-Path $PSScriptRoot "..\..\SpecMd") | Select-Object -ExpandProperty Path

if (Test-Path $specPath) {
    Get-ChildItem -Path $specPath -Recurse | ForEach-Object {
        $relativePath = $_.FullName.Substring($specPath.Length)
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
    Write-Output "Error: SpecMd directory not found at $specPath"
}
