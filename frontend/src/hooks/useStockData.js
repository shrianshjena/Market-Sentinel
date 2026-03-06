import { useEffect } from 'react'
import axios from 'axios'
import useStockStore from '../store/useStockStore'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export function useStockData() {
  const { selectedTicker, setLoading, setStockData, setError } = useStockStore()

  useEffect(() => {
    if (!selectedTicker) return

    let cancelled = false

    const fetchData = async () => {
      setLoading(true)
      try {
        const { data } = await axios.get(`${API_BASE}/api/analyze/${selectedTicker}`)
        if (!cancelled) {
          setStockData(data.data)
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err.response?.data?.detail ||
            'The Intelligence Engine is currently recalibrating. Please try another ticker.'
          )
        }
      }
    }

    fetchData()

    return () => {
      cancelled = true
    }
  }, [selectedTicker, setLoading, setStockData, setError])
}
