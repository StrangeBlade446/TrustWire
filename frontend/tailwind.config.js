/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#0B0D10',
        surface: '#13171D',
        'surface-elevated': '#1B212A',
        panel: '#151A22',
        border: '#222A36',
        'border-focus': '#2F3C4F',
        teal: {
          400: '#2DD4BF',
          500: '#14B8A6',
          600: '#0D9488'
        },
        cyan: {
          400: '#22D3EE',
          500: '#06B6D4'
        },
        amber: {
          400: '#FBBF24',
          500: '#F59E0B'
        },
        rose: {
          500: '#F43F5E',
          600: '#E11D48'
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'monospace']
      }
    },
  },
  plugins: [],
}
