#!/bin/bash

# 投资交易复盘系统启动脚本

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

echo "投资交易复盘分析系统启动中..."
echo "按 Ctrl+C 可以安全退出系统"
echo "========================================"

# 运行主程序
python main.py

echo
echo "系统已退出"
read -p "按回车键继续..."
