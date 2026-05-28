export const storeConfig = {
  name: 'ESSENCE',
  tagline: 'Maison de Parfum',
  description: 'Rare fragrances. Unapologetic luxury.',

  logo: '/logo.svg',
  favicon: '/favicon.ico',
  placeholderImage: '/placeholder-product.webp',

  currency: {
    code: 'USD',
    symbol: '$',
    locale: 'en-US',
  },

  contact: {
    email: 'hello@essence-maison.com',
    phone: '+1 (800) 555-0199',
  },

  social: {
    instagram: 'https://instagram.com/essence',
    twitter: 'https://twitter.com/essence',
  },

  heroTitle: 'Wear Your Obsession',
  heroSubtitle: 'Ultra-rare fragrances. Hand-selected from the world\'s finest perfume houses. Created for those who refuse the ordinary.',
  footerText: '© 2026 ESSENCE Maison de Parfum. All rights reserved.',
} as const

export type StoreConfig = typeof storeConfig
