import { Link } from 'react-router-dom'

const features = [
  { icon: '🎸', title: 'Más de 3,500 canciones', desc: 'Catálogo completo con rock, jazz, metal, clásica y más géneros.' },
  { icon: '🛒', title: 'Compra instantánea', desc: 'Selecciona tus canciones, elige un cliente y genera tu factura al instante.' },
  { icon: '📋', title: 'Historial de compras', desc: 'Consulta todas tus facturas anteriores desde tu perfil.' },
]

function Home() {
  return (
    <div>
      {/* Hero */}
      <div style={{
        background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)',
        padding: '80px 32px',
        textAlign: 'center',
        borderBottom: '1px solid #2d2d4e'
      }}>
        <div style={{ maxWidth: 640, margin: '0 auto' }}>
          <div style={{ fontSize: '3.5rem', marginBottom: '16px' }}>🎵</div>
          <h1 style={{ color: '#f0f4ff', fontSize: '2.6rem', fontWeight: '800', margin: '0 0 16px', lineHeight: 1.2 }}>
            Bienvenido a Chinook Music Store
          </h1>
          <p style={{ color: '#94a3b8', fontSize: '1.1rem', margin: '0 0 36px', lineHeight: 1.6 }}>
            Tu tienda de música digital. Explora el catálogo, selecciona tus canciones favoritas y completa tu compra en segundos.
          </p>
          <div style={{ display: 'flex', gap: '14px', justifyContent: 'center', flexWrap: 'wrap' }}>
            <Link to="/tracks" style={{
              background: '#e94560', color: 'white', textDecoration: 'none',
              padding: '13px 32px', borderRadius: '8px', fontSize: '1rem', fontWeight: '700',
              boxShadow: '0 4px 20px rgba(233,69,96,0.4)'
            }}>Ver Canciones</Link>
            <Link to="/register" style={{
              background: 'transparent', color: '#c8cfe8', textDecoration: 'none',
              padding: '13px 32px', borderRadius: '8px', fontSize: '1rem', fontWeight: '600',
              border: '1px solid #2d2d4e'
            }}>Crear cuenta</Link>
          </div>
        </div>
      </div>

      {/* Feature cards */}
      <div style={{ maxWidth: 960, margin: '60px auto', padding: '0 32px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '20px' }}>
          {features.map(f => (
            <div key={f.title} style={{
              background: '#1a1a2e', border: '1px solid #2d2d4e', borderRadius: '12px',
              padding: '28px 24px'
            }}>
              <div style={{ fontSize: '2rem', marginBottom: '12px' }}>{f.icon}</div>
              <h3 style={{ color: '#f0f4ff', margin: '0 0 8px', fontSize: '1.05rem' }}>{f.title}</h3>
              <p style={{ color: '#64748b', margin: 0, fontSize: '0.9rem', lineHeight: 1.5 }}>{f.desc}</p>
            </div>
          ))}
        </div>

        {/* CTA */}
        <div style={{ textAlign: 'center', marginTop: '56px', paddingBottom: '40px' }}>
          <p style={{ color: '#64748b', marginBottom: '16px' }}>¿Listo para comprar?</p>
          <Link to="/purchase" style={{
            background: '#1a1a2e', color: '#e94560', textDecoration: 'none',
            padding: '12px 28px', borderRadius: '8px', fontSize: '0.95rem',
            border: '1px solid #e94560', fontWeight: '600'
          }}>Comprar</Link>
        </div>
      </div>
    </div>
  )
}

export default Home
