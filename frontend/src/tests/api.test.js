import { describe, it, expect, vi, beforeEach } from 'vitest'

const mockApi = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
}))

vi.mock('../services/api', () => ({
  getTracks: (limit) => mockApi.get(`/tracks?limit=${limit}`),
  searchTracks: (q) => mockApi.get(`/tracks/search?q=${q}`),
  getCustomers: () => mockApi.get('/customers'),
  purchaseTracks: (data) => mockApi.post('/purchase', data),
  default: mockApi,
}))

import { getTracks, searchTracks, getCustomers, purchaseTracks } from '../services/api'

describe('API Service', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('getTracks llama al endpoint correcto', async () => {
    mockApi.get.mockResolvedValue({ data: [] })
    await getTracks(10)
    expect(mockApi.get).toHaveBeenCalledWith('/tracks?limit=10')
  })

  it('searchTracks llama con el query correcto', async () => {
    mockApi.get.mockResolvedValue({ data: [] })
    await searchTracks('rock')
    expect(mockApi.get).toHaveBeenCalledWith('/tracks/search?q=rock')
  })

  it('getCustomers llama al endpoint correcto', async () => {
    mockApi.get.mockResolvedValue({ data: [] })
    await getCustomers()
    expect(mockApi.get).toHaveBeenCalledWith('/customers')
  })

  it('purchaseTracks envía los datos correctos', async () => {
    mockApi.post.mockResolvedValue({ data: { invoice_id: 1, total: '0.99' } })
    const result = await purchaseTracks({ customer_id: 1, track_ids: [1] })
    expect(mockApi.post).toHaveBeenCalledWith('/purchase', { customer_id: 1, track_ids: [1] })
    expect(result.data.invoice_id).toBe(1)
  })

  it('purchaseTracks retorna la factura con total correcto', async () => {
    mockApi.post.mockResolvedValue({ data: { invoice_id: 5, total: '1.98' } })
    const result = await purchaseTracks({ customer_id: 2, track_ids: [1, 2] })
    expect(result.data.total).toBe('1.98')
  })
})