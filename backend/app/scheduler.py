"""
定时任务调度器
"""
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

from app.config import Config
from app.parser import ExcelParser
from app.calculator import PnLCalculator
from app.utils import calculate_file_hash, get_files_in_folder, validate_trade_record

logger = logging.getLogger(__name__)

class TradingScheduler:
    """交易系统定时任务调度器"""

    def __init__(self):
        self.scheduler = BlockingScheduler()
        self.parser = ExcelParser()
        self.storage = Config.get_storage_adapter()
        self.calculator = PnLCalculator(self.storage)
        self.processed_files = set()

        # 配置定时任务
        self._setup_jobs()

    def _setup_jobs(self):
        """配置定时任务"""
        # 每小时检查新文件
        self.scheduler.add_job(
            func=self._check_new_files,
            trigger=IntervalTrigger(hours=Config.CHECK_INTERVAL_HOURS),
            id='check_files',
            name='检查新交易文件',
            max_instances=1
        )

        # 每日18:00执行汇总
        self.scheduler.add_job(
            func=self._daily_summary,
            trigger=CronTrigger(hour=Config.DAILY_SUMMARY_HOUR, minute=0),
            id='daily_summary',
            name='每日汇总统计',
            max_instances=1
        )

        # 启动时立即执行一次检查
        self.scheduler.add_job(
            func=self._check_new_files,
            trigger='date',
            run_date=datetime.now() + timedelta(seconds=5),
            id='initial_check',
            name='启动时检查文件',
            max_instances=1
        )

    def start(self):
        """启动调度器"""
        logger.info("交易系统调度器启动")
        logger.info(f"监控文件夹: {Config.WATCH_FOLDER}")
        logger.info(f"检查间隔: {Config.CHECK_INTERVAL_HOURS} 小时")
        logger.info(f"每日汇总时间: {Config.DAILY_SUMMARY_HOUR}:00")

        try:
            self.scheduler.start()
        except KeyboardInterrupt:
            logger.info("收到中断信号，正在停止调度器...")
            self.scheduler.shutdown()
        except Exception as e:
            logger.error(f"调度器异常: {str(e)}")
            self.scheduler.shutdown()

    def _check_new_files(self):
        """检查并处理新文件"""
        logger.info("=" * 50)
        logger.info(f"开始检查新文件 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        try:
            # 获取监控文件夹中的所有文件
            files = get_files_in_folder(Config.WATCH_FOLDER, Config.SUPPORTED_EXTENSIONS)

            if not files:
                logger.info("未发现任何文件")
                return

            logger.info(f"发现 {len(files)} 个文件，开始检查...")

            processed_count = 0
            for file_path in files:
                try:
                    if self._process_file(file_path):
                        processed_count += 1
                except Exception as e:
                    logger.error(f"处理文件失败 {file_path}: {str(e)}")

            logger.info(f"文件检查完成，处理了 {processed_count} 个文件")

        except Exception as e:
            logger.error(f"检查新文件时发生异常: {str(e)}")

        logger.info("=" * 50)

    def _process_file(self, file_path: str) -> bool:
        """
        处理单个文件

        Returns:
            bool: 是否成功处理
        """
        file_name = Path(file_path).name
        logger.info(f"正在处理文件: {file_name}")

        start_time = time.time()

        try:
            # 计算文件哈希
            file_hash = calculate_file_hash(file_path)

            # 检查文件是否已处理
            existing_log = self.storage.get_import_log_by_hash(file_hash)
            if existing_log and existing_log.get('status') == 'SUCCESS':
                logger.info(f"文件已处理，跳过: {file_name}")
                return False

            # 记录开始处理
            logger.info(f"开始解析文件: {file_name}")

            # 解析Excel文件
            trades = self.parser.parse_file(file_path)

            if not trades:
                logger.warning(f"文件中未发现有效交易记录: {file_name}")
                return False

            # 验证交易记录
            valid_trades = []
            invalid_count = 0

            for trade in trades:
                if validate_trade_record(trade):
                    valid_trades.append(trade)
                else:
                    invalid_count += 1
                    logger.warning(f"无效交易记录: {trade}")

            if not valid_trades:
                logger.warning(f"文件中没有有效的交易记录: {file_name}")
                return False

            logger.info(f"解析完成: 总记录={len(trades)}, 有效记录={len(valid_trades)}, 无效记录={invalid_count}")

            # 插入交易记录到存储
            self.storage.insert_trades(valid_trades)

            # 处理盈亏计算
            logger.info("开始处理盈亏计算...")
            calc_result = self.calculator.process_trades(valid_trades)

            logger.info(f"盈亏计算完成: 处理={calc_result['processed']}, "
                       f"持仓更新={calc_result['positions_updated']}, "
                       f"已平仓={calc_result['closed_positions']}")

            if calc_result['errors']:
                for error in calc_result['errors']:
                    logger.error(error)

            # 记录导入日志
            duration = time.time() - start_time
            log_data = {
                'file_name': file_name,
                'file_path': file_path,
                'file_size': Path(file_path).stat().st_size,
                'file_hash': file_hash,
                'records_count': len(trades),
                'success_count': len(valid_trades),
                'error_count': invalid_count + len(calc_result['errors']),
                'status': 'FAILED' if calc_result['errors'] else 'SUCCESS',
                'error_message': '; '.join(calc_result['errors'][:3]) if calc_result['errors'] else '',
                'import_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'duration_seconds': round(duration, 2)
            }

            self.storage.insert_import_log(log_data)

            logger.info(f"文件处理完成: {file_name} (耗时: {duration:.2f}秒)")
            return True

        except Exception as e:
            # 记录失败日志
            duration = time.time() - start_time
            error_message = str(e)

            try:
                log_data = {
                    'file_name': file_name,
                    'file_path': file_path,
                    'file_size': Path(file_path).stat().st_size if Path(file_path).exists() else 0,
                    'file_hash': '',
                    'records_count': 0,
                    'success_count': 0,
                    'error_count': 1,
                    'status': 'FAILED',
                    'error_message': error_message,
                    'import_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'duration_seconds': round(duration, 2)
                }
                self.storage.insert_import_log(log_data)
            except Exception as log_error:
                logger.error(f"记录失败日志时出错: {str(log_error)}")

            logger.error(f"处理文件失败 {file_name}: {error_message}")
            return False

    def _daily_summary(self):
        """执行每日汇总统计"""
        logger.info("开始执行每日汇总统计")

        try:
            # 获取需要汇总的日期（昨天）
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

            # 计算每日汇总
            summary = self.calculator.calculate_daily_summary(yesterday)

            # 保存汇总结果
            self.storage.insert_or_update_daily_summary(summary)

            logger.info(f"每日汇总完成 - {yesterday}")
            logger.info(f"  交易次数: {summary['total_trades']}")
            logger.info(f"  已实现盈亏: {summary['realized_pnl']:.2f}")
            logger.info(f"  胜率: {summary['win_rate']:.2f}%")

            # 如果今天还有交易，也汇总今天的
            today = datetime.now().strftime('%Y-%m-%d')
            today_summary = self.calculator.calculate_daily_summary(today)
            self.storage.insert_or_update_daily_summary(today_summary)

            if today_summary['total_trades'] > 0:
                logger.info(f"今日汇总完成 - {today}")
                logger.info(f"  交易次数: {today_summary['total_trades']}")

        except Exception as e:
            logger.error(f"每日汇总失败: {str(e)}")

        logger.info("每日汇总统计完成")

    def manual_trigger(self):
        """手动触发文件检查"""
        logger.info("手动触发文件检查")
        self._check_new_files()

    def shutdown(self):
        """关闭调度器"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("调度器已关闭")