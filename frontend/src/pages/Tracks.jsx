import { useState, useEffect } from 'react'
import { getTracks, searchTracks } from '../services/api'

function Tracks() {
  const [tracks, setTracks] = useState([])
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => { loadTracks() }, [])

  const loadTracks = async () => {
    setLoading(true)
    try { const res = await getTracks(50); setTracks(res.data) }
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

  return (
    <div style={{ padding:'20px', maxWidth:800, margin:'0 auto' }}>
      <h2>🎵 Catálogo de Canciones</h2>
      <form onSubmit={handleSearch} style={{ display:'flex', gap:'10px', margin:'20px 0' }}>
        <input value={query} onChange={e => setQuery(e.target.value)} placeholder="Buscar canción, artista o género..."
          style={{ flex:1, padding:'10px', borderRadius:6, border:'1px solid #ccc', fontSize:'1rem' }} />
        <button type="submit" style={{ background:'#1a1a2e', color:'white', border:'none', padding:'10px 20px', borderRadius:6, cursor:'pointer' }}>Buscar</button>
        <button type="button" onClick={() => { setQuery(''); loadTracks() }}
          style={{ background:'#666', color:'white', border:'none', padding:'10px 20px', borderRadius:6, cursor:'pointer' }}>Limpiar</button>
      </form>
      {loading ? <p>Cargando...</p> : (
        <table style={{ width:'100%', borderCollapse:'collapse' }}>
          <thead>
            <tr style={{ background:'#1a1a2e', color:'white' }}>
              <th style={{ padding:'10px', textAlign:'left' }}>Canción</th>
              <th style={{ padding:'10px', textAlign:'left' }}>Álbum</th>
              <th style={{ padding:'10px', textAlign:'left' }}>Género</th>
              <th style={{ padding:'10px', textAlign:'right' }}>Precio</th>
            </tr>
          </thead>
          <tbody>
            {tracks.map((t, i) => (
              <tr key={t.track_id} style={{ background: i%2===0 ? 'white' : '#f9f9f9' }}>
                <td style={{ padding:'8px 10px' }}>{t.name}</td>
                <td style={{ padding:'8px 10px' }}>{t.album}</td>
                <td style={{ padding:'8px 10px' }}>{t.genre}</td>
                <td style={{ padding:'8px 10px', textAlign:'right', color:'#e94560' }}>${t.unit_price}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}

export default Tracks
