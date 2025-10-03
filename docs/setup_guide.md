# Google API配置详细指南

## 概述

本指南将详细说明如何配置Google API，使投资交易复盘分析系统能够正常工作。

## 前置要求

- Google账号
- 稳定的网络连接

## 详细配置步骤

### 步骤1: 创建Google Cloud项目

1. **访问Google Cloud Console**
   - 打开浏览器，访问 [https://console.cloud.google.com/](https://console.cloud.google.com/)
   - 使用您的Google账号登录

2. **创建新项目**
   - 点击顶部项目选择器旁边的"选择项目"
   - 点击"新建项目"
   - 填写项目信息：
     - **项目名称**: `Trading Analysis`
     - **组织**: 无（个人账号）
   - 点击"创建"

3. **等待项目创建完成**
   - 通常需要几秒钟
   - 创建完成后会自动切换到新项目

### 步骤2: 启用必要的API

1. **进入API库**
   - 在左侧菜单中，点击"API和服务" → "库"
   - 或直接访问 [API库](https://console.cloud.google.com/apis/library)

2. **搜索并启用Google Sheets API**
   - 在搜索框中输入"Google Sheets API"
   - 点击搜索结果中的"Google Sheets API"
   - 点击"启用"按钮
   - 等待启用完成

3. **搜索并启用Google Drive API**
   - 返回API库页面
   - 搜索"Google Drive API"
   - 点击搜索结果中的"Google Drive API"
   - 点击"启用"按钮
   - 等待启用完成

4. **验证API启用状态**
   - 进入"API和服务" → "已启用的API和服务"
   - 确认两个API都在列表中

### 步骤3: 创建服务账号

1. **进入服务账号页面**
   - 在左侧菜单中，点击"IAM和管理" → "服务账号"
   - 或直接访问 [服务账号](https://console.cloud.google.com/iam-admin/serviceaccounts)

2. **创建服务账号**
   - 点击"创建服务账号"按钮
   - 填写服务账号详情：
     - **服务账号名称**: `trading-analysis`
     - **服务账号ID**: 自动生成（通常为 `trading-analysis@项目ID.iam.gserviceaccount.com`）
     - **描述**: `投资交易复盘分析系统服务账号`
   - 点击"创建并继续"

3. **分配权限**
   - 在"角色"下拉菜单中，选择以下角色：
     - **项目** → **编辑者** (Project → Editor)
   - 点击"继续"
   - 跳过"向用户授予此服务账号对服务账号的访问权限"步骤
   - 点击"完成"

4. **记录服务账号邮箱**
   - 在服务账号列表中找到刚创建的服务账号
   - 复制邮箱地址（格式：`trading-analysis@项目ID.iam.gserviceaccount.com`）
   - 这个邮箱地址将在步骤5中使用

### 步骤4: 创建并下载密钥

1. **进入服务账号详情**
   - 在服务账号列表中，点击刚创建的服务账号名称

2. **管理密钥**
   - 切换到"密钥"标签页
   - 点击"添加密钥" → "创建新密钥"

3. **选择密钥类型**
   - 选择"JSON"格式（推荐）
   - 点击"创建"

4. **下载密钥文件**
   - 浏览器会自动下载一个JSON文件
   - 文件名通常类似于：`项目名称-数字.json`
   - **重要**: 这是唯一下载机会，请妥善保管

5. **重命名和移动文件**
   - 将下载的JSON文件重命名为 `service_account.json`
   - 将文件移动到项目目录的 `backend/credentials/` 文件夹

### 步骤5: 创建和配置Google Sheets

1. **创建新的电子表格**
   - 访问 [Google Sheets](https://sheets.google.com/)
   - 点击"新建" → "电子表格"
   - 命名为：`投资交易记录`

2. **共享给服务账号**
   - 在电子表格右上角，点击"共享"按钮
   - 在"添加人员和群组"字段中，粘贴步骤3中记录的服务账号邮箱
   - 确保权限设置为"编辑者"
   - 取消勾选"通知收件人"（可选）
   - 点击"发送"

3. **验证共享权限**
   - 电子表格应该显示服务账号为共享用户
   - 系统应该能够访问和编辑该电子表格

### 步骤6: 验证配置

1. **测试系统连接**
   ```bash
   # 进入backend目录
   cd trading-analysis-mvp/backend

   # 运行测试脚本
   python -c "
   from app.config import Config
   from app.google_sheets_adapter import GoogleSheetsAdapter

   try:
       adapter = GoogleSheetsAdapter(
           Config.GOOGLE_CREDENTIALS_PATH,
           Config.SPREADSHEET_NAME
       )
       print('✓ Google Sheets连接成功')
       print(f'✓ 电子表格: {Config.SPREADSHEET_NAME}')
   except Exception as e:
       print(f'✗ 连接失败: {e}')
   "
   ```

2. **检查系统启动**
   - 运行启动脚本：
     - Windows: `scripts/start.bat`
     - macOS/Linux: `bash scripts/start.sh`
   - 确认没有Google API相关的错误信息

## 常见问题解决

### 问题1: "权限不足"错误

**症状**: 系统提示"Insufficient Permission"或类似错误

**解决方案**:
1. 确认服务账号具有"编辑者"权限
2. 检查Google Sheets共享设置
3. 重新生成服务账号密钥

### 问题2: "API未启用"错误

**症状**: 系统提示API未启用

**解决方案**:
1. 确认Google Sheets API和Google Drive API都已启用
2. 检查是否选择了正确的项目
3. 等待几分钟让API生效

### 问题3: "文件不存在"错误

**症状**: 找不到service_account.json文件

**解决方案**:
1. 确认文件在正确的目录：`backend/credentials/service_account.json`
2. 检查文件名拼写
3. 确认文件权限正确（可读）

### 问题4: 服务账号邮箱找不到

**症状**: 无法在IAM管理页面找到服务账号

**解决方案**:
1. 确认选择了正确的项目
2. 检查服务账号是否创建成功
3. 重新创建服务账号

## 安全建议

### 密钥文件安全

1. **不要提交到版本控制**
   - 将 `credentials/` 目录添加到 `.gitignore`
   - 不要将JSON密钥文件上传到GitHub等平台

2. **定期轮换密钥**
   - 建议每6个月更换一次密钥
   - 删除不再使用的旧密钥

3. **限制权限**
   - 服务账号只授予必要的权限
   - 不要使用"所有者"权限

### 数据安全

1. **敏感信息处理**
   - Excel文件中的个人数据会被上传到Google
   - 确认遵守相关的隐私法规

2. **备份策略**
   - 定期备份Google Sheets数据
   - 导出重要的分析结果

## 高级配置

### 自定义电子表格名称

如需使用不同的电子表格名称：

1. 修改配置文件
   ```python
   # backend/app/config.py
   SPREADSHEET_NAME = '您的自定义名称'
   ```

2. 重新创建电子表格并共享

### 多环境配置

对于开发和生产环境，可以：

1. 使用不同的服务账号
2. 创建不同的电子表格
3. 使用环境变量控制配置

```bash
# 设置环境变量
export STORAGE_TYPE=google_sheets
export SPREADSHEET_NAME="投资交易记录_生产环境"
```

---

**配置完成后，系统就可以正常工作了！** 🎉

如果仍有问题，请查看 [用户手册](user_guide.md) 或联系技术支持。