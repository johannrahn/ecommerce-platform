import apiClient from '@/lib/api-client'
import type { User, UserUpdate } from '@/types/user.types'

export async function getMe(): Promise<User> {
  const { data } = await apiClient.get('/users/me')
  return data
}

export async function updateMe(payload: UserUpdate): Promise<User> {
  const { data } = await apiClient.put('/users/me', payload)
  return data
}

export async function adminListUsers(): Promise<User[]> {
  const { data } = await apiClient.get('/users')
  return data
}
