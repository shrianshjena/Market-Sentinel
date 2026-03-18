import { create } from 'zustand'

const useStockStore = create((set) => ({
  selectedTicker: null,
  stockData: null,
  isLoading: false,
  error: null,
  isInfoModalOpen: false,

  setTicker: (ticker) => set({ selectedTicker: ticker, stockData: null, error: null }),
  setLoading: (loading) => set({ isLoading: loading }),
  setStockData: (data) => set({ stockData: data, isLoading: false, error: null }),
  setError: (error) => set({ error, isLoading: false }),
  setInfoModalOpen: (isOpen) => set({ isInfoModalOpen: isOpen }),
  reset: () => set({ selectedTicker: null, stockData: null, isLoading: false, error: null }),
}))

export default useStockStore
