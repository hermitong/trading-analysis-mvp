"""
工具函数
"""
import hashlib
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

def setup_logging():
    """设置日志配置"""
    from app.config import Config

    # 确保日志目录存在
    os.makedirs(Config.LOG_FOLDER, exist_ok=True)

    # 配置日志格式
    log_format = logging.Formatter(Config.LOG_FORMAT)

    # 文件处理器
    file_handler = logging.FileHandler(
        os.path.join(Config.LOG_FOLDER, 'trading_system.log'),
        encoding='utf-8'
    )
    file_handler.setFormatter(log_format)

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)

    # 根日志器配置
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, Config.LOG_LEVEL))
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # 防止重复日志
    root_logger.propagate = False

def calculate_file_hash(file_path: str) -> str:
    """计算文件MD5哈希值"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def format_currency(amount: float, currency: str = '¥') -> str:
    """格式化货币金额"""
    if amount >= 0:
        return f"{currency}{amount:,.2f}"
    else:
        return f"{currency}{abs(amount):,.2f}"

def format_percentage(value: float) -> str:
    """格式化百分比"""
    return f"{value:+.2f}%"

def safe_float(value, default: float = 0.0) -> float:
    """安全转换为浮点数"""
    try:
        return float(value) if value is not None else default
    except (ValueError, TypeError):
        return default

def safe_int(value, default: int = 0) -> int:
    """安全转换为整数"""
    try:
        return int(value) if value is not None else default
    except (ValueError, TypeError):
        return default

def get_files_in_folder(folder_path: str, extensions: List[str] = None) -> List[str]:
    """获取文件夹中指定扩展名的文件"""
    if extensions is None:
        extensions = ['.xlsx', '.xls', '.csv']

    files = []
    for file_path in Path(folder_path).iterdir():
        if file_path.is_file() and file_path.suffix.lower() in extensions:
            files.append(str(file_path))

    return files

def validate_trade_record(trade: Dict) -> bool:
    """验证交易记录的完整性"""
    required_fields = [
        'trade_date', 'symbol', 'action', 'quantity', 'price', 'amount'
    ]

    # 检查必填字段
    for field in required_fields:
        if field not in trade or trade[field] is None:
            return False

    # 检查数值字段
    try:
        float(trade['quantity'])
        float(trade['price'])
        float(trade['amount'])
    except (ValueError, TypeError):
        return False

    # 检查交易方向
    if trade['action'] not in ['BUY', 'SELL']:
        return False

    return True

def clean_symbol(symbol: str) -> str:
    """清理证券代码"""
    if not symbol:
        return ''

    # 移除空格和特殊字符
    symbol = str(symbol).strip().upper()

    # 移除常见的交易所后缀
    for suffix in ['.SS', '.SZ', '.HK', '.OQ', '.N']:
        if symbol.endswith(suffix):
            symbol = symbol[:-len(suffix)]
            break

    return symbol

def calculate_age_days(start_date: str, end_date: str = None) -> int:
    """计算天数差"""
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d') if end_date else datetime.now()
        return (end - start).days
    except ValueError:
        return 0