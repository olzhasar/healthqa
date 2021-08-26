const colors = require("tailwindcss/colors");
const defaultTheme = require("tailwindcss/defaultTheme");

module.exports = {
  purge: {
    content: ["../backend/**/templates/**/*.html", "../backend/**/forms.py"],
    options: {
      safelist: ["/trix-*/"],
    },
  },
  darkMode: false, // or 'media' or 'class'
  theme: {
    colors: {
      gray: colors.blueGray,
      yellow: colors.amber,
      green: colors.teal,
      red: colors.red,
      blue: colors.blue,
      black: colors.black,
      white: colors.white,
    },
    fontFamily: {
      sans: ["Open Sans", ...defaultTheme.fontFamily.sans],
      serif: [...defaultTheme.fontFamily.serif],
      mono: [...defaultTheme.fontFamily.mono],
    },
    extend: {},
  },
  variants: {
    extend: {},
  },
  plugins: [],
};
