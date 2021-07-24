const colors = require("tailwindcss/colors");
const defaultTheme = require("tailwindcss/defaultTheme");

module.exports = {
  purge: {
    enabled: true,
    content: ["../**/templates/**/*.html"],
  },
  darkMode: false, // or 'media' or 'class'
  theme: {
    colors: {
      gray: colors.coolGray,
      yellow: colors.amber,
      green: colors.emerald,
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
