"""
系统配置文件
"""
import os
import logging
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent.parent

class Config:
    """系统配置类"""

    # 基础配置
    APP_NAME = "投资交易复盘分析系统"
    VERSION = "1.0.0"

    # 文件监控配置
    WATCH_FOLDER = os.path.join(BASE_DIR.parent, 'trading_records')
    SUPPORTED_EXTENSIONS = ['.xlsx', '.xls', '.csv']

    # Google Sheets配置
    GOOGLE_CREDENTIALS_PATH = os.path.join(BASE_DIR, 'credentials', 'service_account.json')
    SPREADSHEET_NAME = '投资交易记录'

    # SQLite配置（可选）
    STORAGE_TYPE = os.getenv('STORAGE_TYPE', 'google_sheets')  # 或 'sqlite'
    SQLITE_DB_PATH = os.path.join(BASE_DIR, 'data', 'trading.db')

    # 定时任务配置
    CHECK_INTERVAL_HOURS = 1       # 每小时检查一次
    DAILY_SUMMARY_HOUR = 18        # 每日18:00汇总

    # 日志配置
    LOG_FOLDER = os.path.join(BASE_DIR, 'logs')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # 券商配置
    SUPPORTED_BROKERS = ['富途证券', '老虎证券', '雪盈证券', 'Interactive Brokers', '通用']

    @classmethod
    def init_directories(cls):
        """确保必要目录存在"""
        os.makedirs(cls.WATCH_FOLDER, exist_ok=True)
        os.makedirs(cls.LOG_FOLDER, exist_ok=True)
        os.makedirs(os.path.dirname(cls.GOOGLE_CREDENTIALS_PATH), exist_ok=True)
        os.makedirs(os.path.dirname(cls.SQLITE_DB_PATH), exist_ok=True)

    @classmethod
    def get_storage_adapter(cls):
        """根据配置返回对应的存储适配器"""
        if cls.STORAGE_TYPE == 'sqlite':
            from app.database import SQLiteAdapter
            return SQLiteAdapter(cls.SQLITE_DB_PATH)
        else:
            from app.google_sheets_adapter import GoogleSheetsAdapter
            return GoogleSheetsAdapter(
                cls.GOOGLE_CREDENTIALS_PATH,
                cls.SPREADSHEET_NAME
            )