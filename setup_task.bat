@echo off
chcp 65001 >nul
title GitHub Streak Keeper — 安装计划任务

set SCRIPT_DIR=%~dp0
set TASK_NAME=GitHubStreakKeeper

echo ============================================
echo   GitHub Streak Keeper 计划任务安装
echo ============================================
echo.

:: 创建计划任务（每天 10:00、14:00、20:00 各执行一次）
schtasks /create /tn "%TASK_NAME%" /sc daily /st 10:00 /tr "python \"%SCRIPT_DIR%streak.py\"" /f >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] 10:00 触发器已创建
) else (
    echo [警告] 10:00 触发器创建失败，请以管理员身份运行
)

schtasks /create /tn "%TASK_NAME%_14" /sc daily /st 14:00 /tr "python \"%SCRIPT_DIR%streak.py\"" /f >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] 14:00 触发器已创建
)

schtasks /create /tn "%TASK_NAME%_20" /sc daily /st 20:00 /tr "python \"%SCRIPT_DIR%streak.py\"" /f >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] 20:00 触发器已创建
)

echo.
echo 完成！计划任务已注册，每天 10:00/14:00/20:00 自动执行。
echo.
echo 如需删除任务，运行：schtasks /delete /tn "%TASK_NAME%" /f
echo.
pause
