@echo off
chcp 65001 >nul
echo ========================================
echo 投资交易复盘系统 - Windows安装向导
echo ========================================
echo.

:: 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.10+
    echo 下载地址: https://www.python.org/downloads/
    echo.
    echo 安装时请勾选 "Add Python to PATH"
    pause
    exit /b 1
)

echo [✓] Python环境检查通过
echo.

:: 创建必要目录
echo [1/5] 创建项目目录...
if not exist "..\backend\logs" mkdir "..\backend\logs"
if not exist "..\backend\credentials" mkdir "..\backend\credentials"
if not exist "..\backend\data" mkdir "..\backend\data"
if not exist "..\trading_records" mkdir "..\trading_records"
echo [✓] 目录创建完成
echo.

:: 安装Python依赖
echo [2/5] 安装Python依赖...
cd ..\backend
python -m pip install --upgrade pip
if errorlevel 1 (
    echo [错误] pip升级失败
    pause
    exit /b 1
)

pip install -r requirements.txt
if errorlevel 1 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)
echo [✓] Python依赖安装完成
echo.

:: 检查Google凭证
echo [3/5] 检查Google API凭证...
if not exist "credentials\service_account.json" (
    echo [警告] 未找到Google服务账号密钥文件
    echo.
    echo 请按照以下步骤配置Google API:
    echo 1. 访问 https://console.cloud.google.com/
    echo 2. 创建新项目或选择现有项目
    echo 3. 启用 Google Sheets API 和 Google Drive API
    echo 4. 创建服务账号并下载JSON密钥文件
    echo 5. 将JSON文件重命名为 service_account.json
    echo 6. 将文件放入 backend\credentials\ 目录
    echo.
    echo 详细指南请参考: docs\setup_guide.md
    echo.
) else (
    echo [✓] Google API凭证文件存在
)
echo.

:: 创建启动脚本
echo [4/5] 创建启动脚本...
(
echo @echo off
echo chcp 65001 ^>nul
echo title 投资交易复盘分析系统
echo cd /d "%%~dp0..\backend"
echo python main.py
echo pause
) > "start.bat"

echo [✓] 启动脚本创建完成: scripts\start.bat
echo.

:: 创建快捷方式提示
echo [5/5] 开机自启动配置...
echo.
echo 如需开机自启动，请手动操作:
echo 1. 按 Win+R，输入: shell:startup
echo 2. 将 scripts\start.bat 的快捷方式复制到启动文件夹
echo.
echo 或者立即创建系统计划任务:
echo.

set /p create_task=是否创建系统计划任务? (y/n):
if /i "%create_task%"=="y" (
    echo 正在创建计划任务...
    schtasks /create /tn "投资交易复盘系统" /tr "\"%~dp0start.bat\"" /sc onlogon /f
    if errorlevel 1 (
        echo [错误] 计划任务创建失败
    ) else (
        echo [✓] 计划任务创建成功
        echo 系统将在用户登录时自动启动交易分析系统
    )
)

echo.
echo ========================================
echo 安装完成!
echo ========================================
echo.
echo 下一步操作:
echo 1. 配置Google API凭证（如未配置）
echo 2. 双击 scripts\start.bat 启动系统
echo 3. 将券商Excel文件放入 trading_records 文件夹
echo.
echo 系统将自动:
echo - 解析Excel文件
echo - 计算盈亏
echo - 生成Dashboard
echo.
echo 如需帮助，请查看 docs\ 目录下的文档
echo.
pause