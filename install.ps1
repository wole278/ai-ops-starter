$ErrorActionPreference = 'Stop'
Write-Host "=== AI Ops Starter 一键安装向导 (Windows) ===" -ForegroundColor Cyan

# 1. 检测 Python 3
$hasPython = $false
foreach ($cmd in @('python', 'python3', 'py')) {
    if (Get-Command $cmd -ErrorAction SilentlyContinue) {
        try {
            $ver = if ($cmd -eq 'py') { & py -3 --version 2>&1 } else { & $cmd --version 2>&1 }
            if ($ver -match 'Python 3\.') {
                Write-Host "[OK] 检测到 $ver" -ForegroundColor Green
                $hasPython = $true
                break
            }
        } catch {}
    }
}

if (-not $hasPython) {
    Write-Host "[提示] 未检测到 Python 3，Hooks 护栏需要 Python 3 运行。" -ForegroundColor Yellow
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        Write-Host "正在尝试通过 winget 自动安装 Python 3.12..." -ForegroundColor Cyan
        winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
    } else {
        Write-Host "[请先安装] 请前往 https://www.python.org/downloads/ 下载安装 Python 3（勾选 Add Python to PATH）后重试。" -ForegroundColor Red
    }
}

# 2. 优先使用 agy CLI 安装，否则直接下载并写入插件目录
$installed = $false
if (Get-Command agy -ErrorAction SilentlyContinue) {
    Write-Host "[执行] 正在通过 agy CLI 安装 ai-ops-starter..." -ForegroundColor Cyan
    try {
        & agy plugin install https://github.com/wole278/ai-ops-starter
        if ($LASTEXITCODE -eq 0) { $installed = $true }
    } catch {}
}

if (-not $installed) {
    Write-Host "[执行] 正在下载并安装插件到 Antigravity 插件目录..." -ForegroundColor Cyan
    $tmp = Join-Path $env:TEMP ("ai-ops-starter-" + [guid]::NewGuid().ToString('N'))
    $zip = "$tmp.zip"
    New-Item -ItemType Directory -Path $tmp -Force | Out-Null
    try {
        Invoke-WebRequest -Uri "https://github.com/wole278/ai-ops-starter/archive/refs/heads/main.zip" -OutFile $zip -UseBasicParsing
        Expand-Archive -Path $zip -DestinationPath $tmp -Force
        $src = Join-Path $tmp "ai-ops-starter-main"
        $dst = Join-Path $env:USERPROFILE ".gemini\config\plugins\ai-ops-starter"
        New-Item -ItemType Directory -Path $dst -Force | Out-Null
        foreach ($item in @('plugin.json', 'hooks.json', 'rules', 'skills', 'scripts')) {
            $s = Join-Path $src $item
            if (Test-Path $s) { Copy-Item -Path $s -Destination $dst -Recurse -Force }
        }
        $installed = $true
    } finally {
        Remove-Item $zip -Force -ErrorAction SilentlyContinue
        Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue
    }
}

if ($installed) {
    Write-Host "`n[OK] ai-ops-starter 安装完成！请重启或新开一个 Antigravity 窗口即可生效。" -ForegroundColor Green
} else {
    Write-Host "`n[FAIL] 安装未完成，请检查网络后重试。" -ForegroundColor Red
    exit 1
}
