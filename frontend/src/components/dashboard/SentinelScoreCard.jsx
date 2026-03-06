import { motion } from 'framer-motion'
import GlassPanel from '../layout/GlassPanel'
import { getScoreColor } from '../../utils/constants'

export default function SentinelScoreCard({ score, category }) {
  const color = getScoreColor(score)
  const circumference = 2 * Math.PI * 52
  const offset = circumference * (1 - score / 100)

  return (
    <GlassPanel className="p-6 flex flex-col items-center justify-center">
      <h3 className="text-white/50 text-xs uppercase tracking-wider font-medium mb-4">
        Sentinel Score
      </h3>

      <div className="relative w-36 h-36">
        {/* Background ring */}
        <svg className="w-full h-full -rotate-90" viewBox="0 0 120 120">
          <circle
            cx="60"
            cy="60"
            r="52"
            fill="none"
            stroke="rgba(255,255,255,0.05)"
            strokeWidth="8"
          />
          <motion.circle
            cx="60"
            cy="60"
            r="52"
            fill="none"
            stroke={color}
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: offset }}
            transition={{ duration: 1.5, ease: 'easeOut', delay: 0.3 }}
          />
        </svg>

        {/* Score number */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <motion.span
            className="text-4xl font-bold text-white tabular-nums"
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.5 }}
          >
            {score}
          </motion.span>
          <span className="text-white/30 text-[10px] uppercase tracking-widest mt-1">
            / 100
          </span>
        </div>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8 }}
        className="mt-4 px-4 py-1.5 rounded-full text-xs font-semibold"
        style={{ backgroundColor: `${color}20`, color }}
      >
        {category}
      </motion.div>
    </GlassPanel>
  )
}
