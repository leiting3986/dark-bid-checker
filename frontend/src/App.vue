<template>
  <div class="app-container">
    <!-- 顶部导航 -->
    <el-header class="app-header">
      <div class="header-content">
        <h1>暗标检查工具</h1>
        <el-tag type="info">v1.1</el-tag>
      </div>
    </el-header>

    <!-- 主要内容 -->
    <el-main class="app-main">
      <el-row :gutter="24">
        <!-- 左侧：上传和配置 -->
        <el-col :xs="24" :span="8">
          <el-card class="upload-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span>文件上传</span>
              </div>
            </template>

            <el-upload
              ref="uploadRef"
              class="upload-area"
              drag
              :auto-upload="false"
              :on-change="handleFileChange"
              :on-remove="handleFileRemove"
              :file-list="fileList"
              accept=".doc,.docx"
              :limit="1"
              :on-exceed="handleExceed"
            >
              <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
              <div class="el-upload__text">
                将 .doc 或 .docx 文件拖到此处，或<em>点击上传</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">支持 .doc 和 .docx 格式，最大 50MB</div>
              </template>
            </el-upload>

            <el-button
              type="primary"
              class="check-btn"
              :loading="checking"
              :disabled="!selectedFile || !currentConfig"
              @click="startCheck"
            >
              开始检查
            </el-button>
          </el-card>

          <el-card class="config-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span>暗标要求配置</span>
                <el-button type="primary" link @click="showConfigEditor = true" :disabled="!currentConfig">
                  编辑配置
                </el-button>
              </div>
            </template>

            <div class="config-summary" v-if="currentConfig">
              <el-descriptions :column="1" border size="small">
                <el-descriptions-item label="纸张">{{ currentConfig.requirements?.page?.size || 'A4' }}</el-descriptions-item>
                <el-descriptions-item label="页边距">{{ currentConfig.requirements?.page?.margins?.top_cm || 2.5 }}cm (四边)</el-descriptions-item>
                <el-descriptions-item label="正文字体">{{ currentConfig.requirements?.text?.font || '宋体' }} {{ currentConfig.requirements?.text?.fontSize_name || '四号' }}</el-descriptions-item>
                <el-descriptions-item label="行距">固定值 {{ currentConfig.requirements?.text?.lineSpacing?.value_pt || 28 }} 磅</el-descriptions-item>
                <el-descriptions-item label="表格字体">{{ currentConfig.requirements?.table?.font || '仿宋' }} {{ currentConfig.requirements?.table?.fontSize_name || '五号' }}</el-descriptions-item>
              </el-descriptions>
            </div>
            <div v-else class="config-loading">
              <el-skeleton :rows="5" animated />
            </div>
          </el-card>
        </el-col>

        <!-- 右侧：检查结果 -->
        <el-col :xs="24" :span="16">
          <el-card class="result-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span>检查结果</span>
                <div v-if="checkResult" class="result-actions">
                  <el-button type="success" :loading="fixing" @click="startFix">
                    一键修复
                  </el-button>
                  <el-button v-if="fixedFileId" type="primary" @click="downloadFixedFile">
                    下载修复文件
                  </el-button>
                </div>
              </div>
            </template>

            <!-- 无结果时的空状态 -->
            <div v-if="!checkResult" class="empty-state">
              <el-empty description="请上传 .docx 文件并点击检查" />
            </div>

            <!-- 检查结果 -->
            <div v-else class="result-content">
              <!-- 汇总 -->
              <el-row :gutter="16" class="result-summary">
                <el-col :span="8">
                  <el-statistic title="错误" :value="checkResult.total_errors">
                    <template #suffix>
                      <span class="error-count">项</span>
                    </template>
                  </el-statistic>
                </el-col>
                <el-col :span="8">
                  <el-statistic title="警告" :value="checkResult.total_warnings">
                    <template #suffix>
                      <span class="warning-count">项</span>
                    </template>
                  </el-statistic>
                </el-col>
                <el-col :span="8">
                  <el-statistic title="通过" :value="checkResult.total_passed">
                    <template #suffix>
                      <span class="passed-count">项</span>
                    </template>
                  </el-statistic>
                </el-col>
              </el-row>

              <!-- 是否通过 -->
              <el-alert
                v-if="checkResult.is_valid"
                title="检查通过"
                description="文档格式符合暗标要求"
                type="success"
                show-icon
                :closable="false"
                class="result-alert"
              />
              <el-alert
                v-else
                title="检查未通过"
                description="文档格式不符合暗标要求，请修复后重新检查"
                type="error"
                show-icon
                :closable="false"
                class="result-alert"
              />

              <!-- 错误列表 -->
              <div v-if="checkResult.errors?.length > 0" class="error-list">
                <h4>错误项</h4>
                <el-collapse>
                  <el-collapse-item
                    v-for="(error, index) in checkResult.errors"
                    :key="'error-' + index"
                    :name="index"
                  >
                    <template #title>
                      <el-tag type="danger" size="small" class="error-tag">错误</el-tag>
                      <span class="error-title">{{ error.message }}</span>
                    </template>
                    <div class="error-detail">
                      <p><strong>类别：</strong>{{ error.category }}</p>
                      <p v-if="error.detail"><strong>详情：</strong>{{ error.detail }}</p>
                      <p v-if="error.location"><strong>位置：</strong>{{ error.location }}</p>
                    </div>
                  </el-collapse-item>
                </el-collapse>
              </div>

              <!-- 警告列表 -->
              <div v-if="checkResult.warnings?.length > 0" class="warning-list">
                <h4>警告项</h4>
                <el-collapse>
                  <el-collapse-item
                    v-for="(warning, index) in checkResult.warnings"
                    :key="'warning-' + index"
                    :name="index"
                  >
                    <template #title>
                      <el-tag type="warning" size="small" class="warning-tag">警告</el-tag>
                      <span class="warning-title">{{ warning.message }}</span>
                    </template>
                    <div class="warning-detail">
                      <p><strong>类别：</strong>{{ warning.category }}</p>
                      <p v-if="warning.detail"><strong>详情：</strong>{{ warning.detail }}</p>
                    </div>
                  </el-collapse-item>
                </el-collapse>
              </div>

              <!-- 通过项 -->
              <div v-if="checkResult.passed?.length > 0" class="passed-list">
                <el-collapse>
                  <el-collapse-item title="通过项" name="passed">
                    <div class="passed-tags">
                      <el-tag
                        v-for="(item, index) in checkResult.passed"
                        :key="'passed-' + index"
                        type="success"
                        class="passed-tag"
                      >
                        {{ item }}
                      </el-tag>
                    </div>
                  </el-collapse-item>
                </el-collapse>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-main>

    <!-- 配置编辑弹窗 -->
    <el-dialog
      v-model="showConfigEditor"
      title="编辑暗标要求配置"
      width="800px"
      :close-on-click-modal="false"
    >
      <ConfigEditor
        v-if="showConfigEditor && currentConfig"
        :config="currentConfig"
        @save="handleConfigSave"
        @cancel="showConfigEditor = false"
      />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import { checkDocument, fixDocument, downloadFixed, cleanupFiles, getConfig, updateConfig } from './utils/api'
import ConfigEditor from './components/ConfigEditor.vue'

const uploadRef = ref(null)
const selectedFile = ref(null)
const fileList = ref([])
const checking = ref(false)
const fixing = ref(false)
const checkResult = ref(null)
const fixedFileId = ref(null)
const showConfigEditor = ref(false)
const currentConfig = ref(null)
const fileId = ref(null)

onMounted(async () => {
  try {
    const res = await getConfig('default_requirements.json')
    currentConfig.value = res.data
  } catch (e) {
    ElMessage.error('加载配置失败')
    console.error('加载配置失败', e)
  }
})

const handleFileChange = (file, uploadFileList) => {
  // 文件大小检查 50MB
  if (file.raw.size > 50 * 1024 * 1024) {
    ElMessage.warning('文件大小超过 50MB 限制')
    fileList.value = []
    selectedFile.value = null
    return
  }
  // 文件格式检查
  const name = file.raw.name.toLowerCase()
  if (!name.endsWith('.doc') && !name.endsWith('.docx')) {
    ElMessage.warning('仅支持 .doc 和 .docx 格式')
    fileList.value = []
    selectedFile.value = null
    return
  }
  selectedFile.value = file.raw
  fileList.value = uploadFileList.slice(-1)
  checkResult.value = null
  fixedFileId.value = null
}

const handleFileRemove = () => {
  // 清理之前的服务端文件
  if (fileId.value) {
    cleanupFiles(fileId.value).catch(() => {})
  }
  selectedFile.value = null
  checkResult.value = null
  fixedFileId.value = null
  fileId.value = null
}

const handleExceed = (files) => {
  // 清理之前的服务端文件
  if (fileId.value) {
    cleanupFiles(fileId.value).catch(() => {})
  }
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
  selectedFile.value = files[0]
  fileList.value = [{ name: files[0].name, url: '', raw: files[0] }]
  checkResult.value = null
  fixedFileId.value = null
  fileId.value = null
}

const startCheck = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }

  // 清理之前的服务端文件
  if (fileId.value) {
    cleanupFiles(fileId.value).catch(() => {})
  }

  checking.value = true
  checkResult.value = null
  fixedFileId.value = null

  try {
    const res = await checkDocument(selectedFile.value, 'default_requirements.json')
    checkResult.value = res.data.result
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
  if (!fileId.value) {
    ElMessage.warning('请先检查文件')
    return
  }

  try {
    await ElMessageBox.confirm('将自动修复文档格式，是否继续？', '确认修复', {
      confirmButtonText: '开始修复',
      cancelButtonText: '取消',
      type: 'info',
    })
  } catch {
    // 用户取消
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

const downloadFixedFile = async () => {
  if (!fixedFileId.value) {
    ElMessage.warning('没有可下载的修复文件')
    return
  }

  try {
    const res = await downloadFixed(fixedFileId.value)
    // 检查响应是否为 JSON 错误
    if (res.data.type === 'application/json') {
      const text = await res.data.text()
      const err = JSON.parse(text)
      ElMessage.error(err.detail || '下载失败')
      return
    }
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const link = document.createElement('a')
    link.href = url
    const originalName = selectedFile.value?.name || 'document'
    link.setAttribute('download', `fixed_${originalName}`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  } catch (e) {
    ElMessage.error('下载失败')
  }
}

const handleConfigSave = async (config) => {
  try {
    await updateConfig('default_requirements.json', config)
    currentConfig.value = config
    showConfigEditor.value = false
    ElMessage.success('配置已保存')
  } catch (e) {
    ElMessage.error('保存配置失败: ' + (e.response?.data?.detail || e.message))
  }
}
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  background: #f5f7fa;
}

.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  padding: 0 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-content h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.app-main {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.upload-card,
.config-card,
.result-card {
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.upload-area {
  width: 100%;
}

.check-btn {
  width: 100%;
  margin-top: 16px;
  height: 48px;
  font-size: 16px;
}

.config-summary {
  margin-top: 8px;
}

.config-loading {
  padding: 8px;
}

.result-actions {
  display: flex;
  gap: 12px;
}

.empty-state {
  padding: 60px 0;
}

.result-summary {
  margin-bottom: 24px;
  text-align: center;
}

.result-alert {
  margin-bottom: 24px;
}

.error-list,
.warning-list,
.passed-list {
  margin-bottom: 24px;
}

.error-list h4,
.warning-list h4 {
  margin-bottom: 12px;
  color: #303133;
}

.error-tag,
.warning-tag {
  margin-right: 8px;
}

.error-title,
.warning-title {
  font-weight: 500;
}

.error-detail,
.warning-detail {
  padding: 12px;
  background: #fafafa;
  border-radius: 4px;
}

.error-detail p,
.warning-detail p {
  margin: 4px 0;
  font-size: 14px;
  color: #606266;
}

.passed-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.passed-tag {
  margin: 0;
}

.error-count {
  color: #f56c6c;
}

.warning-count {
  color: #e6a23c;
}

.passed-count {
  color: #67c23a;
}
</style>
