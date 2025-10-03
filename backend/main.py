"""
投资交易复盘分析系统 - 主程序入口
"""
import sys
import os
import logging
import signal
from pathlib import Path

# 添加app目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.config import Config
from app.scheduler import TradingScheduler
from app.utils import setup_logging

def signal_handler(signum, frame):
    """信号处理器"""
    print("\n收到中断信号，正在退出系统...")
    sys.exit(0)

def main():
    """主程序入口"""
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("=" * 60)
    print(f"{Config.APP_NAME} v{Config.VERSION}")
    print("=" * 60)
    print()

    # 初始化配置
    try:
        Config.init_directories()
        print("✓ 目录初始化完成")
    except Exception as e:
        print(f"✗ 目录初始化失败: {e}")
        sys.exit(1)

    # 设置日志
    try:
        setup_logging()
        logger = logging.getLogger(__name__)
        print("✓ 日志系统启动")
    except Exception as e:
        print(f"✗ 日志系统启动失败: {e}")
        sys.exit(1)

    logger.info("=" * 60)
    logger.info(f"{Config.APP_NAME} v{Config.VERSION} 启动")
    logger.info("=" * 60)

    # 显示配置信息
    logger.info(f"监控文件夹: {Config.WATCH_FOLDER}")
    logger.info(f"存储方式: {Config.STORAGE_TYPE}")
    logger.info(f"电子表格: {Config.SPREADSHEET_NAME}")
    logger.info(f"检查间隔: {Config.CHECK_INTERVAL_HOURS} 小时")
    logger.info(f"每日汇总时间: {Config.DAILY_SUMMARY_HOUR}:00")

    print()
    print("系统配置信息:")
    print(f"  监控文件夹: {Config.WATCH_FOLDER}")
    print(f"  存储方式: {Config.STORAGE_TYPE}")
    if Config.STORAGE_TYPE == 'google_sheets':
        print(f"  电子表格: {Config.SPREADSHEET_NAME}")
    else:
        print(f"  本地数据库: {Config.SQLITE_DB_PATH}")
    print(f"  检查间隔: {Config.CHECK_INTERVAL_HOURS} 小时")
    print(f"  每日汇总: {Config.DAILY_SUMMARY_HOUR}:00")
    print()

    # 验证必要条件
    try:
        if Config.STORAGE_TYPE == 'google_sheets':
            credentials_file = Path(Config.GOOGLE_CREDENTIALS_PATH)
            if not credentials_file.exists():
                print("✗ 未找到Google API凭证文件")
                print(f"  请将 service_account.json 放入: {Config.GOOGLE_CREDENTIALS_PATH}")
                print("  详细配置指南请参考: docs/setup_guide.md")
                sys.exit(1)
            else:
                print("✓ Google API凭证文件存在")

        # 检查监控文件夹
        watch_folder = Path(Config.WATCH_FOLDER)
        if not watch_folder.exists():
            print(f"✗ 监控文件夹不存在: {Config.WATCH_FOLDER}")
            sys.exit(1)
        else:
            print(f"✓ 监控文件夹存在: {Config.WATCH_FOLDER}")

    except Exception as e:
        print(f"✗ 系统验证失败: {e}")
        sys.exit(1)

    print()
    print("系统启动中...")
    print("按 Ctrl+C 可以安全退出系统")
    print("=" * 60)
    print()

    # 启动调度器
    try:
        scheduler = TradingScheduler()
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("用户中断，系统退出")
    except Exception as e:
        logger.error(f"系统异常: {str(e)}", exc_info=True)
        print(f"✗ 系统异常: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()