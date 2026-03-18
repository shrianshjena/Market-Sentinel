import { motion, AnimatePresence } from 'framer-motion'
import { X, TrendingUp, Newspaper, MessageSquare, Globe } from 'lucide-react'
import useStockStore from '../../store/useStockStore'

export default function ScoreExplanationModal() {
  const { isInfoModalOpen, setInfoModalOpen } = useStockStore()

  if (!isInfoModalOpen) return null

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-[100] flex items-center justify-center px-4">
        {/* Backdrop */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={() => setInfoModalOpen(false)}
          className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        />

        {/* Modal */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          className="relative w-full max-w-2xl bg-slate-900 border border-white/10 rounded-2xl shadow-2xl overflow-hidden p-6 md:p-8"
        >
          {/* Close Button */}
          <button
            onClick={() => setInfoModalOpen(false)}
            className="absolute top-4 right-4 p-2 rounded-full bg-white/5 hover:bg-white/10 text-white/50 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>

          <div className="mb-6 border-b border-white/5 pb-4">
            <h2 className="text-2xl font-bold text-white mb-2">Sentinel Score Methodology</h2>
            <p className="text-sm text-white/50">
              The proprietary AI scoring system natively aggregates cross-platform data 
              to compute an institutional-grade rating out of 100.
            </p>
          </div>

          <div className="space-y-6">
            <div className="flex gap-4 items-start">
              <div className="p-3 rounded-xl bg-blue-500/10 text-blue-400">
                <TrendingUp className="w-6 h-6" />
              </div>
              <div className="flex-1">
                <h3 className="text-white font-semibold flex items-center gap-2">
                  Price Trend <span className="text-xs px-2 py-0.5 rounded-full bg-white/10 text-white/70">40% Weight</span>
                </h3>
                <p className="text-sm text-white/40 mt-1 leading-relaxed">
                  Evaluates the absolute historical momentum across the past 5 years of trading sessions. 
                  High scores require significant, sustained bullish catalysts (+150% returns map to absolute 100/100).
                </p>
              </div>
            </div>

            <div className="flex gap-4 items-start">
              <div className="p-3 rounded-xl bg-emerald-500/10 text-emerald-400">
                <MessageSquare className="w-6 h-6" />
              </div>
              <div className="flex-1">
                <h3 className="text-white font-semibold flex items-center gap-2">
                  Sentiment Consistency <span className="text-xs px-2 py-0.5 rounded-full bg-white/10 text-white/70">20% Weight</span>
                </h3>
                <p className="text-sm text-white/40 mt-1 leading-relaxed">
                  Quantifies the overall retail and institutional mood interpreted natively by mapping our AI analysis structure. Distinguishes between scattered opinions and consistently strong psychological conviction.
                </p>
              </div>
            </div>

            <div className="flex gap-4 items-start">
              <div className="p-3 rounded-xl bg-amber-500/10 text-amber-400">
                <Newspaper className="w-6 h-6" />
              </div>
              <div className="flex-1">
                <h3 className="text-white font-semibold flex items-center gap-2">
                  Live Headlines <span className="text-xs px-2 py-0.5 rounded-full bg-white/10 text-white/70">20% Weight</span>
                </h3>
                <p className="text-sm text-white/40 mt-1 leading-relaxed">
                  In real-time, the system leverages multi-layered RSS parsing across endpoints like The Economic Times, Google News, and Livemint, calculating the ratio of bullish catalyst phrases versus systemic risks.
                </p>
              </div>
            </div>

            <div className="flex gap-4 items-start">
              <div className="p-3 rounded-xl bg-purple-500/10 text-purple-400">
                <Globe className="w-6 h-6" />
              </div>
              <div className="flex-1">
                <h3 className="text-white font-semibold flex items-center gap-2">
                  Macro & Sector Context <span className="text-xs px-2 py-0.5 rounded-full bg-white/10 text-white/70">20% Weight</span>
                </h3>
                <p className="text-sm text-white/40 mt-1 leading-relaxed">
                  Contextualizes the specific equity within broader economic machinery (e.g. RBI rate expectations, inflation, or government policy shifts) to determine macro-safety.
                </p>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  )
}
