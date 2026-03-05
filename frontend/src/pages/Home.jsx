import { Link } from 'react-router-dom'

function Home() {
  return (
    <div style={{ textAlign:'center', padding:'60px 20px' }}>
      <h1 style={{ color:'#1a1a2e', fontSize:'2.5rem', marginBottom:'1rem' }}>🎵 Bienvenido a Chinook Music Store</h1>
      <p style={{ color:'#666', fontSize:'1.2rem', marginBottom:'2rem' }}>Compra tus canciones favoritas</p>
      <div style={{ display:'flex', gap:'1rem', justifyContent:'center' }}>
        <Link to="/tracks" style={{ background:'#1a1a2e', color:'white', padding:'12px 24px', borderRadius:6, textDecoration:'none' }}>Ver Canciones</Link>
        <Link to="/purchase" style={{ background:'#e94560', color:'white', padding:'12px 24px', borderRadius:6, textDecoration:'none' }}>Comprar</Link>
      </div>
    </div>
  )
}

export default Home
