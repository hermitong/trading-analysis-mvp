#!/bin/bash

# 交易记录管理系统 - 一键启动脚本
# 作者: Claude Code Assistant
# 版本: v2.0

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${PURPLE}[STEP]${NC} $1"
}

# 检查端口是否被占用
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # 端口被占用
    else
        return 1  # 端口可用
    fi
}

# 等待服务启动
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1

    log_info "等待 $service_name 启动..."
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" >/dev/null 2>&1; then
            log_success "$service_name 已启动"
            return 0
        fi
        echo -n "."
        sleep 1
        attempt=$((attempt + 1))
    done

    echo
    log_error "$service_name 启动超时"
    return 1
}

# 显示横幅
show_banner() {
    echo -e "${CYAN}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║                                                              ║"
    echo "║          🚀 交易记录管理系统 - 一键启动脚本 v2.0               ║"
    echo "║                                                              ║"
    echo "║  正在启动完整的Web应用生态系统...                              ║"
    echo "║                                                              ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# 检查依赖
check_dependencies() {
    log_step "检查系统依赖..."

    # 检查Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装"
        exit 1
    fi
    log_success "Python3: $(python3 --version)"

    # 检查Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js 未安装"
        exit 1
    fi
    log_success "Node.js: $(node --version)"

    # 检查npm
    if ! command -v npm &> /dev/null; then
        log_error "npm 未安装"
        exit 1
    fi
    log_success "npm: $(npm --version)"
}

# 激活虚拟环境
activate_venv() {
    log_step "激活Python虚拟环境..."

    if [ ! -d "venv" ]; then
        log_warning "虚拟环境不存在，正在创建..."
        python3 -m venv venv
    fi

    source venv/bin/activate
    log_success "虚拟环境已激活"

    # 安装Python依赖
    if [ -f "backend/requirements.txt" ]; then
        log_info "检查Python依赖..."
        pip install -q -r backend/requirements.txt
        log_success "Python依赖已就绪"
    fi
}

# 启动后端API服务器
start_backend() {
    log_step "启动后端API服务器..."

    # 查找可用端口
    API_PORT=5002
    while check_port $API_PORT; do
        API_PORT=$((API_PORT + 1))
    done

    log_info "使用端口: $API_PORT"

    # 设置环境变量并启动
    export API_PORT=$API_PORT
    export PYTHONPATH="${PWD}/backend:$PYTHONPATH"

    # 在后台启动API服务器
    cd backend
    nohup python app/api_server.py > ../logs/api_server.log 2>&1 &
    API_PID=$!
    cd ..

    # 保存PID到文件
    echo $API_PID > .api_server.pid

    log_success "后端API服务器已启动 (PID: $API_PID, 端口: $API_PORT)"

    # 等待API服务器就绪
    API_URL="http://localhost:$API_PORT/api/health"
    if wait_for_service "$API_URL" "API服务器"; then
        # 更新前端的API地址
        export REACT_APP_API_URL="http://localhost:$API_PORT/api"
        log_success "API服务器已就绪: $API_URL"
    else
        log_error "API服务器启动失败"
        return 1
    fi
}

# 安装前端依赖
install_frontend_deps() {
    log_step "检查前端依赖..."

    cd frontend

    if [ ! -d "node_modules" ]; then
        log_info "安装前端依赖..."
        npm install
    else
        log_info "检查依赖更新..."
        npm ci --silent
    fi

    cd ..
    log_success "前端依赖已就绪"
}

# 启动前端开发服务器
start_frontend() {
    log_step "启动前端开发服务器..."

    cd frontend

    # 查找可用端口
    FRONTEND_PORT=5173
    while check_port $FRONTEND_PORT; do
        FRONTEND_PORT=$((FRONTEND_PORT + 1))
    done

    log_info "使用端口: $FRONTEND_PORT"

    # 在后台启动前端服务器
    nohup npm run dev -- --port $FRONTEND_PORT > ../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    cd ..

    # 保存PID到文件
    echo $FRONTEND_PID > .frontend.pid

    log_success "前端服务器已启动 (PID: $FRONTEND_PID, 端口: $FRONTEND_PORT)"

    # 等待前端服务器就绪
    FRONTEND_URL="http://localhost:$FRONTEND_PORT"
    if wait_for_service "$FRONTEND_URL" "前端服务器"; then
        log_success "前端服务器已就绪: $FRONTEND_URL"
    else
        log_error "前端服务器启动失败"
        return 1
    fi
}

# 创建必要的目录
create_directories() {
    log_step "创建必要的目录..."

    mkdir -p logs
    mkdir -p backend/data
    mkdir -p backend/credentials
    mkdir -p trading_records

    # 确保logs目录有正确的权限
    chmod 755 logs

    log_success "目录结构已创建"
}

# 显示启动完成信息
show_completion_info() {
    echo
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║${NC}                      🎉 启动完成！                             ${GREEN}║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo
    echo -e "${CYAN}📱 前端应用:${NC} ${FRONTEND_URL}"
    echo -e "${CYAN}🔗 API服务器:${NC} ${API_URL}"
    echo -e "${CYAN}📊 健康检查:${NC} ${API_URL/health/health}"
    echo
    echo -e "${YELLOW}📝 日志文件:${NC}"
    echo -e "   • API服务器: logs/api_server.log"
    echo -e "   • 前端服务器: logs/frontend.log"
    echo
    echo -e "${PURPLE}🛑 停止服务:${NC}"
    echo -e "   • 停止所有服务: ./stop.sh"
    echo -e "   • 查看进程状态: ./status.sh"
    echo
    echo -e "${GREEN}🚀 系统已就绪，开始您的交易记录管理之旅！${NC}"
    echo
}

# 错误处理
handle_error() {
    log_error "启动过程中发生错误"
    log_info "请检查日志文件获取详细信息"
    echo
    echo -e "${YELLOW}📋 故障排除:${NC}"
    echo "1. 检查端口是否被其他程序占用"
    echo "2. 确保Python和Node.js已正确安装"
    echo "3. 查看日志文件: tail -f logs/api_server.log"
    echo "4. 手动启动: ./start.sh --manual"
    echo

    # 清理可能已启动的进程
    cleanup
    exit 1
}

# 清理函数
cleanup() {
    if [ -f ".api_server.pid" ]; then
        API_PID=$(cat .api_server.pid)
        if kill -0 $API_PID 2>/dev/null; then
            kill $API_PID 2>/dev/null || true
        fi
        rm -f .api_server.pid
    fi

    if [ -f ".frontend.pid" ]; then
        FRONTEND_PID=$(cat .frontend.pid)
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            kill $FRONTEND_PID 2>/dev/null || true
        fi
        rm -f .frontend.pid
    fi
}

# 设置错误处理
trap handle_error ERR
trap cleanup EXIT

# 手动启动模式
manual_mode=false
if [ "$1" = "--manual" ]; then
    manual_mode=true
    log_warning "启用手动模式"
fi

# 主函数
main() {
    show_banner

    if [ "$manual_mode" = false ]; then
        check_dependencies
        create_directories
        activate_venv
        start_backend
        install_frontend_deps
        start_frontend
    else
        log_info "手动模式已启用，请按步骤手动启动服务"
        echo
        echo "1. 激活虚拟环境: source venv/bin/activate"
        echo "2. 启动后端: cd backend && python app/api_server.py"
        echo "3. 启动前端: cd frontend && npm run dev"
        echo
    fi

    show_completion_info
}

# 运行主函数
main "$@"