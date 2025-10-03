import { create } from 'zustand'
import api from '../services/api'

const useTradeStore = create((set, get) => ({
  trades: [],
  loading: false,
  statistics: {},
  currentTrade: null,

  // 获取交易列表
  fetchTrades: async (filters = {}) => {
    set({ loading: true })
    try {
      const data = await api.get('/trades', { params: filters })
      set({ trades: data.trades, loading: false })
    } catch (error) {
      set({ loading: false })
      throw error
    }
  },

  // 获取统计信息
  fetchStatistics: async () => {
    try {
      const data = await api.get('/statistics')
      set({ statistics: data })
    } catch (error) {
      throw error
    }
  },

  // 创建交易
  createTrade: async (tradeData) => {
    try {
      const data = await api.post('/trades', tradeData)
      const trades = get().trades
      set({ trades: [data.trade, ...trades] })
      return data.trade
    } catch (error) {
      throw error
    }
  },

  // 更新交易
  updateTrade: async (id, tradeData) => {
    try {
      const data = await api.put(`/trades/${id}`, tradeData)
      const trades = get().trades
      const updatedTrades = trades.map(trade =>
        trade.id === id ? { ...trade, ...data.trade } : trade
      )
      set({ trades: updatedTrades })
      return data.trade
    } catch (error) {
      throw error
    }
  },

  // 删除交易
  deleteTrade: async (id) => {
    try {
      await api.delete(`/trades/${id}`)
      const trades = get().trades
      set({ trades: trades.filter(trade => trade.id !== id) })
    } catch (error) {
      throw error
    }
  },

  // 导入交易
  importTrades: async (formData) => {
    try {
      const data = await api.post('/import', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      return data
    } catch (error) {
      throw error
    }
  },

  // 设置当前交易
  setCurrentTrade: (trade) => {
    set({ currentTrade: trade })
  },

  // 清空当前交易
  clearCurrentTrade: () => {
    set({ currentTrade: null })
  }
}))

export { useTradeStore }