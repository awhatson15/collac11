/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/templates/**/*.html"],
  theme: {
    extend: {
      colors: {
        primary: '#006495',
      }
    }
  },
  plugins: [require("daisyui")],
  daisyui: {
    themes: [
      {
        light: {
          "primary": "#006495",
          "primary-focus": "#005481",
          ...require("daisyui/src/theming/themes")["[data-theme=light]"],
        },
      },
    ],
  },
} 