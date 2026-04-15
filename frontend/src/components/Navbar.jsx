import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useCart } from '../context/CartContext'

const link = {
  color: '#c8cfe8',
  textDecoration: 'none',
  fontSize: '0.9rem',
  padding: '6px 10px',
  borderRadius: '6px',
  transition: 'color 0.2s'
}

function Navbar() {
  const { user, logout } = useAuth()
  const { cart } = useCart()
  const navigate = useNavigate()

  const handleLogout = () => { logout(); navigate('/login') }

  return (
    <nav style={{
      background: '#1a1a2e',
      borderBottom: '1px solid #2d2d4e',
      padding: '0 32px',
      height: '62px',
      display: 'flex',
      alignItems: 'center',
      gap: '4px',
      position: 'sticky',
      top: 0,
      zIndex: 100,
      boxShadow: '0 2px 12px rgba(0,0,0,0.4)'
    }}>
      <Link to="/" style={{ color: '#e94560', fontWeight: '800', fontSize: '1.1rem', textDecoration: 'none', marginRight: '20px', letterSpacing: '-0.5px' }}>
        🎵 Chinook Music
      </Link>

      <Link to="/tracks" style={link}>Canciones</Link>

      {user?.role === 'admin' && (
        <Link to="/admin" style={{ ...link, color: '#fbbf24' }}>👑 Admin</Link>
      )}

      <div style={{ marginLeft: 'auto', display: 'flex', gap: '10px', alignItems: 'center' }}>
        <Link to="/purchase" style={{ position: 'relative', textDecoration: 'none', display: 'flex', alignItems: 'center' }}>
          <span style={{ fontSize: '1.3rem' }} title="Carrito">🛒</span>
          {cart.length > 0 && (
            <span style={{
              position: 'absolute', top: '-6px', right: '-8px',
              background: '#e94560', color: 'white', borderRadius: '50%',
              width: '17px', height: '17px', fontSize: '0.65rem',
              display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: '700'
            }}>{cart.length}</span>
          )}
        </Link>

        {user ? (
          <>
            <Link to="/orders" style={link}>Mis Compras</Link>
            <span style={{ color: '#64748b', fontSize: '0.8rem', padding: '0 4px' }}>|</span>
            <span style={{ color: '#94a3b8', fontSize: '0.85rem' }}>
              {user.role === 'admin' ? '👑' : '👤'} {user.email.split('@')[0]}
            </span>
            <button onClick={handleLogout} style={{
              background: 'transparent', color: '#e94560',
              border: '1px solid #e94560', padding: '5px 14px',
              borderRadius: '6px', cursor: 'pointer', fontSize: '0.85rem',
              marginLeft: '4px'
            }}>Salir</button>
          </>
        ) : (
          <>
            <Link to="/login" style={link}>Entrar</Link>
            <Link to="/register" style={{
              background: '#e94560', color: 'white', textDecoration: 'none',
              padding: '7px 16px', borderRadius: '6px', fontSize: '0.85rem', fontWeight: '600'
            }}>Registro</Link>
          </>
        )}
      </div>
    </nav>
  )
}

export default Navbar
