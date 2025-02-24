import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'
import fs from 'fs'

// Load environment variables from the root .env file
const loadRootEnv = () => {
  const rootEnvPath = path.resolve(__dirname, '../../.env')
  if (fs.existsSync(rootEnvPath)) {
    const envContent = fs.readFileSync(rootEnvPath, 'utf-8')
    const env: Record<string, string> = {}
    
    envContent.split('\n').forEach(line => {
      const match = line.match(/^\s*([\w.-]+)\s*=\s*(.*)?\s*$/)
      if (match && !line.startsWith('#')) {
        const key = match[1]
        let value = match[2] || ''
        if (value.startsWith('"') && value.endsWith('"')) {
          value = value.substring(1, value.length - 1)
        }
        env[key] = value
      }
    })
    
    return env
  }
  return {}
}

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // Load env variables
  const env = loadEnv(mode, process.cwd())
  const rootEnv = loadRootEnv()
  
  // Combine env variables, with rootEnv taking precedence
  const combinedEnv = { ...env, ...rootEnv }
  
  // Get backend host and port from env
  const backendHost = combinedEnv.HOST || '127.0.0.1'
  const backendPort = combinedEnv.PORT || '9020'
  
  return {
    plugins: [react()],
    server: {
      proxy: {
        // Proxy API requests to the backend during development
        '/api': {
          target: `http://${backendHost}:${backendPort}`,
          changeOrigin: true,
          secure: false,
        },
      },
    },
    build: {
      // Output to the FastAPI static directory when building for production
      outDir: '../backend/static',
      emptyOutDir: true,
    },
  }
})
