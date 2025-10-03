import React, { useEffect } from 'react'
import { Row, Col, Card, Statistic, Table, Progress, Tag } from 'antd'
import {
  TrendingUpOutlined,
  TrendingDownOutlined,
  DollarOutlined,
  PercentageOutlined,
  StarOutlined,
  CalendarOutlined
} from '@ant-design/icons'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js'
import { Bar, Line, Pie } from 'react-chartjs-2'
import { useTradeStore } from '../stores/tradeStore'
import dayjs from 'dayjs'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
)

function Dashboard() {
  const { trades, statistics, fetchTrades, fetchStatistics } = useTradeStore()

  useEffect(() => {
    fetchTrades()
    fetchStatistics()
  }, [fetchTrades, fetchStatistics])

  // 计算月度交易统计
  const monthlyStats = React.useMemo(() => {
    const stats = {}

    trades.forEach(trade => {
      const month = dayjs(trade.trade_date).format('YYYY-MM')
      if (!stats[month]) {
        stats[month] = {
          month,
          trades: 0,
          profit: 0,
          amount: 0,
          buyCount: 0,
          sellCount: 0
        }
      }

      stats[month].trades++
      stats[month].amount += trade.amount

      if (trade.action === 'BUY') {
        stats[month].buyCount++
      } else {
        stats[month].sellCount++
        // 简单的盈亏计算 (这里需要更复杂的逻辑来匹配买卖)
        stats[month].profit += trade.close_price ? (trade.close_price - trade.price) * trade.quantity : 0
      }
    })

    return Object.values(stats).sort((a, b) => a.month.localeCompare(b.month))
  }, [trades])

  // 按标的统计
  const symbolStats = React.useMemo(() => {
    const stats = {}

    trades.forEach(trade => {
      if (!stats[trade.symbol]) {
        stats[trade.symbol] = {
          symbol: trade.symbol,
          trades: 0,
          amount: 0,
          type: trade.security_type
        }
      }

      stats[trade.symbol].trades++
      stats[trade.symbol].amount += trade.amount
    })

    return Object.values(stats)
      .sort((a, b) => b.amount - a.amount)
      .slice(0, 10)
  }, [trades])

  // 评分分布
  const ratingDistribution = React.useMemo(() => {
    const distribution = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 }

    trades.forEach(trade => {
      if (trade.trade_rating > 0) {
        const rating = Math.round(trade.trade_rating)
        distribution[rating] = (distribution[rating] || 0) + 1
      }
    })

    return distribution
  }, [trades])

  // 消息来源统计
  const sourceStats = React.useMemo(() => {
    const stats = {}

    trades.forEach(trade => {
      if (trade.source) {
        if (!stats[trade.source]) {
          stats[trade.source] = { source: trade.source, count: 0, profit: 0 }
        }
        stats[trade.source].count++
        // 简单盈亏计算
        if (trade.close_price && trade.action === 'SELL') {
          stats[trade.source].profit += (trade.close_price - trade.price) * trade.quantity
        }
      }
    })

    return Object.values(stats).sort((a, b) => b.count - a.count)
  }, [trades])

  // 图表配置
  const monthlyChartConfig = {
    labels: monthlyStats.map(stat => dayjs(stat.month).format('MM月')),
    datasets: [
      {
        label: '交易金额',
        data: monthlyStats.map(stat => stat.amount),
        backgroundColor: 'rgba(54, 162, 235, 0.6)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1,
      },
    ],
  }

  const pieChartConfig = {
    labels: ['期权交易', '股票交易'],
    datasets: [
      {
        data: [statistics.option_trades, statistics.stock_trades],
        backgroundColor: [
          'rgba(54, 162, 235, 0.6)',
          'rgba(75, 192, 192, 0.6)',
        ],
        borderColor: [
          'rgba(54, 162, 235, 1)',
          'rgba(75, 192, 192, 1)',
        ],
        borderWidth: 1,
      },
    ],
  }

  const symbolColumns = [
    {
      title: '标的',
      dataIndex: 'symbol',
      key: 'symbol',
      render: (symbol, record) => (
        <div>
          <Tag color={record.type === 'OPTION' ? 'blue' : 'green'}>
            {symbol}
          </Tag>
        </div>
      ),
    },
    {
      title: '交易次数',
      dataIndex: 'trades',
      key: 'trades',
      align: 'right',
    },
    {
      title: '总金额',
      dataIndex: 'amount',
      key: 'amount',
      align: 'right',
      render: (amount) => `$${amount.toFixed(2)}`,
    },
  ]

  const sourceColumns = [
    {
      title: '消息来源',
      dataIndex: 'source',
      key: 'source',
      render: (source) => (
        <span style={{ fontWeight: 'bold' }}>{source}</span>
      ),
    },
    {
      title: '交易次数',
      dataIndex: 'count',
      key: 'count',
      align: 'right',
    },
    {
      title: '盈亏',
      dataIndex: 'profit',
      key: 'profit',
      align: 'right',
      render: (profit) => (
        <span style={{ color: profit >= 0 ? '#52c41a' : '#ff4d4f' }}>
          ${profit.toFixed(2)}
        </span>
      ),
    },
  ]

  return (
    <div>
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="总交易数"
              value={statistics.total_trades}
              prefix={<CalendarOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="总交易金额"
              value={statistics.total_amount}
              precision={2}
              prefix={<DollarOutlined />}
              suffix="USD"
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="总手续费"
              value={statistics.total_commission}
              precision={2}
              prefix={<DollarOutlined />}
              suffix="USD"
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="平均评分"
              value={statistics.average_rating}
              precision={1}
              prefix={<StarOutlined />}
              suffix="/ 5"
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} lg={12}>
          <Card title="月度交易金额" style={{ height: 400 }}>
            <Bar
              data={monthlyChartConfig}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    display: false,
                  },
                },
              }}
            />
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="交易类型分布" style={{ height: 400 }}>
            <Pie
              data={pieChartConfig}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    position: 'bottom',
                  },
                },
              }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} lg={12}>
          <Card title="热门标的 (前10)">
            <Table
              columns={symbolColumns}
              dataSource={symbolStats}
              pagination={false}
              size="small"
              rowKey="symbol"
            />
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="消息来源统计">
            <Table
              columns={sourceColumns}
              dataSource={sourceStats}
              pagination={false}
              size="small"
              rowKey="source"
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24}>
          <Card title="评分分布">
            <Row gutter={16}>
              {Object.entries(ratingDistribution).map(([rating, count]) => (
                <Col xs={24} sm={12} md={4} key={rating}>
                  <div style={{ textAlign: 'center', marginBottom: 16 }}>
                    <div style={{ fontSize: 16, fontWeight: 'bold', marginBottom: 8 }}>
                      {rating} 星
                    </div>
                    <Progress
                      type="circle"
                      percent={Math.round((count / trades.filter(t => t.trade_rating > 0).length) * 100) || 0}
                      format={() => `${count} 笔`}
                      strokeColor={rating >= 4 ? '#52c41a' : rating >= 3 ? '#faad14' : '#ff4d4f'}
                    />
                  </div>
                </Col>
              ))}
            </Row>
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default Dashboard