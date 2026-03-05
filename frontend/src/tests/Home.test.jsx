import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { describe, it, expect } from 'vitest'
import Home from '../pages/Home'

describe('Home', () => {
  it('muestra el título de bienvenida', () => {
    render(<BrowserRouter><Home /></BrowserRouter>)
    expect(screen.getByText(/Bienvenido a Chinook Music Store/i)).toBeInTheDocument()
  })

  it('muestra el botón Ver Canciones', () => {
    render(<BrowserRouter><Home /></BrowserRouter>)
    expect(screen.getByText('Ver Canciones')).toBeInTheDocument()
  })

  it('muestra el botón Comprar', () => {
    render(<BrowserRouter><Home /></BrowserRouter>)
    expect(screen.getByText('Comprar')).toBeInTheDocument()
  })

  it('el botón Ver Canciones apunta a /tracks', () => {
    render(<BrowserRouter><Home /></BrowserRouter>)
    expect(screen.getByText('Ver Canciones').closest('a')).toHaveAttribute('href', '/tracks')
  })
})
