"""
Web API服务 - 为Dashboard提供数据接口
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
from app.config import Config
from app.google_sheets_adapter import GoogleSheetsAdapter

logger = logging.getLogger(__name__)

def create_app():
    """创建Flask应用"""
    app = Flask(__name__)
    CORS(app)  # 允许跨域请求

    # 初始化数据存储
    storage = Config.get_storage_adapter()

    @app.route('/')
    def dashboard():
        """主Dashboard页面"""
        html_template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>投资交易复盘分析系统</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }

        .header {
            text-align: center;
            margin-bottom: 40px;
        }

        .header h1 {
            color: #2c3e50;
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .header p {
            color: #7f8c8d;
            font-size: 1.1em;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }

        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }

        .stat-card:hover {
            transform: translateY(-5px);
        }

        .stat-card.profit {
            background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
        }

        .stat-card.loss {
            background: linear-gradient(135deg, #c0392b 0%, #e74c3c 100%);
        }

        .stat-card h3 {
            font-size: 1.2em;
            margin-bottom: 10px;
            opacity: 0.9;
        }

        .stat-card .value {
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 5px;
        }

        .stat-card .change {
            font-size: 0.9em;
            opacity: 0.8;
        }

        .charts-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 40px;
        }

        .chart-card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }

        .chart-card h3 {
            color: #2c3e50;
            margin-bottom: 20px;
            font-size: 1.3em;
        }

        .chart-container {
            position: relative;
            height: 300px;
        }

        .full-width {
            grid-column: 1 / -1;
        }

        .loading {
            text-align: center;
            padding: 40px;
            color: #7f8c8d;
        }

        .error {
            background: #fee;
            color: #c33;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
        }

        .last-updated {
            text-align: center;
            color: #7f8c8d;
            margin-top: 30px;
            font-size: 0.9em;
        }

        @media (max-width: 768px) {
            .charts-container {
                grid-template-columns: 1fr;
            }

            .container {
                padding: 20px;
            }

            .header h1 {
                font-size: 2em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📈 投资交易复盘分析系统</h1>
            <p>数据驱动的投资决策助手</p>
        </div>

        <div id="loading" class="loading">
            <p>正在加载数据...</p>
        </div>

        <div id="error-message" class="error" style="display: none;"></div>

        <div id="dashboard-content" style="display: none;">
            <!-- 统计卡片 -->
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>总交易次数</h3>
                    <div class="value" id="total-trades">-</div>
                    <div class="change">累计交易</div>
                </div>

                <div class="stat-card" id="pnl-card">
                    <h3>总盈亏</h3>
                    <div class="value" id="total-pnl">-</div>
                    <div class="change" id="pnl-change">已实现盈亏</div>
                </div>

                <div class="stat-card">
                    <h3>胜率</h3>
                    <div class="value" id="win-rate">-</div>
                    <div class="change">盈利交易占比</div>
                </div>

                <div class="stat-card">
                    <h3>当前持仓</h3>
                    <div class="value" id="positions">-</div>
                    <div class="change">持仓标的数</div>
                </div>
            </div>

            <!-- 图表区域 -->
            <div class="charts-container">
                <div class="chart-card full-width">
                    <h3>📊 每日盈亏趋势</h3>
                    <div class="chart-container">
                        <canvas id="pnl-chart"></canvas>
                    </div>
                </div>

                <div class="chart-card">
                    <h3>🏆 盈利TOP5</h3>
                    <div class="chart-container">
                        <canvas id="top-profits-chart"></canvas>
                    </div>
                </div>

                <div class="chart-card">
                    <h3>📉 亏损TOP5</h3>
                    <div class="chart-container">
                        <canvas id="top-losses-chart"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <div class="last-updated" id="last-updated">
            最后更新: -
        </div>
    </div>

    <script>
        // 全局变量
        let charts = {};

        // 格式化货币
        function formatCurrency(amount) {
            const absAmount = Math.abs(amount);
            const formatted = absAmount.toLocaleString('zh-CN', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
            return amount >= 0 ? `+¥${formatted}` : `-¥${formatted}`;
        }

        // 格式化百分比
        function formatPercentage(value) {
            return `${value.toFixed(1)}%`;
        }

        // 获取数据
        async function fetchDashboardData() {
            try {
                const response = await fetch('/api/dashboard');
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                return data;
            } catch (error) {
                console.error('获取数据失败:', error);
                throw error;
            }
        }

        // 更新统计卡片
        function updateStatsCards(data) {
            const totalPnl = data.overview.total_pnl || 0;
            const pnlCard = document.getElementById('pnl-card');

            document.getElementById('total-trades').textContent = data.overview.total_trades || 0;
            document.getElementById('total-pnl').textContent = formatCurrency(totalPnl);
            document.getElementById('win-rate').textContent = formatPercentage(data.overview.win_rate || 0);
            document.getElementById('positions').textContent = data.overview.positions_count || 0;

            // 根据盈亏设置颜色
            if (totalPnl > 0) {
                pnlCard.className = 'stat-card profit';
            } else if (totalPnl < 0) {
                pnlCard.className = 'stat-card loss';
            } else {
                pnlCard.className = 'stat-card';
            }
        }

        // 创建盈亏趋势图
        function createPnlChart(data) {
            const ctx = document.getElementById('pnl-chart').getContext('2d');

            if (charts.pnlChart) {
                charts.pnlChart.destroy();
            }

            const dailyData = data.daily_trend || [];
            const labels = dailyData.map(item => item.date);
            const pnlData = dailyData.map(item => item.pnl);
            const cumulativeData = [];
            let cumulative = 0;

            pnlData.forEach(pnl => {
                cumulative += pnl;
                cumulativeData.push(cumulative);
            });

            charts.pnlChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: '每日盈亏',
                        data: pnlData,
                        backgroundColor: pnlData.map(value => value >= 0 ? '#27ae60' : '#e74c3c'),
                        borderColor: pnlData.map(value => value >= 0 ? '#27ae60' : '#e74c3c'),
                        borderWidth: 1,
                        yAxisID: 'y',
                        order: 2
                    }, {
                        label: '累计盈亏',
                        data: cumulativeData,
                        type: 'line',
                        borderColor: '#3498db',
                        backgroundColor: 'rgba(52, 152, 219, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        yAxisID: 'y',
                        order: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {
                        mode: 'index',
                        intersect: false,
                    },
                    scales: {
                        x: {
                            grid: {
                                display: false
                            }
                        },
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return formatCurrency(value);
                                }
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top'
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    let label = context.dataset.label || '';
                                    if (label) {
                                        label += ': ';
                                    }
                                    label += formatCurrency(context.parsed.y);
                                    return label;
                                }
                            }
                        }
                    }
                }
            });
        }

        // 创建TOP图表
        function createTopChart(chartId, data, label, color) {
            const ctx = document.getElementById(chartId).getContext('2d');

            if (charts[chartId]) {
                charts[chartId].destroy();
            }

            charts[chartId] = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.map(item => item.symbol),
                    datasets: [{
                        label: label,
                        data: data.map(item => item.pnl),
                        backgroundColor: color,
                        borderColor: color,
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    indexAxis: 'y',
                    scales: {
                        x: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return formatCurrency(value);
                                }
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const item = data[context.dataIndex];
                                    return [
                                        `盈亏: ${formatCurrency(item.pnl)}`,
                                        `收益率: ${formatPercentage(item.return_rate)}`
                                    ];
                                }
                            }
                        }
                    }
                }
            });
        }

        // 更新图表
        function updateCharts(data) {
            createPnlChart(data);
            createTopChart('top-profits-chart', data.top_profits || [], '盈利', '#27ae60');
            createTopChart('top-losses-chart', data.top_losses || [], '亏损', '#e74c3c');
        }

        // 更新最后更新时间
        function updateLastUpdated() {
            const now = new Date();
            document.getElementById('last-updated').textContent =
                `最后更新: ${now.toLocaleString('zh-CN')}`;
        }

        // 显示错误信息
        function showError(message) {
            const errorElement = document.getElementById('error-message');
            errorElement.textContent = `错误: ${message}`;
            errorElement.style.display = 'block';
            document.getElementById('loading').style.display = 'none';
        }

        // 主函数
        async function initDashboard() {
            try {
                // 显示加载状态
                document.getElementById('loading').style.display = 'block';
                document.getElementById('dashboard-content').style.display = 'none';
                document.getElementById('error-message').style.display = 'none';

                // 获取数据
                const data = await fetchDashboardData();

                // 更新界面
                updateStatsCards(data);
                updateCharts(data);
                updateLastUpdated();

                // 显示内容
                document.getElementById('loading').style.display = 'none';
                document.getElementById('dashboard-content').style.display = 'block';

            } catch (error) {
                console.error('初始化Dashboard失败:', error);
                showError(`加载数据失败: ${error.message}`);
            }
        }

        // 页面加载完成后初始化
        document.addEventListener('DOMContentLoaded', initDashboard);

        // 每5分钟自动刷新
        setInterval(initDashboard, 5 * 60 * 1000);
    </script>
</body>
</html>
        """
        return render_template_string(html_template)

    @app.route('/api/dashboard')
    def get_dashboard_data():
        """获取Dashboard数据"""
        try:
            # 获取基础统计
            all_trades = storage.get_all_trades()
            positions = storage.get_open_positions()
            closed_positions = storage.get_all_closed_positions()

            # 计算基础指标
            total_trades = len(all_trades)
            total_pnl = sum(float(pos.get('net_pnl', 0)) for pos in closed_positions)
            positions_count = len([p for p in positions if float(p.get('total_quantity', 0)) > 0])

            # 计算胜率
            winning_trades = len([cp for cp in closed_positions if float(cp.get('net_pnl', 0)) > 0])
            losing_trades = len([cp for cp in closed_positions if float(cp.get('net_pnl', 0)) < 0])
            win_rate = (winning_trades / len(closed_positions) * 100) if closed_positions else 0

            # 每日盈亏趋势
            daily_pnl = {}
            for trade in all_trades:
                date = trade.get('trade_date', '')
                if date:
                    if date not in daily_pnl:
                        daily_pnl[date] = 0

            for cp in closed_positions:
                date = cp.get('close_date', '')
                pnl = float(cp.get('net_pnl', 0))
                if date in daily_pnl:
                    daily_pnl[date] += pnl

            # 排序并格式化每日数据
            sorted_dates = sorted(daily_pnl.keys())
            daily_trend = [{'date': date, 'pnl': daily_pnl[date]} for date in sorted_dates[-30:]]  # 最近30天

            # 盈利TOP5
            profits_by_symbol = {}
            for cp in closed_positions:
                symbol = cp.get('symbol', '')
                pnl = float(cp.get('net_pnl', 0))
                if pnl > 0:
                    if symbol not in profits_by_symbol:
                        profits_by_symbol[symbol] = {'pnl': 0, 'trades': 0, 'total_cost': 0}
                    profits_by_symbol[symbol]['pnl'] += pnl
                    profits_by_symbol[symbol]['trades'] += 1
                    profits_by_symbol[symbol]['total_cost'] += float(cp.get('total_cost', 0))

            top_profits = []
            for symbol, data in sorted(profits_by_symbol.items(), key=lambda x: x[1]['pnl'], reverse=True)[:5]:
                return_rate = (data['pnl'] / data['total_cost'] * 100) if data['total_cost'] > 0 else 0
                top_profits.append({
                    'symbol': symbol,
                    'pnl': data['pnl'],
                    'return_rate': return_rate,
                    'trades': data['trades']
                })

            # 亏损TOP5
            losses_by_symbol = {}
            for cp in closed_positions:
                symbol = cp.get('symbol', '')
                pnl = float(cp.get('net_pnl', 0))
                if pnl < 0:
                    if symbol not in losses_by_symbol:
                        losses_by_symbol[symbol] = {'pnl': 0, 'trades': 0, 'total_cost': 0}
                    losses_by_symbol[symbol]['pnl'] += pnl
                    losses_by_symbol[symbol]['trades'] += 1
                    losses_by_symbol[symbol]['total_cost'] += float(cp.get('total_cost', 0))

            top_losses = []
            for symbol, data in sorted(losses_by_symbol.items(), key=lambda x: x[1]['pnl'])[:5]:
                return_rate = (data['pnl'] / data['total_cost'] * 100) if data['total_cost'] > 0 else 0
                top_losses.append({
                    'symbol': symbol,
                    'pnl': data['pnl'],
                    'return_rate': return_rate,
                    'trades': data['trades']
                })

            return jsonify({
                'overview': {
                    'total_trades': total_trades,
                    'total_pnl': total_pnl,
                    'win_rate': win_rate,
                    'positions_count': positions_count
                },
                'daily_trend': daily_trend,
                'top_profits': top_profits,
                'top_losses': top_losses,
                'last_updated': datetime.now().isoformat()
            })

        except Exception as e:
            logger.error(f"获取Dashboard数据失败: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/refresh')
    def refresh_data():
        """手动刷新数据"""
        try:
            # 这里可以触发重新处理Excel文件的逻辑
            return jsonify({'status': 'success', 'message': '数据刷新成功'})
        except Exception as e:
            logger.error(f"刷新数据失败: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/health')
    def health_check():
        """健康检查"""
        return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5001, debug=True)