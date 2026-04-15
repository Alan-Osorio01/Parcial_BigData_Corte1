import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getTracks, searchTracks } from '../services/api'
import { useCart } from '../context/CartContext'

function Tracks() {
  const [tracks, setTracks] = useState([])
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const { addToCart, removeFromCart, isInCart, cart } = useCart()
  const navigate = useNavigate()

  useEffect(() => { loadTracks() }, [])

  const loadTracks = async () => {
    setLoading(true)
    try { const res = await getTracks(100); setTracks(res.data) }
    catch (e) { console.error(e) }
    finally { setLoading(false) }
  }

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!query.trim()) return loadTracks()
    setLoading(true)
    try { const res = await searchTracks(query); setTracks(res.data) }
    catch { setTracks([]) }
    finally { setLoading(false) }
  }

  const handleClear = () => { setQuery(''); loadTracks() }

  return (
    <div style={{ maxWidth: 1000, margin: '0 auto', padding: '32px 24px' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '24px', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h2 style={{ color: '#f0f4ff', fontSize: '1.6rem', fontWeight: '700', margin: '0 0 4px' }}>🎵 Catálogo</h2>
          <p style={{ color: '#64748b', margin: 0, fontSize: '0.9rem' }}>
            {tracks.length} canciones {query && `para "${query}"`}
          </p>
        </div>
        {cart.length > 0 && (
          <button onClick={() => navigate('/purchase')} style={{
            background: '#e94560', color: 'white', border: 'none',
            padding: '10px 20px', borderRadius: '8px', cursor: 'pointer',
            fontSize: '0.9rem', fontWeight: '600'
          }}>
            🛒 Ver carrito ({cart.length})
          </button>
        )}
      </div>

      {/* Buscador */}
      <form onSubmit={handleSearch} style={{ display: 'flex', gap: '10px', marginBottom: '24px' }}>
        <input
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="Buscar canción, artista o género..."
          style={{
            flex: 1, padding: '11px 16px', borderRadius: '8px',
            border: '1px solid #2d2d4e', background: '#1a1a2e',
            color: '#f0f4ff', fontSize: '0.95rem', outline: 'none'
          }}
        />
        <button type="submit" style={btnPrimary}>Buscar</button>
        {query && (
          <button type="button" onClick={handleClear} style={btnSecondary}>✕</button>
        )}
      </form>

      {/* Lista */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '60px', color: '#64748b' }}>
          <div style={{ fontSize: '2rem', marginBottom: '12px' }}>⏳</div>
          Cargando catálogo...
        </div>
      ) : tracks.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '60px', color: '#64748b' }}>
          <div style={{ fontSize: '2rem', marginBottom: '12px' }}>🔍</div>
          No se encontraron canciones
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {tracks.map((t) => {
            const inCart = isInCart(t.track_id)
            return (
              <div key={t.track_id} style={{
                background: inCart ? '#1e2a1e' : '#1a1a2e',
                border: `1px solid ${inCart ? '#10b981' : '#2d2d4e'}`,
                borderRadius: '10px',
                padding: '14px 18px',
                display: 'flex',
                alignItems: 'center',
                gap: '16px',
                transition: 'border-color 0.2s'
              }}>
                {/* Icono */}
                <div style={{
                  width: '40px', height: '40px', borderRadius: '8px',
                  background: 'linear-gradient(135deg, #e94560, #7c3aed)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: '1.1rem', flexShrink: 0
                }}>🎵</div>

                {/* Info */}
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ color: '#f0f4ff', fontWeight: '600', fontSize: '0.95rem', marginBottom: '2px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {t.name}
                  </div>
                  <div style={{ color: '#64748b', fontSize: '0.82rem' }}>
                    {t.artist && <span>{t.artist}</span>}
                    {t.artist && t.album && <span style={{ margin: '0 6px' }}>·</span>}
                    {t.album && <span>{t.album}</span>}
                  </div>
                </div>

                {/* Genre badge */}
                {t.genre && (
                  <span style={{
                    background: '#2d2d4e', color: '#94a3b8',
                    padding: '3px 10px', borderRadius: '20px', fontSize: '0.75rem',
                    flexShrink: 0, display: 'none'  // hidden on mobile via this trick
                  }}>{t.genre}</span>
                )}

                {/* Precio */}
                <span style={{ color: '#e94560', fontWeight: '700', fontSize: '0.95rem', flexShrink: 0 }}>
                  ${Number(t.unit_price).toFixed(2)}
                </span>

                {/* Botón */}
                <button
                  onClick={() => inCart ? removeFromCart(t.track_id) : addToCart(t)}
                  style={{
                    background: inCart ? 'transparent' : '#e94560',
                    color: inCart ? '#10b981' : 'white',
                    border: inCart ? '1px solid #10b981' : 'none',
                    padding: '7px 16px', borderRadius: '6px',
                    cursor: 'pointer', fontSize: '0.8rem', fontWeight: '600',
                    flexShrink: 0, minWidth: '90px'
                  }}
                >
                  {inCart ? '✓ Agregado' : '+ Carrito'}
                </button>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

const btnPrimary = {
  background: '#e94560', color: 'white', border: 'none',
  padding: '11px 20px', borderRadius: '8px', cursor: 'pointer',
  fontSize: '0.9rem', fontWeight: '600'
}

const btnSecondary = {
  background: '#1a1a2e', color: '#94a3b8',
  border: '1px solid #2d2d4e', padding: '11px 16px',
  borderRadius: '8px', cursor: 'pointer', fontSize: '0.9rem'
}

export default Tracks
