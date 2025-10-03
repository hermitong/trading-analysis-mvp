# 投资交易复盘分析系统

一个零成本、自动化、数据驱动的交易复盘分析工具，通过"扔进文件夹即可自动分析"的极简体验，帮助个人投资者洞察交易行为，优化决策策略。

## 🚀 第二阶段更新 (v2.0)

### ✨ 新功能
- **现代化Web界面** - 基于React的完整前端应用
- **期权智能解析** - 支持 `AVGO0919C` 等多种期权格式
- **交易评价系统** - 1-5星评分 + 消息来源追踪
- **Excel导入增强** - 支持郑兄格式等多种券商
- **数据可视化** - 交互式图表和统计分析
- **RESTful API** - 完整的CRUD操作支持

## 🚀 快速开始

### 安装（5分钟）

1. **克隆项目**
   ```bash
   git clone https://github.com/hermitong/trading-analysis-mvp.git
   cd trading-analysis-mvp
   ```

2. **启动后端API服务器**
   ```bash
   source venv/bin/activate
   API_PORT=5002 python backend/app/api_server.py
   ```

3. **启动前端应用** (新终端)
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **访问应用**
   - 前端界面：http://localhost:5173
   - API服务器：http://localhost:5002

## 🎯 核心功能

### 📊 Web仪表板
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
- 消息来源追踪 (🐳巨鲸, 🏫社区等)

### 📁 Excel导入
- 支持郑兄格式Excel文件
- 智能格式识别
- 期权信息自动提取
- 货币和日期格式处理

## 🏗️ 系统架构

```
Excel文件 → 解析器 → 数据库 → API → 前端界面
    ↓         ↓       ↓      ↓      ↓
多种格式 → 智能解析 → SQLite → REST → React
```

## 📁 项目结构

```
trading-analysis-mvp/
├── backend/                 # 后端服务
│   ├── app/
│   │   ├── api_server.py   # Web API服务器
│   │   ├── database.py     # 数据库模型
│   │   ├── option_parser.py # 期权解析器
│   │   ├── parser.py       # Excel解析器
│   │   └── ...
│   ├── data/              # SQLite数据库
│   └── requirements.txt   # Python依赖
├── frontend/              # React前端
│   ├── src/
│   │   ├── components/    # React组件
│   │   ├── stores/        # 状态管理
│   │   └── ...
│   └── package.json
├── PHASE2_SUMMARY.md      # 第二阶段开发总结
├── QUICK_START.md         # 快速启动指南
└── docs/                  # 详细文档
```

## 💻 技术栈

### 后端
- **Python 3.13** + Flask
- **SQLite** 数据库
- **pandas** Excel处理
- **Werkzeug** Web服务器

### 前端
- **React 18** + Vite
- **Ant Design** UI组件库
- **Chart.js** 图表可视化
- **Zustand** 状态管理

## ✨ 特性

✅ **现代化界面** - 基于React的专业Web应用
✅ **期权智能解析** - 自动识别多种期权格式
✅ **交易评价系统** - 完善的评分和来源追踪
✅ **Excel一键导入** - 支持多种券商格式
✅ **数据可视化** - 交互式图表和统计分析
✅ **本地部署** - 数据安全可控

## 🧪 测试

```bash
# 测试API工作流程
source venv/bin/activate
python test_full_workflow.py

# 测试期权解析器
python test_option_parser.py

# 测试郑兄格式解析
python test_zheng_parser.py
```

## 📖 文档

- [快速启动指南](QUICK_START.md)
- [第二阶段总结](PHASE2_SUMMARY.md)
- [用户手册](docs/user_guide.md)
- [安装指南](docs/setup_guide.md)
- [常见问题](docs/faq.md)

## 🚀 版本历史

- **v1.0 (MVP)**: Google生态，零成本快速验证
- **v2.0 (当前)**: 完整Web应用，期权支持，评价系统
- **v3.0 (规划)**: 实时行情，AI分析，移动端

## 📄 许可证

MIT License

---

> 🎯 让每一位投资者都能像专业机构一样，用数据驱动自己的交易决策。
