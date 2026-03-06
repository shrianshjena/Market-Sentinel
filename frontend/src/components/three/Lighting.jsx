export default function Lighting() {
  return (
    <>
      <ambientLight intensity={0.3} />
      <directionalLight position={[5, 5, 5]} intensity={1} color="#ffffff" />
      <directionalLight position={[-5, 3, -5]} intensity={0.4} color="#4A90D9" />
      <pointLight position={[0, -2, 3]} intensity={0.3} color="#f97316" />
    </>
  )
}
