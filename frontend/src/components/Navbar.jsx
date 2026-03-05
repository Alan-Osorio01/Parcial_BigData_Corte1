import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => { logout(); navigate('/login') }

  return (
    <nav style={{ background:'#1a1a2e', padding:'15px 30px', display:'flex', gap:'20px', alignItems:'center' }}>
      <span style={{ color:'#e94560', fontWeight:'bold', fontSize:'20px' }}>🎵 Chinook Music</span>
      <Link to="/" style={{ color:'white', textDecoration:'none' }}>Inicio</Link>
      <Link to="/tracks" style={{ color:'white', textDecoration:'none' }}>Canciones</Link>
      <Link to="/purchase" style={{ color:'white', textDecoration:'none' }}>Comprar</Link>
      {user?.role === 'admin' && (
        <Link to="/admin" style={{ color:'#ffd700', textDecoration:'none', fontWeight:'bold' }}>👑 Admin</Link>
      )}
      <div style={{ marginLeft:'auto', display:'flex', gap:'15px', alignItems:'center' }}>
        {user ? (
          <>
            <span style={{ color:'#90cdf4' }}>{user.role === 'admin' ? '👑' : '👤'} {user.email}</span>
            <button onClick={handleLogout} style={{ background:'#e94560', color:'white', border:'none', padding:'6px 14px', borderRadius:4, cursor:'pointer' }}>Salir</button>
          </>
        ) : (
          <>
            <Link to="/login" style={{ color:'#90cdf4', textDecoration:'none' }}>Login</Link>
            <Link to="/register" style={{ color:'#90cdf4', textDecoration:'none' }}>Registro</Link>
          </>
        )}
      </div>
    </nav>
  )
}

export default Navbar
