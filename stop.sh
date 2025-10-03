#!/bin/bash

# 交易记录管理系统 - 停止脚本
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

# 停止进程
stop_process() {
    local pid_file=$1
    local service_name=$2

    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 $pid 2>/dev/null; then
            log_info "正在停止 $service_name (PID: $pid)..."

            # 尝试优雅停止
            kill $pid 2>/dev/null

            # 等待进程停止
            local count=0
            while kill -0 $pid 2>/dev/null && [ $count -lt 10 ]; do
                echo -n "."
                sleep 1
                count=$((count + 1))
            done

            # 如果进程仍在运行，强制停止
            if kill -0 $pid 2>/dev/null; then
                log_warning "强制停止 $service_name..."
                kill -9 $pid 2>/dev/null
                sleep 1
            fi

            if ! kill -0 $pid 2>/dev/null; then
                log_success "$service_name 已停止"
            else
                log_error "$service_name 停止失败"
            fi
        else
            log_warning "$service_name 进程不存在"
        fi

        # 删除PID文件
        rm -f "$pid_file"
    else
        log_warning "$service_name PID文件不存在"
    fi
}

# 清理端口
cleanup_port() {
    local port=$1
    local service_name=$2

    local pid=$(lsof -ti :$port 2>/dev/null)
    if [ ! -z "$pid" ]; then
        log_info "清理端口 $port 上的进程 (PID: $pid)..."
        kill $pid 2>/dev/null
        sleep 1

        if kill -0 $pid 2>/dev/null; then
            kill -9 $pid 2>/dev/null
        fi

        log_success "端口 $port 已清理"
    fi
}

# 显示停止横幅
show_stop_banner() {
    echo -e "${RED}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║                                                              ║"
    echo "║          🛑 交易记录管理系统 - 停止所有服务                       ║"
    echo "║                                                              ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# 显示完成信息
show_completion_info() {
    echo
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║${NC}                      ✅ 停止完成！                             ${GREEN}║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo
    echo -e "${BLUE}🔄 重新启动:${NC}"
    echo -e "   • 完整启动: ${GREEN}./start.sh${NC}"
    echo -e "   • 手动模式: ${YELLOW}./start.sh --manual${NC}"
    echo
    echo -e "${PURPLE}📊 检查状态:${NC}"
    echo -e "   • 查看状态: ${CYAN}./status.sh${NC}"
    echo
    echo -e "${GREEN}感谢使用交易记录管理系统！${NC}"
    echo
}

# 主函数
main() {
    show_stop_banner

    log_info "正在停止所有服务..."

    # 停止前端服务器
    echo -e "${YELLOW}🌐 停止前端服务器...${NC}"
    stop_process ".frontend.pid" "前端服务器"

    # 清理前端可能的端口
    for port in 5173 5174 5175 5176 5177; do
        cleanup_port $port "前端服务器"
    done
    echo

    # 停止API服务器
    echo -e "${YELLOW}🔗 停止API服务器...${NC}"
    stop_process ".api_server.pid" "API服务器"

    # 清理API可能的端口
    for port in 5000 5001 5002 5003 5004 5005; do
        cleanup_port $port "API服务器"
    done
    echo

    # 清理其他可能的进程
    echo -e "${YELLOW}🧹 清理相关进程...${NC}"

    # 查找并停止可能的Python API服务器进程
    local python_pids=$(ps aux | grep "api_server.py" | grep -v grep | awk '{print $2}')
    if [ ! -z "$python_pids" ]; then
        for pid in $python_pids; do
            log_info "停止Python API服务器进程 (PID: $pid)"
            kill $pid 2>/dev/null
            sleep 1
            if kill -0 $pid 2>/dev/null; then
                kill -9 $pid 2>/dev/null
            fi
        done
    fi

    # 查找并停止可能的Node.js前端进程
    local node_pids=$(ps aux | grep "npm run dev" | grep -v grep | awk '{print $2}')
    if [ ! -z "$node_pids" ]; then
        for pid in $node_pids; do
            log_info "停止Node.js前端进程 (PID: $pid)"
            kill $pid 2>/dev/null
            sleep 1
            if kill -0 $pid 2>/dev/null; then
                kill -9 $pid 2>/dev/null
            fi
        done
    fi

    # 清理PID文件
    rm -f .api_server.pid .frontend.pid

    echo
    log_success "所有服务已停止"

    show_completion_info
}

# 运行主函数
main "$@"