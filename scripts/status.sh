#!/bin/bash

# 系统状态检查脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR/.."

echo "========================================"
echo "投资交易复盘系统 - 状态检查"
echo "========================================"
echo

echo "项目路径: $PROJECT_ROOT"
echo

# 检查虚拟环境
if [ -d "$PROJECT_ROOT/venv" ]; then
    echo -e "\033[0;32m✓\033[0m 虚拟环境存在"
else
    echo -e "\033[0;31m✗\033[0m 虚拟环境不存在"
fi

# 检查依赖
if [ -d "$PROJECT_ROOT/venv" ]; then
    source "$PROJECT_ROOT/venv/bin/activate"
    echo -e "\033[0;32m✓\033[0m Python环境已激活"
    python --version
    echo "已安装的包:"
    pip list | grep -E "(pandas|gspread|openpyxl|APScheduler)"
fi

# 检查Google凭证
if [ -f "$PROJECT_ROOT/backend/credentials/service_account.json" ]; then
    echo -e "\033[0;32m✓\033[0m Google API凭证文件存在"
else
    echo -e "\033[1;33m⚠\033[0m Google API凭证文件不存在"
fi

# 检查目录
echo
echo "目录结构:"
ls -la $PROJECT_ROOT/{backend/{logs,credentials,data},trading_records} 2>/dev/null

echo
echo "========================================"
