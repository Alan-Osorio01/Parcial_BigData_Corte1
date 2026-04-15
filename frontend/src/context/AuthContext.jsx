import { createContext, useContext, useState } from 'react'

export const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      const stored = localStorage.getItem('chinook_user')
      return stored ? JSON.parse(stored) : null
    } catch {
      return null
    }
  })

  const login = (userData, token) => {
    localStorage.setItem('chinook_user', JSON.stringify(userData))
    localStorage.setItem('chinook_token', token)
    setUser(userData)
  }

  const logout = () => {
    localStorage.removeItem('chinook_user')
    localStorage.removeItem('chinook_token')
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
