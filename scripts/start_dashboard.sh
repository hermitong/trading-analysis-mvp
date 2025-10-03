#!/bin/bash

# 投资交易复盘系统 - Web Dashboard启动脚本

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR/.."

# 激活虚拟环境
if [ -d "$PROJECT_ROOT/venv" ]; then
    source "$PROJECT_ROOT/venv/bin/activate"
    echo "虚拟环境已激活"
else
    echo "警告: 未找到虚拟环境，使用系统Python"
fi

# 切换到后端目录
cd "$PROJECT_ROOT/backend"

echo "========================================"
echo "投资交易复盘分析系统 - Web Dashboard"
echo "========================================"
echo
echo "正在启动Web服务器..."
echo "Dashboard地址: http://localhost:5001"
echo "按 Ctrl+C 可以停止服务"
echo "========================================"
echo

# 运行Web应用
python app/web_api.py

echo
echo "Web服务已停止"
read -p "按回车键继续..."