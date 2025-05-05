/** @type {import('tailwindcss').Config} */
const colors = require('tailwindcss/colors');

module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        ...colors, 

        
        bleu_bg: '#E7EDF4',
        blue_nav: '#1A3852',
        blue_top: '#C9DEF6',
        bleu_selected: "#0086CA",
        title: '#303133',
        text: '#272525',
        blue: '#0086CA',  
        grey: '#121212',
        green: '#10A142',
        violet: '#2D5F8B'
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
