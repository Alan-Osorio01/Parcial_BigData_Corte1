import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { registerUser } from '../services/api'

function Register() {
  const [form, setForm] = useState({ email: '', password: '' })
  const [success, setSuccess] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault(); setError(''); setLoading(true)
    try {
      await registerUser({ ...form, role: 'usuario' })
      setSuccess('¡Cuenta creada! Redirigiendo...')
      setTimeout(() => navigate('/login'), 1500)
    } catch (err) { setError(err.response?.data?.detail || 'Error al registrar') }
    finally { setLoading(false) }
  }

  return (
    <div style={{ minHeight: '85vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '24px' }}>
      <div style={{ width: '100%', maxWidth: 400 }}>
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <div style={{ fontSize: '2.5rem', marginBottom: '12px' }}>🎵</div>
          <h2 style={{ color: '#f0f4ff', fontSize: '1.6rem', fontWeight: '700', margin: '0 0 6px' }}>Crear Cuenta</h2>
          <p style={{ color: '#64748b', margin: 0, fontSize: '0.9rem' }}>Únete a Chinook Music Store</p>
        </div>

        <div style={{ background: '#1a1a2e', border: '1px solid #2d2d4e', borderRadius: '16px', padding: '32px' }}>
          {success && (
            <div style={{ background: '#0d2d1b', border: '1px solid #10b981', color: '#6ee7b7', padding: '10px 14px', borderRadius: '8px', fontSize: '0.85rem', marginBottom: '20px' }}>
              {success}
            </div>
          )}
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
            <div style={{ marginBottom: '8px' }}>
              <label style={{ color: '#94a3b8', fontSize: '0.85rem', display: 'block', marginBottom: '6px' }}>Contraseña</label>
              <input
                type="password" value={form.password} required minLength={6}
                onChange={e => setForm({ ...form, password: e.target.value })}
                placeholder="Mínimo 6 caracteres"
                style={inputStyle}
              />
            </div>
            <p style={{ color: '#64748b', fontSize: '0.78rem', marginBottom: '20px' }}>
              💡 Para ver historial de compras, usa un email que exista en la BD Chinook.
            </p>
            <button type="submit" disabled={loading} style={{
              width: '100%', padding: '12px', background: loading ? '#2d2d4e' : '#10b981',
              color: 'white', border: 'none', borderRadius: '8px',
              cursor: loading ? 'not-allowed' : 'pointer', fontSize: '0.95rem', fontWeight: '700'
            }}>
              {loading ? 'Creando...' : 'Registrarse'}
            </button>
          </form>
          <p style={{ textAlign: 'center', marginTop: '20px', color: '#64748b', fontSize: '0.9rem' }}>
            ¿Ya tienes cuenta?{' '}
            <Link to="/login" style={{ color: '#e94560', textDecoration: 'none', fontWeight: '600' }}>Inicia sesión</Link>
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

export default Register
