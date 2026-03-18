import { Suspense } from 'react'
import { Canvas } from '@react-three/fiber'
import { Environment, ContactShadows } from '@react-three/drei'
import StockContainer3D from './StockContainer3D'
import Lighting from './Lighting'
import useStockStore from '../../store/useStockStore'
import { FEATURED_TICKERS } from '../../utils/constants'

export default function StockScene() {
  const { selectedTicker, setTicker } = useStockStore()

  const positions = [
    [0, 1.2, 0],       // TATASTEEL - top
    [1.2, -0.2, -0.5], // COALINDIA - middle right
    [-0.8, -1.5, -1],  // NALCO - bottom left
    [1.6, 1.3, -1.2],  // HINDZINC - top right
    [-1.4, 0.4, -0.8], // HINDCOPPER - middle left
  ]

  return (
    <div className="w-full h-[420px] relative">
      <Canvas
        camera={{ position: [0, 0, 6], fov: 42 }}
        dpr={[1, 2]}
        gl={{ antialias: true, alpha: true }}
        style={{ background: 'transparent' }}
      >
        <Suspense fallback={null}>
          <Lighting />
          {FEATURED_TICKERS.map((ticker, i) => (
            <StockContainer3D
              key={ticker}
              ticker={ticker}
              position={positions[i]}
              onClick={setTicker}
              isSelected={selectedTicker === ticker}
            />
          ))}
          <ContactShadows
            position={[0, -2.5, 0]}
            opacity={0.3}
            blur={2.5}
            far={4}
          />
          <Environment preset="city" />
        </Suspense>
      </Canvas>
    </div>
  )
}
