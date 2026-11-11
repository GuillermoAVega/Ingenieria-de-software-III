import { existsSync } from 'node:fs'
import { spawn } from 'node:child_process'
import path from 'node:path'

const root = process.cwd()
const backend = path.join(root, 'Backend')
const virtualEnvPython = process.platform === 'win32'
  ? path.join(backend, '.venv', 'Scripts', 'python.exe')
  : path.join(backend, '.venv', 'bin', 'python')

const python = existsSync(virtualEnvPython) ? virtualEnvPython : 'python'
const child = spawn(
  python,
  ['-m', 'uvicorn', 'src.main:app', '--reload', '--host', '127.0.0.1', '--port', '8000'],
  {
    cwd: backend,
    stdio: 'inherit',
  },
)

child.on('error', (error) => {
  console.error(`No se pudo iniciar el backend con ${python}: ${error.message}`)
  process.exit(1)
})

child.on('exit', (code, signal) => {
  if (signal) {
    process.kill(process.pid, signal)
  } else {
    process.exit(code ?? 1)
  }
})
