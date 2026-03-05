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
    <div style={{ minHeight:'80vh', background:'#f0f4f8', display:'flex', alignItems:'center', justifyContent:'center' }}>
      <div style={{ background:'white', padding:'2.5rem', borderRadius:12, boxShadow:'0 4px 20px rgba(0,0,0,0.1)', width:'100%', maxWidth:400 }}>
        <h2 style={{ textAlign:'center', color:'#1a1a2e', marginBottom:'1.5rem' }}>📝 Crear Cuenta</h2>
        {success && <div style={{ background:'#e0ffe0', padding:'0.75rem', borderRadius:6, marginBottom:'1rem', color:'#060' }}>{success}</div>}
        {error && <div style={{ background:'#ffe0e0', padding:'0.75rem', borderRadius:6, marginBottom:'1rem', color:'#c00' }}>{error}</div>}
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom:'1rem' }}>
            <label style={{ fontWeight:'bold' }}>Email</label><br/>
            <input type="email" value={form.email} required onChange={e => setForm({...form, email:e.target.value})}
              style={{ width:'100%', padding:'10px', marginTop:6, borderRadius:6, border:'1px solid #ccc', fontSize:'1rem' }} />
          </div>
          <div style={{ marginBottom:'1.5rem' }}>
            <label style={{ fontWeight:'bold' }}>Contraseña</label><br/>
            <input type="password" value={form.password} required minLength={6} onChange={e => setForm({...form, password:e.target.value})}
              style={{ width:'100%', padding:'10px', marginTop:6, borderRadius:6, border:'1px solid #ccc', fontSize:'1rem' }} />
          </div>
          <button type="submit" disabled={loading}
            style={{ width:'100%', padding:'12px', background:'#16a34a', color:'white', border:'none', borderRadius:6, cursor:'pointer', fontSize:'1rem', fontWeight:'bold' }}>
            {loading ? 'Creando...' : 'Registrarse'}
          </button>
        </form>
        <p style={{ textAlign:'center', marginTop:'1rem' }}>¿Ya tienes cuenta? <Link to="/login" style={{ color:'#e94560' }}>Inicia sesión</Link></p>
      </div>
    </div>
  )
}

export default Register
