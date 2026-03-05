import { useState, useEffect } from 'react'
import { getTracks, getCustomers, purchaseTracks } from '../services/api'

function Purchase() {
  const [tracks, setTracks] = useState([])
  const [customers, setCustomers] = useState([])
  const [selectedTracks, setSelectedTracks] = useState([])
  const [customerId, setCustomerId] = useState('')
  const [invoice, setInvoice] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    getTracks(50).then(r => setTracks(r.data)).catch(console.error)
    getCustomers().then(r => setCustomers(r.data)).catch(console.error)
  }, [])

  const toggleTrack = (id) => setSelectedTracks(prev =>
    prev.includes(id) ? prev.filter(t => t !== id) : [...prev, id]
  )

  const handlePurchase = async (e) => {
    e.preventDefault()
    if (!customerId || selectedTracks.length === 0) return setError('Selecciona cliente y canciones')
    setLoading(true); setError(''); setInvoice(null)
    try {
      const res = await purchaseTracks({ customer_id: parseInt(customerId), track_ids: selectedTracks })
      setInvoice(res.data); setSelectedTracks([])
    } catch (e) { setError(e.response?.data?.detail || 'Error al procesar') }
    finally { setLoading(false) }
  }

  return (
    <div style={{ padding:'20px', maxWidth:600, margin:'0 auto' }}>
      <h2>🛒 Comprar Canciones</h2>
      {invoice && <div style={{ background:'#e0ffe0', padding:'1rem', borderRadius:6, margin:'1rem 0', color:'#060' }}>
        ✅ Compra exitosa! Factura #{invoice.invoice_id} — Total: ${invoice.total}
      </div>}
      {error && <div style={{ background:'#ffe0e0', padding:'1rem', borderRadius:6, margin:'1rem 0', color:'#c00' }}>{error}</div>}
      <form onSubmit={handlePurchase}>
        <div style={{ marginBottom:'1rem' }}>
          <label style={{ fontWeight:'bold' }}>Cliente:</label><br/>
          <select value={customerId} onChange={e => setCustomerId(e.target.value)} required
            style={{ width:'100%', padding:'10px', marginTop:6, borderRadius:6, border:'1px solid #ccc' }}>
            <option value="">-- Selecciona un cliente --</option>
            {customers.map(c => <option key={c.customer_id} value={c.customer_id}>{c.first_name} {c.last_name} — {c.email}</option>)}
          </select>
        </div>
        <div style={{ marginBottom:'1rem' }}>
          <label style={{ fontWeight:'bold' }}>Canciones ({selectedTracks.length} seleccionadas):</label>
          <div style={{ border:'1px solid #ccc', borderRadius:6, maxHeight:300, overflowY:'auto', marginTop:6 }}>
            {tracks.map(t => (
              <div key={t.track_id} onClick={() => toggleTrack(t.track_id)}
                style={{ padding:'8px 12px', cursor:'pointer', display:'flex', justifyContent:'space-between',
                  background: selectedTracks.includes(t.track_id) ? '#dbeafe' : 'white',
                  borderBottom:'1px solid #eee' }}>
                <span>{selectedTracks.includes(t.track_id) ? '✅' : '☐'} {t.name}</span>
                <span style={{ color:'#e94560' }}>${t.unit_price}</span>
              </div>
            ))}
          </div>
        </div>
        <button type="submit" disabled={loading}
          style={{ width:'100%', padding:'12px', background:'#e94560', color:'white', border:'none', borderRadius:6, cursor:'pointer', fontSize:'1rem', fontWeight:'bold' }}>
          {loading ? 'Procesando...' : 'Realizar Compra'}
        </button>
      </form>
    </div>
  )
}

export default Purchase
