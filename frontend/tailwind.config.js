/** @type {import('tailwindcss').Config} */
const colors = require('tailwindcss/colors');

module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Conserver les couleurs standard de Tailwind
        slate: colors.slate,
        gray: colors.gray,
        zinc: colors.zinc,
        neutral: colors.neutral,
        stone: colors.stone,
        red: colors.red,
        orange: colors.orange,
        amber: colors.amber,
        yellow: colors.yellow,
        lime: colors.lime,
        green: colors.green,
        emerald: colors.emerald,
        teal: colors.teal,
        cyan: colors.cyan,
        sky: colors.sky,
        blue: colors.blue, // Ceci préserve les bleu-600, bleu-500, etc.
        indigo: colors.indigo,
        violet: colors.violet,
        purple: colors.purple,
        fuchsia: colors.fuchsia,
        pink: colors.pink,
        rose: colors.rose,
        
        // Vos couleurs personnalisées
        bleu_bg: '#E7EDF4',
        blue_nav: '#1A3852',
        blue_top: '#C9DEF6',
        bleu_selected: "#0086CA",
        title: '#303133',
        text: '#272525',
        blue_custom: '#0086CA',  // Renommé pour éviter le conflit avec colors.blue
        grey: '#121212',
        green_custom: '#10A142', // Renommé pour éviter le conflit avec colors.green
        violet_custom: '#2D5F8B'  // Renommé pour éviter le conflit avec colors.violet
      },
      fontFamily: {
        nunito: ['Nunito'],
        poppins: ['Poppins'],
      },
      screens: {
        xs: '430px',
      },
    },
  },
  plugins: [],
}