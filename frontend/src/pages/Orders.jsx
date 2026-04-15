import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getMyInvoices } from '../services/api'
import { useAuth } from '../context/AuthContext'

function Orders() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const { user } = useAuth()

  useEffect(() => {
    if (!user) return
    getMyInvoices()
      .then(r => setData(r.data))
      .catch(e => setError(e.response?.data?.detail || 'Error al cargar el historial'))
      .finally(() => setLoading(false))
  }, [user])

  if (!user) {
    return (
      <div style={{ maxWidth: 480, margin: '80px auto', padding: '0 24px', textAlign: 'center' }}>
        <div style={{ fontSize: '2.5rem', marginBottom: '16px' }}>🔒</div>
        <h2 style={{ color: '#f0f4ff', marginBottom: '12px' }}>Inicia sesión</h2>
        <p style={{ color: '#64748b', marginBottom: '24px' }}>Necesitas una cuenta para ver tu historial de compras.</p>
        <Link to="/login" style={{ background: '#e94560', color: 'white', textDecoration: 'none', padding: '11px 28px', borderRadius: '8px', fontWeight: '600' }}>
          Iniciar sesión
        </Link>
      </div>
    )
  }

  return (
    <div style={{ maxWidth: 760, margin: '0 auto', padding: '32px 24px' }}>
      <div style={{ marginBottom: '28px' }}>
        <h2 style={{ color: '#f0f4ff', fontSize: '1.6rem', fontWeight: '700', margin: '0 0 4px' }}>📋 Mis Compras</h2>
        <p style={{ color: '#64748b', margin: 0, fontSize: '0.9rem' }}>
          {user.email}
          {data?.customer && <span style={{ color: '#94a3b8' }}> · {data.customer}</span>}
        </p>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '60px', color: '#64748b' }}>
          <div style={{ fontSize: '2rem', marginBottom: '12px' }}>⏳</div>
          Cargando historial...
        </div>
      ) : error ? (
        <div style={{ background: '#2d1b1b', border: '1px solid #e94560', color: '#f87171', padding: '16px', borderRadius: '10px' }}>
          {error}
        </div>
      ) : !data?.invoices?.length ? (
        <div style={{
          background: '#1a1a2e', border: '1px solid #2d2d4e', borderRadius: '12px',
          padding: '60px', textAlign: 'center'
        }}>
          <div style={{ fontSize: '2.5rem', marginBottom: '16px' }}>🛒</div>
          <p style={{ color: '#64748b', margin: '0 0 20px' }}>
            {data?.customer
              ? 'Aún no tienes compras registradas.'
              : 'Tu email no coincide con ningún cliente en la base de datos. Realiza una compra para ver el historial.'}
          </p>
          <Link to="/tracks" style={{ color: '#e94560', textDecoration: 'none', fontWeight: '600' }}>
            Explorar catálogo →
          </Link>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {data.invoices.map(inv => (
            <div key={inv.invoice_id} style={{
              background: '#1a1a2e', border: '1px solid #2d2d4e', borderRadius: '12px', overflow: 'hidden'
            }}>
              {/* Header de factura */}
              <div style={{
                padding: '14px 20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                borderBottom: '1px solid #2d2d4e', background: '#161628'
              }}>
                <div>
                  <span style={{ color: '#94a3b8', fontSize: '0.8rem' }}>Factura </span>
                  <span style={{ color: '#f0f4ff', fontWeight: '700' }}>#{inv.invoice_id}</span>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ color: '#e94560', fontWeight: '700', fontSize: '1rem' }}>${Number(inv.total).toFixed(2)}</div>
                  <div style={{ color: '#64748b', fontSize: '0.75rem' }}>
                    {new Date(inv.date).toLocaleDateString('es-CO', { year: 'numeric', month: 'short', day: 'numeric' })}
                  </div>
                </div>
              </div>

              {/* Tracks de la factura */}
              <div style={{ padding: '12px 20px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {inv.tracks.map((t, i) => (
                  <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ color: '#c8cfe8', fontSize: '0.88rem' }}>🎵 {t.name}</span>
                    <span style={{ color: '#64748b', fontSize: '0.82rem' }}>${Number(t.price).toFixed(2)}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default Orders
