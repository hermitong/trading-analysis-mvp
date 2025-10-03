@echo off
chcp 65001 >nul
title 投资交易复盘分析系统 - Web Dashboard

cd /d "%~dp0..\backend"

echo ========================================
echo 投资交易复盘分析系统 - Web Dashboard
echo ========================================
echo.
echo 正在启动Web服务器...
echo Dashboard地址: http://localhost:5001
echo 按 Ctrl+C 可以停止服务
echo ========================================
echo.

python app/web_api.py

echo.
echo Web服务已停止
pause