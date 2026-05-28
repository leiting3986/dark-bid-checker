const { app, BrowserWindow } = require('electron')
const path = require('path')
const http = require('http')
const fs = require('fs')
const { spawn } = require('child_process')

let mainWindow = null
let backendProcess = null

const BACKEND_PORT = 8000
const BACKEND_URL = `http://127.0.0.1:${BACKEND_PORT}`
const FRONTEND_BASE_PORT = 3000
let frontendUrl = `http://localhost:${FRONTEND_BASE_PORT}`

function waitForService(url, maxRetries = 30) {
  return new Promise((resolve) => {
    let retries = 0
    const check = () => {
      console.log(`检查服务: ${url} (尝试 ${retries + 1}/${maxRetries})`)
      http.get(url, (res) => {
        console.log(`服务就绪: ${url}, 状态: ${res.statusCode}`)
        resolve(true)
      }).on('error', (err) => {
        console.log(`服务未就绪: ${err.message}`)
        retries++
        if (retries >= maxRetries) {
          resolve(false)
        } else {
          setTimeout(check, 1000)
        }
      })
    }
    check()
  })
}

function startBackend() {
  const rootDir = path.resolve(__dirname, '..', '..')
  const backendDir = path.join(rootDir, 'backend')
  const backendScript = path.join(backendDir, 'main.py')
  const packagedExe = path.join(process.resourcesPath || '', 'backend', 'main.exe')

  if (fs.existsSync(packagedExe)) {
    backendProcess = spawn(packagedExe, [], { cwd: path.dirname(packagedExe), windowsHide: true })
    return true
  }

  if (fs.existsSync(backendScript)) {
    backendProcess = spawn('python', [backendScript], { cwd: backendDir, windowsHide: true })
    backendProcess.stdout.on('data', (data) => console.log(`[backend] ${data}`))
    backendProcess.stderr.on('data', (data) => console.error(`[backend] ${data}`))
    return true
  }

  return false
}

async function ensureBackendReady() {
  if (await waitForService(BACKEND_URL, 3)) return true
  console.log('后端未运行，尝试自动启动...')
  if (!startBackend()) return false
  return waitForService(BACKEND_URL, 30)
}

async function detectFrontendPort() {
  console.log('开始检测前端端口...')
  for (let port = FRONTEND_BASE_PORT; port <= 3010; port++) {
    try {
      console.log(`尝试端口: ${port}`)
      await new Promise((resolve, reject) => {
        const req = http.get(`http://localhost:${port}`, (res) => {
          frontendUrl = `http://localhost:${port}`
          console.log(`找到前端端口: ${port}, 状态: ${res.statusCode}`)
          resolve()
        })
        req.on('error', (err) => {
          console.log(`端口 ${port} 错误: ${err.message}`)
          reject(err)
        })
        req.setTimeout(2000, () => {
          req.destroy()
          reject(new Error('timeout'))
        })
      })
      return
    } catch (e) {
      continue
    }
  }
  frontendUrl = BACKEND_URL
  console.log('未找到 Vite 前端，使用后端静态页面:', frontendUrl)
}

function createWindow(backendReady) {
  console.log('创建窗口，加载:', backendReady ? frontendUrl : '错误页')
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    title: '暗标检查工具',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true
    }
  })

  if (backendReady) {
    mainWindow.loadURL(frontendUrl)
  } else {
    mainWindow.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent('<h2>后端服务启动失败</h2><p>请确认 Python 环境可用，或手动运行 backend/main.py。</p>')}`)
  }

  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

app.whenReady().then(async () => {
  console.log('Electron 就绪，等待服务...')
  const backendReady = await ensureBackendReady()
  if (backendReady) await detectFrontendPort()
  createWindow(backendReady)
})

app.on('window-all-closed', () => {
  app.quit()
})

app.on('before-quit', () => {
  if (backendProcess) backendProcess.kill()
})
