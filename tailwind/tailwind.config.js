/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "../templates/**/*.html",
    "../**/templates/**/*.html",
    "../**/templates/**/*.html",
  ],
  theme: {
    extend: {
      colors: {
        // Brand emerald palette (matches your usual emerald #006c49 vibe)
        brand: { DEFAULT: "#006c49", dark: "#005539" },
      },
    },
  },
  plugins: [],
};
