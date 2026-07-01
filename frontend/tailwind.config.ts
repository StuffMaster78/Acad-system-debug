/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{vue,ts}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Plus Jakarta Sans", "ui-sans-serif", "system-ui", "-apple-system", "sans-serif"],
      },
      colors: {
        // Core semantic colors
        ink:      "#1a1f2e",  // primary text — slightly warmer
        graphite: "#4b5563",  // secondary text
        mist:     "#f1f5f9",  // page / panel background
        // Brand blue (aligns with marketing site) — flat alias kept for compat
        signal: {
          DEFAULT: "#163e88",
          50:  "#eef4ff",
          100: "#dde9ff",
          200: "#bbd3ff",
          300: "#93b8ff",
          400: "#5b8de0",
          500: "#2563c8",
          600: "#1d4fa8",
          700: "#163e88",
          800: "#112f6a",
          900: "#0d2455",
        },
        // Status accents
        saffron: "#d97706",  // amber / ratings
        // Rose / danger — flat alias kept for compat
        berry: {
          DEFAULT: "#e11d48",
          50:  "#fff1f2",
          100: "#ffe4e6",
          200: "#fecdd3",
          300: "#fda4af",
          400: "#fb7185",
          500: "#f43f5e",
          600: "#e11d48",
          700: "#be123c",
          800: "#9f1239",
          900: "#881337",
        },
        // Writer cosmos palette (dark space / auth theme)
        cosmos: {
          950: "#04060f",
          900: "#070b18",
          800: "#0c1225",
          700: "#111a35",
          600: "#172347",
        },
        nebula: {
          DEFAULT: "#7c3aed",
          cyan:   "#06b6d4",
          violet: "#8b5cf6",
          pink:   "#ec4899",
          gold:   "#f59e0b",
        },
        // Brand scale (matches marketing site)
        brand: {
          50:  "#eef4ff",
          100: "#dde9ff",
          200: "#bbd3ff",
          300: "#93b8ff",
          500: "#2563c8",
          600: "#1d4fa8",
          700: "#163e88",
          800: "#112f6a",
          900: "#0d2455",
        },
      },
      boxShadow: {
        panel: "0 1px 3px rgba(26,31,46,0.08), 0 1px 2px rgba(26,31,46,0.04)",
        card:  "0 2px 8px rgba(26,31,46,0.07), 0 1px 2px rgba(26,31,46,0.04)",
        soft:  "0 4px 16px rgba(26,31,46,0.10)",
      },
      borderRadius: {
        "2xl": "1rem",
        "3xl": "1.5rem",
      },
    },
  },
  plugins: [],
};
