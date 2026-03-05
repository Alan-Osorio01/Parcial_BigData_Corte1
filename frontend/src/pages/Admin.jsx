import { useAuth } from '../context/AuthContext'
import { useNavigate, Link } from 'react-router-dom'
import { useEffect } from 'react'

function Admin() {
  const { user } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (!user || user.role !== 'admin') navigate('/')
  }, [user])

  if (!user || user.role !== 'admin') return null

  return (
    <div style={{ padding:'2rem', maxWidth:700, margin:'0 auto' }}>
      <h2 style={{ color:'#1a1a2e' }}>👑 Panel de Administración</h2>
      <p style={{ color:'#666', marginBottom:'2rem' }}>Bienvenido, <strong>{user.email}</strong></p>

      <div style={{ display:'grid', gap:'1rem', gridTemplateColumns:'1fr 1fr' }}>
        <div style={{ background:'white', padding:'1.5rem', borderRadius:8, boxShadow:'0 2px 8px rgba(0,0,0,0.1)' }}>
          <h3>🎵 Canciones</h3>
          <p style={{ color:'#666', marginTop:'0.5rem' }}>Gestiona el catálogo de canciones</p>
          <Link to="/tracks" style={{ display:'inline-block', marginTop:'1rem', background:'#1a1a2e', color:'white', padding:'8px 16px', borderRadius:4, textDecoration:'none' }}>Ver Canciones</Link>
        </div>
        <div style={{ background:'white', padding:'1.5rem', borderRadius:8, boxShadow:'0 2px 8px rgba(0,0,0,0.1)' }}>
          <h3>🛒 Compras</h3>
          <p style={{ color:'#666', marginTop:'0.5rem' }}>Gestiona las compras de clientes</p>
          <Link to="/purchase" style={{ display:'inline-block', marginTop:'1rem', background:'#e94560', color:'white', padding:'8px 16px', borderRadius:4, textDecoration:'none' }}>Ver Compras</Link>
        </div>
        <div style={{ background:'white', padding:'1.5rem', borderRadius:8, boxShadow:'0 2px 8px rgba(0,0,0,0.1)', gridColumn:'1/-1' }}>
          <h3>ℹ️ Información del sistema</h3>
          <p style={{ color:'#666', marginTop:'0.5rem' }}>Backend: <code>http://44.216.77.83:8000/api</code></p>
          <p style={{ color:'#666' }}>Rol actual: <strong style={{ color:'#e94560' }}>{user.role}</strong></p>
        </div>
      </div>
    </div>
  )
}

export default Admin
