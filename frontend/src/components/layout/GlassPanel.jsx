import { motion } from 'framer-motion'

export default function GlassPanel({ children, className = '', animate = true, ...props }) {
  const Component = animate ? motion.div : 'div'
  const animateProps = animate
    ? {
        initial: { opacity: 0, y: 20 },
        animate: { opacity: 1, y: 0 },
        transition: { duration: 0.5 },
      }
    : {}

  return (
    <Component
      className={`bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl shadow-2xl shadow-black/20 ${className}`}
      {...animateProps}
      {...props}
    >
      {children}
    </Component>
  )
}
