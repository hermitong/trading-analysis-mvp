import React, { useState } from 'react'
import {
  Table,
  Button,
  Space,
  Tag,
  Tooltip,
  Modal,
  message,
  Input,
  Select,
  DatePicker,
  Rate
} from 'antd'
import {
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  StarOutlined
} from '@ant-design/icons'
import { useTradeStore } from '../stores/tradeStore'
import dayjs from 'dayjs'

const { Search } = Input
const { RangePicker } = DatePicker

function TradeList({ trades, loading, onEdit }) {
  const [searchText, setSearchText] = useState('')
  const [dateRange, setDateRange] = useState(null)
  const [securityTypeFilter, setSecurityTypeFilter] = useState('')
  const [viewModalVisible, setViewModalVisible] = useState(false)
  const [selectedTrade, setSelectedTrade] = useState(null)

  const { deleteTrade } = useTradeStore()

  // 过滤交易记录
  const filteredTrades = trades.filter(trade => {
    let matchesSearch = true
    let matchesDate = true
    let matchesSecurityType = true

    if (searchText) {
      matchesSearch = trade.symbol.toLowerCase().includes(searchText.toLowerCase()) ||
                     trade.security_name.toLowerCase().includes(searchText.toLowerCase()) ||
                     trade.source.toLowerCase().includes(searchText.toLowerCase())
    }

    if (dateRange && dateRange.length === 2) {
      const tradeDate = dayjs(trade.trade_date)
      matchesDate = tradeDate.isAfter(dateRange[0]) && tradeDate.isBefore(dateRange[1])
    }

    if (securityTypeFilter) {
      matchesSecurityType = trade.security_type === securityTypeFilter
    }

    return matchesSearch && matchesDate && matchesSecurityType
  })

  const handleDelete = async (tradeId) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这条交易记录吗？此操作不可撤销。',
      okText: '删除',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        try {
          await deleteTrade(tradeId)
          message.success('删除成功')
        } catch (error) {
          message.error(`删除失败: ${error.message}`)
        }
      }
    })
  }

  const handleView = (trade) => {
    setSelectedTrade(trade)
    setViewModalVisible(true)
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount)
  }

  const getSourceIcon = (source) => {
    const sourceMap = {
      '🐳巨鲸': '🐳',
      '🏫社区': '🏫',
      '✅判断': '✅',
      '🛜社交媒体': '📱'
    }
    return sourceMap[source] || '📊'
  }

  const getCloseReasonClass = (reason) => {
    if (!reason) return 'neutral-reason'
    if (reason.includes('止盈')) return 'profit-reason'
    if (reason.includes('止损')) return 'loss-reason'
    if (reason.includes('做T')) return 'neutral-reason'
    return 'neutral-reason'
  }

  const columns = [
    {
      title: '日期',
      dataIndex: 'trade_date',
      key: 'trade_date',
      width: 100,
      sorter: (a, b) => dayjs(a.trade_date).unix() - dayjs(b.trade_date).unix(),
    },
    {
      title: '标的',
      dataIndex: 'symbol',
      key: 'symbol',
      width: 80,
      render: (symbol, record) => (
        <div>
          <div style={{ fontWeight: 'bold' }}>{symbol}</div>
          {record.security_type === 'OPTION' && (
            <div style={{ fontSize: '11px', color: '#666' }}>
              {record.option_type} ${record.strike_price}
            </div>
          )}
        </div>
      ),
    },
    {
      title: '类型',
      dataIndex: 'security_type',
      key: 'security_type',
      width: 80,
      render: (type) => (
        <Tag
          className={type === 'OPTION' ? 'option-badge' : 'stock-badge'}
        >
          {type === 'OPTION' ? '期权' : '股票'}
        </Tag>
      ),
    },
    {
      title: '操作',
      dataIndex: 'action',
      key: 'action',
      width: 60,
      render: (action) => (
        <Tag color={action === 'BUY' ? 'green' : 'red'}>
          {action === 'BUY' ? '买入' : '卖出'}
        </Tag>
      ),
    },
    {
      title: '数量',
      dataIndex: 'quantity',
      key: 'quantity',
      width: 80,
      align: 'right',
    },
    {
      title: '价格',
      dataIndex: 'price',
      key: 'price',
      width: 80,
      align: 'right',
      render: (price) => formatCurrency(price),
    },
    {
      title: '金额',
      dataIndex: 'amount',
      key: 'amount',
      width: 100,
      align: 'right',
      render: (amount) => formatCurrency(amount),
    },
    {
      title: '消息来源',
      dataIndex: 'source',
      key: 'source',
      width: 100,
      render: (source) => (
        <Tooltip title={source}>
          <span className="source-tag">
            {getSourceIcon(source)} {source}
          </span>
        </Tooltip>
      ),
    },
    {
      title: '评分',
      dataIndex: 'trade_rating',
      key: 'trade_rating',
      width: 100,
      render: (rating) => (
        rating > 0 ? (
          <Rate disabled value={rating} style={{ fontSize: 14 }} />
        ) : (
          <span style={{ color: '#ccc' }}>未评分</span>
        )
      ),
    },
    {
      title: '平仓理由',
      dataIndex: 'close_reason',
      key: 'close_reason',
      width: 100,
      render: (reason) => (
        reason ? (
          <span className={`close-reason ${getCloseReasonClass(reason)}`}>
            {reason}
          </span>
        ) : (
          <span style={{ color: '#ccc' }}>未平仓</span>
        )
      ),
    },
    {
      title: '操作',
      key: 'actions',
      width: 150,
      render: (_, record) => (
        <Space size="small">
          <Tooltip title="查看详情">
            <Button
              type="text"
              icon={<EyeOutlined />}
              onClick={() => handleView(record)}
            />
          </Tooltip>
          <Tooltip title="编辑">
            <Button
              type="text"
              icon={<EditOutlined />}
              onClick={() => onEdit(record)}
            />
          </Tooltip>
          <Tooltip title="删除">
            <Button
              type="text"
              danger
              icon={<DeleteOutlined />}
              onClick={() => handleDelete(record.id)}
            />
          </Tooltip>
        </Space>
      ),
    },
  ]

  return (
    <div className="trade-table">
      <div style={{ marginBottom: 16 }}>
        <Space wrap>
          <Search
            placeholder="搜索标的、名称或来源"
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            style={{ width: 200 }}
          />
          <Select
            placeholder="证券类型"
            value={securityTypeFilter}
            onChange={setSecurityTypeFilter}
            style={{ width: 120 }}
            allowClear
          >
            <Select.Option value="STOCK">股票</Select.Option>
            <Select.Option value="OPTION">期权</Select.Option>
          </Select>
          <RangePicker
            placeholder={['开始日期', '结束日期']}
            value={dateRange}
            onChange={setDateRange}
            style={{ width: 240 }}
          />
        </Space>
      </div>

      <Table
        columns={columns}
        dataSource={filteredTrades}
        loading={loading}
        rowKey="id"
        pagination={{
          total: filteredTrades.length,
          pageSize: 20,
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total) => `共 ${total} 条记录`,
        }}
        scroll={{ x: 1200 }}
      />

      {/* 查看详情模态框 */}
      <Modal
        title="交易详情"
        open={viewModalVisible}
        onCancel={() => setViewModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setViewModalVisible(false)}>
            关闭
          </Button>
        ]}
        width={800}
      >
        {selectedTrade && (
          <div>
            <div style={{ marginBottom: 16 }}>
              <h4>基本信息</h4>
              <p><strong>标的代码:</strong> {selectedTrade.symbol}</p>
              <p><strong>证券名称:</strong> {selectedTrade.security_name}</p>
              <p><strong>证券类型:</strong> {selectedTrade.security_type === 'OPTION' ? '期权' : '股票'}</p>
              <p><strong>交易方向:</strong> {selectedTrade.action === 'BUY' ? '买入' : '卖出'}</p>
              <p><strong>交易日期:</strong> {selectedTrade.trade_date}</p>
              <p><strong>交易时间:</strong> {selectedTrade.trade_time}</p>
            </div>

            <div style={{ marginBottom: 16 }}>
              <h4>交易信息</h4>
              <p><strong>交易数量:</strong> {selectedTrade.quantity}</p>
              <p><strong>交易价格:</strong> {formatCurrency(selectedTrade.price)}</p>
              <p><strong>交易金额:</strong> {formatCurrency(selectedTrade.amount)}</p>
              <p><strong>手续费:</strong> {formatCurrency(selectedTrade.commission)}</p>
              <p><strong>净金额:</strong> {formatCurrency(selectedTrade.net_amount)}</p>
            </div>

            {selectedTrade.security_type === 'OPTION' && (
              <div style={{ marginBottom: 16 }}>
                <h4>期权信息</h4>
                <p><strong>标的证券:</strong> {selectedTrade.underlying_symbol}</p>
                <p><strong>行权价:</strong> {formatCurrency(selectedTrade.strike_price)}</p>
                <p><strong>到期日:</strong> {selectedTrade.expiration_date}</p>
                <p><strong>期权类型:</strong> {selectedTrade.option_type === 'CALL' ? '看涨期权' : '看跌期权'}</p>
              </div>
            )}

            <div style={{ marginBottom: 16 }}>
              <h4>扩展信息</h4>
              <p><strong>消息来源:</strong> {selectedTrade.source}</p>
              <p><strong>交易评分:</strong> {
                selectedTrade.trade_rating > 0 ? (
                  <Rate disabled value={selectedTrade.trade_rating} />
                ) : '未评分'
              }</p>
              <p><strong>交易类型:</strong> {selectedTrade.trade_type || '-'}</p>
              <p><strong>笔记:</strong> {selectedTrade.notes || '-'}</p>
            </div>

            {(selectedTrade.close_date || selectedTrade.close_price) && (
              <div style={{ marginBottom: 16 }}>
                <h4>平仓信息</h4>
                <p><strong>平仓日期:</strong> {selectedTrade.close_date || '-'}</p>
                <p><strong>平仓价格:</strong> {
                  selectedTrade.close_price ? formatCurrency(selectedTrade.close_price) : '-'
                }</p>
                <p><strong>平仓数量:</strong> {selectedTrade.close_quantity || '-'}</p>
                <p><strong>平仓理由:</strong> {selectedTrade.close_reason || '-'}</p>
              </div>
            )}

            <div>
              <h4>元数据</h4>
              <p><strong>券商:</strong> {selectedTrade.broker}</p>
              <p><strong>账户:</strong> {selectedTrade.account_id || '-'}</p>
              <p><strong>源文件:</strong> {selectedTrade.source_file}</p>
              <p><strong>导入时间:</strong> {selectedTrade.import_time}</p>
            </div>
          </div>
        )}
      </Modal>
    </div>
  )
}

export default TradeList