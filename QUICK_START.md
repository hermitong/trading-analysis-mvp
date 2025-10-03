# 🚀 交易记录管理系统 - 快速启动指南

## 📋 系统要求

- Python 3.13+
- Node.js 16+
- Git

## ⚡ 快速启动

### 1. 启动后端API服务器
```bash
cd trading-analysis-mvp
source venv/bin/activate
API_PORT=5002 python backend/app/api_server.py
```

### 2. 启动前端应用
```bash
# 新开一个终端窗口
cd trading-analysis-mvp/frontend
npm install
npm run dev
```

### 3. 访问应用
- 🌐 前端界面：http://localhost:5173
- 🔗 API服务器：http://localhost:5002
- ❤️ 健康检查：http://localhost:5002/api/health

## 🎯 主要功能

### 📊 仪表板
- 交易统计概览
- 月度交易金额图表
- 交易类型分布
- 热门标的统计
- 评分分布分析

### 📝 交易管理
- 查看、添加、编辑、删除交易记录
- 支持股票和期权交易
- 期权信息自动解析
- 交易评分系统 (1-5星)
- 消息来源追踪

### 📁 Excel导入
- 支持郑兄格式Excel文件
- 智能格式识别
- 期权信息自动提取
- 货币和日期格式处理

## 🧪 测试功能

### 测试API工作流程
```bash
source venv/bin/activate
python test_full_workflow.py
```

### 测试期权解析器
```bash
source venv/bin/activate
python test_option_parser.py
```

### 测试郑兄格式解析
```bash
source venv/bin/activate
python test_zheng_parser.py
```

## 📱 界面预览

### 交易列表
- 🔍 搜索和过滤功能
- 🏷️ 期权/股票标签
- ⭐ 评分显示
- 📊 来源和理由标记

### 交易表单
- 📈 股票/期权切换
- 💰 金额自动计算
- 📅 日期时间选择
- 🎯 评价字段

### 仪表板
- 📊 统计卡片
- 📈 图表可视化
- 🔥 热门分析
- ⭐ 评分分布

## 🛠️ 故障排除

### API服务器无法启动
```bash
# 检查端口占用
lsof -i :5002

# 更换端口
API_PORT=5003 python backend/app/api_server.py
```

### 前端无法连接后端
- 确保API服务器正在运行
- 检查端口配置是否正确
- 查看浏览器控制台错误信息

### Excel导入失败
- 确认文件格式为.xlsx或.xls
- 检查文件大小不超过16MB
- 确认Excel包含必要的列名

## 📞 技术支持

如有问题，请检查：
1. Python和Node.js版本是否符合要求
2. 所有依赖是否正确安装
3. 端口是否被占用
4. 防火墙设置是否阻止连接

## 🎉 开始使用

1. 启动API服务器
2. 启动前端应用
3. 在浏览器中访问 http://localhost:5173
4. 开始管理您的交易记录！

祝您交易愉快！📈💰