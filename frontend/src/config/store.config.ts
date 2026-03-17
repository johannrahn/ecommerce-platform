export const storeConfig = {
  name: 'ESSENCE',
  tagline: 'Premium Fragrances',
  description: 'Discover your signature scent',

  logo: '/logo.svg',
  favicon: '/favicon.ico',
  placeholderImage: '/placeholder-product.webp',

  currency: {
    code: 'USD',
    symbol: '$',
    locale: 'en-US',
  },

  contact: {
    email: 'hello@essence-perfumes.com',
    phone: '+1 (555) 123-4567',
  },

  social: {
    instagram: 'https://instagram.com/essence',
    twitter: 'https://twitter.com/essence',
  },

  heroTitle: 'Find Your Signature Scent',
  heroSubtitle: 'Explore our curated collection of premium fragrances',
  footerText: '\u00a9 2026 ESSENCE. All rights reserved.',
} as const

export type StoreConfig = typeof storeConfig
