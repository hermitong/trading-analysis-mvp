# 投资交易复盘分析系统

一个零成本、自动化、数据驱动的交易复盘分析工具，通过"扔进文件夹即可自动分析"的极简体验，帮助个人投资者洞察交易行为，优化决策策略。

## 快速开始

### 安装（5分钟）

1. **下载项目**
   ```bash
   git clone <repository-url>
   cd trading-analysis-mvp
   ```

2. **运行安装脚本**
   - Windows: 双击 `scripts/install.bat`
   - macOS/Linux: 运行 `bash scripts/install.sh`

3. **配置Google API**
   - 按照 `docs/setup_guide.md` 配置Google服务账号
   - 将 `service_account.json` 放入 `backend/credentials/` 目录

4. **启动系统**
   - Windows: 双击 `scripts/start.bat`
   - macOS/Linux: 运行 `bash scripts/start.sh`

### 日常使用（10秒）

1. 从券商下载Excel交易记录
2. 将Excel文件放入 `trading_records/` 文件夹
3. 打开浏览器查看Dashboard（Looker Studio）

就这么简单！

## 系统架构

```
用户放入Excel → 自动解析 → 数据存储 → Dashboard展示
     ↓              ↓         ↓         ↓
trading_records/ → Python → Google → Looker
               文件夹    解析引擎  Sheets   Studio
```

## 项目结构

```
trading-analysis-mvp/
├── backend/                 # 后端服务
│   ├── app/                # 核心模块
│   ├── credentials/        # Google API凭证
│   ├── data/              # SQLite数据库（可选）
│   ├── logs/              # 日志文件
│   └── requirements.txt   # Python依赖
├── trading_records/        # 用户Excel存放目录
├── docs/                  # 文档
├── scripts/               # 安装和启动脚本
└── frontend/             # React前端（可选）
```

## 技术栈

- **后端**: Python 3.10+, pandas, Google Sheets API
- **数据存储**: Google Sheets (MVP) / SQLite (可选)
- **可视化**: Google Looker Studio
- **调度**: APScheduler + 系统任务

## 特性

✅ **零成本启动** - MVP阶段完全免费
✅ **自动化处理** - 用户只需放入文件
✅ **数据驱动** - 三层指标体系分析
✅ **多券商支持** - 适配主流券商格式
✅ **云端访问** - 任何设备打开浏览器即可查看

## 文档

- [用户手册](docs/user_guide.md)
- [安装指南](docs/setup_guide.md)
- [常见问题](docs/faq.md)

## 版本

- **v1.0 (MVP)**: Google生态，零成本快速验证
- **v2.0 (增强版)**: 双模式，本地数据库选项
- **v3.0 (专业版)**: React前端，实时行情，AI分析

## 许可证

MIT License

---

> 让每一位投资者都能像专业机构一样，用数据驱动自己的交易决策。