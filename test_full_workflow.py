#!/usr/bin/env python3
"""
测试完整工作流程
"""
import sys
import os
import time
import requests
from pathlib import Path

# 添加backend目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_api_workflow():
    """测试API工作流程"""
    print("测试完整工作流程")
    print("=" * 50)

    # API基础URL
    base_url = "http://localhost:5002/api"

    try:
        # 1. 健康检查
        print("1. 健康检查...")
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("   ✓ API服务器运行正常")
        else:
            print(f"   ✗ API服务器响应异常: {response.status_code}")
            return False

        # 2. 获取统计信息（初始状态）
        print("2. 获取初始统计信息...")
        response = requests.get(f"{base_url}/statistics", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            print(f"   ✓ 总交易数: {stats.get('total_trades', 0)}")
        else:
            print(f"   ✗ 获取统计信息失败: {response.status_code}")

        # 3. 创建测试交易记录
        print("3. 创建测试交易记录...")
        test_trade = {
            "trade_date": "2025-01-03",
            "trade_time": "10:00:00",
            "symbol": "AAPL",
            "security_name": "Apple Inc.",
            "security_type": "STOCK",
            "action": "BUY",
            "quantity": 100,
            "price": 150.0,
            "amount": 15000.0,
            "commission": 10.0,
            "source": "📊技术分析",
            "trade_rating": 4.0,
            "trade_type": "短线交易",
            "notes": "测试交易记录",
            "broker": "测试券商"
        }

        response = requests.post(f"{base_url}/trades", json=test_trade, timeout=5)
        if response.status_code == 201:
            trade_data = response.json()
            trade_id = trade_data['trade']['id']
            print(f"   ✓ 成功创建交易记录，ID: {trade_id}")
        else:
            print(f"   ✗ 创建交易记录失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return False

        # 4. 创建期权交易记录
        print("4. 创建期权交易记录...")
        option_trade = {
            "trade_date": "2025-01-03",
            "trade_time": "10:30:00",
            "symbol": "TSLA250117C150",
            "security_name": "TSLA Call 150 2025-01-17",
            "security_type": "OPTION",
            "action": "BUY",
            "quantity": 1,
            "price": 5.50,
            "amount": 550.0,
            "commission": 1.0,
            "underlying_symbol": "TSLA",
            "strike_price": 150.0,
            "expiration_date": "2025-01-17",
            "option_type": "CALL",
            "source": "🐳巨鲸",
            "trade_rating": 5.0,
            "close_date": "2025-01-05",
            "close_price": 8.25,
            "close_quantity": 1,
            "close_reason": "✅止盈",
            "broker": "测试券商"
        }

        response = requests.post(f"{base_url}/trades", json=option_trade, timeout=5)
        if response.status_code == 201:
            option_data = response.json()
            option_id = option_data['trade']['id']
            print(f"   ✓ 成功创建期权交易记录，ID: {option_id}")
        else:
            print(f"   ✗ 创建期权交易记录失败: {response.status_code}")
            print(f"   错误信息: {response.text}")

        # 5. 获取交易列表
        print("5. 获取交易列表...")
        response = requests.get(f"{base_url}/trades", timeout=5)
        if response.status_code == 200:
            trades_data = response.json()
            print(f"   ✓ 获取到 {len(trades_data['trades'])} 条交易记录")
        else:
            print(f"   ✗ 获取交易列表失败: {response.status_code}")

        # 6. 更新交易记录
        print("6. 更新交易记录...")
        update_data = {
            "notes": "更新后的测试笔记",
            "trade_rating": 3.5
        }
        response = requests.put(f"{base_url}/trades/{trade_id}", json=update_data, timeout=5)
        if response.status_code == 200:
            print("   ✓ 交易记录更新成功")
        else:
            print(f"   ✗ 更新交易记录失败: {response.status_code}")

        # 7. 获取更新后的统计信息
        print("7. 获取更新后的统计信息...")
        response = requests.get(f"{base_url}/statistics", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            print(f"   ✓ 总交易数: {stats.get('total_trades', 0)}")
            print(f"   ✓ 股票交易: {stats.get('stock_trades', 0)}")
            print(f"   ✓ 期权交易: {stats.get('option_trades', 0)}")
            print(f"   ✓ 平均评分: {stats.get('average_rating', 0):.1f}")
        else:
            print(f"   ✗ 获取统计信息失败: {response.status_code}")

        print("\n✅ API工作流程测试完成！")
        return True

    except requests.exceptions.ConnectionError:
        print("   ✗ 无法连接到API服务器")
        print("   请确保API服务器正在运行: python backend/app/api_server.py")
        return False
    except Exception as e:
        print(f"   ✗ 测试过程中发生错误: {str(e)}")
        return False

def test_excel_import():
    """测试Excel导入功能"""
    print("\n测试Excel导入功能")
    print("=" * 50)

    base_url = "http://localhost:5002/api"
    excel_path = "/Users/edwin/Downloads/郑兄长期权策略.xlsx"

    try:
        # 检查Excel文件是否存在
        if not os.path.exists(excel_path):
            print(f"   ✗ Excel文件不存在: {excel_path}")
            return False

        print(f"   ✓ 找到Excel文件: {excel_path}")

        # 上传Excel文件
        print("   上传Excel文件...")
        with open(excel_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{base_url}/import", files=files, timeout=30)

        if response.status_code == 200:
            result = response.json()
            print(f"   ✓ 成功导入 {result['trades_count']} 条交易记录")
            print(f"   ✓ 消息: {result['message']}")
            return True
        else:
            print(f"   ✗ 导入失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print("   ✗ 无法连接到API服务器")
        return False
    except Exception as e:
        print(f"   ✗ 导入过程中发生错误: {str(e)}")
        return False

def main():
    """主函数"""
    print("交易记录管理系统 - 完整工作流程测试")
    print("=" * 60)

    # 检查API服务器是否运行
    try:
        response = requests.get("http://localhost:5002/api/health", timeout=2)
        if response.status_code != 200:
            print("❌ API服务器未正常运行，请先启动: python backend/app/api_server.py")
            return
        print("✅ API服务器运行正常")
    except:
        print("❌ 无法连接到API服务器，请先启动: python backend/app/api_server.py")
        return

    # 测试API工作流程
    api_success = test_api_workflow()

    # 测试Excel导入
    excel_success = test_excel_import()

    # 总结
    print("\n" + "=" * 60)
    print("测试总结:")
    print(f"API工作流程: {'✅ 通过' if api_success else '❌ 失败'}")
    print(f"Excel导入: {'✅ 通过' if excel_success else '❌ 失败'}")

    if api_success and excel_success:
        print("\n🎉 所有测试通过！系统可以正常使用。")
        print("\n启动前端应用:")
        print("cd frontend && npm install && npm run dev")
        print("\n然后访问: http://localhost:5173")
    else:
        print("\n❌ 部分测试失败，请检查系统配置。")

if __name__ == '__main__':
    main()