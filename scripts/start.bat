@echo off
chcp 65001 >nul
title 投资交易复盘分析系统

cd /d "%~dp0..\backend"

echo 投资交易复盘分析系统启动中...
echo 按 Ctrl+C 可以安全退出系统
echo ========================================

python main.py

echo.
echo 系统已退出
pause