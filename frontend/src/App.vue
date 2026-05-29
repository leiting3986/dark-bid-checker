<template>
  <div class="app">
    <!-- 背景 -->
    <div class="bg-gradient"></div>
    <div class="bg-orbs">
      <div class="orb orb-1"></div>
      <div class="orb orb-2"></div>
      <div class="orb orb-3"></div>
    </div>

    <!-- 主容器 -->
    <div class="container">
      <!-- 头部 -->
      <header class="header">
        <div class="logo">
          <div class="logo-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="logo-text">
            <h1>暗标检查工具</h1>
            <span class="version">v1.6</span>
          </div>
        </div>
      </header>

      <!-- 主内容 -->
      <main class="main">
        <!-- 左侧面板 -->
        <aside class="sidebar">
          <!-- 上传卡片 -->
          <div class="glass-card upload-card">
            <div class="card-header">
              <h2>文件上传</h2>
            </div>
            <div class="card-body">
              <div
                class="upload-zone"
                :class="{ 'has-file': selectedFile }"
                @dragover.prevent
                @drop.prevent="handleDrop"
              >
                <input
                  ref="fileInput"
                  type="file"
                  accept=".doc,.docx"
                  @change="handleFileSelect"
                  hidden
                />
                <div v-if="!selectedFile" class="upload-placeholder" @click="$refs.fileInput.click()">
                  <div class="upload-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                      <path d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                  </div>
                  <p class="upload-text">拖拽文件到此处</p>
                  <p class="upload-hint">或点击选择 .doc / .docx 文件</p>
                </div>
                <div v-else class="upload-file">
                  <div class="file-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                      <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                  </div>
                  <div class="file-info">
                    <p class="file-name">{{ selectedFile.name }}</p>
                    <p class="file-size">{{ formatSize(selectedFile.size) }}</p>
                  </div>
                  <button class="file-remove" @click="removeFile">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                      <path d="M6 18L18 6M6 6l12 12" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                  </button>
                </div>
              </div>

              <button
                class="btn btn-primary"
                :disabled="!selectedFile || checking"
                @click="startCheck"
              >
                <span v-if="checking" class="btn-loading"></span>
                <span v-else>开始检查</span>
              </button>
            </div>
          </div>

          <!-- 配置卡片 -->
          <div class="glass-card config-card">
            <div class="card-header">
              <h2>配置要求</h2>
              <button class="btn-text" @click="showConfig = true">编辑</button>
            </div>
            <div class="card-body">
              <div v-if="config" class="config-list">
                <div class="config-item">
                  <span class="config-label">纸张</span>
                  <span class="config-value">{{ config.requirements?.page?.size || 'A4' }}</span>
                </div>
                <div class="config-item">
                  <span class="config-label">页边距</span>
                  <span class="config-value">{{ config.requirements?.page?.margins?.top_cm || 2.5 }}cm</span>
                </div>
                <div class="config-item">
                  <span class="config-label">正文字体</span>
                  <span class="config-value">{{ config.requirements?.text?.font || '宋体' }}</span>
                </div>
                <div class="config-item">
                  <span class="config-label">字号</span>
                  <span class="config-value">{{ config.requirements?.text?.fontSize_name || '四号' }}</span>
                </div>
                <div class="config-item">
                  <span class="config-label">行距</span>
                  <span class="config-value">{{ config.requirements?.text?.lineSpacing?.value_pt || 28 }}磅</span>
                </div>
              </div>
              <div v-else class="config-loading">
                <div class="skeleton"></div>
              </div>
            </div>
          </div>
        </aside>

        <!-- 右侧结果 -->
        <section class="content">
          <div class="glass-card result-card">
            <div class="card-header">
              <h2>检查结果</h2>
              <div v-if="result" class="result-actions">
                <button
                  v-if="!fixedFileId && !result.is_valid"
                  class="btn btn-success"
                  :disabled="fixing"
                  @click="startFix"
                >
                  <span v-if="fixing" class="btn-loading"></span>
                  <span v-else>一键修复</span>
                </button>
                <button
                  v-if="fixedFileId"
                  class="btn btn-primary"
                  @click="downloadFile"
                >
                  下载修复文件
                </button>
              </div>
            </div>
            <div class="card-body">
              <!-- 空状态 -->
              <div v-if="!result" class="empty-state">
                <div class="empty-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
                    <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </div>
                <p>上传文件并点击检查</p>
              </div>

              <!-- 结果内容 -->
              <div v-else class="result-content">
                <!-- 统计卡片 -->
                <div class="stats">
                  <div class="stat-item stat-error">
                    <span class="stat-value">{{ result.total_errors }}</span>
                    <span class="stat-label">错误</span>
                  </div>
                  <div class="stat-item stat-warning">
                    <span class="stat-value">{{ result.total_warnings }}</span>
                    <span class="stat-label">警告</span>
                  </div>
                  <div class="stat-item stat-passed">
                    <span class="stat-value">{{ result.total_passed }}</span>
                    <span class="stat-label">通过</span>
                  </div>
                </div>

                <!-- 状态提示 -->
                <div class="status-banner" :class="result.is_valid ? 'success' : 'error'">
                  <svg v-if="result.is_valid" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  <span>{{ result.is_valid ? '检查通过，文档格式符合要求' : '检查未通过，请修复后重新检查' }}</span>
                </div>

                <!-- 错误列表 -->
                <div v-if="result.errors?.length" class="issue-section">
                  <h3 class="section-title">错误项</h3>
                  <div class="issue-list">
                    <div v-for="(item, i) in result.errors" :key="i" class="issue-item error">
                      <div class="issue-header">
                        <span class="issue-badge">错误</span>
                        <span class="issue-message">{{ item.message }}</span>
                      </div>
                      <div class="issue-detail">
                        <p v-if="item.detail">{{ item.detail }}</p>
                        <p v-if="item.location" class="issue-location">{{ item.location }}</p>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- 警告列表 -->
                <div v-if="result.warnings?.length" class="issue-section">
                  <h3 class="section-title">警告项</h3>
                  <div class="issue-list">
                    <div v-for="(item, i) in result.warnings" :key="i" class="issue-item warning">
                      <div class="issue-header">
                        <span class="issue-badge">警告</span>
                        <span class="issue-message">{{ item.message }}</span>
                      </div>
                      <div class="issue-detail">
                        <p v-if="item.detail">{{ item.detail }}</p>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- 通过项 -->
                <div v-if="result.passed?.length" class="issue-section">
                  <h3 class="section-title">通过项</h3>
                  <div class="passed-tags">
                    <span v-for="(item, i) in result.passed" :key="i" class="passed-tag">
                      {{ item }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>

    <!-- 配置编辑弹窗 -->
    <Teleport to="body">
      <div v-if="showConfig" class="modal-overlay" @click.self="showConfig = false">
        <div class="modal glass-card">
          <div class="modal-header">
            <h2>编辑配置</h2>
            <button class="modal-close" @click="showConfig = false">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M6 18L18 6M6 6l12 12" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
          </div>
          <div class="modal-body">
            <ConfigEditor
              v-if="config"
              :config="config"
              @save="handleConfigSave"
              @cancel="showConfig = false"
            />
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { checkDocument, fixDocument, downloadFixed, cleanupFiles, getConfig, updateConfig } from './utils/api'
import ConfigEditor from './components/ConfigEditor.vue'

const fileInput = ref(null)
const selectedFile = ref(null)
const checking = ref(false)
const fixing = ref(false)
const result = ref(null)
const fixedFileId = ref(null)
const showConfig = ref(false)
const config = ref(null)
const fileId = ref(null)

const fontSizeMap = {
  42: '初号', 36: '小初', 26: '一号', 24: '小一', 22: '二号',
  18: '小二', 16: '三号', 15: '小三', 14: '四号', 12: '小四',
  10.5: '五号', 9: '小五', 7.5: '六号', 6.5: '小六', 5.5: '七号', 5: '八号'
}

const normalizeConfigDisplay = (nextConfig) => {
  const text = nextConfig.requirements?.text
  const table = nextConfig.requirements?.table
  if (text) text.fontSize_name = fontSizeMap[text.fontSize_pt] || text.fontSize_name || ''
  if (table) table.fontSize_name = fontSizeMap[table.fontSize_pt] || table.fontSize_name || ''
  return nextConfig
}

onMounted(async () => {
  try {
    const res = await getConfig('default_requirements.json')
    config.value = normalizeConfigDisplay(res.data)
  } catch (e) {
    ElMessage.error('加载配置失败')
  }
})

const formatSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

const handleDrop = (e) => {
  const file = e.dataTransfer.files[0]
  if (file) validateAndSetFile(file)
}

const handleFileSelect = (e) => {
  const file = e.target.files[0]
  if (file) validateAndSetFile(file)
}

const validateAndSetFile = (file) => {
  const name = file.name.toLowerCase()
  if (!name.endsWith('.doc') && !name.endsWith('.docx')) {
    ElMessage.warning('仅支持 .doc 和 .docx 格式')
    return
  }
  if (file.size > 50 * 1024 * 1024) {
    ElMessage.warning('文件大小超过 50MB 限制')
    return
  }
  selectedFile.value = file
  result.value = null
  fixedFileId.value = null
}

const removeFile = () => {
  if (fileId.value) cleanupFiles(fileId.value).catch(() => {})
  selectedFile.value = null
  result.value = null
  fixedFileId.value = null
  fileId.value = null
}

const startCheck = async () => {
  if (!selectedFile.value) return
  if (fileId.value) cleanupFiles(fileId.value).catch(() => {})

  checking.value = true
  result.value = null
  fixedFileId.value = null

  try {
    const res = await checkDocument(selectedFile.value, 'default_requirements.json')
    result.value = res.data.result
    fileId.value = res.data.file_id

    if (res.data.result.is_valid) {
      ElMessage.success('检查通过！')
    } else {
      ElMessage.warning(`发现 ${res.data.result.total_errors} 个错误`)
    }
  } catch (e) {
    ElMessage.error('检查失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    checking.value = false
  }
}

const startFix = async () => {
  if (!fileId.value) return

  try {
    await ElMessageBox.confirm('将自动修复文档格式，是否继续？', '确认修复', {
      confirmButtonText: '开始修复',
      cancelButtonText: '取消',
    })
  } catch {
    return
  }

  fixing.value = true

  try {
    const res = await fixDocument(fileId.value, 'default_requirements.json')
    fixedFileId.value = fileId.value
    ElMessage.success(`修复完成，共修改 ${res.data.result.total_changes} 处`)
  } catch (e) {
    ElMessage.error('修复失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    fixing.value = false
  }
}

const downloadFile = async () => {
  if (!fixedFileId.value) return

  try {
    const res = await downloadFixed(fixedFileId.value)
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const link = document.createElement('a')
    link.href = url
    const name = selectedFile.value?.name || 'document'
    link.setAttribute('download', `fixed_${name}`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  } catch (e) {
    ElMessage.error('下载失败')
  }
}

const handleConfigSave = async (newConfig) => {
  try {
    await updateConfig('default_requirements.json', newConfig)
    config.value = normalizeConfigDisplay(newConfig)
    showConfig.value = false
    ElMessage.success('配置已保存')
  } catch (e) {
    ElMessage.error('保存失败')
  }
}
</script>

<style>
/* ========== 基础变量 ========== */
:root {
  --bg-primary: #f5f5f7;
  --bg-glass: rgba(255, 255, 255, 0.72);
  --bg-glass-hover: rgba(255, 255, 255, 0.85);
  --border-glass: rgba(255, 255, 255, 0.5);
  --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.04);
  --shadow-md: 0 8px 32px rgba(0, 0, 0, 0.08);
  --shadow-lg: 0 16px 48px rgba(0, 0, 0, 0.12);
  --text-primary: #1d1d1f;
  --text-secondary: #86868b;
  --text-tertiary: #aeaeb2;
  --accent-blue: #0071e3;
  --accent-blue-hover: #0077ed;
  --accent-green: #34c759;
  --accent-orange: #ff9f0a;
  --accent-red: #ff3b30;
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-xl: 20px;
  --blur: 20px;
  --font-sans: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Helvetica Neue", "PingFang SC", "Microsoft YaHei", sans-serif;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: var(--font-sans);
  background: var(--bg-primary);
  color: var(--text-primary);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  overflow-x: hidden;
}

/* ========== 背景 ========== */
.app {
  min-height: 100vh;
  position: relative;
}

.bg-gradient {
  position: fixed;
  inset: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  opacity: 0.12;
  z-index: 0;
}

.bg-orbs {
  position: fixed;
  inset: 0;
  overflow: hidden;
  z-index: 0;
}

.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.3;
  animation: float 20s ease-in-out infinite;
}

.orb-1 {
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, #667eea, transparent);
  top: -10%;
  left: -10%;
  animation-delay: 0s;
}

.orb-2 {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, #764ba2, transparent);
  top: 50%;
  right: -5%;
  animation-delay: -7s;
}

.orb-3 {
  width: 350px;
  height: 350px;
  background: radial-gradient(circle, #f093fb, transparent);
  bottom: -10%;
  left: 30%;
  animation-delay: -14s;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(30px, -30px) scale(1.05); }
  66% { transform: translate(-20px, 20px) scale(0.95); }
}

/* ========== 容器 ========== */
.container {
  position: relative;
  z-index: 1;
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* ========== 头部 ========== */
.header {
  margin-bottom: 32px;
  animation: slideDown 0.6s ease-out;
}

@keyframes slideDown {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}

.logo {
  display: flex;
  align-items: center;
  gap: 14px;
}

.logo-icon {
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, var(--accent-blue), #5856d6);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 4px 16px rgba(0, 113, 227, 0.3);
}

.logo-icon svg {
  width: 24px;
  height: 24px;
}

.logo-text h1 {
  font-size: 22px;
  font-weight: 600;
  letter-spacing: -0.3px;
  color: var(--text-primary);
}

.version {
  font-size: 12px;
  color: var(--text-tertiary);
  font-weight: 500;
}

/* ========== 主布局 ========== */
.main {
  display: grid;
  grid-template-columns: 340px 1fr;
  gap: 24px;
  flex: 1;
  animation: fadeUp 0.6s ease-out 0.1s both;
}

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ========== 毛玻璃卡片 ========== */
.glass-card {
  background: var(--bg-glass);
  backdrop-filter: blur(var(--blur));
  -webkit-backdrop-filter: blur(var(--blur));
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-md);
  overflow: hidden;
  transition: all 0.3s ease;
}

.glass-card:hover {
  background: var(--bg-glass-hover);
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
}

.card-header h2 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.card-body {
  padding: 24px;
}

/* ========== 侧边栏 ========== */
.sidebar {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* ========== 上传区域 ========== */
.upload-zone {
  border: 2px dashed rgba(0, 0, 0, 0.08);
  border-radius: var(--radius-lg);
  transition: all 0.3s ease;
  cursor: pointer;
  margin-bottom: 16px;
}

.upload-zone:hover {
  border-color: var(--accent-blue);
  background: rgba(0, 113, 227, 0.03);
}

.upload-zone.has-file {
  border-style: solid;
  border-color: var(--accent-blue);
  background: rgba(0, 113, 227, 0.03);
}

.upload-placeholder {
  padding: 32px;
  text-align: center;
}

.upload-icon {
  width: 48px;
  height: 48px;
  margin: 0 auto 16px;
  color: var(--text-tertiary);
  transition: color 0.3s;
}

.upload-zone:hover .upload-icon {
  color: var(--accent-blue);
}

.upload-icon svg {
  width: 100%;
  height: 100%;
}

.upload-text {
  font-size: 15px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.upload-hint {
  font-size: 13px;
  color: var(--text-tertiary);
}

.upload-file {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
}

.file-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, var(--accent-blue), #5856d6);
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.file-icon svg {
  width: 22px;
  height: 22px;
}

.file-info {
  flex: 1;
  min-width: 0;
}

.file-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-size {
  font-size: 12px;
  color: var(--text-tertiary);
  margin-top: 2px;
}

.file-remove {
  width: 28px;
  height: 28px;
  border: none;
  background: rgba(0, 0, 0, 0.04);
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-tertiary);
  transition: all 0.2s;
  flex-shrink: 0;
}

.file-remove:hover {
  background: rgba(255, 59, 48, 0.1);
  color: var(--accent-red);
}

.file-remove svg {
  width: 14px;
  height: 14px;
}

/* ========== 按钮 ========== */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  height: 44px;
  border: none;
  border-radius: var(--radius-md);
  font-size: 15px;
  font-weight: 500;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--accent-blue);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: var(--accent-blue-hover);
  box-shadow: 0 4px 16px rgba(0, 113, 227, 0.3);
  transform: translateY(-1px);
}

.btn-success {
  background: var(--accent-green);
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: #2db84e;
  box-shadow: 0 4px 16px rgba(52, 199, 89, 0.3);
  transform: translateY(-1px);
}

.btn-text {
  border: none;
  background: none;
  color: var(--accent-blue);
  font-size: 14px;
  font-weight: 500;
  font-family: inherit;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: var(--radius-sm);
  transition: all 0.2s;
}

.btn-text:hover {
  background: rgba(0, 113, 227, 0.08);
}

.btn-loading {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ========== 配置列表 ========== */
.config-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.config-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: var(--radius-sm);
}

.config-label {
  font-size: 13px;
  color: var(--text-secondary);
}

.config-value {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.config-loading {
  padding: 8px;
}

.skeleton {
  height: 200px;
  background: linear-gradient(90deg, rgba(0,0,0,0.04) 25%, rgba(0,0,0,0.08) 50%, rgba(0,0,0,0.04) 75%);
  background-size: 200% 100%;
  border-radius: var(--radius-sm);
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  from { background-position: 200% 0; }
  to { background-position: -200% 0; }
}

/* ========== 空状态 ========== */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  color: var(--text-tertiary);
}

.empty-icon {
  width: 64px;
  height: 64px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-icon svg {
  width: 100%;
  height: 100%;
}

.empty-state p {
  font-size: 15px;
}

/* ========== 统计卡片 ========== */
.stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-item {
  text-align: center;
  padding: 20px;
  border-radius: var(--radius-md);
  background: rgba(0, 0, 0, 0.02);
}

.stat-value {
  display: block;
  font-size: 32px;
  font-weight: 600;
  letter-spacing: -1px;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 13px;
  color: var(--text-secondary);
}

.stat-error .stat-value { color: var(--accent-red); }
.stat-warning .stat-value { color: var(--accent-orange); }
.stat-passed .stat-value { color: var(--accent-green); }

/* ========== 状态横幅 ========== */
.status-banner {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  border-radius: var(--radius-md);
  margin-bottom: 24px;
  font-size: 14px;
  font-weight: 500;
}

.status-banner svg {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.status-banner.success {
  background: rgba(52, 199, 89, 0.1);
  color: #1b7a35;
}

.status-banner.error {
  background: rgba(255, 59, 48, 0.1);
  color: #d70015;
}

/* ========== 问题列表 ========== */
.issue-section {
  margin-bottom: 24px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.issue-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

.issue-item {
  padding: 12px 14px;
  border-radius: var(--radius-md);
  background: rgba(0, 0, 0, 0.02);
  border-left: 3px solid transparent;
}

.issue-item.error {
  border-left-color: var(--accent-red);
}

.issue-item.warning {
  border-left-color: var(--accent-orange);
}

.issue-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}

.issue-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.issue-item.error .issue-badge {
  background: rgba(255, 59, 48, 0.1);
  color: var(--accent-red);
}

.issue-item.warning .issue-badge {
  background: rgba(255, 159, 10, 0.1);
  color: var(--accent-orange);
}

.issue-message {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.issue-detail {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
  padding-left: 48px;
}

.issue-location {
  margin-top: 4px;
  color: var(--text-tertiary);
  font-size: 12px;
}

/* ========== 通过标签 ========== */
.passed-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.passed-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  background: rgba(52, 199, 89, 0.08);
  color: #1b7a35;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
}

.passed-tag::before {
  content: '';
  width: 6px;
  height: 6px;
  background: var(--accent-green);
  border-radius: 50%;
}

/* ========== 结果操作 ========== */
.result-actions {
  display: flex;
  gap: 10px;
}

.result-actions .btn {
  width: auto;
  padding: 0 20px;
  height: 36px;
  font-size: 14px;
}

/* ========== 弹窗 ========== */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal {
  width: 90%;
  max-width: 700px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  animation: scaleIn 0.3s ease;
}

@keyframes scaleIn {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
}

.modal-header h2 {
  font-size: 18px;
  font-weight: 600;
}

.modal-close {
  width: 32px;
  height: 32px;
  border: none;
  background: rgba(0, 0, 0, 0.04);
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  transition: all 0.2s;
}

.modal-close:hover {
  background: rgba(0, 0, 0, 0.08);
  color: var(--text-primary);
}

.modal-close svg {
  width: 16px;
  height: 16px;
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
  flex: 1;
}

/* ========== 响应式 ========== */
@media (max-width: 900px) {
  .main {
    grid-template-columns: 1fr;
  }

  .container {
    padding: 16px;
  }

  .stats {
    grid-template-columns: repeat(3, 1fr);
  }

  .issue-list {
    grid-template-columns: 1fr;
  }
}
</style>
