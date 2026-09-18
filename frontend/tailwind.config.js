/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["'Manrope'", "system-ui", "sans-serif"],
      },
      colors: {
        ink: "#1F2937",
        muted: "#6B7280",
        canvas: "#F3F5F7",
        admin: {
          DEFAULT: "#3E6B52",
          dark: "#2F5540",
          soft: "#E7F0EA",
        },
        ong: {
          DEFAULT: "#33566F",
          dark: "#274456",
          soft: "#E6EDF2",
        },
        adopter: {
          DEFAULT: "#6A4C8C",
          dark: "#553C72",
          soft: "#EFE8F5",
        },
      },
      boxShadow: {
        card: "0 1px 2px rgba(15, 23, 42, 0.06), 0 1px 1px rgba(15,23,42,0.04)",
      },
    },
  },
  plugins: [],
}

