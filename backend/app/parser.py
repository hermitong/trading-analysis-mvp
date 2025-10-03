"""
Excel解析器 - 支持多券商格式
"""
import pandas as pd
import logging
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class ExcelParser:
    """Excel交易记录解析器"""

    def __init__(self):
        self.supported_brokers = {
            '富途证券': self._parse_futu,
            '老虎证券': self._parse_tiger,
            '雪盈证券': self._parse_snowball,
            'Interactive Brokers': self._parse_ib,
            '通用': self._parse_generic
        }

    def parse_file(self, file_path: str) -> List[Dict]:
        """
        解析Excel文件

        Args:
            file_path: Excel文件路径

        Returns:
            交易记录列表
        """
        try:
            # 读取Excel文件
            df = pd.read_excel(file_path)
            logger.info(f"成功读取文件: {file_path}, 记录数: {len(df)}")

            # 识别券商格式
            broker = self._identify_broker(df)
            logger.info(f"识别券商: {broker}")

            # 根据券商选择解析器
            if broker in self.supported_brokers:
                trades = self.supported_brokers[broker](df)
            else:
                # 使用通用解析器
                trades = self.supported_brokers['通用'](df)

            # 添加元数据
            for trade in trades:
                trade.update({
                    'broker': broker,
                    'source_file': Path(file_path).name,
                    'import_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })

            logger.info(f"解析完成，有效交易记录: {len(trades)}")
            return trades

        except Exception as e:
            logger.error(f"解析文件失败 {file_path}: {str(e)}")
            raise ParserException(f"文件解析失败: {str(e)}")

    def _identify_broker(self, df: pd.DataFrame) -> str:
        """根据Excel结构识别券商"""
        columns = set(df.columns.str.lower())

        # 富途证券特征列（新版本）
        if {'order status', 'symbol', 'direction', 'executed qty', 'avg price'}.issubset(columns):
            return '富途证券'

        # 富途证券特征列（旧版本）
        if {'成交日期', '成交时间', '证券代码', '交易方向'}.issubset(columns):
            return '富途证券'

        # 老虎证券特征列
        if {'date', 'time', 'symbol', 'side'}.issubset(columns):
            return '老虎证券'

        # IB特征列
        if {'Date', 'Time', 'Symbol', 'Action'}.issubset(columns):
            return 'Interactive Brokers'

        # 雪盈证券特征列
        if {'成交日期', '股票代码', '方向', '数量'}.issubset(columns):
            return '雪盈证券'

        # 默认使用通用解析器
        return '通用'

    def _parse_futu(self, df: pd.DataFrame) -> List[Dict]:
        """解析富途证券格式"""
        trades = []

        # 检查是否为新版本富途格式
        if 'Order Status' in df.columns:
            return self._parse_futu_new(df)
        else:
            return self._parse_futu_old(df)

    def _parse_futu_new(self, df: pd.DataFrame) -> List[Dict]:
        """解析新版本富途证券格式"""
        trades = []

        # 只处理已成交的订单
        df_executed = df[df['Order Status'] == '已成交'].copy()

        for _, row in df_executed.iterrows():
            try:
                # 检查是否有执行数量
                executed_qty = float(row.get('Executed Qty', 0))
                if executed_qty == 0:
                    continue

                # 解析日期时间
                order_time = str(row.get('Order Time', ''))
                trade_date, trade_time = self._parse_futu_datetime(order_time)

                trade = {
                    'trade_date': trade_date,
                    'trade_time': trade_time,
                    'symbol': str(row['Symbol']).strip(),
                    'security_name': str(row.get('Stock Name', '')).strip(),
                    'security_type': self._identify_security_type(str(row['Symbol'])),
                    'action': self._normalize_action(str(row['Direction'])),
                    'quantity': executed_qty,
                    'price': float(row.get('Avg Price', 0)),
                    'amount': float(row.get('Turnover', 0)),
                    'commission': 0,  # 富途新格式中手续费不在此文件显示
                    'account_id': '',
                    'notes': f"订单号: {row.get('Order No.', '')}"
                }

                # 处理期权格式
                symbol = trade['symbol']
                if 'Call' in symbol or 'Put' in symbol:
                    trade['security_type'] = 'OPTION'

                # 计算净金额
                trade['net_amount'] = trade['amount'] + trade['commission']

                trades.append(trade)

            except Exception as e:
                logger.warning(f"解析富途新格式记录失败: {row}, 错误: {e}")
                continue

        return trades

    def _parse_futu_old(self, df: pd.DataFrame) -> List[Dict]:
        """解析旧版本富途证券格式"""
        trades = []

        for _, row in df.iterrows():
            try:
                trade = {
                    'trade_date': self._parse_date(row['成交日期']),
                    'trade_time': self._parse_time(row.get('成交时间', '')),
                    'symbol': str(row['证券代码']).strip(),
                    'security_name': str(row.get('证券名称', '')).strip(),
                    'security_type': self._identify_security_type(str(row['证券代码'])),
                    'action': self._normalize_action(str(row['交易方向'])),
                    'quantity': float(row['成交数量']),
                    'price': float(row['成交价格']),
                    'amount': float(row['成交金额']),
                    'commission': float(row.get('手续费', 0)),
                    'account_id': str(row.get('账户', '')).strip(),
                    'notes': str(row.get('备注', '')).strip()
                }

                # 计算净金额
                trade['net_amount'] = trade['amount'] + trade['commission']

                trades.append(trade)

            except Exception as e:
                logger.warning(f"解析富途旧格式记录失败: {row}, 错误: {e}")
                continue

        return trades

    def _parse_futu_datetime(self, datetime_str: str) -> tuple:
        """解析富途日期时间格式"""
        try:
            # 格式: 2025-06-13 16:03:19 ET
            if 'ET' in datetime_str:
                # 移除时区信息
                datetime_str = datetime_str.replace(' ET', '').strip()

            # 分割日期和时间
            parts = datetime_str.split(' ')
            if len(parts) >= 2:
                date_part = parts[0]
                time_part = parts[1]
                return date_part, time_part
            else:
                # 如果格式不符合预期，使用默认值
                return datetime_str[:10], '00:00:00'
        except Exception:
            return datetime.now().strftime('%Y-%m-%d'), '00:00:00'

    def _parse_tiger(self, df: pd.DataFrame) -> List[Dict]:
        """解析老虎证券格式"""
        trades = []

        for _, row in df.iterrows():
            try:
                trade = {
                    'trade_date': self._parse_date(row['date']),
                    'trade_time': self._parse_time(row.get('time', '')),
                    'symbol': str(row['symbol']).strip(),
                    'security_name': str(row.get('name', '')).strip(),
                    'security_type': self._identify_security_type(str(row['symbol'])),
                    'action': self._normalize_action(str(row['side'])),
                    'quantity': float(row['quantity']),
                    'price': float(row['price']),
                    'amount': float(row['amount']),
                    'commission': float(row.get('commission', 0)),
                    'account_id': str(row.get('account', '')).strip(),
                    'notes': str(row.get('notes', '')).strip()
                }

                trade['net_amount'] = trade['amount'] + trade['commission']
                trades.append(trade)

            except Exception as e:
                logger.warning(f"解析老虎记录失败: {row}, 错误: {e}")
                continue

        return trades

    def _parse_ib(self, df: pd.DataFrame) -> List[Dict]:
        """解析Interactive Brokers格式"""
        trades = []

        for _, row in df.iterrows():
            try:
                trade = {
                    'trade_date': self._parse_date(row['Date']),
                    'trade_time': self._parse_time(row.get('Time', '')),
                    'symbol': str(row['Symbol']).strip(),
                    'security_name': str(row.get('Description', '')).strip(),
                    'security_type': self._identify_security_type(str(row['Symbol'])),
                    'action': self._normalize_action(str(row['Action'])),
                    'quantity': float(row['Quantity']),
                    'price': float(row['Price']),
                    'amount': float(row['Amount']),
                    'commission': float(row.get('Commission', 0)),
                    'account_id': str(row.get('Account', '')).strip(),
                    'notes': str(row.get('Notes', '')).strip()
                }

                trade['net_amount'] = trade['amount'] + trade['commission']
                trades.append(trade)

            except Exception as e:
                logger.warning(f"解析IB记录失败: {row}, 错误: {e}")
                continue

        return trades

    def _parse_snowball(self, df: pd.DataFrame) -> List[Dict]:
        """解析雪盈证券格式"""
        trades = []

        for _, row in df.iterrows():
            try:
                trade = {
                    'trade_date': self._parse_date(row['成交日期']),
                    'trade_time': self._parse_time(row.get('成交时间', '')),
                    'symbol': str(row['股票代码']).strip(),
                    'security_name': str(row.get('股票名称', '')).strip(),
                    'security_type': self._identify_security_type(str(row['股票代码'])),
                    'action': self._normalize_action(str(row['方向'])),
                    'quantity': float(row['数量']),
                    'price': float(row['成交价']),
                    'amount': float(row['成交额']),
                    'commission': float(row.get('手续费', 0)),
                    'account_id': str(row.get('账户', '')).strip(),
                    'notes': str(row.get('备注', '')).strip()
                }

                trade['net_amount'] = trade['amount'] + trade['commission']
                trades.append(trade)

            except Exception as e:
                logger.warning(f"解析雪盈记录失败: {row}, 错误: {e}")
                continue

        return trades

    def _parse_generic(self, df: pd.DataFrame) -> List[Dict]:
        """通用解析器 - 尝试智能识别列名"""
        trades = []

        # 列名映射
        column_mapping = {
            'date': ['日期', 'date', '成交日期', '交易日期'],
            'time': ['时间', 'time', '成交时间', '交易时间'],
            'symbol': ['代码', 'symbol', '股票代码', '证券代码'],
            'name': ['名称', 'name', '股票名称', '证券名称'],
            'action': ['方向', 'action', '交易方向', '买卖方向', 'side'],
            'quantity': ['数量', 'quantity', '成交数量', '交易数量'],
            'price': ['价格', 'price', '成交价', '成交价格'],
            'amount': ['金额', 'amount', '成交额', '成交金额'],
            'commission': ['手续费', 'commission', '佣金', '费用']
        }

        # 智能匹配列名
        mapped_columns = {}
        for field, possible_names in column_mapping.items():
            for col in df.columns:
                if str(col).lower() in [name.lower() for name in possible_names]:
                    mapped_columns[field] = col
                    break

        # 检查必要列是否存在
        required_fields = ['date', 'symbol', 'action', 'quantity', 'price']
        missing_fields = [field for field in required_fields if field not in mapped_columns]

        if missing_fields:
            raise ParserException(f"无法识别必要列: {missing_fields}")

        # 解析每一行
        for _, row in df.iterrows():
            try:
                # 计算金额（如果没有明确金额列）
                amount = row.get(mapped_columns.get('amount', 'amount'),
                               row[mapped_columns['quantity']] * row[mapped_columns['price']])

                trade = {
                    'trade_date': self._parse_date(row[mapped_columns['date']]),
                    'trade_time': self._parse_time(row.get(mapped_columns.get('time', 'time'), '')),
                    'symbol': str(row[mapped_columns['symbol']]).strip(),
                    'security_name': str(row.get(mapped_columns.get('name', 'name'), '')).strip(),
                    'security_type': self._identify_security_type(str(row[mapped_columns['symbol']])),
                    'action': self._normalize_action(str(row[mapped_columns['action']])),
                    'quantity': float(row[mapped_columns['quantity']]),
                    'price': float(row[mapped_columns['price']]),
                    'amount': float(amount),
                    'commission': float(row.get(mapped_columns.get('commission', 'commission'), 0)),
                    'account_id': '',
                    'notes': ''
                }

                trade['net_amount'] = trade['amount'] + trade['commission']
                trades.append(trade)

            except Exception as e:
                logger.warning(f"解析通用格式记录失败: {row}, 错误: {e}")
                continue

        return trades

    def _parse_date(self, date_value) -> str:
        """解析日期"""
        if pd.isna(date_value):
            return datetime.now().strftime('%Y-%m-%d')

        if isinstance(date_value, str):
            # 尝试多种日期格式
            for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%m/%d/%Y', '%d/%m/%Y']:
                try:
                    return datetime.strptime(date_value, fmt).strftime('%Y-%m-%d')
                except ValueError:
                    continue

        # 如果是datetime对象
        if hasattr(date_value, 'strftime'):
            return date_value.strftime('%Y-%m-%d')

        # 最后尝试用pandas解析
        try:
            return pd.to_datetime(date_value).strftime('%Y-%m-%d')
        except:
            return datetime.now().strftime('%Y-%m-%d')

    def _parse_time(self, time_value) -> str:
        """解析时间"""
        if pd.isna(time_value) or time_value == '':
            return '00:00:00'

        if isinstance(time_value, str):
            # 尝试多种时间格式
            for fmt in ['%H:%M:%S', '%H:%M', '%H:%M:%S.%f']:
                try:
                    return datetime.strptime(time_value, fmt).strftime('%H:%M:%S')
                except ValueError:
                    continue

        # 如果是datetime对象
        if hasattr(time_value, 'strftime'):
            return time_value.strftime('%H:%M:%S')

        # 最后尝试用pandas解析
        try:
            return pd.to_datetime(time_value).strftime('%H:%M:%S')
        except:
            return '00:00:00'

    def _normalize_action(self, action: str) -> str:
        """标准化交易方向"""
        action = action.strip().upper()

        # 买入方向映射
        buy_keywords = ['买', '买入', 'BUY', 'BOUGHT', 'PURCHASE']
        if action in buy_keywords:
            return 'BUY'

        # 卖出方向映射
        sell_keywords = ['卖', '卖出', 'SELL', 'SOLD', 'SALE']
        if action in sell_keywords:
            return 'SELL'

        # 默认返回
        return action

    def _identify_security_type(self, symbol: str) -> str:
        """识别证券类型"""
        symbol = str(symbol).upper()

        # 期权特征：包含C/P（Call/Put）
        if 'C' in symbol[-5:] or 'P' in symbol[-5:]:
            return 'OPTION'

        # 美股特征：纯字母
        if symbol.isalpha():
            return 'STOCK'

        # A股特征：6位数字
        if symbol.isdigit() and len(symbol) == 6:
            if symbol.startswith('6'):
                return 'STOCK'  # 上海
            elif symbol.startswith('0') or symbol.startswith('3'):
                return 'STOCK'  # 深圳/创业板

        return 'UNKNOWN'


class ParserException(Exception):
    """解析异常"""
    pass