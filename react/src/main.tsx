import { SocketProvider } from '@/contexts/socket'
import { StrictMode } from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import { PostHogProvider } from 'posthog-js/react'
import '@/assets/style/index.css'

const posthogKey = import.meta.env.VITE_PUBLIC_POSTHOG_KEY
const posthogHost = import.meta.env.VITE_PUBLIC_POSTHOG_HOST

const options = {
  api_host: posthogHost,
}

const rootElement = document.getElementById('root')!
if (!rootElement.innerHTML) {
  const root = ReactDOM.createRoot(rootElement)
  
  const AppWithProviders = () => (
    <SocketProvider>
      <App />
    </SocketProvider>
  )
  
  root.render(
    <StrictMode>
      {posthogKey ? (
        <PostHogProvider apiKey={posthogKey} options={options}>
          <AppWithProviders />
        </PostHogProvider>
      ) : (
        <AppWithProviders />
      )}
    </StrictMode>
  )
}
