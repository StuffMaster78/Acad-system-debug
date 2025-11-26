/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  // Note: In Tailwind v4, theme is defined in CSS using @theme directive
  // This config file is kept minimal - colors are defined in src/style.css
}

