import { Activity, Info } from 'lucide-react'
import useStockStore from '../../store/useStockStore'

export default function Navbar() {
  const { setInfoModalOpen } = useStockStore()
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-white/5 backdrop-blur-xl border-b border-white/10">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
            <Activity className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-white font-bold text-lg tracking-tight leading-none">
              Market Sentinel
            </h1>
            <p className="text-white/40 text-[11px] italic mt-0.5">
              Developed by Shriansh Jena
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <span className="text-white/30 text-xs hidden sm:block">
            AI-Driven Equity Research
          </span>
          <button 
            onClick={() => setInfoModalOpen(true)}
            className="text-white/30 hover:text-white/70 transition-colors mr-2 cursor-help"
            title="How the Sentinel Score works"
          >
            <Info className="w-4 h-4" />
          </button>
          <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
        </div>
      </div>
    </nav>
  )
}
