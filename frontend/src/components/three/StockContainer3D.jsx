import { useRef, useState } from 'react'
import { useFrame } from '@react-three/fiber'
import { RoundedBox, Float, Text } from '@react-three/drei'
import { getTicker3DConfig } from '../../utils/constants'

export default function StockContainer3D({
  ticker,
  position = [0, 0, 0],
  onClick,
  isSelected = false,
}) {
  const meshRef = useRef()
  const [hovered, setHovered] = useState(false)
  const config = getTicker3DConfig(ticker)

  useFrame((state) => {
    if (!meshRef.current) return
    // Gentle idle rotation
    meshRef.current.rotation.y =
      Math.sin(state.clock.elapsedTime * 0.4 + position[1]) * 0.12
    meshRef.current.rotation.x =
      Math.sin(state.clock.elapsedTime * 0.3 + position[1]) * 0.05

    // Scale on hover/select
    const targetScale = hovered || isSelected ? 1.08 : 1
    meshRef.current.scale.lerp(
      { x: targetScale, y: targetScale, z: targetScale },
      0.1
    )
  })

  const emissiveIntensity = isSelected ? 0.6 : hovered ? 0.4 : 0.15

  return (
    <Float speed={1.5} rotationIntensity={0.15} floatIntensity={0.4}>
      <group
        ref={meshRef}
        position={position}
        onClick={(e) => {
          e.stopPropagation()
          onClick?.(ticker)
        }}
        onPointerOver={(e) => {
          e.stopPropagation()
          setHovered(true)
          document.body.style.cursor = 'pointer'
        }}
        onPointerOut={() => {
          setHovered(false)
          document.body.style.cursor = 'default'
        }}
      >
        {/* Main container body */}
        <RoundedBox args={[2.8, 1.6, 0.25]} radius={0.12} smoothness={4}>
          <meshPhysicalMaterial
            color={config.color}
            emissive={config.emissive}
            emissiveIntensity={emissiveIntensity}
            metalness={config.metalness}
            roughness={config.roughness}
            clearcoat={1}
            clearcoatRoughness={0.1}
            reflectivity={1}
            envMapIntensity={1.2}
          />
        </RoundedBox>

        {/* Edge accent strip */}
        <mesh position={[0, -0.7, 0.13]}>
          <boxGeometry args={[2.4, 0.04, 0.02]} />
          <meshStandardMaterial
            color={config.emissive}
            emissive={config.emissive}
            emissiveIntensity={isSelected ? 2 : 0.8}
          />
        </mesh>

        {/* Ticker label */}
        <Text
          position={[0, 0.2, 0.14]}
          fontSize={0.28}
          color="white"
          anchorX="center"
          anchorY="middle"
          letterSpacing={0.08}
          font={undefined}
        >
          {ticker}
        </Text>

        {/* Description label */}
        <Text
          position={[0, -0.2, 0.14]}
          fontSize={0.12}
          color="rgba(255,255,255,0.5)"
          anchorX="center"
          anchorY="middle"
          font={undefined}
        >
          {config.description}
        </Text>

        {/* Selection indicator glow */}
        {isSelected && (
          <pointLight
            position={[0, 0, 0.5]}
            intensity={0.5}
            color={config.color}
            distance={3}
          />
        )}
      </group>
    </Float>
  )
}
