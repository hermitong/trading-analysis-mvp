#!/bin/bash

# 交易记录管理系统 - 一键启动脚本（双击运行版本）
# 双击此文件即可启动整个系统！

# 设置颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# 显示横幅
clear
echo -e "${CYAN}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║          🚀 交易记录管理系统 - 一键启动脚本                   ║"
echo "║                                                              ║"
echo "║           双击运行，自动启动完整Web应用生态                       ║"
echo "║                                                              ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo

# 检查依赖
echo -e "${BLUE}🔍 检查系统依赖...${NC}"

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 未安装${NC}"
    echo "请先安装Python 3.13+:"
    echo "brew install python3"
    echo
    read -p "按任意键退出..."
    exit 1
fi
echo -e "${GREEN}✅ Python3: $(python3 --version)${NC}"

# 检查Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js 未安装${NC}"
    echo "请先安装Node.js 16+:"
    echo "brew install node"
    echo
    read -p "按任意键退出..."
    exit 1
fi
echo -e "${GREEN}✅ Node.js: $(node --version)${NC}"

# 切换到脚本所在目录
cd "$(dirname "$0")"

# 检查是否有服务在运行
if pgrep -f "api_server.py" > /dev/null || pgrep -f "npm run dev" > /dev/null; then
    echo
    echo -e "${YELLOW}⚠️  检测到已有服务正在运行${NC}"
    echo
    echo -e "${BLUE}选择操作:${NC}"
    echo "1) 🔄 重新启动服务"
    echo "2) 📊 查看服务状态"
    echo "3) 🛑 停止所有服务"
    echo "4) 🚀 启动新实例"
    echo "5) ❌ 取消"
    echo
    read -p "请输入选择 (1-5): " choice

    case $choice in
        1)
            echo -e "${YELLOW}🔄 正在重新启动服务...${NC}"
            pkill -f "api_server.py" 2>/dev/null || true
            pkill -f "npm run dev" 2>/dev/null || true
            sleep 2
            ;;
        2)
            echo -e "${BLUE}📊 服务状态:${NC}"
            if pgrep -f "api_server.py" > /dev/null; then
                echo -e "${GREEN}✅ API服务器运行中${NC}"
            else
                echo -e "${RED}❌ API服务器未运行${NC}"
            fi
            if pgrep -f "npm run dev" > /dev/null; then
                echo -e "${GREEN}✅ 前端服务器运行中${NC}"
            else
                echo -e "${RED}❌ 前端服务器未运行${NC}"
            fi
            echo
            read -p "按任意键继续..."
            exit 0
            ;;
        3)
            echo -e "${YELLOW}🛑 正在停止所有服务...${NC}"
            pkill -f "api_server.py" 2>/dev/null || true
            pkill -f "npm run dev" 2>/dev/null || true
            rm -f .api_server.pid .frontend.pid
            echo -e "${GREEN}✅ 所有服务已停止${NC}"
            echo
            read -p "按任意键退出..."
            exit 0
            ;;
        4)
            echo -e "${BLUE}🚀 将启动新实例...${NC}"
            ;;
        5)
            echo -e "${RED}❌ 取消启动${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ 无效选择${NC}"
            exit 1
            ;;
    esac
fi

# 开始启动流程
echo
echo -e "${PURPLE}🚀 启动完整工作流程...${NC}"
echo

# 激活虚拟环境
if [ ! -d "venv" ]; then
    echo -e "${BLUE}📦 创建Python虚拟环境...${NC}"
    python3 -m venv venv
fi

echo -e "${BLUE}🔄 激活虚拟环境...${NC}"
source venv/bin/activate

# 安装依赖
if [ -f "backend/requirements.txt" ]; then
    echo -e "${BLUE}📦 检查Python依赖...${NC}"
    pip install -q -r backend/requirements.txt
fi

# 创建目录
echo -e "${BLUE}📁 创建必要目录...${NC}"
mkdir -p logs backend/data backend/credentials trading_records

# 查找可用端口
API_PORT=5002
while lsof -Pi :$API_PORT -sTCP:LISTEN -t >/dev/null 2>&1; do
    API_PORT=$((API_PORT + 1))
done
echo -e "${GREEN}✅ 使用API端口: $API_PORT${NC}"

# 设置环境变量
export API_PORT=$API_PORT
export PYTHONPATH="${PWD}/backend:$PYTHONPATH"
export REACT_APP_API_URL="http://localhost:$API_PORT/api"

# 启动API服务器
echo -e "${BLUE}🔗 启动后端API服务器...${NC}"
cd backend
nohup python app/api_server.py > ../logs/api_server.log 2>&1 &
API_PID=$!
echo $API_PID > ../.api_server.pid
cd ..

# 等待API服务器启动
echo -e "${BLUE}⏳ 等待API服务器就绪...${NC}"
for i in {1..30}; do
    if curl -s "http://localhost:$API_PORT/api/health" >/dev/null 2>&1; then
        break
    fi
    echo -n "."
    sleep 1
done
echo
echo -e "${GREEN}✅ API服务器已就绪: http://localhost:$API_PORT/api/health${NC}"

# 启动前端服务器
echo -e "${BLUE}🌐 启动前端开发服务器...${NC}"
cd frontend

if [ ! -d "node_modules" ]; then
    echo -e "${BLUE}📦 安装前端依赖...${NC}"
    npm install
fi

# 查找可用端口
FRONTEND_PORT=5173
while lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; do
    FRONTEND_PORT=$((FRONTEND_PORT + 1))
done
echo -e "${GREEN}✅ 使用前端端口: $FRONTEND_PORT${NC}"

# 启动前端服务器
npm run dev -- --port $FRONTEND_PORT > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../.frontend.pid
cd ..

# 等待前端服务器启动
echo -e "${BLUE}⏳ 等待前端服务器就绪...${NC}"
for i in {1..30}; do
    if curl -s "http://localhost:$FRONTEND_PORT" >/dev/null 2>&1; then
        break
    fi
    echo -n "."
    sleep 1
done
echo
echo -e "${GREEN}✅ 前端服务器已就绪: http://localhost:$FRONTEND_PORT${NC}"

# 显示完成信息
echo
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║${NC}                      🎉 启动完成！                             ${GREEN}║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo
echo -e "${CYAN}🌐 前端应用:${NC} http://localhost:$FRONTEND_PORT"
echo -e "${CYAN}🔗 API服务器:${NC} http://localhost:$API_PORT/api/health"
echo -e "${CYAN}📊 健康检查:${NC} http://localhost:$API_PORT/api/health"
echo
echo -e "${YELLOW}📝 日志文件:${NC}"
echo "   • API服务器: logs/api_server.log"
echo "   • 前端服务器: logs/frontend.log"
echo
echo -e "${PURPLE}🛑 停止服务:${NC}"
echo "   • 关闭此终端，或运行: ./stop.sh"
echo "   • 查看进程状态: ./status.sh"
echo

# 显示macOS通知
osascript -e "display notification \"交易记录管理系统\" with subtitle \"系统已启动，正在打开浏览器...\"" 2>/dev/null || true

# 自动打开浏览器
open "http://localhost:$FRONTEND_PORT"

echo -e "${GREEN}🎊 系统已在后台运行，浏览器已打开！${NC}"
echo
echo -e "${BLUE}💡 提示: 关闭此终端窗口不会停止服务${NC}"
echo -e "${BLUE}💡 提示: 使用 ./stop.sh 可优雅停止所有服务${NC}"
echo

# 保持终端打开
echo -e "${PURPLE}按 Ctrl+C 或关闭窗口退出（服务将继续运行）...${NC}"
echo