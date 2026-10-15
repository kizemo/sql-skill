# register-cron-sync.ps1 — 注册 Windows Task Scheduler 每日 02:00 跑 cron-sync-sql-skill.sh
# 用法:PowerShell -ExecutionPolicy Bypass -File register-cron-sync.ps1
# 卸载:Unregister-ScheduledTask -TaskName "gbrain-sql-skill-sync"

$TaskName = "gbrain-sql-skill-sync"
$ScriptPath = "F:\soft\00selfmade\sql-skill\tools\cron-sync-sql-skill.sh"
$Description = "每日同步 sql-skill vault 到 gbrain(sql-skill v2.2)"

# 检查并删除同名任务
$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "[INFO] Removing existing task: $TaskName" -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# 创建任务
Write-Host "[INFO] Creating daily sync task: $TaskName" -ForegroundColor Green

$action = New-ScheduledTaskAction `
    -Execute "C:\Program Files\Git\usr\bin\bash.exe" `
    -Argument "`"$ScriptPath`"" `
    -WorkingDirectory "F:\soft\00selfmade\sql-skill\tools"

$trigger = New-ScheduledTaskTrigger `
    -Daily `
    -At "2:00AM"

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 1)

$principal = New-ScheduledTaskPrincipal `
    -UserId $env:USERNAME `
    -LogonType Interactive `
    -RunLevel Highest

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal `
    -Description $Description

# 验证
$verify = Get-ScheduledTask -TaskName $TaskName
if ($verify) {
    Write-Host "[OK] Task registered: $TaskName" -ForegroundColor Green
    Write-Host "  Trigger: Daily at 02:00 AM" -ForegroundColor Cyan
    Write-Host "  Command: bash $ScriptPath" -ForegroundColor Cyan
    Write-Host "  Log: F:\soft\00selfmade\sql-skill\logs\sync-cron.log" -ForegroundColor Cyan
} else {
    Write-Host "[ERROR] Task registration failed" -ForegroundColor Red
    exit 1
}
