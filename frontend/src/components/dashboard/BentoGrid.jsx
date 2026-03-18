import { motion, AnimatePresence } from 'framer-motion'
import SparklineChart from './SparklineChart'
import SentinelScoreCard from './SentinelScoreCard'
import AnalystSummary from './AnalystSummary'
import GlassPanel from '../layout/GlassPanel'
import useStockStore from '../../store/useStockStore'
import { getTicker3DConfig } from '../../utils/constants'

export default function BentoGrid() {
  const { stockData, isLoading, error, selectedTicker } = useStockStore()

  if (!selectedTicker) return null

  if (isLoading) return <LoadingSkeleton />

  if (error) return <ErrorState message={error} />

  if (!stockData) return null

  const { current_price, historical_1y, analysis } = stockData
  const tickerLabel = getTicker3DConfig(selectedTicker).label

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={selectedTicker}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.4 }}
        className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-6xl mx-auto px-6"
      >
        {/* Row 1: Price + Score */}
        <GlassPanel className="md:col-span-2 p-6">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-white/50 text-xs uppercase tracking-wider font-medium">
              {tickerLabel}
            </h3>
            <span className="text-white/30 text-xs">NSE</span>
          </div>
          <div className="flex items-baseline gap-3">
            <motion.span
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-white text-4xl font-bold tabular-nums"
            >
              ₹{current_price?.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
            </motion.span>
          </div>
          <p className="text-white/30 text-xs mt-2">
            Powered by Proprietary Data Bridge
          </p>
        </GlassPanel>

        <SentinelScoreCard
          score={analysis.sentinel_score}
          category={analysis.score_category}
        />

        {/* Row 2: Chart + Info */}
        <div className="md:col-span-2">
          <SparklineChart data={historical_1y} ticker={selectedTicker} />
        </div>

        <GlassPanel className="p-6 flex flex-col justify-center gap-4">
          <div>
            <h4 className="text-white/40 text-[11px] uppercase tracking-wider mb-1">
              Data Source
            </h4>
            <p className="text-white/80 text-sm font-medium">
              Proprietary Data Bridge
            </p>
          </div>
          <div>
            <h4 className="text-white/40 text-[11px] uppercase tracking-wider mb-1">
              Analysis Engine
            </h4>
            <p className="text-white/80 text-sm font-medium">
              Intelligence Engine v1.0
            </p>
          </div>
          <div>
            <h4 className="text-white/40 text-[11px] uppercase tracking-wider mb-1">
              Data Points
            </h4>
            <p className="text-white/80 text-sm font-medium">
              {historical_1y?.length || 0} trading days
            </p>
          </div>
        </GlassPanel>

        {/* Row 3: Analyst summary */}
        <div className="md:col-span-2">
          <AnalystSummary analysis={analysis} />
        </div>

        <GlassPanel className="p-6 flex flex-col justify-center items-center text-center">
          <div className="w-10 h-10 rounded-2xl bg-white/5 flex items-center justify-center mb-3">
            <span className="text-lg">🎯</span>
          </div>
          <h4 className="text-white/40 text-[11px] uppercase tracking-wider mb-2">
            Score Breakdown
          </h4>
          <div className="space-y-1.5 text-xs w-full">
            <div className="flex justify-between text-white/60">
              <span>Price Trend</span>
              <span className="text-white/80">40%</span>
            </div>
            <div className="flex justify-between text-white/60">
              <span>Headlines</span>
              <span className="text-white/80">40%</span>
            </div>
            <div className="flex justify-between text-white/60">
              <span>Sentiment</span>
              <span className="text-white/80">20%</span>
            </div>
          </div>
        </GlassPanel>
      </motion.div>
    </AnimatePresence>
  )
}

function LoadingSkeleton() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-6xl mx-auto px-6">
      {[2, 1, 2, 1, 2, 1].map((span, i) => (
        <div
          key={i}
          className={`bg-white/5 rounded-3xl animate-pulse ${
            span === 2 ? 'md:col-span-2' : ''
          }`}
          style={{ height: i < 2 ? '180px' : '200px' }}
        />
      ))}
    </div>
  )
}

function ErrorState({ message }) {
  return (
    <div className="max-w-6xl mx-auto px-6">
      <GlassPanel className="p-12 text-center">
        <div className="w-12 h-12 rounded-2xl bg-red-500/10 flex items-center justify-center mx-auto mb-4">
          <span className="text-2xl">⚠️</span>
        </div>
        <p className="text-red-400/80 text-sm mb-2">{message}</p>
        <p className="text-white/30 text-xs">
          The Intelligence Engine is currently recalibrating. Please try another ticker.
        </p>
      </GlassPanel>
    </div>
  )
}
