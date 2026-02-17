/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#1d4ed8",
          foreground: "#ffffff"
        },
        muted: {
          DEFAULT: "#f3f4f6",
          foreground: "#4b5563"
        }
      }
    }
  },
  plugins: []
};

