/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./404.html",
    "./src/**/*.{js,ts,jsx,tsx,html}",
  ],
  theme: {
    screens: {
      'sm': '640px',
      'tablet': '760px',
      'md': '768px',
      'lg': '1024px',
      'desktop': '1440px',
      'xl': '1280px',
      '2xl': '1536px',
    },
    extend: {
      colors: {
        brand: {
          dark: '#0E1014',
          surface: '#14171D',
          'surface-light': '#1B1F27',
          'surface-card': '#161920',
          red: '#E02D37',
          'red-hover': '#C7242D',
          'red-glow': 'rgba(224, 45, 55, 0.25)',
          muted: '#8E95A5',
          dim: '#5A6275',
          light: '#F2F4F8',
        }
      },
      fontFamily: {
        condensed: ['"Fira Sans Extra Condensed"', '"Sofia Sans Condensed"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
        sans: ['"Onest"', 'sans-serif'],
      },
      animation: {
        'marquee': 'marquee 25s linear infinite',
        'marquee-reverse': 'marquee-reverse 25s linear infinite',
        'pulse-rec': 'pulseRec 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        marquee: {
          '0%': { transform: 'translateX(0%)' },
          '100%': { transform: 'translateX(-50%)' },
        },
        'marquee-reverse': {
          '0%': { transform: 'translateX(-50%)' },
          '100%': { transform: 'translateX(0%)' },
        },
        pulseRec: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.2' },
        }
      }
    },
  },
  plugins: [],
}
