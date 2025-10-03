#!/bin/bash

# 交易记录管理系统 - Mac双击启动命令
# 保存为 .command 文件即可双击运行

# 获取脚本所在目录
cd "$(dirname "$0")"

# 显示启动信息
echo "🚀 启动交易记录管理系统..."
echo "正在启动完整的工作流程..."

# 切换到项目根目录并运行启动脚本
if [ -f "start.sh" ]; then
    exec ./start.sh
else
    echo "❌ 找不到 start.sh 文件"
    echo "请确保在项目根目录运行"
    echo "按任意键退出..."
    read -r
fi