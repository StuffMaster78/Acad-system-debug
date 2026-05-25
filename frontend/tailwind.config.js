/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{vue,ts}"],
  theme: {
    extend: {
      colors: {
        ink: "#17202a",
        graphite: "#2f3a45",
        mist: "#eef3f6",
        signal: "#0f766e",
        saffron: "#b7791f",
        berry: "#9f1239",
      },
      boxShadow: {
        panel: "0 1px 2px rgba(23, 32, 42, 0.08)",
      },
    },
  },
  plugins: [],
};
