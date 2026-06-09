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
        // Brand blue (aligns with marketing site)
        signal:   "#163e88",
        // Status accents
        saffron:  "#d97706",  // amber / ratings
        berry:    "#e11d48",  // rose / danger
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
