/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        border: "#E5E7EB",
        background: "#FFFFFF",
        foreground: "#0F172A",
        muted: "#F8FAFC",
        "muted-foreground": "#64748B",
        accent: "#F1F5F9",
      }
    },
  },
  plugins: [],
}
