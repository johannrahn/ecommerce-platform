import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import * as authApi from '@/api/auth.api'
import * as usersApi from '@/api/users.api'
import * as cartApi from '@/api/cart.api'
import { useAuthStore } from '@/stores/auth.store'
import { useGuestCartStore } from '@/stores/guest-cart.store'
import { cartKeys } from '@/lib/query-keys'
import { toast } from 'sonner'
import type { LoginRequest, RegisterRequest } from '@/types/auth.types'

export function useCurrentUser() {
  const token = useAuthStore((s) => s.token)

  return useQuery({
    queryKey: ['auth', 'me'],
    queryFn: usersApi.getMe,
    enabled: !!token,
  })
}

export function useLogin() {
  const navigate = useNavigate()
  const setAuth = useAuthStore((s) => s.setAuth)
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: LoginRequest) => {
      const tokenResponse = await authApi.login(data)
      useAuthStore.getState().setAuth(tokenResponse.access_token, null!)
      const user = await usersApi.getMe()
      return { token: tokenResponse.access_token, user }
    },
    onSuccess: async ({ token, user }) => {
      setAuth(token, user)

      // Merge guest cart into backend cart
      const guestItems = useGuestCartStore.getState().items
      if (guestItems.length > 0) {
        await Promise.allSettled(
          guestItems.map((g) =>
            cartApi.addItem({ product_id: g.product_id, quantity: g.quantity })
          )
        )
        useGuestCartStore.getState().clearItems()
        queryClient.invalidateQueries({ queryKey: cartKeys.mine() })
      }

      toast.success('Welcome back!')
      navigate('/')
    },
    onError: (err: { message: string }) => {
      toast.error(err.message)
    },
  })
}

export function useRegister() {
  const navigate = useNavigate()

  return useMutation({
    mutationFn: (data: RegisterRequest) => authApi.register(data),
    onSuccess: () => {
      toast.success('Account created! Please log in.')
      navigate('/login')
    },
    onError: (err: { message: string }) => {
      toast.error(err.message)
    },
  })
}

export function useLogout() {
  const navigate = useNavigate()
  const logout = useAuthStore((s) => s.logout)
  const queryClient = useQueryClient()

  return () => {
    logout()
    useGuestCartStore.getState().clearItems()
    queryClient.clear()
    navigate('/login')
  }
}

export function useUpdateProfile() {
  const setUser = useAuthStore((s) => s.setUser)

  return useMutation({
    mutationFn: usersApi.updateMe,
    onSuccess: (user) => {
      setUser(user)
      toast.success('Profile updated')
    },
    onError: (err: { message: string }) => {
      toast.error(err.message)
    },
  })
}
