#!/bin/bash

# 投资交易复盘系统 - macOS/Linux安装脚本

echo "========================================"
echo "投资交易复盘系统 - 安装向导"
echo "========================================"
echo

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_PATH="$PROJECT_ROOT/venv"

echo -e "${BLUE}项目根目录: $PROJECT_ROOT${NC}"
echo

# 检查Python
echo "[1/6] 检查Python环境..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo -e "${GREEN}✓${NC} Python环境检查通过: $PYTHON_VERSION"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
    echo -e "${GREEN}✓${NC} Python环境检查通过: $PYTHON_VERSION"
else
    echo -e "${RED}✗${NC} 未检测到Python，请先安装Python 3.10+"
    echo "macOS: brew install python3"
    echo "Ubuntu/Debian: sudo apt-get install python3 python3-pip python3-venv"
    echo "CentOS/RHEL: sudo yum install python3 python3-pip"
    exit 1
fi

echo

# 创建项目目录
echo "[2/6] 创建项目目录..."
mkdir -p "$PROJECT_ROOT/backend/logs"
mkdir -p "$PROJECT_ROOT/backend/credentials"
mkdir -p "$PROJECT_ROOT/backend/data"
mkdir -p "$PROJECT_ROOT/trading_records"
echo -e "${GREEN}✓${NC} 目录创建完成"
echo

# 创建虚拟环境
echo "[3/6] 创建Python虚拟环境..."
if [ ! -d "$VENV_PATH" ]; then
    echo "正在创建虚拟环境..."
    $PYTHON_CMD -m venv "$VENV_PATH"
    if [ $? -ne 0 ]; then
        echo -e "${RED}✗${NC} 虚拟环境创建失败"
        echo "请确保已安装python3-venv包"
        echo "Ubuntu/Debian: sudo apt-get install python3-venv"
        exit 1
    fi
    echo -e "${GREEN}✓${NC} 虚拟环境创建完成"
else
    echo -e "${YELLOW}⚠${NC} 虚拟环境已存在，跳过创建"
fi
echo

# 激活虚拟环境并安装依赖
echo "[4/6] 安装Python依赖..."
echo "激活虚拟环境..."
source "$VENV_PATH/bin/activate"

echo "升级pip..."
pip install --upgrade pip
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠${NC} pip升级失败，继续安装依赖..."
fi

echo "安装项目依赖..."
cd "$PROJECT_ROOT/backend"
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}✗${NC} 依赖安装失败"
    exit 1
fi

echo -e "${GREEN}✓${NC} Python依赖安装完成"
echo

# 检查Google凭证
echo "[5/6] 检查Google API凭证..."
if [ ! -f "$PROJECT_ROOT/backend/credentials/service_account.json" ]; then
    echo -e "${YELLOW}⚠${NC} 未找到Google服务账号密钥文件"
    echo
    echo "请按照以下步骤配置Google API:"
    echo "1. 访问 https://console.cloud.google.com/"
    echo "2. 创建新项目或选择现有项目"
    echo "3. 启用 Google Sheets API 和 Google Drive API"
    echo "4. 创建服务账号并下载JSON密钥文件"
    echo "5. 将JSON文件重命名为 service_account.json"
    echo "6. 将文件放入 backend/credentials/ 目录"
    echo
    echo "详细指南请参考: docs/setup_guide.md"
    echo
else
    echo -e "${GREEN}✓${NC} Google API凭证文件存在"
fi

# 创建启动脚本
echo "[6/6] 创建启动脚本..."
cat > "$PROJECT_ROOT/scripts/start.sh" << EOF
#!/bin/bash

# 投资交易复盘系统启动脚本

# 获取脚本所在目录
SCRIPT_DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="\$SCRIPT_DIR/.."

# 激活虚拟环境
if [ -d "\$PROJECT_ROOT/venv" ]; then
    source "\$PROJECT_ROOT/venv/bin/activate"
    echo "虚拟环境已激活"
else
    echo "警告: 未找到虚拟环境，使用系统Python"
fi

# 切换到后端目录
cd "\$PROJECT_ROOT/backend"

echo "投资交易复盘分析系统启动中..."
echo "按 Ctrl+C 可以安全退出系统"
echo "========================================"

# 运行主程序
python main.py

echo
echo "系统已退出"
read -p "按回车键继续..."
EOF

chmod +x "$PROJECT_ROOT/scripts/start.sh"
echo -e "${GREEN}✓${NC} 启动脚本创建完成: scripts/start.sh"
echo

# 创建状态检查脚本
cat > "$PROJECT_ROOT/scripts/status.sh" << EOF
#!/bin/bash

# 系统状态检查脚本

SCRIPT_DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="\$SCRIPT_DIR/.."

echo "========================================"
echo "投资交易复盘系统 - 状态检查"
echo "========================================"
echo

echo "项目路径: \$PROJECT_ROOT"
echo

# 检查虚拟环境
if [ -d "\$PROJECT_ROOT/venv" ]; then
    echo -e "${GREEN}✓${NC} 虚拟环境存在"
else
    echo -e "${RED}✗${NC} 虚拟环境不存在"
fi

# 检查依赖
if [ -d "\$PROJECT_ROOT/venv" ]; then
    source "\$PROJECT_ROOT/venv/bin/activate"
    echo -e "${GREEN}✓${NC} Python环境已激活"
    python --version
    echo "已安装的包:"
    pip list | grep -E "(pandas|gspread|openpyxl|APScheduler)"
fi

# 检查Google凭证
if [ -f "\$PROJECT_ROOT/backend/credentials/service_account.json" ]; then
    echo -e "${GREEN}✓${NC} Google API凭证文件存在"
else
    echo -e "${YELLOW}⚠${NC} Google API凭证文件不存在"
fi

# 检查目录
echo
echo "目录结构:"
ls -la \$PROJECT_ROOT/{backend/{logs,credentials,data},trading_records} 2>/dev/null

echo
echo "========================================"
EOF

chmod +x "$PROJECT_ROOT/scripts/status.sh"
echo -e "${GREEN}✓${NC} 状态检查脚本创建完成: scripts/status.sh"
echo

# 开机自启动配置
echo "开机自启动配置:"
echo

# macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "macOS用户:"
    echo "1. 打开'系统偏好设置' > '用户与群组' > '登录项'"
    echo "2. 点击 + 按钮，添加 $PROJECT_ROOT/scripts/start.sh"
    echo "或使用以下命令创建Launch Agent:"
    echo "cp $PROJECT_ROOT/scripts/com.tradinganalysis.plist ~/Library/LaunchAgents/"
    echo "launchctl load ~/Library/LaunchAgents/com.tradinganalysis.plist"
    echo

# Linux
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Linux用户:"
    echo "1. 创建systemd服务文件:"
    echo "sudo cp $PROJECT_ROOT/scripts/trading-analysis.service /etc/systemd/system/"
    echo "2. 启用服务:"
    echo "sudo systemctl enable trading-analysis.service"
    echo "sudo systemctl start trading-analysis.service"
    echo
fi

echo "========================================"
echo -e "${GREEN}安装完成!${NC}"
echo "========================================"
echo
echo "下一步操作:"
echo "1. 配置Google API凭证（如未配置）"
echo "2. 运行 bash scripts/start.sh 启动系统"
echo "3. 运行 bash scripts/status.sh 检查状态"
echo "4. 将券商Excel文件放入 trading_records 文件夹"
echo
echo "系统将自动:"
echo "- 解析Excel文件"
echo "- 计算盈亏"
echo "- 生成Dashboard"
echo
echo "如需帮助，请查看 docs/ 目录下的文档"
echo