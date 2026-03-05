import axios from 'axios'

const API = axios.create({
  baseURL: 'http://44.216.77.83:8000/api'
})

export const getTracks = (limit = 50) => API.get(`/tracks?limit=${limit}`)
export const searchTracks = (q) => API.get(`/tracks/search?q=${q}`)
export const getCustomers = () => API.get('/customers')
export const purchaseTracks = (data) => API.post('/purchase', data)
export const registerUser = (data) => API.post('/auth/register', data)
export const loginUser = (data) => API.post('/auth/login', data)

export default API
