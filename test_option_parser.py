#!/usr/bin/env python3
"""
测试期权解析器
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.option_parser import parse_symbol, is_option_symbol

def test_option_parser():
    """测试期权解析器"""
    print("期权解析器测试")
    print("=" * 50)

    # 测试紧凑格式
    print("\n1. 测试紧凑格式 (AVGO0919C):")
    result = parse_symbol("AVGO0919C")
    print(f"解析结果: {result}")
    print(f"是否期权: {is_option_symbol('AVGO0919C')}")

    # 测试Excel分离格式
    print("\n2. 测试Excel分离格式 (ABAT):")
    result = parse_symbol("ABAT", strike_price=6.0, expiration_date="2025-12-19", option_type="CALL")
    print(f"解析结果: {result}")
    print(f"是否期权: {is_option_symbol('ABAT', 6.0, 'CALL')}")

    # 测试股票格式
    print("\n3. 测试股票格式 (AAPL):")
    result = parse_symbol("AAPL")
    print(f"解析结果: {result}")
    print(f"是否期权: {is_option_symbol('AAPL')}")

    # 测试多种格式
    test_cases = [
        ("AVGO0919C", None, None, None),
        ("TSLA1220P", None, None, None),
        ("MSFT", 250.0, "2025-12-20", "PUT"),
        ("GOOGL", 150.0, "2025/10/17", "CALL"),
    ]

    print("\n4. 批量测试:")
    for symbol, strike, exp_date, opt_type in test_cases:
        result = parse_symbol(symbol, strike, exp_date, opt_type)
        is_opt = is_option_symbol(symbol, strike, opt_type)
        print(f"{symbol:15s} -> {result.format_type:8s} | 期权: {is_opt}")

if __name__ == '__main__':
    test_option_parser()