import { motion } from 'framer-motion'
import { TrendingUp, Newspaper, MessageSquare, Target, Building2, Globe2, Activity, PieChart } from 'lucide-react'
import GlassPanel from '../layout/GlassPanel'

const sections = [
  { key: 'company_details', label: 'Company Overview', icon: Building2 },
  { key: 'overall_context', label: 'Macro Context', icon: Globe2 },
  { key: 'fundamental_analysis', label: 'Fundamental Valuation', icon: PieChart },
  { key: 'trend_summary', label: 'Trend Analysis', icon: TrendingUp },
  { key: 'headline_impact', label: 'Headline Pulse', icon: Newspaper },
  { key: 'market_sentiment', label: 'Market Sentiment', icon: Activity },
  { key: 'sentiment_consistency', label: 'Sentiment Consistency', icon: MessageSquare },
  { key: 'recommendation', label: 'Recommendation', icon: Target },
]

export default function AnalystSummary({ analysis }) {
  if (!analysis) return null

  return (
    <GlassPanel className="p-6">
      <h3 className="text-white/50 text-xs uppercase tracking-wider font-medium mb-5">
        Intelligence Engine Analysis
      </h3>

      <div className="space-y-4">
        {sections.map(({ key, label, icon: Icon }, index) => (
          <motion.div
            key={key}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 + index * 0.15 }}
            className="flex gap-3"
          >
            <div className="mt-0.5 flex-shrink-0">
              <div className="w-7 h-7 rounded-lg bg-white/5 flex items-center justify-center">
                <Icon className="w-3.5 h-3.5 text-white/40" />
              </div>
            </div>
            <div className="min-w-0">
              <h4 className="text-white/60 text-[11px] uppercase tracking-wider font-medium mb-1">
                {label}
              </h4>
              <p className={`text-sm leading-relaxed ${
                key === 'recommendation'
                  ? 'text-white font-semibold'
                  : 'text-white/80'
              }`}>
                {analysis[key] || 'Data unavailable'}
              </p>
            </div>
          </motion.div>
        ))}
      </div>
    </GlassPanel>
  )
}
