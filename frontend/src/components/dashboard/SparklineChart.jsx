import {
  AreaChart,
  Area,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { motion } from 'framer-motion'
import GlassPanel from '../layout/GlassPanel'

export default function SparklineChart({ data }) {
  if (!data || data.length === 0) return null

  const isPositive = data[data.length - 1].close >= data[0].close
  const strokeColor = isPositive ? '#22c55e' : '#ef4444'

  const firstPrice = data[0].close
  const lastPrice = data[data.length - 1].close
  const change = ((lastPrice - firstPrice) / firstPrice * 100).toFixed(2)

  return (
    <GlassPanel className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-white/50 text-xs uppercase tracking-wider font-medium">
          1-Year Performance
        </h3>
        <motion.span
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className={`text-sm font-semibold ${isPositive ? 'text-emerald-400' : 'text-red-400'}`}
        >
          {isPositive ? '+' : ''}{change}%
        </motion.span>
      </div>

      <ResponsiveContainer width="100%" height={160}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="sparkGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={strokeColor} stopOpacity={0.25} />
              <stop offset="100%" stopColor={strokeColor} stopOpacity={0} />
            </linearGradient>
          </defs>
          <XAxis dataKey="date" hide />
          <YAxis domain={['auto', 'auto']} hide />
          <Tooltip
            contentStyle={{
              background: 'rgba(0, 0, 0, 0.85)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '12px',
              fontSize: '12px',
              padding: '8px 12px',
            }}
            labelStyle={{ color: '#999', fontSize: '11px' }}
            formatter={(value) => [`₹${value.toFixed(2)}`, 'Close']}
          />
          <Area
            type="monotone"
            dataKey="close"
            stroke={strokeColor}
            fill="url(#sparkGradient)"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4, fill: strokeColor, stroke: '#fff', strokeWidth: 1 }}
          />
        </AreaChart>
      </ResponsiveContainer>

      <div className="flex justify-between mt-2 text-[10px] text-white/30">
        <span>{data[0].date}</span>
        <span>{data[data.length - 1].date}</span>
      </div>
    </GlassPanel>
  )
}
