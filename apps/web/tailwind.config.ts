import type { Config } from 'tailwindcss'

export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        void: '#07090d',
        neural: '#5eead4',
        signal: '#ffcf74',
        companion: '#8a6df1',
      },
    },
  },
  plugins: [],
} satisfies Config
