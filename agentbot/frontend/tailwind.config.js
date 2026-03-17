/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#e6f0ff',
          100: '#cce0ff',
          200: '#99c2ff',
          300: '#66a3ff',
          400: '#3385ff',
          500: '#1e4d8c',
          600: '#0066ff',
          700: '#0052cc',
          800: '#003d99',
          900: '#002966',
        },
        dental: {
          blue: '#3498db',
          red: '#e74c3c',
          green: '#27ae60',
          orange: '#f39c12',
          purple: '#9b59b6',
          dark: '#2c3e50',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
