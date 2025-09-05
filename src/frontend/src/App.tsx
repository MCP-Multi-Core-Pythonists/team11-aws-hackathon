import { useState } from 'react'

function App() {
  const [status, setStatus] = useState<string>('Ready')

  const testBackend = async () => {
    try {
      setStatus('Testing...')
      const response = await fetch('/api/health')
      const data = await response.json()
      setStatus(`Backend OK: ${data.status}`)
    } catch (error) {
      setStatus(`Backend Error: ${error}`)
    }
  }

  const testAuth = async () => {
    try {
      setStatus('Testing Auth...')
      const response = await fetch('/api/v1/auth/oauth/google/url')
      const data = await response.json()
      setStatus(`Auth URL: ${data.auth_url}`)
    } catch (error) {
      setStatus(`Auth Error: ${error}`)
    }
  }

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>TeamSync Pro - Test Dashboard</h1>
      
      <div style={{ marginBottom: '20px' }}>
        <h2>Backend Status</h2>
        <p>Status: {status}</p>
        <button onClick={testBackend} style={{ marginRight: '10px' }}>
          Test Backend Health
        </button>
        <button onClick={testAuth}>
          Test Auth Endpoint
        </button>
      </div>

      <div>
        <h2>Features</h2>
        <ul>
          <li>✅ VS Code Extension Structure</li>
          <li>✅ Backend API with Authentication</li>
          <li>✅ Team Management</li>
          <li>✅ Configuration Sync</li>
          <li>🔄 Frontend UI (In Progress)</li>
        </ul>
      </div>
    </div>
  )
}

export default App
