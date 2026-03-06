import { useState } from 'react'
import { Search } from 'lucide-react'
import useStockStore from '../../store/useStockStore'
import { FEATURED_TICKERS, getTicker3DConfig } from '../../utils/constants'

export default function TickerSelector() {
  const { selectedTicker, setTicker } = useStockStore()
  const [searchInput, setSearchInput] = useState('')

  const handleSearch = (e) => {
    e.preventDefault()
    const symbol = searchInput.trim().toUpperCase()
    if (symbol) {
      setTicker(symbol)
      setSearchInput('')
    }
  }

  return (
    <div className="space-y-3">
      {/* Featured ticker buttons */}
      <div className="flex gap-2 flex-wrap">
        {FEATURED_TICKERS.map((ticker) => {
          const config = getTicker3DConfig(ticker)
          const isActive = selectedTicker === ticker

          return (
            <button
              key={ticker}
              onClick={() => setTicker(ticker)}
              className={`
                px-4 py-2 rounded-2xl text-sm font-medium transition-all duration-300
                ${isActive
                  ? 'bg-white/15 text-white border border-white/20 shadow-lg shadow-white/5'
                  : 'bg-white/5 text-white/50 border border-transparent hover:bg-white/10 hover:text-white/70'}
              `}
            >
              {config.label}
            </button>
          )
        })}
      </div>

      {/* Search any NSE ticker */}
      <form onSubmit={handleSearch} className="flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
          <input
            type="text"
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value.toUpperCase())}
            placeholder="Search any NSE ticker..."
            className="w-full pl-9 pr-4 py-2.5 rounded-2xl text-sm bg-white/5 border border-white/10 text-white placeholder-white/30 focus:outline-none focus:border-white/20 focus:bg-white/8 transition-all"
          />
        </div>
        <button
          type="submit"
          className="px-5 py-2.5 rounded-2xl text-sm font-medium bg-gradient-to-r from-blue-500/20 to-purple-500/20 border border-white/10 text-white/80 hover:text-white hover:border-white/20 transition-all"
        >
          Analyze
        </button>
      </form>
    </div>
  )
}
