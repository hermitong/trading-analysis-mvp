# 🚀 一键启动脚本使用指南

## 概述

交易记录管理系统现在提供了一键启动脚本，能够自动启动整个Web应用生态系统，包括后端API服务器和前端开发服务器。

## 📁 脚本文件

| 脚本文件 | 适用系统 | 功能描述 |
|---------|---------|---------|
| `start.sh` | Linux/macOS | 完整自动化启动脚本 |
| `start.bat` | Windows | Windows批处理启动脚本 |
| `stop.sh` | Linux/macOS | 停止所有服务脚本 |
| `status.sh` | Linux/macOS | 检查系统状态脚本 |

## 🎯 快速使用

### Linux/macOS 用户

```bash
# 启动所有服务
./start.sh

# 检查系统状态
./status.sh

# 停止所有服务
./stop.sh
```

### Windows 用户

```batch
# 启动所有服务
start.bat

# 停止服务（关闭弹出的命令行窗口）
# 或运行 stop.bat（如果存在）
```

## ⚙️ 脚本功能特性

### 🔧 自动检测和配置
- ✅ 检查Python和Node.js版本
- ✅ 自动创建虚拟环境（如果不存在）
- ✅ 自动安装依赖包
- ✅ 智能端口分配（避免冲突）
- ✅ 健康检查和状态监控

### 🚀 启动流程
1. **依赖检查** - 验证系统环境
2. **环境准备** - 创建目录和虚拟环境
3. **后端启动** - 启动API服务器
4. **前端启动** - 启动开发服务器
5. **健康检查** - 验证服务状态
6. **浏览器打开** - 自动打开Web界面

### 📊 日志管理
- 所有日志保存在 `logs/` 目录
- API服务器日志：`logs/api_server.log`
- 前端服务器日志：`logs/frontend.log`

### 🔒 进程管理
- 自动保存进程PID文件
- 优雅的进程停止机制
- 端口清理和冲突处理

## 🛠️ 高级功能

### 手动模式
```bash
# 启用手动模式（需要自己启动服务）
./start.sh --manual
```

### 端口配置
脚本会自动查找可用端口：
- API服务器：5002（默认），冲突时自动递增
- 前端服务器：5173（默认），冲突时自动递增

### 环境变量
自动设置以下环境变量：
- `API_PORT` - API服务器端口
- `PYTHONPATH` - Python路径
- `REACT_APP_API_URL` - 前端API地址

## 🔍 故障排除

### 常见问题

#### 1. 端口被占用
```bash
# 查看端口占用
lsof -i :5002
lsof -i :5173

# 停止占用端口的进程
./stop.sh
```

#### 2. 依赖安装失败
```bash
# 手动激活虚拟环境
source venv/bin/activate

# 升级pip
pip install --upgrade pip

# 重新安装依赖
pip install -r backend/requirements.txt
```

#### 3. 服务启动失败
```bash
# 查看详细日志
tail -f logs/api_server.log
tail -f logs/frontend.log

# 检查系统状态
./status.sh
```

#### 4. 前端连接API失败
- 确保API服务器已启动
- 检查端口配置
- 查看浏览器控制台错误信息

### 调试模式

#### 手动启动API服务器
```bash
source venv/bin/activate
cd backend
python app/api_server.py
```

#### 手动启动前端服务器
```bash
cd frontend
npm install
npm run dev
```

## 📋 系统要求

### 最低要求
- **Python**: 3.13+
- **Node.js**: 16+
- **npm**: 7+
- **操作系统**: Linux, macOS, Windows

### 推荐配置
- **内存**: 4GB+ RAM
- **存储**: 2GB+ 可用空间
- **网络**: 稳定的互联网连接

## 🔄 开发工作流

### 日常开发
```bash
# 1. 启动开发环境
./start.sh

# 2. 进行开发工作
# - 修改代码
# - 查看日志
# - 测试功能

# 3. 检查状态
./status.sh

# 4. 停止服务（可选）
./stop.sh
```

### 日志监控
```bash
# 实时查看API日志
tail -f logs/api_server.log

# 实时查看前端日志
tail -f logs/frontend.log

# 查看所有日志
ls -la logs/
```

## 📈 性能优化

### 启动时间优化
- 使用 `npm ci` 替代 `npm install`（如果存在package-lock.json）
- 缓存Python依赖包
- 并行启动前后端服务

### 内存使用优化
- 脚本会自动清理不需要的进程
- 定期检查并重启长时间运行的进程

## 🎉 最佳实践

1. **首次使用**：运行 `./start.sh` 前确保系统环境满足要求
2. **日常使用**：使用 `./status.sh` 检查服务状态
3. **问题排查**：查看日志文件获取详细信息
4. **停止服务**：使用 `./stop.sh` 优雅停止所有服务
5. **定期更新**：定期更新依赖包和系统环境

---

**享受您的交易记录管理体验！** 🚀📊