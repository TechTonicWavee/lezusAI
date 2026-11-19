/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        canvas: '#090D18',
        sidebar: '#101625',
        content: '#0D1321',
        card: '#141C2D',
        elevated: '#192338',
        border: '#273247',
        brand: {
          purple: '#8B5CF6',
          secondary: '#A78BFA',
          blue: '#60A5FA',
          dark: '#6D28D9'
        },
        status: {
          success: '#22C55E',
          warning: '#F59E0B',
          error: '#EF4444',
          critical: '#DC2626',
          info: '#60A5FA'
        },
        txt: {
          primary: '#E5E7EB',
          secondary: '#94A3B8',
          muted: '#64748B'
        }
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'Menlo', 'monospace']
      }
    },
  },
  plugins: [],
}
