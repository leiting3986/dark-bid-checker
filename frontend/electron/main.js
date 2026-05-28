const { app, BrowserWindow } = require('electron')
const path = require('path')
const http = require('http')

let mainWindow = null

const BACKEND_PORT = 8000
const BACKEND_URL = `http://127.0.0.1:${BACKEND_PORT}`
const FRONTEND_BASE_PORT = 3000
let frontendUrl = `http://localhost:${FRONTEND_BASE_PORT}`

// 等待服务就绪
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

// 检测前端端口
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
  console.log('使用默认端口:', FRONTEND_BASE_PORT)
}

// 创建主窗口
function createWindow() {
  console.log('创建窗口，加载:', frontendUrl)
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    title: '暗标检查工具',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true
    }
  })

  mainWindow.loadURL(frontendUrl)

  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

// 应用就绪
app.whenReady().then(async () => {
  console.log('Electron 就绪，等待服务...')

  // 等待后端
  await waitForService(BACKEND_URL)
  console.log('后端就绪')

  // 检测前端端口
  await detectFrontendPort()

  // 创建窗口
  createWindow()
})

app.on('window-all-closed', () => {
  app.quit()
})
