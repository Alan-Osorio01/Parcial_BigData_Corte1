import axios from 'axios'

const API = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
})

API.interceptors.request.use(config => {
  const token = localStorage.getItem('chinook_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export const getTracks = (limit = 50, offset = 0) => API.get(`/tracks?limit=${limit}&offset=${offset}`)
export const searchTracks = (q) => API.get(`/tracks/search?q=${q}`)
export const getCustomers = () => API.get('/customers')
export const purchaseTracks = (data) => API.post('/purchase', data)
export const registerUser = (data) => API.post('/auth/register', data)
export const loginUser = (data) => API.post('/auth/login', data)
export const getMyInvoices = () => API.get('/invoices/me')

export default API
