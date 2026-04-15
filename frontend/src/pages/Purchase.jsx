import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getCustomers, purchaseTracks } from '../services/api'
import { useCart } from '../context/CartContext'

function Purchase() {
  const [customers, setCustomers] = useState([])
  const [customerId, setCustomerId] = useState('')
  const [invoice, setInvoice] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { cart, removeFromCart, clearCart, total } = useCart()

  useEffect(() => {
    getCustomers().then(r => setCustomers(r.data)).catch(console.error)
  }, [])

  const handlePurchase = async (e) => {
    e.preventDefault()
    if (!customerId) return setError('Selecciona un cliente')
    if (cart.length === 0) return setError('Tu carrito está vacío')
    setLoading(true); setError(''); setInvoice(null)
    try {
      const res = await purchaseTracks({
        customer_id: parseInt(customerId),
        track_ids: cart.map(t => t.track_id)
      })
      setInvoice(res.data)
      clearCart()
    } catch (e) { setError(e.response?.data?.detail || 'Error al procesar la compra') }
    finally { setLoading(false) }
  }

  // Estado: compra exitosa
  if (invoice) {
    return (
      <div style={{ maxWidth: 560, margin: '60px auto', padding: '0 24px' }}>
        <div style={{
          background: '#1a1a2e', border: '1px solid #10b981',
          borderRadius: '16px', padding: '40px', textAlign: 'center'
        }}>
          <div style={{ fontSize: '3rem', marginBottom: '16px' }}>🎉</div>
          <h2 style={{ color: '#10b981', margin: '0 0 8px' }}>¡Compra exitosa!</h2>
          <p style={{ color: '#64748b', margin: '0 0 28px' }}>Factura #{invoice.invoice_id} generada</p>

          <div style={{ background: '#0f0f1a', borderRadius: '10px', padding: '20px', textAlign: 'left', marginBottom: '24px' }}>
            <p style={{ color: '#94a3b8', fontSize: '0.85rem', margin: '0 0 12px' }}>DETALLE DE COMPRA</p>
            {invoice.tracks?.map((name, i) => (
              <div key={i} style={{ color: '#f0f4ff', fontSize: '0.9rem', padding: '6px 0', borderBottom: '1px solid #2d2d4e' }}>
                🎵 {name}
              </div>
            ))}
            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '16px' }}>
              <span style={{ color: '#94a3b8' }}>Cliente</span>
              <span style={{ color: '#f0f4ff' }}>{invoice.customer}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '8px' }}>
              <span style={{ color: '#94a3b8' }}>Total</span>
              <span style={{ color: '#e94560', fontWeight: '700', fontSize: '1.1rem' }}>${Number(invoice.total).toFixed(2)}</span>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
            <Link to="/tracks" style={{
              background: '#e94560', color: 'white', textDecoration: 'none',
              padding: '10px 24px', borderRadius: '8px', fontWeight: '600'
            }}>Seguir comprando</Link>
            <Link to="/orders" style={{
              background: 'transparent', color: '#94a3b8', textDecoration: 'none',
              padding: '10px 24px', borderRadius: '8px', border: '1px solid #2d2d4e'
            }}>Ver historial</Link>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div style={{ maxWidth: 800, margin: '0 auto', padding: '32px 24px', display: 'grid', gridTemplateColumns: '1fr 340px', gap: '24px', alignItems: 'start' }}>
      {/* Carrito */}
      <div>
        <h2 style={{ color: '#f0f4ff', fontSize: '1.5rem', fontWeight: '700', margin: '0 0 20px' }}>🛒 Tu Carrito</h2>

        {cart.length === 0 ? (
          <div style={{
            background: '#1a1a2e', border: '1px solid #2d2d4e', borderRadius: '12px',
            padding: '48px', textAlign: 'center'
          }}>
            <div style={{ fontSize: '2.5rem', marginBottom: '12px' }}>🎵</div>
            <p style={{ color: '#64748b', margin: '0 0 20px' }}>Tu carrito está vacío</p>
            <Link to="/tracks" style={{
              color: '#e94560', textDecoration: 'none', fontWeight: '600', fontSize: '0.9rem'
            }}>← Explorar catálogo</Link>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {cart.map(t => (
              <div key={t.track_id} style={{
                background: '#1a1a2e', border: '1px solid #2d2d4e', borderRadius: '10px',
                padding: '14px 16px', display: 'flex', alignItems: 'center', gap: '12px'
              }}>
                <div style={{
                  width: '36px', height: '36px', borderRadius: '6px', flexShrink: 0,
                  background: 'linear-gradient(135deg, #e94560, #7c3aed)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1rem'
                }}>🎵</div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ color: '#f0f4ff', fontSize: '0.9rem', fontWeight: '600', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{t.name}</div>
                  <div style={{ color: '#64748b', fontSize: '0.8rem' }}>{t.artist}</div>
                </div>
                <span style={{ color: '#e94560', fontWeight: '700', flexShrink: 0 }}>${Number(t.unit_price).toFixed(2)}</span>
                <button onClick={() => removeFromCart(t.track_id)} style={{
                  background: 'transparent', color: '#64748b', border: 'none',
                  cursor: 'pointer', fontSize: '1rem', padding: '4px 8px', borderRadius: '4px'
                }}>✕</button>
              </div>
            ))}

            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 0 0', borderTop: '1px solid #2d2d4e', marginTop: '4px' }}>
              <span style={{ color: '#94a3b8' }}>{cart.length} canción{cart.length !== 1 ? 'es' : ''}</span>
              <span style={{ color: '#f0f4ff', fontWeight: '700', fontSize: '1.1rem' }}>Total: ${total.toFixed(2)}</span>
            </div>
          </div>
        )}
      </div>

      {/* Checkout */}
      <div style={{ background: '#1a1a2e', border: '1px solid #2d2d4e', borderRadius: '12px', padding: '24px', position: 'sticky', top: '80px' }}>
        <h3 style={{ color: '#f0f4ff', margin: '0 0 20px', fontSize: '1.1rem' }}>Finalizar compra</h3>

        {error && (
          <div style={{ background: '#2d1b1b', border: '1px solid #e94560', color: '#f87171', padding: '10px 14px', borderRadius: '8px', fontSize: '0.85rem', marginBottom: '16px' }}>
            {error}
          </div>
        )}

        <form onSubmit={handlePurchase}>
          <label style={{ color: '#94a3b8', fontSize: '0.85rem', display: 'block', marginBottom: '6px' }}>Cliente</label>
          <select
            value={customerId}
            onChange={e => setCustomerId(e.target.value)}
            required
            style={{
              width: '100%', padding: '10px 12px', borderRadius: '8px',
              border: '1px solid #2d2d4e', background: '#0f0f1a',
              color: customerId ? '#f0f4ff' : '#64748b', fontSize: '0.9rem',
              marginBottom: '20px', outline: 'none'
            }}
          >
            <option value="">Selecciona un cliente...</option>
            {customers.map(c => (
              <option key={c.customer_id} value={c.customer_id}>
                {c.first_name} {c.last_name}
              </option>
            ))}
          </select>

          <div style={{ background: '#0f0f1a', borderRadius: '8px', padding: '14px', marginBottom: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
              <span style={{ color: '#64748b', fontSize: '0.85rem' }}>Canciones</span>
              <span style={{ color: '#94a3b8', fontSize: '0.85rem' }}>{cart.length}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#64748b', fontSize: '0.85rem' }}>Total</span>
              <span style={{ color: '#e94560', fontWeight: '700' }}>${total.toFixed(2)}</span>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading || cart.length === 0}
            style={{
              width: '100%', padding: '12px', background: cart.length === 0 ? '#2d2d4e' : '#e94560',
              color: cart.length === 0 ? '#64748b' : 'white',
              border: 'none', borderRadius: '8px', cursor: cart.length === 0 ? 'not-allowed' : 'pointer',
              fontSize: '0.95rem', fontWeight: '700'
            }}
          >
            {loading ? 'Procesando...' : 'Confirmar compra'}
          </button>
        </form>

        <Link to="/tracks" style={{ display: 'block', textAlign: 'center', color: '#64748b', textDecoration: 'none', fontSize: '0.85rem', marginTop: '14px' }}>
          ← Seguir explorando
        </Link>
      </div>
    </div>
  )
}

export default Purchase
