import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { loginUser } from '../services/api'
import { useAuth } from '../context/AuthContext'

function Login() {
  const [form, setForm] = useState({ email: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault(); setError(''); setLoading(true)
    try {
      const res = await loginUser(form)
      login({ email: form.email, role: res.data.role }, res.data.access_token)
      navigate('/')
    } catch (err) { setError(err.response?.data?.detail || 'Credenciales incorrectas') }
    finally { setLoading(false) }
  }

  return (
    <div style={{ minHeight: '85vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '24px' }}>
      <div style={{ width: '100%', maxWidth: 400 }}>
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <div style={{ fontSize: '2.5rem', marginBottom: '12px' }}>🎵</div>
          <h2 style={{ color: '#f0f4ff', fontSize: '1.6rem', fontWeight: '700', margin: '0 0 6px' }}>Iniciar Sesión</h2>
          <p style={{ color: '#64748b', margin: 0, fontSize: '0.9rem' }}>Bienvenido de nuevo</p>
        </div>

        <div style={{ background: '#1a1a2e', border: '1px solid #2d2d4e', borderRadius: '16px', padding: '32px' }}>
          {error && (
            <div style={{ background: '#2d1b1b', border: '1px solid #e94560', color: '#f87171', padding: '10px 14px', borderRadius: '8px', fontSize: '0.85rem', marginBottom: '20px' }}>
              {error}
            </div>
          )}
          <form onSubmit={handleSubmit}>
            <div style={{ marginBottom: '16px' }}>
              <label style={{ color: '#94a3b8', fontSize: '0.85rem', display: 'block', marginBottom: '6px' }}>Email</label>
              <input
                type="email" value={form.email} required
                onChange={e => setForm({ ...form, email: e.target.value })}
                placeholder="tu@email.com"
                style={inputStyle}
              />
            </div>
            <div style={{ marginBottom: '24px' }}>
              <label style={{ color: '#94a3b8', fontSize: '0.85rem', display: 'block', marginBottom: '6px' }}>Contraseña</label>
              <input
                type="password" value={form.password} required
                onChange={e => setForm({ ...form, password: e.target.value })}
                placeholder="••••••••"
                style={inputStyle}
              />
            </div>
            <button type="submit" disabled={loading} style={{
              width: '100%', padding: '12px', background: loading ? '#2d2d4e' : '#e94560',
              color: 'white', border: 'none', borderRadius: '8px',
              cursor: loading ? 'not-allowed' : 'pointer', fontSize: '0.95rem', fontWeight: '700'
            }}>
              {loading ? 'Ingresando...' : 'Ingresar'}
            </button>
          </form>
          <p style={{ textAlign: 'center', marginTop: '20px', color: '#64748b', fontSize: '0.9rem' }}>
            ¿No tienes cuenta?{' '}
            <Link to="/register" style={{ color: '#e94560', textDecoration: 'none', fontWeight: '600' }}>Regístrate</Link>
          </p>
        </div>
      </div>
    </div>
  )
}

const inputStyle = {
  width: '100%', padding: '10px 14px', borderRadius: '8px',
  border: '1px solid #2d2d4e', background: '#0f0f1a',
  color: '#f0f4ff', fontSize: '0.95rem', outline: 'none',
  boxSizing: 'border-box'
}

export default Login
