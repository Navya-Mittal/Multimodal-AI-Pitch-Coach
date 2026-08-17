/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#0B0B0F",
        surface: "#16161D",
        accent: "#7C5CFF",
      },
    },
  },
  plugins: [],
};
