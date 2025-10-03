"""
期权标的解析器 - 支持多种期权格式解析
"""
import re
import logging
from datetime import datetime
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class OptionSymbol:
    """期权解析结果"""
    underlying_symbol: str      # 标的代码
    strike_price: float         # 行权价
    expiration_date: str        # 到期日 (YYYY-MM-DD)
    option_type: str           # 期权类型: CALL/PUT
    original_symbol: str        # 原始代码
    format_type: str           # 格式类型: COMPACT/SEPARATE/STOCK

class OptionParser:
    """期权标的解析器"""

    def __init__(self):
        self.compact_pattern = re.compile(r'^([A-Z]+)(\d{4,6})([CP])$')
        self.excel_pattern = re.compile(r'^([A-Z]+)$')

    def parse_option_symbol(self, symbol: str, strike_price: Optional[float] = None,
                          expiration_date: Optional[str] = None, option_type: Optional[str] = None) -> OptionSymbol:
        """
        解析期权标的

        Args:
            symbol: 期权代码 (如 AVGO0919C 或 AVGO)
            strike_price: 行权价 (来自Excel单独字段)
            expiration_date: 到期日 (来自Excel单独字段)
            option_type: 期权类型 (来自Excel单独字段)

        Returns:
            OptionSymbol: 解析结果
        """
        symbol = str(symbol).strip().upper()

        # 尝试解析紧凑格式 (AVGO0919C)
        compact_result = self._parse_compact_format(symbol)
        if compact_result:
            logger.debug(f"解析紧凑格式期权: {symbol} -> {compact_result}")
            return compact_result

        # 尝试解析Excel分离格式
        if strike_price is not None or expiration_date is not None or option_type is not None:
            excel_result = self._parse_excel_format(symbol, strike_price, expiration_date, option_type)
            if excel_result:
                logger.debug(f"解析Excel分离格式期权: {symbol} -> {excel_result}")
                return excel_result

        # 如果都不匹配，当作股票处理
        logger.debug(f"无法解析为期权格式，当作股票处理: {symbol}")
        return OptionSymbol(
            underlying_symbol=symbol,
            strike_price=0.0,
            expiration_date='',
            option_type='',
            original_symbol=symbol,
            format_type='STOCK'
        )

    def _parse_compact_format(self, symbol: str) -> Optional[OptionSymbol]:
        """解析紧凑格式期权 (如 AVGO0919C)"""
        match = self.compact_pattern.match(symbol)
        if not match:
            return None

        underlying, date_str, option_char = match.groups()

        # 解析日期 (MMDD -> MM-DD)
        if len(date_str) == 4:
            date_formatted = f"{date_str[:2]}-{date_str[2:]}"
            # 假设是当前年份
            current_year = datetime.now().year
            full_date = f"{current_year}-{date_formatted}"
        elif len(date_str) == 6:
            # YYMMDD 格式
            year = f"20{date_str[:2]}"
            month_day = f"{date_str[2:4]}-{date_str[4:6]}"
            full_date = f"{year}-{month_day}"
        else:
            full_date = date_str

        option_type = 'CALL' if option_char == 'C' else 'PUT'

        return OptionSymbol(
            underlying_symbol=underlying,
            strike_price=0.0,  # 紧凑格式中不包含行权价，需要从其他地方获取
            expiration_date=full_date,
            option_type=option_type,
            original_symbol=symbol,
            format_type='COMPACT'
        )

    def _parse_excel_format(self, symbol: str, strike_price: Optional[float],
                          expiration_date: Optional[str], option_type: Optional[str]) -> Optional[OptionSymbol]:
        """解析Excel分离格式"""
        try:
            # 只要有任何一个期权相关字段就认为是期权
            if not (strike_price or expiration_date or option_type):
                return None

            # 标准化期权类型
            normalized_type = ''
            if option_type:
                option_type_str = str(option_type).strip().upper()
                if option_type_str in ['CALL', 'C', '看涨']:
                    normalized_type = 'CALL'
                elif option_type_str in ['PUT', 'P', '看跌']:
                    normalized_type = 'PUT'
                else:
                    normalized_type = option_type_str

            # 标准化日期格式
            normalized_date = self._normalize_date(expiration_date) if expiration_date else ''

            # 标准化行权价
            normalized_strike = float(strike_price) if strike_price else 0.0

            return OptionSymbol(
                underlying_symbol=symbol,
                strike_price=normalized_strike,
                expiration_date=normalized_date,
                option_type=normalized_type,
                original_symbol=symbol,
                format_type='SEPARATE'
            )

        except Exception as e:
            logger.warning(f"解析Excel分离格式失败: {symbol}, 错误: {e}")
            return None

    def _normalize_date(self, date_str: Optional[str]) -> str:
        """标准化日期格式为 YYYY-MM-DD"""
        if not date_str:
            return ''

        date_str = str(date_str).strip()

        # 如果已经是标准格式
        if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
            return date_str[:10]  # 去掉时间部分

        # 尝试解析其他格式
        date_formats = [
            '%Y/%m/%d',
            '%m/%d/%Y',
            '%d/%m/%Y',
            '%Y-%m-%d %H:%M:%S',
            '%m/%d/%y',
            '%Y%m%d'
        ]

        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                continue

        # 如果都无法解析，返回原字符串
        logger.warning(f"无法解析日期格式: {date_str}")
        return date_str

    def is_option(self, symbol: str, strike_price: Optional[float] = None,
                 option_type: Optional[str] = None) -> bool:
        """判断是否为期权"""
        result = self.parse_option_symbol(symbol, strike_price, None, option_type)
        return result.format_type in ['COMPACT', 'SEPARATE']

    def format_option_display(self, option: OptionSymbol) -> str:
        """格式化期权显示名称"""
        if option.format_type == 'STOCK':
            return option.underlying_symbol

        if option.format_type == 'COMPACT':
            return f"{option.underlying_symbol} {option.expiration_date[5:]} {option.option_type}"
        else:  # SEPARATE
            return f"{option.underlying_symbol} {option.expiration_date} ${option.strike_price} {option.option_type}"

# 全局解析器实例
option_parser = OptionParser()

def parse_symbol(symbol: str, strike_price: Optional[float] = None,
                expiration_date: Optional[str] = None,
                option_type: Optional[str] = None) -> OptionSymbol:
    """便捷函数：解析期权标的"""
    return option_parser.parse_option_symbol(symbol, strike_price, expiration_date, option_type)

def is_option_symbol(symbol: str, strike_price: Optional[float] = None,
                     option_type: Optional[str] = None) -> bool:
    """便捷函数：判断是否为期权"""
    return option_parser.is_option(symbol, strike_price, option_type)