# 🚀 Looker Studio Dashboard 快速创建指南

## 📋 当前数据状态

✅ **Google Sheets已准备就绪**
- **trades**: 58条交易记录
- **positions**: 9条持仓记录
- **closed_positions**: 4条已平仓记录
- **电子表格名称**: "投资交易记录"

## 🎯 5分钟快速创建Dashboard

### 第一步：打开Looker Studio
1. 访问 [https://lookerstudio.google.com/](https://lookerstudio.google.com/)
2. 用您的Google账号登录

### 第二步：连接数据源
1. 点击 **"创建"** → **"报表"**
2. 选择 **"Google Sheets"**
3. 找到 **"投资交易记录**" 电子表格
4. 选择 **"trades"** 工作表
5. 点击 **"连接"**

### 第三步：创建第一个图表
1. 添加 **"记分卡"** 组件
2. 指标选择：**ID 计数**
3. 标题设置为：**"总交易次数"**

### 第四步：添加盈亏显示
1. 再次添加数据源，这次选择 **"closed_positions"** 工作表
2. 添加 **"记分卡"** 组件
3. 指标选择：**net_pnl 总计**
4. 标题设置为：**"总盈亏"**

### 第五步：保存和查看
1. 点击右上角 **"保存"**
2. 命名为：**"我的交易分析Dashboard"**

## 🎨 推荐的图表配置

### 核心指标（第一层）
```
总交易次数 → trades.ID 计数
总盈亏 → closed_positions.net_pnl 总计
胜率 → (盈利交易数 / 总交易数) × 100
持仓数 → positions.symbol 计数
```

### 趋势图表（第二层）
```
每日盈亏 → trades.trade_date (X轴), trades.net_amount (Y轴)
交易分布 → trades.symbol, trades.amount
```

### 深度分析（第三层）
```
盈利TOP5 → closed_positions按net_pnl排序
亏损TOP5 → closed_positions按net_pnl升序
持仓明细 → positions所有字段
```

## 🔧 快速配置技巧

### 数据源设置
- **刷新频率**: 每5分钟
- **字段类型**: 确保日期和数字字段正确识别

### 颜色配置
- **盈利**: 绿色 (#4CAF50)
- **亏损**: 红色 (#F44336)
- **中性**: 蓝色 (#2196F3)

### 条件格式
- net_pnl > 0: 绿色渐变
- net_pnl < 0: 红色渐变

## 📱 访问您的Dashboard

### 获取链接
1. 完成创建后点击右上角 **"分享"**
2. 选择 **"获取链接"**
3. 复制链接到浏览器书签

### 移动端访问
- Dashboard自动适配移动设备
- 在手机/平板上同样可用

## ⚡ 实时更新

系统会自动：
- **每5分钟**刷新数据
- **每小时**检查新的Excel文件
- **自动计算**新的盈亏和持仓

## 🆘 需要帮助？

如果遇到问题：
1. 查看 [详细配置指南](docs/dashboard_setup.md)
2. 检查 [用户手册](docs/user_guide.md)
3. 确认Google Sheets中的数据格式正确

---

**🎉 现在就开始创建您的第一个交易Dashboard吧！**

只需访问 lookerstudio.google.com 并按照上述步骤操作，您就能在几分钟内拥有一个专业的交易分析仪表板。