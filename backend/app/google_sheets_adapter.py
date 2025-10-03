"""
Google Sheets适配器 - 数据存储层
"""
import logging
from datetime import datetime
from typing import List, Dict, Optional
import gspread
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import Request

logger = logging.getLogger(__name__)

class GoogleSheetsAdapter:
    """Google Sheets存储适配器"""

    def __init__(self, credentials_path: str, spreadsheet_name: str):
        """
        初始化Google Sheets适配器

        Args:
            credentials_path: Google服务账号凭证文件路径
            spreadsheet_name: 电子表格名称
        """
        self.credentials_path = credentials_path
        self.spreadsheet_name = spreadsheet_name
        self.spreadsheet = None
        self._connect()

    def _connect(self):
        """连接到Google Sheets"""
        try:
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]

            credentials = Credentials.from_service_account_file(
                self.credentials_path, scopes=scopes
            )
            client = gspread.authorize(credentials)

            # 尝试打开现有电子表格
            try:
                self.spreadsheet = client.open(self.spreadsheet_name)
                logger.info(f"已连接到电子表格: {self.spreadsheet_name}")
            except gspread.exceptions.SpreadsheetNotFound:
                # 创建新的电子表格
                self.spreadsheet = client.create(self.spreadsheet_name)
                logger.info(f"已创建新电子表格: {self.spreadsheet_name}")
                self._initialize_worksheets()

        except Exception as e:
            logger.error(f"连接Google Sheets失败: {str(e)}")
            raise ConnectionError(f"无法连接到Google Sheets: {str(e)}")

    def _initialize_worksheets(self):
        """初始化工作表结构"""
        worksheets_config = [
            {
                'name': 'trades',
                'headers': [
                    'id', 'trade_date', 'trade_time', 'symbol', 'security_name', 'security_type',
                    'action', 'quantity', 'price', 'amount', 'commission', 'net_amount',
                    'broker', 'account_id', 'notes', 'source_file', 'import_time'
                ]
            },
            {
                'name': 'positions',
                'headers': [
                    'id', 'symbol', 'security_name', 'security_type',
                    'total_quantity', 'avg_cost', 'total_cost',
                    'current_price', 'market_value', 'unrealized_pnl', 'unrealized_pnl_pct',
                    'last_trade_date', 'updated_at'
                ]
            },
            {
                'name': 'closed_positions',
                'headers': [
                    'id', 'symbol', 'security_name',
                    'open_date', 'close_date', 'holding_days',
                    'quantity', 'open_price', 'close_price',
                    'total_cost', 'total_revenue', 'commission',
                    'net_pnl', 'pnl_pct', 'created_at'
                ]
            },
            {
                'name': 'daily_summary',
                'headers': [
                    'id', 'summary_date',
                    'total_trades', 'buy_trades', 'sell_trades',
                    'total_volume', 'total_commission', 'realized_pnl',
                    'winning_trades', 'losing_trades', 'win_rate',
                    'largest_profit', 'largest_loss', 'avg_profit', 'avg_loss', 'profit_factor',
                    'created_at', 'updated_at'
                ]
            },
            {
                'name': 'import_logs',
                'headers': [
                    'id', 'file_name', 'file_path', 'file_size', 'file_hash',
                    'records_count', 'success_count', 'error_count',
                    'status', 'error_message', 'import_time', 'duration_seconds'
                ]
            }
        ]

        for config in worksheets_config:
            try:
                worksheet = self.spreadsheet.add_worksheet(
                    title=config['name'],
                    rows="1000",
                    cols="20"
                )
                worksheet.append_row(config['headers'])
                logger.info(f"已创建工作表: {config['name']}")
            except Exception as e:
                logger.error(f"创建工作表失败 {config['name']}: {str(e)}")

    def insert_trades(self, trades: List[Dict]) -> int:
        """插入交易记录"""
        try:
            worksheet = self.spreadsheet.worksheet('trades')

            # 获取现有记录数
            existing_count = len(worksheet.col_values(1)) - 1  # 减去标题行

            # 准备数据行
            rows = []
            for i, trade in enumerate(trades):
                row_id = existing_count + i + 1
                row = [
                    row_id,
                    trade.get('trade_date', ''),
                    trade.get('trade_time', ''),
                    trade.get('symbol', ''),
                    trade.get('security_name', ''),
                    trade.get('security_type', 'UNKNOWN'),
                    trade.get('action', ''),
                    trade.get('quantity', 0),
                    trade.get('price', 0),
                    trade.get('amount', 0),
                    trade.get('commission', 0),
                    trade.get('net_amount', trade.get('amount', 0)),
                    trade.get('broker', ''),
                    trade.get('account_id', ''),
                    trade.get('notes', ''),
                    trade.get('source_file', ''),
                    trade.get('import_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                ]
                rows.append(row)

            # 批量插入
            if rows:
                worksheet.append_rows(rows)
                logger.info(f"已插入 {len(rows)} 条交易记录")
                return len(rows)
            else:
                return 0

        except Exception as e:
            logger.error(f"插入交易记录失败: {str(e)}")
            raise

    def get_all_trades(self) -> List[Dict]:
        """获取所有交易记录"""
        try:
            worksheet = self.spreadsheet.worksheet('trades')
            records = worksheet.get_all_records()
            return records
        except Exception as e:
            logger.error(f"获取交易记录失败: {str(e)}")
            return []

    def get_trades_by_symbol(self, symbol: str) -> List[Dict]:
        """根据标的获取交易记录"""
        try:
            all_trades = self.get_all_trades()
            symbol_trades = [t for t in all_trades if t.get('symbol') == symbol]
            return symbol_trades
        except Exception as e:
            logger.error(f"获取标的交易记录失败 {symbol}: {str(e)}")
            return []

    def get_trades_by_date(self, date: str) -> List[Dict]:
        """根据日期获取交易记录"""
        try:
            all_trades = self.get_all_trades()
            date_trades = [t for t in all_trades if t.get('trade_date') == date]
            return date_trades
        except Exception as e:
            logger.error(f"获取日期交易记录失败 {date}: {str(e)}")
            return []

    def update_position(self, symbol: str, position_data: Dict):
        """更新持仓信息"""
        try:
            worksheet = self.spreadsheet.worksheet('positions')

            # 查找现有记录
            all_records = worksheet.get_all_records()
            existing_index = None

            for i, record in enumerate(all_records):
                if record.get('symbol') == symbol:
                    existing_index = i + 2  # +2 因为有标题行和从0开始的索引
                    break

            # 准备数据行
            row = [
                existing_index - 1 if existing_index else len(all_records) + 1,  # id
                position_data.get('symbol', ''),
                position_data.get('security_name', ''),
                position_data.get('security_type', 'UNKNOWN'),
                position_data.get('total_quantity', 0),
                position_data.get('avg_cost', 0),
                position_data.get('total_cost', 0),
                position_data.get('current_price', 0),
                position_data.get('market_value', 0),
                position_data.get('unrealized_pnl', 0),
                position_data.get('unrealized_pnl_pct', 0),
                position_data.get('last_trade_date', ''),
                position_data.get('updated_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            ]

            if existing_index:
                # 更新现有记录
                worksheet.update(f'A{existing_index}:M{existing_index}', [row])
                logger.debug(f"已更新持仓 {symbol}")
            else:
                # 插入新记录
                worksheet.append_row(row)
                logger.debug(f"已插入新持仓 {symbol}")

        except Exception as e:
            logger.error(f"更新持仓失败 {symbol}: {str(e)}")
            raise

    def get_open_positions(self) -> List[Dict]:
        """获取所有开仓持仓"""
        try:
            worksheet = self.spreadsheet.worksheet('positions')
            records = worksheet.get_all_records()
            # 过滤出有持仓的记录
            open_positions = [r for r in records if r.get('total_quantity', 0) > 0]
            return open_positions
        except Exception as e:
            logger.error(f"获取开仓持仓失败: {str(e)}")
            return []

    def insert_closed_position(self, closed_data: Dict):
        """插入已平仓记录"""
        try:
            worksheet = self.spreadsheet.worksheet('closed_positions')

            # 获取现有记录数
            existing_count = len(worksheet.col_values(1)) - 1
            next_id = existing_count + 1

            row = [
                next_id,
                closed_data.get('symbol', ''),
                closed_data.get('security_name', ''),
                closed_data.get('open_date', ''),
                closed_data.get('close_date', ''),
                closed_data.get('holding_days', 0),
                closed_data.get('quantity', 0),
                closed_data.get('open_price', 0),
                closed_data.get('close_price', 0),
                closed_data.get('total_cost', 0),
                closed_data.get('total_revenue', 0),
                closed_data.get('commission', 0),
                closed_data.get('net_pnl', 0),
                closed_data.get('pnl_pct', 0),
                closed_data.get('created_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            ]

            worksheet.append_row(row)
            logger.debug(f"已插入已平仓记录: {closed_data.get('symbol')}")

        except Exception as e:
            logger.error(f"插入已平仓记录失败: {str(e)}")
            raise

    def get_closed_positions_by_date(self, date: str) -> List[Dict]:
        """根据日期获取已平仓记录"""
        try:
            worksheet = self.spreadsheet.worksheet('closed_positions')
            all_records = worksheet.get_all_records()
            date_records = [r for r in all_records if r.get('close_date') == date]
            return date_records
        except Exception as e:
            logger.error(f"获取日期已平仓记录失败 {date}: {str(e)}")
            return []

    def get_all_closed_positions(self) -> List[Dict]:
        """获取所有已平仓记录"""
        try:
            worksheet = self.spreadsheet.worksheet('closed_positions')
            records = worksheet.get_all_records()
            return records
        except Exception as e:
            logger.error(f"获取已平仓记录失败: {str(e)}")
            return []

    def insert_or_update_daily_summary(self, summary_data: Dict):
        """插入或更新每日汇总"""
        try:
            worksheet = self.spreadsheet.worksheet('daily_summary')

            # 查找现有记录
            all_records = worksheet.get_all_records()
            existing_index = None

            for i, record in enumerate(all_records):
                if record.get('summary_date') == summary_data.get('summary_date'):
                    existing_index = i + 2  # +2 因为有标题行和从0开始的索引
                    break

            # 准备数据行
            row = [
                existing_index - 1 if existing_index else len(all_records) + 1,  # id
                summary_data.get('summary_date', ''),
                summary_data.get('total_trades', 0),
                summary_data.get('buy_trades', 0),
                summary_data.get('sell_trades', 0),
                summary_data.get('total_volume', 0),
                summary_data.get('total_commission', 0),
                summary_data.get('realized_pnl', 0),
                summary_data.get('winning_trades', 0),
                summary_data.get('losing_trades', 0),
                summary_data.get('win_rate', 0),
                summary_data.get('largest_profit', 0),
                summary_data.get('largest_loss', 0),
                summary_data.get('avg_profit', 0),
                summary_data.get('avg_loss', 0),
                summary_data.get('profit_factor', 0),
                summary_data.get('created_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                summary_data.get('updated_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            ]

            if existing_index:
                # 更新现有记录
                worksheet.update(f'A{existing_index}:R{existing_index}', [row])
                logger.debug(f"已更新每日汇总 {summary_data.get('summary_date')}")
            else:
                # 插入新记录
                worksheet.append_row(row)
                logger.debug(f"已插入新每日汇总 {summary_data.get('summary_date')}")

        except Exception as e:
            logger.error(f"插入/更新每日汇总失败: {str(e)}")
            raise

    def insert_import_log(self, log_data: Dict):
        """插入导入日志"""
        try:
            worksheet = self.spreadsheet.worksheet('import_logs')

            # 获取现有记录数
            existing_count = len(worksheet.col_values(1)) - 1
            next_id = existing_count + 1

            row = [
                next_id,
                log_data.get('file_name', ''),
                log_data.get('file_path', ''),
                log_data.get('file_size', 0),
                log_data.get('file_hash', ''),
                log_data.get('records_count', 0),
                log_data.get('success_count', 0),
                log_data.get('error_count', 0),
                log_data.get('status', ''),
                log_data.get('error_message', ''),
                log_data.get('import_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                log_data.get('duration_seconds', 0)
            ]

            worksheet.append_row(row)
            logger.debug(f"已插入导入日志: {log_data.get('file_name')}")

        except Exception as e:
            logger.error(f"插入导入日志失败: {str(e)}")
            raise

    def get_import_log_by_hash(self, file_hash: str) -> Optional[Dict]:
        """根据文件哈希获取导入日志"""
        try:
            worksheet = self.spreadsheet.worksheet('import_logs')
            all_records = worksheet.get_all_records()
            for record in all_records:
                if record.get('file_hash') == file_hash:
                    return record
            return None
        except Exception as e:
            logger.error(f"获取导入日志失败 {file_hash}: {str(e)}")
            return None

    def clear_all_data(self):
        """清空所有数据（仅用于测试）"""
        try:
            worksheets = ['trades', 'positions', 'closed_positions', 'daily_summary', 'import_logs']

            for sheet_name in worksheets:
                worksheet = self.spreadsheet.worksheet(sheet_name)
                # 保留标题行，删除其他所有行
                rows = len(worksheet.col_values(1))
                if rows > 1:
                    worksheet.delete_rows(2, rows)
                    logger.info(f"已清空工作表: {sheet_name}")

        except Exception as e:
            logger.error(f"清空数据失败: {str(e)}")
            raise