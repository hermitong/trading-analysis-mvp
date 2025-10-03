import React, { useEffect } from 'react'
import {
  Modal,
  Form,
  Input,
  Select,
  InputNumber,
  DatePicker,
  Rate,
  Button,
  Space,
  Divider,
  Switch,
  message
} from 'antd'
import dayjs from 'dayjs'

const { Option } = Select

function TradeForm({ visible, editingTrade, onSubmit, onCancel }) {
  const [form] = Form.useForm()
  const [isOption, setIsOption] = React.useState(false)

  useEffect(() => {
    if (visible) {
      if (editingTrade) {
        // 编辑模式，填充表单数据
        const formData = {
          ...editingTrade,
          trade_date: editingTrade.trade_date ? dayjs(editingTrade.trade_date) : null,
          close_date: editingTrade.close_date ? dayjs(editingTrade.close_date) : null,
          expiration_date: editingTrade.expiration_date ? dayjs(editingTrade.expiration_date) : null,
        }
        form.setFieldsValue(formData)
        setIsOption(editingTrade.security_type === 'OPTION')
      } else {
        // 新建模式，重置表单
        form.resetFields()
        setIsOption(false)
      }
    }
  }, [visible, editingTrade, form])

  const handleSecurityTypeChange = (value) => {
    setIsOption(value === 'OPTION')
    if (value !== 'OPTION') {
      form.setFieldsValue({
        option_type: null,
        strike_price: null,
        expiration_date: null,
        underlying_symbol: ''
      })
    }
  }

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()

      // 格式化日期字段
      const formattedValues = {
        ...values,
        trade_date: values.trade_date ? values.trade_date.format('YYYY-MM-DD') : null,
        close_date: values.close_date ? values.close_date.format('YYYY-MM-DD') : null,
        expiration_date: values.expiration_date ? values.expiration_date.format('YYYY-MM-DD') : null,
        trade_time: values.trade_time || '00:00:00',
      }

      await onSubmit(formattedValues)
    } catch (error) {
      message.error('请检查表单填写是否正确')
    }
  }

  const sourceOptions = [
    { label: '🐳巨鲸', value: '🐳巨鲸' },
    { label: '🏫社区', value: '🏫社区' },
    { label: '✅判断', value: '✅判断' },
    { label: '🛜社交媒体', value: '🛜社交媒体' },
    { label: '📰新闻', value: '📰新闻' },
    { label: '📊技术分析', value: '📊技术分析' },
    { label: '其他', value: '其他' }
  ]

  const closeReasonOptions = [
    { label: '✅止盈', value: '✅止盈' },
    { label: '❌止损', value: '❌止损' },
    { label: '⬆️做T', value: '⬆️做T' },
    { label: '⬇️做T', value: '⬇️做T' },
    { label: '📅到期', value: '📅到期' },
    { label: '📰突发消息', value: '📰突发消息' },
    { label: '💰资金需求', value: '💰资金需求' },
    { label: '其他', value: '其他' }
  ]

  const tradeTypeOptions = [
    { label: '日内交易', value: '日内交易' },
    { label: '短线交易', value: '短线交易' },
    { label: '波段交易', value: '波段交易' },
    { label: '长线投资', value: '长线投资' },
    { label: '套利', value: '套利' },
    { label: '其他', value: '其他' }
  ]

  return (
    <Modal
      title={editingTrade ? '编辑交易记录' : '添加交易记录'}
      open={visible}
      onCancel={onCancel}
      width={800}
      footer={[
        <Button key="cancel" onClick={onCancel}>
          取消
        </Button>,
        <Button key="submit" type="primary" onClick={handleSubmit}>
          {editingTrade ? '更新' : '创建'}
        </Button>
      ]}
    >
      <Form
        form={form}
        layout="vertical"
        initialValues={{
          action: 'BUY',
          security_type: 'STOCK',
          quantity: 100,
          commission: 0,
          trade_time: '00:00:00'
        }}
      >
        {/* 基本信息 */}
        <Divider>基本信息</Divider>

        <Form.Item
          label="证券类型"
          name="security_type"
          rules={[{ required: true, message: '请选择证券类型' }]}
        >
          <Select onChange={handleSecurityTypeChange}>
            <Option value="STOCK">股票</Option>
            <Option value="OPTION">期权</Option>
          </Select>
        </Form.Item>

        <Form.Item
          label="标的代码"
          name="symbol"
          rules={[{ required: true, message: '请输入标的代码' }]}
        >
          <Input placeholder="如: AAPL, TSLA" />
        </Form.Item>

        <Form.Item
          label="证券名称"
          name="security_name"
        >
          <Input placeholder="如: Apple Inc." />
        </Form.Item>

        <Form.Item
          label="交易方向"
          name="action"
          rules={[{ required: true, message: '请选择交易方向' }]}
        >
          <Select>
            <Option value="BUY">买入</Option>
            <Option value="SELL">卖出</Option>
          </Select>
        </Form.Item>

        <Form.Item
          label="交易日期"
          name="trade_date"
          rules={[{ required: true, message: '请选择交易日期' }]}
        >
          <DatePicker style={{ width: '100%' }} />
        </Form.Item>

        <Form.Item
          label="交易时间"
          name="trade_time"
        >
          <Input placeholder="格式: HH:MM:SS" />
        </Form.Item>

        {/* 交易信息 */}
        <Divider>交易信息</Divider>

        <Form.Item
          label="交易数量"
          name="quantity"
          rules={[{ required: true, message: '请输入交易数量' }]}
        >
          <InputNumber
            style={{ width: '100%' }}
            min={0}
            step={1}
          />
        </Form.Item>

        <Form.Item
          label="交易价格"
          name="price"
          rules={[{ required: true, message: '请输入交易价格' }]}
        >
          <InputNumber
            style={{ width: '100%' }}
            min={0}
            step={0.01}
            precision={2}
            prefix="$"
          />
        </Form.Item>

        <Form.Item
          label="交易金额"
          name="amount"
          rules={[{ required: true, message: '请输入交易金额' }]}
        >
          <InputNumber
            style={{ width: '100%' }}
            min={0}
            step={0.01}
            precision={2}
            prefix="$"
          />
        </Form.Item>

        <Form.Item
          label="手续费"
          name="commission"
        >
          <InputNumber
            style={{ width: '100%' }}
            min={0}
            step={0.01}
            precision={2}
            prefix="$"
          />
        </Form.Item>

        {/* 期权信息 */}
        {isOption && (
          <>
            <Divider>期权信息</Divider>

            <Form.Item
              label="标的证券"
              name="underlying_symbol"
            >
              <Input placeholder="如: AAPL (期权标的的股票代码)" />
            </Form.Item>

            <Form.Item
              label="期权类型"
              name="option_type"
            >
              <Select>
                <Option value="CALL">看涨期权 (CALL)</Option>
                <Option value="PUT">看跌期权 (PUT)</Option>
              </Select>
            </Form.Item>

            <Form.Item
              label="行权价"
              name="strike_price"
            >
              <InputNumber
                style={{ width: '100%' }}
                min={0}
                step={0.01}
                precision={2}
                prefix="$"
              />
            </Form.Item>

            <Form.Item
              label="到期日"
              name="expiration_date"
            >
              <DatePicker style={{ width: '100%' }} />
            </Form.Item>
          </>
        )}

        {/* 扩展信息 */}
        <Divider>扩展信息</Divider>

        <Form.Item
          label="消息来源"
          name="source"
        >
          <Select
            placeholder="选择消息来源"
            allowClear
            options={sourceOptions}
          />
        </Form.Item>

        <Form.Item
          label="交易评分"
          name="trade_rating"
        >
          <Rate style={{ fontSize: 16 }} />
        </Form.Item>

        <Form.Item
          label="交易类型"
          name="trade_type"
        >
          <Select
            placeholder="选择交易类型"
            allowClear
            options={tradeTypeOptions}
          />
        </Form.Item>

        <Form.Item
          label="笔记"
          name="notes"
        >
          <Input.TextArea
            rows={3}
            placeholder="添加交易笔记或备注..."
          />
        </Form.Item>

        {/* 平仓信息 */}
        <Divider>平仓信息 (可选)</Divider>

        <Form.Item
          label="平仓日期"
          name="close_date"
        >
          <DatePicker style={{ width: '100%' }} />
        </Form.Item>

        <Form.Item
          label="平仓价格"
          name="close_price"
        >
          <InputNumber
            style={{ width: '100%' }}
            min={0}
            step={0.01}
            precision={2}
            prefix="$"
          />
        </Form.Item>

        <Form.Item
          label="平仓数量"
          name="close_quantity"
        >
          <InputNumber
            style={{ width: '100%' }}
            min={0}
            step={1}
          />
        </Form.Item>

        <Form.Item
          label="平仓理由"
          name="close_reason"
        >
          <Select
            placeholder="选择平仓理由"
            allowClear
            options={closeReasonOptions}
          />
        </Form.Item>

        {/* 账户信息 */}
        <Divider>账户信息</Divider>

        <Form.Item
          label="券商"
          name="broker"
        >
          <Input placeholder="如: 富途证券" />
        </Form.Item>

        <Form.Item
          label="账户ID"
          name="account_id"
        >
          <Input placeholder="账户标识" />
        </Form.Item>
      </Form>
    </Modal>
  )
}

export default TradeForm