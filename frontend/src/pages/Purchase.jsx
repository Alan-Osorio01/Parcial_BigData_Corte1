import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getMyCustomer, purchaseTracks } from '../services/api'
import { useCart } from '../context/CartContext'
import { useAuth } from '../context/AuthContext'

function Purchase() {
  const [customer, setCustomer] = useState(null)
  const [loadingCustomer, setLoadingCustomer] = useState(false)
  const [invoice, setInvoice] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { cart, removeFromCart, clearCart, total } = useCart()
  const { user } = useAuth()

  useEffect(() => {
    if (!user) return
    setLoadingCustomer(true)
    getMyCustomer()
      .then(r => setCustomer(r.data))
      .catch(() => setError('No se pudo cargar tu perfil de cliente'))
      .finally(() => setLoadingCustomer(false))
  }, [user])

  const handlePurchase = async (e) => {
    e.preventDefault()
    if (cart.length === 0) return setError('Tu carrito está vacío')
    setLoading(true); setError(''); setInvoice(null)
    try {
      const res = await purchaseTracks({
        customer_id: customer.customer_id,
        track_ids: cart.map(t => t.track_id)
      })
      setInvoice(res.data)
      clearCart()
    } catch (e) { setError(e.response?.data?.detail || 'Error al procesar la compra') }
    finally { setLoading(false) }
  }

  // Guard: no logueado
  if (!user) {
    return (
      <div style={{ maxWidth: 480, margin: '80px auto', padding: '0 24px', textAlign: 'center' }}>
        <div style={{ background: '#1a1a2e', border: '1px solid #2d2d4e', borderRadius: '16px', padding: '48px 32px' }}>
          <div style={{ fontSize: '2.5rem', marginBottom: '16px' }}>🔒</div>
          <h2 style={{ color: '#f0f4ff', margin: '0 0 12px' }}>Inicia sesión para comprar</h2>
          <p style={{ color: '#64748b', margin: '0 0 28px', lineHeight: 1.6 }}>
            Necesitas una cuenta para realizar compras. Tu sesión actúa como cliente.
          </p>
          <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
            <Link to="/login" style={{
              background: '#e94560', color: 'white', textDecoration: 'none',
              padding: '11px 28px', borderRadius: '8px', fontWeight: '700'
            }}>Iniciar sesión</Link>
            <Link to="/register" style={{
              background: 'transparent', color: '#94a3b8', textDecoration: 'none',
              padding: '11px 28px', borderRadius: '8px', border: '1px solid #2d2d4e'
            }}>Crear cuenta</Link>
          </div>
        </div>
      </div>
    )
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
    <div style={{ maxWidth: 800, margin: '0 auto', padding: '32px 24px', display: 'grid', gridTemplateColumns: '1fr 320px', gap: '24px', alignItems: 'start' }}>
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
            <Link to="/tracks" style={{ color: '#e94560', textDecoration: 'none', fontWeight: '600', fontSize: '0.9rem' }}>
              ← Explorar catálogo
            </Link>
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

        {/* Cliente (cuenta logueada) */}
        <div style={{ marginBottom: '20px' }}>
          <p style={{ color: '#94a3b8', fontSize: '0.85rem', margin: '0 0 8px' }}>Comprando como</p>
          {loadingCustomer ? (
            <div style={{ color: '#64748b', fontSize: '0.9rem' }}>Cargando...</div>
          ) : customer ? (
            <div style={{ background: '#0f0f1a', borderRadius: '8px', padding: '12px 14px', display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span style={{ fontSize: '1.4rem' }}>👤</span>
              <div>
                <div style={{ color: '#f0f4ff', fontWeight: '600', fontSize: '0.95rem' }}>
                  {customer.first_name} {customer.last_name}
                </div>
                <div style={{ color: '#64748b', fontSize: '0.8rem' }}>{customer.email}</div>
              </div>
            </div>
          ) : null}
        </div>

        {/* Resumen */}
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
          onClick={handlePurchase}
          disabled={loading || cart.length === 0 || !customer}
          style={{
            width: '100%', padding: '12px',
            background: (cart.length === 0 || !customer) ? '#2d2d4e' : '#e94560',
            color: (cart.length === 0 || !customer) ? '#64748b' : 'white',
            border: 'none', borderRadius: '8px',
            cursor: (cart.length === 0 || !customer) ? 'not-allowed' : 'pointer',
            fontSize: '0.95rem', fontWeight: '700'
          }}
        >
          {loading ? 'Procesando...' : 'Confirmar compra'}
        </button>

        <Link to="/tracks" style={{ display: 'block', textAlign: 'center', color: '#64748b', textDecoration: 'none', fontSize: '0.85rem', marginTop: '14px' }}>
          ← Seguir explorando
        </Link>
      </div>
    </div>
  )
}

export default Purchase
