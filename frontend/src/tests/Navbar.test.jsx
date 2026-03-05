import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { describe, it, expect } from 'vitest'
import Navbar from '../components/Navbar'

describe('Navbar', () => {
  it('renderiza el título Chinook Music', () => {
    render(<BrowserRouter><Navbar /></BrowserRouter>)
    expect(screen.getByText(/Chinook Music/i)).toBeInTheDocument()
  })

  it('muestra los links de navegación', () => {
    render(<BrowserRouter><Navbar /></BrowserRouter>)
    expect(screen.getByText('Inicio')).toBeInTheDocument()
    expect(screen.getByText('Canciones')).toBeInTheDocument()
    expect(screen.getByText('Comprar')).toBeInTheDocument()
  })

  it('los links tienen href correctos', () => {
    render(<BrowserRouter><Navbar /></BrowserRouter>)
    expect(screen.getByText('Canciones').closest('a')).toHaveAttribute('href', '/tracks')
    expect(screen.getByText('Comprar').closest('a')).toHaveAttribute('href', '/purchase')
  })
})
