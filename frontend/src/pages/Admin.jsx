import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { getAdminUsers, deleteUser, addTrack, getGenres } from '../services/api'

function Admin() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [tab, setTab] = useState('users')

  // Usuarios
  const [users, setUsers] = useState([])
  const [loadingUsers, setLoadingUsers] = useState(false)
  const [deleteError, setDeleteError] = useState('')

  // Nueva canción
  const [genres, setGenres] = useState([])
  const [trackForm, setTrackForm] = useState({ name: '', artist_name: '', genre_id: '', unit_price: '0.99' })
  const [trackSuccess, setTrackSuccess] = useState('')
  const [trackError, setTrackError] = useState('')
  const [savingTrack, setSavingTrack] = useState(false)

  useEffect(() => {
    if (!user || user.role !== 'admin') navigate('/')
  }, [user])

  useEffect(() => {
    if (tab === 'users') loadUsers()
    if (tab === 'tracks') loadGenres()
  }, [tab])

  const loadUsers = async () => {
    setLoadingUsers(true); setDeleteError('')
    try { const r = await getAdminUsers(); setUsers(r.data) }
    catch { setDeleteError('No se pudo cargar la lista de usuarios') }
    finally { setLoadingUsers(false) }
  }

  const loadGenres = async () => {
    try { const r = await getGenres(); setGenres(r.data) } catch {}
  }

  const handleDelete = async (userId, email) => {
    if (!confirm(`¿Eliminar a ${email}?`)) return
    try {
      await deleteUser(userId)
      setUsers(prev => prev.filter(u => u.user_id !== userId))
    } catch (e) { setDeleteError(e.response?.data?.detail || 'Error al eliminar') }
  }

  const handleAddTrack = async (e) => {
    e.preventDefault(); setTrackError(''); setTrackSuccess(''); setSavingTrack(true)
    try {
      const res = await addTrack({ ...trackForm, genre_id: parseInt(trackForm.genre_id), unit_price: parseFloat(trackForm.unit_price) })
      setTrackSuccess(`✅ "${res.data.name}" de ${res.data.artist} agregada (ID: ${res.data.track_id})`)
      setTrackForm({ name: '', artist_name: '', genre_id: trackForm.genre_id, unit_price: '0.99' })
    } catch (e) { setTrackError(e.response?.data?.detail || 'Error al agregar la canción') }
    finally { setSavingTrack(false) }
  }

  if (!user || user.role !== 'admin') return null

  return (
    <div style={{ maxWidth: 860, margin: '0 auto', padding: '32px 24px' }}>
      {/* Header */}
      <div style={{ marginBottom: '28px' }}>
        <h2 style={{ color: '#f0f4ff', fontSize: '1.6rem', fontWeight: '700', margin: '0 0 4px' }}>👑 Panel de Administración</h2>
        <p style={{ color: '#64748b', margin: 0, fontSize: '0.9rem' }}>{user.email}</p>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '4px', marginBottom: '24px', background: '#1a1a2e', padding: '4px', borderRadius: '10px', width: 'fit-content' }}>
        {[
          { key: 'users', label: '👥 Usuarios' },
          { key: 'tracks', label: '🎵 Agregar Canción' }
        ].map(t => (
          <button key={t.key} onClick={() => setTab(t.key)} style={{
            padding: '8px 20px', borderRadius: '7px', border: 'none', cursor: 'pointer',
            background: tab === t.key ? '#e94560' : 'transparent',
            color: tab === t.key ? 'white' : '#94a3b8',
            fontSize: '0.9rem', fontWeight: tab === t.key ? '600' : '400'
          }}>{t.label}</button>
        ))}
      </div>

      {/* ── TAB: USUARIOS ── */}
      {tab === 'users' && (
        <div>
          {deleteError && (
            <div style={{ background: '#2d1b1b', border: '1px solid #e94560', color: '#f87171', padding: '10px 14px', borderRadius: '8px', fontSize: '0.85rem', marginBottom: '16px' }}>
              {deleteError}
            </div>
          )}

          {loadingUsers ? (
            <div style={{ textAlign: 'center', padding: '40px', color: '#64748b' }}>Cargando usuarios...</div>
          ) : (
            <div style={{ background: '#1a1a2e', border: '1px solid #2d2d4e', borderRadius: '12px', overflow: 'hidden' }}>
              {/* Header tabla */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 100px 160px 80px', padding: '12px 20px', background: '#161628', borderBottom: '1px solid #2d2d4e' }}>
                <span style={{ color: '#64748b', fontSize: '0.8rem', fontWeight: '600', textTransform: 'uppercase' }}>Email</span>
                <span style={{ color: '#64748b', fontSize: '0.8rem', fontWeight: '600', textTransform: 'uppercase' }}>Rol</span>
                <span style={{ color: '#64748b', fontSize: '0.8rem', fontWeight: '600', textTransform: 'uppercase' }}>Creado</span>
                <span></span>
              </div>

              {users.length === 0 ? (
                <div style={{ padding: '32px', textAlign: 'center', color: '#64748b' }}>No hay usuarios registrados</div>
              ) : users.map(u => (
                <div key={u.user_id} style={{
                  display: 'grid', gridTemplateColumns: '1fr 100px 160px 80px',
                  padding: '14px 20px', borderBottom: '1px solid #2d2d4e', alignItems: 'center'
                }}>
                  <span style={{ color: '#f0f4ff', fontSize: '0.9rem', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {u.email}
                    {u.email === user.email && <span style={{ color: '#64748b', fontSize: '0.75rem', marginLeft: '8px' }}>(tú)</span>}
                  </span>
                  <span>
                    <span style={{
                      background: u.role === 'admin' ? '#3b1f6e' : '#1e2a3a',
                      color: u.role === 'admin' ? '#c084fc' : '#60a5fa',
                      padding: '3px 10px', borderRadius: '20px', fontSize: '0.75rem', fontWeight: '600'
                    }}>{u.role}</span>
                  </span>
                  <span style={{ color: '#64748b', fontSize: '0.82rem' }}>
                    {u.created_at ? new Date(u.created_at).toLocaleDateString('es-CO') : '—'}
                  </span>
                  <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                    {u.email !== user.email && (
                      <button onClick={() => handleDelete(u.user_id, u.email)} style={{
                        background: 'transparent', color: '#e94560',
                        border: '1px solid #e94560', padding: '5px 12px',
                        borderRadius: '6px', cursor: 'pointer', fontSize: '0.78rem'
                      }}>Eliminar</button>
                    )}
                  </div>
                </div>
              ))}

              <div style={{ padding: '12px 20px', borderTop: '1px solid #2d2d4e', color: '#64748b', fontSize: '0.8rem' }}>
                {users.length} usuario{users.length !== 1 ? 's' : ''} registrado{users.length !== 1 ? 's' : ''}
              </div>
            </div>
          )}
        </div>
      )}

      {/* ── TAB: AGREGAR CANCIÓN ── */}
      {tab === 'tracks' && (
        <div style={{ maxWidth: 520 }}>
          <div style={{ background: '#1a1a2e', border: '1px solid #2d2d4e', borderRadius: '12px', padding: '28px' }}>
            <h3 style={{ color: '#f0f4ff', margin: '0 0 20px', fontSize: '1.1rem' }}>Nueva Canción</h3>

            {trackSuccess && (
              <div style={{ background: '#0d2d1b', border: '1px solid #10b981', color: '#6ee7b7', padding: '10px 14px', borderRadius: '8px', fontSize: '0.85rem', marginBottom: '16px' }}>
                {trackSuccess}
              </div>
            )}
            {trackError && (
              <div style={{ background: '#2d1b1b', border: '1px solid #e94560', color: '#f87171', padding: '10px 14px', borderRadius: '8px', fontSize: '0.85rem', marginBottom: '16px' }}>
                {trackError}
              </div>
            )}

            <form onSubmit={handleAddTrack} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div>
                <label style={labelStyle}>Nombre de la canción</label>
                <input
                  required value={trackForm.name}
                  onChange={e => setTrackForm({ ...trackForm, name: e.target.value })}
                  placeholder="Ej: Bohemian Rhapsody"
                  style={inputStyle}
                />
              </div>
              <div>
                <label style={labelStyle}>Artista</label>
                <input
                  required value={trackForm.artist_name}
                  onChange={e => setTrackForm({ ...trackForm, artist_name: e.target.value })}
                  placeholder="Ej: Queen (existente o nuevo)"
                  style={inputStyle}
                />
                <p style={{ color: '#64748b', fontSize: '0.75rem', margin: '4px 0 0' }}>
                  Si el artista no existe, se crea automáticamente.
                </p>
              </div>
              <div>
                <label style={labelStyle}>Género</label>
                <select
                  required value={trackForm.genre_id}
                  onChange={e => setTrackForm({ ...trackForm, genre_id: e.target.value })}
                  style={inputStyle}
                >
                  <option value="">Selecciona un género...</option>
                  {genres.map(g => <option key={g.genre_id} value={g.genre_id}>{g.name}</option>)}
                </select>
              </div>
              <div>
                <label style={labelStyle}>Precio (USD)</label>
                <input
                  required type="number" step="0.01" min="0.01"
                  value={trackForm.unit_price}
                  onChange={e => setTrackForm({ ...trackForm, unit_price: e.target.value })}
                  style={inputStyle}
                />
              </div>
              <button type="submit" disabled={savingTrack} style={{
                padding: '12px', background: savingTrack ? '#2d2d4e' : '#e94560',
                color: 'white', border: 'none', borderRadius: '8px',
                cursor: savingTrack ? 'not-allowed' : 'pointer',
                fontSize: '0.95rem', fontWeight: '700', marginTop: '4px'
              }}>
                {savingTrack ? 'Guardando...' : '+ Agregar Canción'}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

const labelStyle = { color: '#94a3b8', fontSize: '0.85rem', display: 'block', marginBottom: '6px' }
const inputStyle = {
  width: '100%', padding: '10px 14px', borderRadius: '8px',
  border: '1px solid #2d2d4e', background: '#0f0f1a',
  color: '#f0f4ff', fontSize: '0.9rem', outline: 'none', boxSizing: 'border-box'
}

export default Admin
