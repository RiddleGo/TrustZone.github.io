# 任正非讲话实录站点 - 本地静态服务器
# 用法: .\start-server.ps1 [-Port 8080]

param(
    [int]$Port = 8080
)

$SiteRoot = $PSScriptRoot
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " 任正非讲话实录站点" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "站点目录: $SiteRoot"
Write-Host "访问地址:"
Write-Host "  本机:     http://localhost:$Port/"
Write-Host "  局域网:   http://$(Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike '127.*' } | Select-Object -First 1 -ExpandProperty IPAddress):$Port/"
Write-Host ""
Write-Host "GitHub Pages: https://riddlego.github.io/TrustZone.github.io/"
Write-Host ""
Write-Host "按 Ctrl+C 停止服务器" -ForegroundColor Yellow
Write-Host ""

Set-Location $SiteRoot
python -m http.server $Port
