import { createContext, useContext, useState } from 'react'

const CartContext = createContext(null)

export function CartProvider({ children }) {
  const [cart, setCart] = useState([])

  const addToCart = (track) => {
    setCart(prev => prev.find(t => t.track_id === track.track_id) ? prev : [...prev, track])
  }

  const removeFromCart = (trackId) => {
    setCart(prev => prev.filter(t => t.track_id !== trackId))
  }

  const clearCart = () => setCart([])

  const isInCart = (trackId) => cart.some(t => t.track_id === trackId)

  const total = cart.reduce((sum, t) => sum + Number(t.unit_price), 0)

  return (
    <CartContext.Provider value={{ cart, addToCart, removeFromCart, clearCart, isInCart, total }}>
      {children}
    </CartContext.Provider>
  )
}

export function useCart() {
  return useContext(CartContext)
}
