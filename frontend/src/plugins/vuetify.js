import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

const light = {
  dark: false,
  colors: {
    background: '#F5F5F5',
    surface: '#FFFFFF',
    primary: '#1565C0',
    secondary: '#43A047',
    accent: '#FF8F00',
    error: '#D32F2F',
  },
}

const dark = {
  dark: true,
  colors: {
    background: '#121212',
    surface: '#1E1E1E',
    primary: '#42A5F5',
    secondary: '#66BB6A',
    accent: '#FFA726',
    error: '#EF5350',
  },
}

export default createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: localStorage.getItem('theme') || 'light',
    themes: { light, dark },
  },
  defaults: {
    VCard: { elevation: 2, rounded: 'lg' },
    VBtn: { variant: 'flat', rounded: 'lg' },
    VDataTable: { hover: true },
    VChip: { rounded: 'md' },
  },
})
