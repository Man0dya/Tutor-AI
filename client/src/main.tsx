import React from 'react'
import ReactDOM from 'react-dom/client'
import { ChakraProvider, extendTheme, ColorModeScript } from '@chakra-ui/react'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import { AuthProvider } from './context/AuthContext'

const config = {
  initialColorMode: 'system',
  useSystemColorMode: true,
} as const

const theme = extendTheme({
  config,
  semanticTokens: {
    colors: {
      bg: { default: 'gray.50', _dark: '#0b0b0d' },
      surface: { default: 'white', _dark: '#0f1113' },
      text: { default: 'gray.800', _dark: 'gray.100' },
      muted: { default: 'gray.600', _dark: 'gray.300' },
      border: { default: 'gray.200', _dark: 'gray.700' },
      codeBg: { default: 'gray.900', _dark: '#0f1113' },
      codeInlineBg: { default: 'gray.100', _dark: 'gray.700' },
      accent: { default: 'purple.500', _dark: 'purple.300' },
    },
  },
  styles: {
    global: {
      'html, body': {
        bg: 'bg',
        color: 'text',
      },
      '#root': {
        bg: 'bg',
        color: 'text',
        minHeight: '100vh',
      },
    },
  },
})

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ChakraProvider theme={theme}>
      <ColorModeScript initialColorMode={theme.config.initialColorMode} />
      <BrowserRouter>
        <AuthProvider>
          <App />
        </AuthProvider>
      </BrowserRouter>
    </ChakraProvider>
  </React.StrictMode>
)
