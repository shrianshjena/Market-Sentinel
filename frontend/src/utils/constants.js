// Featured tickers displayed as 3D containers on the landing page
export const FEATURED_TICKERS = ['TATASTEEL', 'COALINDIA', 'NATIONALUM']

// Visual config for featured tickers (3D materials)
export const TICKER_3D_CONFIG = {
  TATASTEEL: {
    label: 'Tata Steel',
    color: '#4A90D9',
    emissive: '#1a3a6a',
    metalness: 0.9,
    roughness: 0.15,
    description: 'Steel & Iron',
  },
  COALINDIA: {
    label: 'Coal India',
    color: '#3D3D3D',
    emissive: '#4A3728',
    metalness: 0.7,
    roughness: 0.4,
    description: 'Mining & Minerals',
  },
  NATIONALUM: {
    label: 'NALCO',
    color: '#C0C0C0',
    emissive: '#6B7B8D',
    metalness: 0.95,
    roughness: 0.1,
    description: 'Aluminium',
  },
}

// Default 3D config for any non-featured ticker
export const DEFAULT_3D_CONFIG = {
  color: '#5A6B7C',
  emissive: '#2A3B4C',
  metalness: 0.8,
  roughness: 0.2,
  description: 'Equity',
}

export function getTicker3DConfig(symbol) {
  return TICKER_3D_CONFIG[symbol] || { ...DEFAULT_3D_CONFIG, label: symbol }
}

export const SCORE_CONFIG = {
  'Strong Catalyst': { color: '#22c55e', min: 81 },
  'Bullish Lean': { color: '#84cc16', min: 61 },
  'Neutral': { color: '#eab308', min: 41 },
  'Cautionary': { color: '#f97316', min: 21 },
  'Distressed': { color: '#ef4444', min: 0 },
}

export function getScoreColor(score) {
  if (score >= 81) return '#22c55e'
  if (score >= 61) return '#84cc16'
  if (score >= 41) return '#eab308'
  if (score >= 21) return '#f97316'
  return '#ef4444'
}
