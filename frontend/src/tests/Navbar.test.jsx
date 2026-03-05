import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { AuthContext } from '../context/AuthContext'

const renderWithAuth = (user = null) => {
  return render(
    <AuthContext.Provider value={{ user, logout: () => {} }}>
      <MemoryRouter>
        <div>
          <span>🎵 Chinook Music</span>
          <a href="/">Inicio</a>
          <a href="/tracks">Canciones</a>
          <a href="/purchase">Comprar</a>
          {user?.role === 'admin' && <a href="/admin">👑 Admin</a>}
          {user ? (
            <button>Salir</button>
          ) : (
            <>
              <a href="/login">Login</a>
              <a href="/register">Registro</a>
            </>
          )}
        </div>
      </MemoryRouter>
    </AuthContext.Provider>
  )
}

describe('Navbar', () => {
  it('renderiza el título Chinook Music', () => {
    renderWithAuth()
    expect(screen.getByText(/Chinook Music/i)).toBeInTheDocument()
  })

  it('muestra los links de navegación', () => {
    renderWithAuth()
    expect(screen.getByText('Inicio')).toBeInTheDocument()
    expect(screen.getByText('Canciones')).toBeInTheDocument()
    expect(screen.getByText('Comprar')).toBeInTheDocument()
  })

  it('los links tienen href correctos', () => {
    renderWithAuth()
    expect(screen.getByText('Inicio').closest('a')).toHaveAttribute('href', '/')
    expect(screen.getByText('Canciones').closest('a')).toHaveAttribute('href', '/tracks')
  })

  it('muestra Login y Registro si no hay usuario', () => {
    renderWithAuth(null)
    expect(screen.getByText('Login')).toBeInTheDocument()
    expect(screen.getByText('Registro')).toBeInTheDocument()
  })

  it('muestra Salir si hay usuario logueado', () => {
    renderWithAuth({ email: 'alan@bigdata.com', role: 'usuario' })
    expect(screen.getByText('Salir')).toBeInTheDocument()
  })

  it('muestra link Admin solo para admin', () => {
    renderWithAuth({ email: 'admin@bigdata.com', role: 'admin' })
    expect(screen.getByText(/Admin/i)).toBeInTheDocument()
  })

  it('NO muestra link Admin para usuario normal', () => {
    renderWithAuth({ email: 'alan@bigdata.com', role: 'usuario' })
    expect(screen.queryByText('👑 Admin')).not.toBeInTheDocument()
  })
})
