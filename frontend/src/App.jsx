import Navbar from './components/layout/Navbar'
import Footer from './components/layout/Footer'
import StockScene from './components/three/StockScene'
import TickerSelector from './components/dashboard/TickerSelector'
import BentoGrid from './components/dashboard/BentoGrid'
import { useStockData } from './hooks/useStockData'

function App() {
  // Initialize the data fetching hook
  useStockData()

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-slate-900 to-gray-950 relative overflow-x-hidden">
      {/* Ambient background glow */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-500/5 rounded-full blur-3xl" />
        <div className="absolute bottom-1/3 right-1/4 w-80 h-80 bg-purple-500/5 rounded-full blur-3xl" />
      </div>

      <Navbar />

      <main className="relative pt-24 pb-8">
        {/* Hero Section */}
        <section className="max-w-7xl mx-auto px-6 mb-12">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
            {/* Left: Hero text */}
            <div>
              <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold text-white leading-tight tracking-tight">
                India's Premiere
                <br />
                Stock Sentinel.
              </h2>
              <p className="text-lg text-white/40 mt-4 max-w-md leading-relaxed">
                Analyze 1 Year. Understand Sentiment.
                <br />
                AI-Driven Equity Research.
              </p>

              <div className="mt-8">
                <TickerSelector />
              </div>

              <p className="text-white/20 text-xs mt-4">
                Select a ticker above or click a 3D container to begin analysis
              </p>
            </div>

            {/* Right: 3D Scene */}
            <div>
              <StockScene />
            </div>
          </div>
        </section>

        {/* Dashboard */}
        <section className="mb-8">
          <BentoGrid />
        </section>
      </main>

      <Footer />
    </div>
  )
}

export default App
