/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        dark: {
          950: "#070709",
          900: "#0d0d12",
          850: "#131318",
          800: "#1d1d24",
          700: "#272732",
          600: "#3f3f4e"
        },
        brand: {
          emerald: "#10b981",
          mint: "#34d399",
          purple: "#a855f7",
          violet: "#8b5cf6",
          amber: "#f59e0b",
          red: "#ef4444"
        }
      }
    },
  },
  plugins: [],
}
