import { Routes, Route } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import { CartProvider } from './context/CartContext'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import Tracks from './pages/Tracks'
import Purchase from './pages/Purchase'
import Login from './pages/Login'
import Register from './pages/Register'
import Admin from './pages/Admin'
import Orders from './pages/Orders'

function App() {
  return (
    <AuthProvider>
      <CartProvider>
        <div style={{ minHeight: '100vh', background: '#0f0f1a', color: '#f0f4ff' }}>
          <Navbar />
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/tracks" element={<Tracks />} />
            <Route path="/purchase" element={<Purchase />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/admin" element={<Admin />} />
            <Route path="/orders" element={<Orders />} />
          </Routes>
        </div>
      </CartProvider>
    </AuthProvider>
  )
}

export default App
