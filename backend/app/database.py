"""
数据库模型和适配器
"""
import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class TradeRecord:
    """交易记录数据模型"""

    def __init__(self, **kwargs):
        # 基础字段
        self.id = kwargs.get('id')
        self.trade_date = kwargs.get('trade_date', '')
        self.trade_time = kwargs.get('trade_time', '')
        self.symbol = kwargs.get('symbol', '')
        self.security_name = kwargs.get('security_name', '')
        self.security_type = kwargs.get('security_type', 'STOCK')
        self.action = kwargs.get('action', '')  # BUY/SELL

        # 数量和价格
        self.quantity = float(kwargs.get('quantity', 0))
        self.price = float(kwargs.get('price', 0))
        self.amount = float(kwargs.get('amount', 0))
        self.commission = float(kwargs.get('commission', 0))
        self.net_amount = float(kwargs.get('net_amount', 0))

        # 期权特定字段
        self.underlying_symbol = kwargs.get('underlying_symbol', '')
        self.strike_price = float(kwargs.get('strike_price', 0))
        self.expiration_date = kwargs.get('expiration_date', '')
        self.option_type = kwargs.get('option_type', '')

        # 扩展字段（来自郑兄Excel格式）
        self.source = kwargs.get('source', '')  # 消息来源
        self.close_date = kwargs.get('close_date', '')  # 平仓日期
        self.close_price = float(kwargs.get('close_price', 0))  # 平仓价格
        self.close_quantity = float(kwargs.get('close_quantity', 0))  # 平仓数量
        self.close_reason = kwargs.get('close_reason', '')  # 平仓理由
        self.trade_rating = float(kwargs.get('trade_rating', 0))  # 交易评分
        self.trade_type = kwargs.get('trade_type', '')  # 交易类型
        self.notes = kwargs.get('notes', '')  # 笔记

        # 元数据
        self.broker = kwargs.get('broker', '')
        self.account_id = kwargs.get('account_id', '')
        self.source_file = kwargs.get('source_file', '')
        self.import_time = kwargs.get('import_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        self.created_at = kwargs.get('created_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        self.updated_at = kwargs.get('updated_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'trade_date': self.trade_date,
            'trade_time': self.trade_time,
            'symbol': self.symbol,
            'security_name': self.security_name,
            'security_type': self.security_type,
            'action': self.action,
            'quantity': self.quantity,
            'price': self.price,
            'amount': self.amount,
            'commission': self.commission,
            'net_amount': self.net_amount,
            'underlying_symbol': self.underlying_symbol,
            'strike_price': self.strike_price,
            'expiration_date': self.expiration_date,
            'option_type': self.option_type,
            'source': self.source,
            'close_date': self.close_date,
            'close_price': self.close_price,
            'close_quantity': self.close_quantity,
            'close_reason': self.close_reason,
            'trade_rating': self.trade_rating,
            'trade_type': self.trade_type,
            'notes': self.notes,
            'broker': self.broker,
            'account_id': self.account_id,
            'source_file': self.source_file,
            'import_time': self.import_time,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TradeRecord':
        """从字典创建实例"""
        return cls(**data)

class DatabaseAdapter:
    """数据库适配器基类"""

    def save_trades(self, trades: List[TradeRecord]) -> bool:
        """保存交易记录"""
        raise NotImplementedError

    def get_trades(self, limit: Optional[int] = None,
                   filters: Optional[Dict] = None) -> List[TradeRecord]:
        """获取交易记录"""
        raise NotImplementedError

    def update_trade(self, trade_id: int, updates: Dict) -> bool:
        """更新交易记录"""
        raise NotImplementedError

    def delete_trade(self, trade_id: int) -> bool:
        """删除交易记录"""
        raise NotImplementedError

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        raise NotImplementedError

class SQLiteAdapter(DatabaseAdapter):
    """SQLite数据库适配器"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """初始化数据库表"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 创建交易记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trade_date TEXT NOT NULL,
                    trade_time TEXT,
                    symbol TEXT NOT NULL,
                    security_name TEXT,
                    security_type TEXT DEFAULT 'STOCK',
                    action TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    price REAL NOT NULL,
                    amount REAL NOT NULL,
                    commission REAL DEFAULT 0,
                    net_amount REAL NOT NULL,
                    underlying_symbol TEXT,
                    strike_price REAL DEFAULT 0,
                    expiration_date TEXT,
                    option_type TEXT,
                    source TEXT,
                    close_date TEXT,
                    close_price REAL DEFAULT 0,
                    close_quantity REAL DEFAULT 0,
                    close_reason TEXT,
                    trade_rating REAL DEFAULT 0,
                    trade_type TEXT,
                    notes TEXT,
                    broker TEXT,
                    account_id TEXT,
                    source_file TEXT,
                    import_time TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            ''')

            # 创建索引
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_symbol ON trades(symbol)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_trade_date ON trades(trade_date)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_security_type ON trades(security_type)
            ''')

            conn.commit()
            logger.info("SQLite数据库初始化完成")

    @contextmanager
    def get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def save_trades(self, trades: List[TradeRecord]) -> bool:
        """保存交易记录"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                for trade in trades:
                    # 检查是否已存在相同记录（避免重复导入）
                    cursor.execute('''
                        SELECT id FROM trades
                        WHERE trade_date = ? AND trade_time = ? AND symbol = ?
                        AND action = ? AND quantity = ? AND price = ?
                        LIMIT 1
                    ''', (trade.trade_date, trade.trade_time, trade.symbol,
                          trade.action, trade.quantity, trade.price))

                    if cursor.fetchone():
                        logger.debug(f"跳过重复记录: {trade.symbol} {trade.trade_date}")
                        continue

                    # 插入新记录
                    cursor.execute('''
                        INSERT INTO trades (
                            trade_date, trade_time, symbol, security_name, security_type,
                            action, quantity, price, amount, commission, net_amount,
                            underlying_symbol, strike_price, expiration_date, option_type,
                            source, close_date, close_price, close_quantity, close_reason,
                            trade_rating, trade_type, notes, broker, account_id,
                            source_file, import_time, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        trade.trade_date, trade.trade_time, trade.symbol, trade.security_name,
                        trade.security_type, trade.action, trade.quantity, trade.price,
                        trade.amount, trade.commission, trade.net_amount,
                        trade.underlying_symbol, trade.strike_price, trade.expiration_date,
                        trade.option_type, trade.source, trade.close_date, trade.close_price,
                        trade.close_quantity, trade.close_reason, trade.trade_rating,
                        trade.trade_type, trade.notes, trade.broker, trade.account_id,
                        trade.source_file, trade.import_time, trade.created_at, trade.updated_at
                    ))

                conn.commit()
                logger.info(f"成功保存 {len(trades)} 条交易记录")
                return True

        except Exception as e:
            logger.error(f"保存交易记录失败: {e}")
            return False

    def get_trades(self, limit: Optional[int] = None,
                   filters: Optional[Dict] = None) -> List[TradeRecord]:
        """获取交易记录"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                query = "SELECT * FROM trades WHERE 1=1"
                params = []

                # 添加过滤条件
                if filters:
                    if 'symbol' in filters:
                        query += " AND symbol = ?"
                        params.append(filters['symbol'])
                    if 'security_type' in filters:
                        query += " AND security_type = ?"
                        params.append(filters['security_type'])
                    if 'start_date' in filters:
                        query += " AND trade_date >= ?"
                        params.append(filters['start_date'])
                    if 'end_date' in filters:
                        query += " AND trade_date <= ?"
                        params.append(filters['end_date'])

                query += " ORDER BY trade_date DESC, trade_time DESC"

                if limit:
                    query += " LIMIT ?"
                    params.append(limit)

                cursor.execute(query, params)
                rows = cursor.fetchall()

                trades = []
                for row in rows:
                    trade_data = dict(row)
                    trades.append(TradeRecord.from_dict(trade_data))

                return trades

        except Exception as e:
            logger.error(f"获取交易记录失败: {e}")
            return []

    def update_trade(self, trade_id: int, updates: Dict) -> bool:
        """更新交易记录"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # 添加更新时间
                updates['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                # 构建更新语句
                set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
                params = list(updates.values()) + [trade_id]

                cursor.execute(f'''
                    UPDATE trades SET {set_clause} WHERE id = ?
                ''', params)

                conn.commit()
                logger.info(f"更新交易记录 {trade_id} 成功")
                return True

        except Exception as e:
            logger.error(f"更新交易记录失败: {e}")
            return False

    def delete_trade(self, trade_id: int) -> bool:
        """删除交易记录"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM trades WHERE id = ?", (trade_id,))
                conn.commit()
                logger.info(f"删除交易记录 {trade_id} 成功")
                return True
        except Exception as e:
            logger.error(f"删除交易记录失败: {e}")
            return False

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # 基础统计
                cursor.execute("SELECT COUNT(*) FROM trades")
                total_trades = cursor.fetchone()[0]

                cursor.execute('''
                    SELECT
                        SUM(CASE WHEN action = 'BUY' THEN 1 ELSE 0 END) as buy_count,
                        SUM(CASE WHEN action = 'SELL' THEN 1 ELSE 0 END) as sell_count,
                        SUM(amount) as total_amount,
                        SUM(commission) as total_commission,
                        AVG(trade_rating) as avg_rating
                    FROM trades
                ''')
                stats = cursor.fetchone()

                # 期权统计
                cursor.execute('''
                    SELECT COUNT(*) FROM trades WHERE security_type = 'OPTION'
                ''')
                option_trades = cursor.fetchone()[0]

                return {
                    'total_trades': total_trades,
                    'buy_trades': stats[0] or 0,
                    'sell_trades': stats[1] or 0,
                    'total_amount': stats[2] or 0,
                    'total_commission': stats[3] or 0,
                    'average_rating': stats[4] or 0,
                    'option_trades': option_trades,
                    'stock_trades': total_trades - option_trades
                }

        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {}