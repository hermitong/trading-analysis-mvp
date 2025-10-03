"""
盈亏计算引擎 - FIFO算法实现
"""
import logging
from datetime import datetime
from typing import List, Dict, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)

class PnLCalculator:
    """盈亏计算器"""

    def __init__(self, storage):
        """
        初始化计算器

        Args:
            storage: 存储适配器实例
        """
        self.storage = storage

    def process_trades(self, trades: List[Dict]) -> Dict:
        """
        处理交易记录，更新持仓和已平仓记录

        Args:
            trades: 交易记录列表

        Returns:
            处理结果统计
        """
        result = {
            'processed': 0,
            'positions_updated': 0,
            'closed_positions': 0,
            'errors': []
        }

        # 按标的和日期排序
        sorted_trades = sorted(trades, key=lambda x: (x['symbol'], x['trade_date'], x['trade_time']))

        # 按标的分组处理
        symbol_groups = defaultdict(list)
        for trade in sorted_trades:
            symbol_groups[trade['symbol']].append(trade)

        for symbol, symbol_trades in symbol_groups.items():
            try:
                logger.info(f"处理标的 {symbol}, 交易数: {len(symbol_trades)}")

                # 获取当前持仓
                current_position = self._get_current_position(symbol)

                # 获取未配对的买入记录（用于FIFO）
                open_buy_trades = self._get_open_buy_trades(symbol)

                for trade in symbol_trades:
                    if trade['action'] == 'BUY':
                        self._process_buy(trade, current_position)
                        open_buy_trades.append(trade)
                    elif trade['action'] == 'SELL':
                        closed_count = self._process_sell(trade, current_position, open_buy_trades)
                        result['closed_positions'] += closed_count

                    result['processed'] += 1

                # 更新持仓
                if current_position:
                    self.storage.update_position(symbol, current_position)
                    result['positions_updated'] += 1

            except Exception as e:
                error_msg = f"处理标的 {symbol} 失败: {str(e)}"
                logger.error(error_msg)
                result['errors'].append(error_msg)

        return result

    def _process_buy(self, trade: Dict, current_position: Dict):
        """处理买入交易"""
        symbol = trade['symbol']
        old_quantity = current_position.get('total_quantity', 0)
        old_avg_cost = current_position.get('avg_cost', 0)
        old_total_cost = old_quantity * old_avg_cost

        # 计算新的持仓和成本
        new_quantity = old_quantity + trade['quantity']
        new_total_cost = old_total_cost + trade['amount'] + trade['commission']
        new_avg_cost = new_total_cost / new_quantity if new_quantity > 0 else 0

        # 更新持仓信息
        current_position.update({
            'symbol': symbol,
            'security_name': trade.get('security_name', ''),
            'security_type': trade.get('security_type', 'UNKNOWN'),
            'total_quantity': new_quantity,
            'avg_cost': new_avg_cost,
            'total_cost': new_total_cost,
            'last_trade_date': trade['trade_date'],
            'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

        logger.debug(f"买入处理完成 {symbol}: 数量={new_quantity}, 均价={new_avg_cost:.4f}")

    def _process_sell(self, trade: Dict, current_position: Dict, open_buy_trades: List[Dict]) -> int:
        """
        处理卖出交易，使用FIFO算法

        Returns:
            生成的已平仓记录数量
        """
        symbol = trade['symbol']
        sell_quantity = trade['quantity']
        remaining_sell_qty = sell_quantity
        closed_count = 0

        logger.info(f"处理卖出 {symbol}: 数量={sell_quantity}")

        # 检查是否有足够持仓
        if current_position.get('total_quantity', 0) < sell_quantity:
            logger.warning(f"卖出数量超过持仓 {symbol}: 持仓={current_position.get('total_quantity', 0)}, 卖出={sell_quantity}")
            # 仍然处理，但标记警告
            remaining_sell_qty = current_position.get('total_quantity', 0)

        # FIFO配对
        for buy_trade in open_buy_trades[:]:
            if remaining_sell_qty <= 0:
                break

            buy_remaining = buy_trade.get('remaining_quantity', buy_trade['quantity'])
            if buy_remaining <= 0:
                continue

            # 计算本次配对数量
            match_qty = min(remaining_sell_qty, buy_remaining)

            # 创建已平仓记录
            closed_position = self._create_closed_position(buy_trade, trade, match_qty)
            self.storage.insert_closed_position(closed_position)
            closed_count += 1

            # 更新买入交易的剩余数量
            buy_trade['remaining_quantity'] = buy_remaining - match_qty

            # 更新卖出交易的剩余数量
            remaining_sell_qty -= match_qty

            logger.debug(f"FIFO配对 {symbol}: 配对数量={match_qty}, 剩余卖出={remaining_sell_qty}")

        # 更新持仓
        old_quantity = current_position.get('total_quantity', 0)
        new_quantity = old_quantity - sell_quantity
        current_position['total_quantity'] = max(0, new_quantity)
        current_position['last_trade_date'] = trade['trade_date']
        current_position['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 如果持仓为0，清空成本信息
        if current_position['total_quantity'] == 0:
            current_position['avg_cost'] = 0
            current_position['total_cost'] = 0

        logger.info(f"卖出处理完成 {symbol}: 剩余持仓={current_position['total_quantity']}")

        return closed_count

    def _create_closed_position(self, buy_trade: Dict, sell_trade: Dict, quantity: float) -> Dict:
        """创建已平仓记录"""
        symbol = buy_trade['symbol']

        # 计算持有天数
        holding_days = 0
        try:
            buy_date = datetime.strptime(buy_trade['trade_date'], '%Y-%m-%d')
            sell_date = datetime.strptime(sell_trade['trade_date'], '%Y-%m-%d')
            holding_days = (sell_date - buy_date).days
        except ValueError:
            pass

        # 按比例分摊手续费
        buy_commission = (buy_trade['commission'] / buy_trade['quantity']) * quantity
        sell_commission = (sell_trade['commission'] / sell_trade['quantity']) * quantity
        total_commission = buy_commission + sell_commission

        # 计算成本和收益
        total_cost = quantity * buy_trade['price'] + buy_commission
        total_revenue = quantity * sell_trade['price'] - sell_commission
        net_pnl = total_revenue - total_cost
        pnl_pct = (net_pnl / total_cost) * 100 if total_cost > 0 else 0

        return {
            'symbol': symbol,
            'security_name': buy_trade.get('security_name', ''),
            'open_date': buy_trade['trade_date'],
            'close_date': sell_trade['trade_date'],
            'holding_days': holding_days,
            'quantity': quantity,
            'open_price': buy_trade['price'],
            'close_price': sell_trade['price'],
            'total_cost': total_cost,
            'total_revenue': total_revenue,
            'commission': total_commission,
            'net_pnl': net_pnl,
            'pnl_pct': pnl_pct,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    def _get_current_position(self, symbol: str) -> Dict:
        """获取当前持仓信息"""
        positions = self.storage.get_open_positions()
        for pos in positions:
            if pos['symbol'] == symbol:
                return pos.copy()
        return {
            'symbol': symbol,
            'total_quantity': 0,
            'avg_cost': 0,
            'total_cost': 0
        }

    def _get_open_buy_trades(self, symbol: str) -> List[Dict]:
        """获取未完全配对的买入记录"""
        trades = self.storage.get_trades_by_symbol(symbol)
        open_trades = []

        for trade in trades:
            if trade['action'] == 'BUY':
                # 计算剩余未配对数量
                closed_qty = self._get_closed_quantity_by_trade(trade)
                remaining_qty = trade['quantity'] - closed_qty

                if remaining_qty > 0:
                    trade_copy = trade.copy()
                    trade_copy['remaining_quantity'] = remaining_qty
                    open_trades.append(trade_copy)

        # 按日期排序（FIFO）
        open_trades.sort(key=lambda x: (x['trade_date'], x['trade_time']))
        return open_trades

    def _get_closed_quantity_by_trade(self, trade: Dict) -> float:
        """计算某笔买入交易已平仓的数量"""
        # 这里需要查询closed_positions表，计算与该笔买入相关的平仓数量
        # 简化实现，实际应该更精确
        return 0.0

    def calculate_daily_summary(self, date: str) -> Dict:
        """计算每日汇总统计"""
        try:
            # 获取当日交易
            trades = self.storage.get_trades_by_date(date)

            if not trades:
                return self._empty_daily_summary(date)

            # 基础统计
            total_trades = len(trades)
            buy_trades = len([t for t in trades if t['action'] == 'BUY'])
            sell_trades = len([t for t in trades if t['action'] == 'SELL'])

            total_volume = sum(t['amount'] for t in trades)
            total_commission = sum(t['commission'] for t in trades)

            # 盈亏统计
            closed_positions = self.storage.get_closed_positions_by_date(date)
            winning_trades = [cp for cp in closed_positions if cp['net_pnl'] > 0]
            losing_trades = [cp for cp in closed_positions if cp['net_pnl'] < 0]

            realized_pnl = sum(cp['net_pnl'] for cp in closed_positions)
            win_rate = (len(winning_trades) / len(closed_positions) * 100) if closed_positions else 0

            largest_profit = max((cp['net_pnl'] for cp in winning_trades), default=0)
            largest_loss = min((cp['net_pnl'] for cp in losing_trades), default=0)

            avg_profit = sum(cp['net_pnl'] for cp in winning_trades) / len(winning_trades) if winning_trades else 0
            avg_loss = sum(cp['net_pnl'] for cp in losing_trades) / len(losing_trades) if losing_trades else 0

            profit_factor = abs(avg_profit / avg_loss) if avg_loss != 0 else 0

            summary = {
                'summary_date': date,
                'total_trades': total_trades,
                'buy_trades': buy_trades,
                'sell_trades': sell_trades,
                'total_volume': total_volume,
                'total_commission': total_commission,
                'realized_pnl': realized_pnl,
                'winning_trades': len(winning_trades),
                'losing_trades': len(losing_trades),
                'win_rate': win_rate,
                'largest_profit': largest_profit,
                'largest_loss': largest_loss,
                'avg_profit': avg_profit,
                'avg_loss': avg_loss,
                'profit_factor': profit_factor,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            return summary

        except Exception as e:
            logger.error(f"计算每日汇总失败 {date}: {str(e)}")
            return self._empty_daily_summary(date)

    def _empty_daily_summary(self, date: str) -> Dict:
        """返回空的每日汇总结构"""
        return {
            'summary_date': date,
            'total_trades': 0,
            'buy_trades': 0,
            'sell_trades': 0,
            'total_volume': 0,
            'total_commission': 0,
            'realized_pnl': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0,
            'largest_profit': 0,
            'largest_loss': 0,
            'avg_profit': 0,
            'avg_loss': 0,
            'profit_factor': 0,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }