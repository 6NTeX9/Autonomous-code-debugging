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
          900: "#0b0f19",
          850: "#0f172a",
          800: "#1e293b",
          700: "#334155",
          600: "#475569"
        },
        brand: {
          blue: "#38bdf8",
          purple: "#a855f7",
          green: "#22c55e",
          amber: "#f59e0b",
          red: "#ef4444"
        }
      }
    },
  },
  plugins: [],
}
