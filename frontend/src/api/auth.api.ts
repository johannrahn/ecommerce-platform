import apiClient from '@/lib/api-client'
import type { LoginRequest, RegisterRequest, TokenResponse } from '@/types/auth.types'
import type { User } from '@/types/user.types'

export async function login(data: LoginRequest): Promise<TokenResponse> {
  const { data: response } = await apiClient.post('/auth/login', data)
  return response
}

export async function register(data: RegisterRequest): Promise<User> {
  const { data: response } = await apiClient.post('/auth/register', data)
  return response
}
