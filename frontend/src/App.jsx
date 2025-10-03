import React, { useState, useEffect } from 'react'
import { Layout, Menu, Typography, Tabs, Button, Space, Upload, message, Card, Row, Col, Statistic } from 'antd'
import {
  DashboardOutlined,
  FileTextOutlined,
  UploadOutlined,
  BarChartOutlined,
  PlusOutlined
} from '@ant-design/icons'
import TradeList from './components/TradeList'
import TradeForm from './components/TradeForm'
import Dashboard from './components/Dashboard'
import { useTradeStore } from './stores/tradeStore'
import './App.css'

const { Header, Sider, Content } = Layout
const { Title } = Typography

function App() {
  const [selectedTab, setSelectedTab] = useState('trades')
  const [editingTrade, setEditingTrade] = useState(null)
  const [formVisible, setFormVisible] = useState(false)
  const {
    trades,
    loading,
    statistics,
    fetchTrades,
    fetchStatistics,
    importTrades,
    updateTrade,
    createTrade
  } = useTradeStore()

  useEffect(() => {
    fetchTrades()
    fetchStatistics()
  }, [fetchTrades, fetchStatistics])

  const handleImport = async (file) => {
    try {
      const formData = new FormData()
      formData.append('file', file)

      await importTrades(formData)
      message.success('文件导入成功')
      fetchTrades()
      fetchStatistics()
    } catch (error) {
      message.error(`导入失败: ${error.message}`)
    }
  }

  const handleEdit = (trade) => {
    setEditingTrade(trade)
    setFormVisible(true)
  }

  const handleFormSubmit = async (values) => {
    try {
      if (editingTrade) {
        await updateTrade(editingTrade.id, values)
        message.success('交易记录更新成功')
      } else {
        await createTrade(values)
        message.success('交易记录创建成功')
      }

      setFormVisible(false)
      setEditingTrade(null)
      fetchTrades()
      fetchStatistics()
    } catch (error) {
      message.error(`操作失败: ${error.message}`)
    }
  }

  const menuItems = [
    {
      key: 'dashboard',
      icon: <DashboardOutlined />,
      label: '仪表板',
    },
    {
      key: 'trades',
      icon: <FileTextOutlined />,
      label: '交易记录',
    },
    {
      key: 'import',
      icon: <UploadOutlined />,
      label: '数据导入',
    },
  ]

  const handleMenuClick = (e) => {
    if (e.key === 'dashboard') {
      setSelectedTab('dashboard')
    } else if (e.key === 'trades') {
      setSelectedTab('trades')
    } else if (e.key === 'import') {
      setSelectedTab('import')
    }
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header>
        <Title level={3} style={{ color: 'white', margin: 0 }}>
          交易记录管理系统
        </Title>
      </Header>

      <Layout>
        <Sider width={200} style={{ background: '#fff' }}>
          <Menu
            mode="inline"
            selectedKeys={[selectedTab]}
            items={menuItems}
            onClick={handleMenuClick}
            style={{ height: '100%', borderRight: 0 }}
          />
        </Sider>

        <Layout style={{ padding: '0' }}>
          <Content style={{ background: '#fff', padding: '24px', margin: 0 }}>
            {selectedTab === 'dashboard' && (
              <Dashboard />
            )}

            {selectedTab === 'trades' && (
              <div>
                <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Title level={2}>交易记录管理</Title>
                  <Button
                    type="primary"
                    icon={<PlusOutlined />}
                    onClick={() => {
                      setEditingTrade(null)
                      setFormVisible(true)
                    }}
                  >
                    添加交易
                  </Button>
                </div>

                <Row gutter={16} style={{ marginBottom: 16 }}>
                  <Col span={4}>
                    <Card>
                      <Statistic
                        title="总交易数"
                        value={statistics.total_trades}
                        prefix={<BarChartOutlined />}
                      />
                    </Card>
                  </Col>
                  <Col span={4}>
                    <Card>
                      <Statistic
                        title="期权交易"
                        value={statistics.option_trades}
                        valueStyle={{ color: '#1890ff' }}
                      />
                    </Card>
                  </Col>
                  <Col span={4}>
                    <Card>
                      <Statistic
                        title="股票交易"
                        value={statistics.stock_trades}
                        valueStyle={{ color: '#52c41a' }}
                      />
                    </Card>
                  </Col>
                  <Col span={4}>
                    <Card>
                      <Statistic
                        title="总金额"
                        value={statistics.total_amount}
                        precision={2}
                        prefix="$"
                      />
                    </Card>
                  </Col>
                  <Col span={4}>
                    <Card>
                      <Statistic
                        title="平均评分"
                        value={statistics.average_rating}
                        precision={1}
                        suffix="/ 5"
                      />
                    </Card>
                  </Col>
                  <Col span={4}>
                    <Card>
                      <Statistic
                        title="总手续费"
                        value={statistics.total_commission}
                        precision={2}
                        prefix="$"
                      />
                    </Card>
                  </Col>
                </Row>

                <TradeList
                  trades={trades}
                  loading={loading}
                  onEdit={handleEdit}
                />
              </div>
            )}

            {selectedTab === 'import' && (
              <div>
                <Title level={2}>数据导入</Title>
                <Card>
                  <Upload
                    accept=".xlsx,.xls"
                    beforeUpload={(file) => {
                      handleImport(file)
                      return false
                    }}
                    showUploadList={false}
                  >
                    <Button icon={<UploadOutlined />}>上传Excel文件</Button>
                  </Upload>
                  <p style={{ marginTop: 16, color: '#666' }}>
                    支持富途证券、老虎证券、雪盈证券、Interactive Brokers以及郑兄格式的Excel文件
                  </p>
                </Card>
              </div>
            )}
          </Content>
        </Layout>
      </Layout>

      <TradeForm
        visible={formVisible}
        editingTrade={editingTrade}
        onSubmit={handleFormSubmit}
        onCancel={() => {
          setFormVisible(false)
          setEditingTrade(null)
        }}
      />
    </Layout>
  )
}

export default App