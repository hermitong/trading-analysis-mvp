#!/bin/bash

# 交易记录管理系统 - 状态检查脚本
# 版本: v2.0

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
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

# 检查进程是否运行
check_process() {
    local pid_file=$1
    local service_name=$2
    local port=$3

    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 $pid 2>/dev/null; then
            log_success "$service_name 运行中 (PID: $pid, 端口: $port)"
            return 0
        else
            log_warning "$service_name PID文件存在但进程不存在"
            rm -f "$pid_file"
            return 1
        fi
    else
        log_warning "$service_name 未运行 (PID文件不存在)"
        return 1
    fi
}

# 检查端口占用
check_port() {
    local port=$1
    local service_name=$2

    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        local pid=$(lsof -ti :$port)
        log_success "$service_name 端口 $port 被占用 (PID: $pid)"
        return 0
    else
        log_warning "$service_name 端口 $port 未被占用"
        return 1
    fi
}

# 检查服务健康状态
check_health() {
    local url=$1
    local service_name=$2

    if curl -s "$url" >/dev/null 2>&1; then
        log_success "$service_name 健康检查通过"
        return 0
    else
        log_error "$service_name 健康检查失败"
        return 1
    fi
}

# 显示系统信息
show_system_info() {
    echo -e "${PURPLE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║${NC}                    📊 系统状态报告                         ${PURPLE}║${NC}"
    echo -e "${PURPLE}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo
}

# 主检查函数
main() {
    show_system_info

    # 检查API服务器
    echo -e "${BLUE}🔗 后端API服务器:${NC}"
    if check_process ".api_server.pid" "API服务器" "5002"; then
        check_health "http://localhost:5002/api/health" "API服务器"
    else
        # 检查可能的端口
        for port in 5001 5003 5004 5005; do
            if check_port $port "API服务器"; then
                check_health "http://localhost:$port/api/health" "API服务器"
                break
            fi
        done
    fi
    echo

    # 检查前端服务器
    echo -e "${BLUE}🌐 前端开发服务器:${NC}"
    if check_process ".frontend.pid" "前端服务器" "5173"; then
        check_health "http://localhost:5173" "前端服务器"
    else
        # 检查可能的端口
        for port in 5174 5175 5176 5177; do
            if check_port $port "前端服务器"; then
                check_health "http://localhost:$port" "前端服务器"
                break
            fi
        done
    fi
    echo

    # 检查日志文件
    echo -e "${BLUE}📝 日志文件状态:${NC}"
    if [ -f "logs/api_server.log" ]; then
        local size=$(du -h logs/api_server.log | cut -f1)
        local lines=$(wc -l < logs/api_server.log)
        echo -e "   API服务器日志: ${GREEN}$size${NC} ($lines 行)"
    else
        echo -e "   API服务器日志: ${YELLOW}不存在${NC}"
    fi

    if [ -f "logs/frontend.log" ]; then
        local size=$(du -h logs/frontend.log | cut -f1)
        local lines=$(wc -l < logs/frontend.log)
        echo -e "   前端服务器日志: ${GREEN}$size${NC} ($lines 行)"
    else
        echo -e "   前端服务器日志: ${YELLOW}不存在${NC}"
    fi
    echo

    # 检查数据库
    echo -e "${BLUE}💾 数据库状态:${NC}"
    if [ -f "backend/data/trading.db" ]; then
        local size=$(du -h backend/data/trading.db | cut -f1)
        echo -e "   SQLite数据库: ${GREEN}$size${NC}"
    else
        echo -e "   SQLite数据库: ${YELLOW}不存在${NC}"
    fi
    echo

    # 显示快速操作提示
    echo -e "${PURPLE}🚀 快速操作:${NC}"
    echo -e "   • 启动服务: ${GREEN}./start.sh${NC}"
    echo -e "   • 停止服务: ${YELLOW}./stop.sh${NC}"
    echo -e "   • 重启服务: ${BLUE}./stop.sh && ./start.sh${NC}"
    echo -e "   • 查看API日志: ${CYAN}tail -f logs/api_server.log${NC}"
    echo -e "   • 查看前端日志: ${CYAN}tail -f logs/frontend.log${NC}"
    echo
}

# 运行主函数
main "$@"