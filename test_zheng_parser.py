#!/usr/bin/env python3
"""
测试郑兄格式解析器
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.parser import ExcelParser
from app.database import TradeRecord

def test_zheng_parser():
    """测试郑兄格式解析器"""
    print("郑兄格式解析器测试")
    print("=" * 50)

    # 创建解析器
    parser = ExcelParser()

    # 解析文件
    file_path = '/Users/edwin/Downloads/郑兄长期权策略.xlsx'
    print(f"解析文件: {file_path}")

    try:
        trades_data = parser.parse_file(file_path)
        print(f"解析成功，共 {len(trades_data)} 条记录")

        # 显示前几条记录
        print("\n前3条记录详情:")
        for i, trade_data in enumerate(trades_data[:3]):
            print(f"\n记录 {i+1}:")
            trade = TradeRecord.from_dict(trade_data)
            print(f"  代码: {trade.symbol}")
            print(f"  日期: {trade.trade_date}")
            print(f"  操作: {trade.action}")
            print(f"  数量: {trade.quantity}")
            print(f"  价格: ${trade.price}")
            print(f"  证券类型: {trade.security_type}")
            print(f"  期权类型: {trade.option_type}")
            print(f"  行权价: ${trade.strike_price}")
            print(f"  到期日: {trade.expiration_date}")
            print(f"  消息来源: {trade.source}")
            print(f"  平仓理由: {trade.close_reason}")
            print(f"  交易评分: {trade.trade_rating}")

        # 统计信息
        print(f"\n统计信息:")
        option_trades = [t for t in trades_data if t.get('security_type') == 'OPTION']
        stock_trades = [t for t in trades_data if t.get('security_type') == 'STOCK']
        print(f"期权交易: {len(option_trades)} 条")
        print(f"股票交易: {len(stock_trades)} 条")
        print(f"有评分的交易: {len([t for t in trades_data if t.get('trade_rating', 0) > 0])} 条")
        print(f"有平仓记录的交易: {len([t for t in trades_data if t.get('close_date')])} 条")

    except Exception as e:
        print(f"解析失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_zheng_parser()