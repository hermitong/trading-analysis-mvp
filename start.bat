@echo off
setlocal enabledelayedexpansion

REM 交易记录管理系统 - Windows一键启动脚本
REM 版本: v2.0

REM 设置颜色
color 0A

REM 显示横幅
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║          🚀 交易记录管理系统 - 一键启动脚本 v2.0               ║
echo ║                                                              ║
echo ║  正在启动完整的Web应用生态系统...                              ║
echo ║                                                              ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM 检查Python
echo [STEP] 检查Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python未安装或不在PATH中
    echo 请先安装Python 3.13+
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [SUCCESS] Python: %PYTHON_VERSION%

REM 检查Node.js
echo [STEP] 检查Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js未安装或不在PATH中
    echo 请先安装Node.js 16+
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
echo [SUCCESS] Node.js: %NODE_VERSION%

REM 检查npm
echo [STEP] 检查npm...
npm --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] npm未安装或不在PATH中
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('npm --version') do set NPM_VERSION=%%i
echo [SUCCESS] npm: %NPM_VERSION%

REM 创建必要的目录
echo [STEP] 创建必要的目录...
if not exist "logs" mkdir logs
if not exist "backend\data" mkdir backend\data
if not exist "backend\credentials" mkdir backend\credentials
if not exist "trading_records" mkdir trading_records
echo [SUCCESS] 目录结构已创建

REM 检查虚拟环境
echo [STEP] 检查Python虚拟环境...
if not exist "venv" (
    echo [WARNING] 虚拟环境不存在，正在创建...
    python -m venv venv
    echo [SUCCESS] 虚拟环境已创建
)

REM 激活虚拟环境
echo [STEP] 激活虚拟环境...
call venv\Scripts\activate.bat
echo [SUCCESS] 虚拟环境已激活

REM 安装Python依赖
echo [STEP] 检查Python依赖...
if exist "backend\requirements.txt" (
    pip install -q -r backend\requirements.txt
    echo [SUCCESS] Python依赖已就绪
)

REM 查找可用端口
set API_PORT=5002
:check_api_port
netstat -ano | findstr ":%API_PORT%" >nul
if not errorlevel 1 (
    set /a API_PORT+=1
    goto check_api_port
)
echo [INFO] 使用API端口: %API_PORT%

REM 设置环境变量
set API_PORT=%API_PORT%
set PYTHONPATH=%CD%\backend;%PYTHONPATH%
set REACT_APP_API_URL=http://localhost:%API_PORT%/api

REM 启动后端API服务器
echo [STEP] 启动后端API服务器...
cd backend
start "API Server" cmd /k "python app/api_server.py"
cd ..

REM 保存API端口
echo %API_PORT% > .api_port.txt

REM 等待API服务器启动
echo [INFO] 等待API服务器启动...
timeout /t 3 /nobreak >nul

REM 检查API服务器健康状态
:check_api_health
curl -s http://localhost:%API_PORT%/api/health >nul 2>&1
if errorlevel 1 (
    echo [INFO] 等待API服务器就绪...
    timeout /t 2 /nobreak >nul
    goto check_api_health
)
echo [SUCCESS] API服务器已就绪: http://localhost:%API_PORT%/api/health

REM 安装前端依赖
echo [STEP] 检查前端依赖...
cd frontend
if not exist "node_modules" (
    echo [INFO] 安装前端依赖...
    call npm install
) else (
    echo [INFO] 检查依赖更新...
    call npm ci --silent
)
cd ..
echo [SUCCESS] 前端依赖已就绪

REM 查找可用端口
set FRONTEND_PORT=5173
:check_frontend_port
netstat -ano | findstr ":%FRONTEND_PORT%" >nul
if not errorlevel 1 (
    set /a FRONTEND_PORT+=1
    goto check_frontend_port
)
echo [INFO] 使用前端端口: %FRONTEND_PORT%

REM 启动前端开发服务器
echo [STEP] 启动前端开发服务器...
cd frontend
start "Frontend Server" cmd /k "npm run dev -- --port %FRONTEND_PORT%"
cd ..

REM 等待前端服务器启动
echo [INFO] 等待前端服务器启动...
timeout /t 5 /nobreak >nul

REM 检查前端服务器健康状态
:check_frontend_health
curl -s http://localhost:%FRONTEND_PORT% >nul 2>&1
if errorlevel 1 (
    echo [INFO] 等待前端服务器就绪...
    timeout /t 2 /nobreak >nul
    goto check_frontend_health
)
echo [SUCCESS] 前端服务器已就绪: http://localhost:%FRONTEND_PORT%

REM 显示完成信息
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                      🎉 启动完成！                             ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo 📱 前端应用: http://localhost:%FRONTEND_PORT%
echo 🔗 API服务器: http://localhost:%API_PORT%/api/health
echo 📊 健康检查: http://localhost:%API_PORT%/api/health
echo.
echo 📝 日志文件:
echo    • API服务器: logs\api_server.log
echo    • 前端服务器: logs\frontend.log
echo.
echo 🛑 停止服务:
echo    • 关闭弹出的命令行窗口
echo    • 或运行: stop.bat
echo.
echo 🚀 系统已就绪，开始您的交易记录管理之旅！
echo.

REM 打开浏览器
echo [INFO] 正在打开浏览器...
start http://localhost:%FRONTEND_PORT%

echo.
echo 按任意键退出此窗口，服务将继续在后台运行...
pause >nul