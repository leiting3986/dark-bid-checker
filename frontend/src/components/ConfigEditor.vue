<template>
  <div class="config-editor">
    <!-- 一键导入 -->
    <div class="import-section">
      <button class="btn btn-import" @click="showImport = true">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="16" height="16">
          <path d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        一键导入配置
      </button>
      <button class="btn btn-restore" @click="handleRestore">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="16" height="16">
          <path d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        恢复默认
      </button>
    </div>

    <!-- 导入弹窗 -->
    <div v-if="showImport" class="import-overlay" @click.self="showImport = false">
      <div class="import-dialog">
        <h3>粘贴配置要求</h3>
        <p class="import-hint">粘贴招标文件中的格式要求，系统自动识别</p>
        <textarea
          v-model="importText"
          rows="8"
          placeholder="例如：纸张A4，页边距上下2.5cm，左右3cm，正文宋体四号，行距28磅，表格仿宋五号，禁止页眉页脚"
        ></textarea>
        <div v-if="importResult" class="import-preview">
          <h4>识别结果：</h4>
          <ul>
            <li v-for="(item, i) in importResult" :key="i">{{ item }}</li>
          </ul>
        </div>
        <div class="import-actions">
          <button class="btn btn-secondary" @click="showImport = false">取消</button>
          <button class="btn btn-secondary" @click="handleParse">解析</button>
          <button class="btn btn-primary" :disabled="!importResult" @click="handleApply">应用</button>
        </div>
        <p v-if="importError" class="import-error">{{ importError }}</p>
      </div>
    </div>

    <!-- 页面设置 -->
    <div class="section">
      <h3 class="section-title">页面设置</h3>
      <div class="form-grid">
        <div class="form-item">
          <label>纸张大小</label>
          <select v-model="form.requirements.page.size">
            <option value="A4">A4</option>
            <option value="A3">A3</option>
            <option value="B5">B5</option>
          </select>
        </div>
        <div class="form-item">
          <label>页边距 (cm)</label>
          <div class="margin-inputs">
            <div class="margin-field">
              <span>上</span>
              <input type="number" v-model.number="form.requirements.page.margins.top_cm" step="0.1" min="0" />
            </div>
            <div class="margin-field">
              <span>下</span>
              <input type="number" v-model.number="form.requirements.page.margins.bottom_cm" step="0.1" min="0" />
            </div>
            <div class="margin-field">
              <span>左</span>
              <input type="number" v-model.number="form.requirements.page.margins.left_cm" step="0.1" min="0" />
            </div>
            <div class="margin-field">
              <span>右</span>
              <input type="number" v-model.number="form.requirements.page.margins.right_cm" step="0.1" min="0" />
            </div>
          </div>
        </div>
        <div class="form-item">
          <label>页眉页脚</label>
          <div class="checkbox-group">
            <label class="checkbox">
              <input type="checkbox" v-model="form.requirements.page.noHeader" />
              <span>禁止页眉</span>
            </label>
            <label class="checkbox">
              <input type="checkbox" v-model="form.requirements.page.noFooter" />
              <span>禁止页脚</span>
            </label>
          </div>
        </div>
      </div>
    </div>

    <!-- 正文格式 -->
    <div class="section">
      <h3 class="section-title">正文格式</h3>
      <div class="form-grid">
        <div class="form-item">
          <label>字体</label>
          <select v-model="form.requirements.text.font">
            <option value="宋体">宋体</option>
            <option value="仿宋">仿宋</option>
            <option value="黑体">黑体</option>
            <option value="楷体">楷体</option>
          </select>
        </div>
        <div class="form-item">
          <label>字号</label>
          <div class="number-input">
            <input type="number" v-model.number="form.requirements.text.fontSize_pt" :min="8" :max="36" :step="0.5" />
            <span class="hint">{{ fontSizeName }}</span>
          </div>
        </div>
        <div class="form-item">
          <label>行距 (磅)</label>
          <div class="number-input">
            <input type="number" v-model.number="form.requirements.text.lineSpacing.value_pt" :min="12" :max="60" />
            <span class="hint">固定值</span>
          </div>
        </div>
        <div class="form-item">
          <label>段间距 (磅)</label>
          <input type="number" v-model.number="form.requirements.text.paragraphSpacing_pt" :min="0" :max="36" />
        </div>
      </div>
    </div>

    <!-- 表格格式 -->
    <div class="section">
      <h3 class="section-title">表格格式</h3>
      <div class="form-grid">
        <div class="form-item">
          <label>表格字体</label>
          <select v-model="form.requirements.table.font">
            <option value="仿宋">仿宋</option>
            <option value="宋体">宋体</option>
            <option value="黑体">黑体</option>
            <option value="楷体">楷体</option>
          </select>
        </div>
        <div class="form-item">
          <label>表格字号</label>
          <div class="number-input">
            <input type="number" v-model.number="form.requirements.table.fontSize_pt" :min="8" :max="24" :step="0.5" />
            <span class="hint">{{ tableFontSizeName }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 禁止内容 -->
    <div class="section">
      <h3 class="section-title">禁止内容</h3>
      <div class="form-item full">
        <label>投标人名称</label>
        <textarea
          v-model="forbiddenText"
          rows="4"
          placeholder="每行一个投标人名称，检查时将禁止出现这些内容"
        ></textarea>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="actions">
      <button class="btn btn-secondary" @click="$emit('cancel')">取消</button>
      <button class="btn btn-primary" @click="handleSave">保存配置</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { importConfig, resetConfig } from '../utils/api'

const props = defineProps({
  config: { type: Object, required: true }
})

const emit = defineEmits(['save', 'cancel'])

const form = ref(JSON.parse(JSON.stringify(props.config)))

const pageSizeMap = {
  A3: { width_mm: 297, height_mm: 420 },
  A4: { width_mm: 210, height_mm: 297 },
  B5: { width_mm: 176, height_mm: 250 }
}

const ensurePath = (root, parts) => {
  let target = root
  for (const part of parts) {
    if (!target[part] || typeof target[part] !== 'object') target[part] = {}
    target = target[part]
  }
  return target
}

const syncPageSize = () => {
  const page = form.value.requirements.page
  const size = page.size
  if (pageSizeMap[size]) {
    page.width_mm = pageSizeMap[size].width_mm
    page.height_mm = pageSizeMap[size].height_mm
  }
}

watch(() => form.value.requirements.page.size, syncPageSize)

const fontSizeMap = {
  42: '初号', 36: '小初', 26: '一号', 24: '小一', 22: '二号',
  18: '小二', 16: '三号', 15: '小三', 14: '四号', 12: '小四',
  10.5: '五号', 9: '小五', 7.5: '六号', 6.5: '小六', 5.5: '七号', 5: '八号'
}

const fontSizeName = computed(() => fontSizeMap[form.value.requirements.text.fontSize_pt] || '')
const tableFontSizeName = computed(() => fontSizeMap[form.value.requirements.table.fontSize_pt] || '')

const forbiddenText = computed({
  get: () => {
    const names = form.value.requirements.forbiddenContent.bidderNames || []
    const companies = form.value.requirements.forbiddenContent.companyNames || []
    return [...new Set([...names, ...companies])].join('\n')
  },
  set: (val) => {
    const lines = val.split('\n').filter(l => l.trim())
    form.value.requirements.forbiddenContent.bidderNames = lines
    form.value.requirements.forbiddenContent.companyNames = lines
  }
})

// 一键导入
const showImport = ref(false)
const importText = ref('')
const importResult = ref(null)
const importError = ref('')
let parsedData = null

const handleParse = async () => {
  if (!importText.value.trim()) return
  importError.value = ''
  importResult.value = null
  try {
    const res = await importConfig(importText.value)
    importResult.value = res.data.fields
    parsedData = res.data.parsed
  } catch (e) {
    importError.value = e.response?.data?.detail || '解析失败'
  }
}

const handleApply = () => {
  if (!parsedData) return
  const req = form.value.requirements

  for (const [key, value] of Object.entries(parsedData)) {
    const parts = key.split('.')
    const target = ensurePath(req, parts.slice(0, -1))
    target[parts[parts.length - 1]] = value
  }
  syncPageSize()

  showImport.value = false
  importText.value = ''
  importResult.value = null
  parsedData = null
}

const handleRestore = async () => {
  if (!confirm('确定恢复默认配置？当前修改将丢失')) return
  try {
    const res = await resetConfig('default_requirements.json')
    form.value = JSON.parse(JSON.stringify(res.data.config))
  } catch (e) {
    alert('恢复失败')
  }
}

const handleSave = () => {
  syncPageSize()
  emit('save', form.value)
}
</script>

<style scoped>
.config-editor {
  max-height: 65vh;
  overflow-y: auto;
  padding-right: 8px;
}

.config-editor::-webkit-scrollbar {
  width: 6px;
}

.config-editor::-webkit-scrollbar-track {
  background: transparent;
}

.config-editor::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 3px;
}

/* 一键导入 */
.import-section {
  display: flex;
  gap: 10px;
  margin-bottom: 24px;
}

.btn-import {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  border: 1px dashed rgba(0, 113, 227, 0.3);
  border-radius: 10px;
  background: rgba(0, 113, 227, 0.04);
  color: var(--accent-blue);
  font-size: 14px;
  font-weight: 500;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-import:hover {
  background: rgba(0, 113, 227, 0.08);
  border-color: rgba(0, 113, 227, 0.5);
}

.btn-restore {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 10px;
  background: rgba(0, 0, 0, 0.02);
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-restore:hover {
  background: rgba(0, 0, 0, 0.05);
}

.import-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.import-dialog {
  width: 90%;
  max-width: 520px;
  background: white;
  border-radius: 16px;
  padding: 28px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

.import-dialog h3 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 6px;
}

.import-hint {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 16px;
}

.import-dialog textarea {
  width: 100%;
  padding: 12px 14px;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 10px;
  background: rgba(0, 0, 0, 0.02);
  font-size: 14px;
  font-family: inherit;
  line-height: 1.6;
  resize: vertical;
  outline: none;
  transition: all 0.2s;
}

.import-dialog textarea:focus {
  border-color: var(--accent-blue);
  box-shadow: 0 0 0 3px rgba(0, 113, 227, 0.1);
}

.import-preview {
  margin-top: 16px;
  padding: 14px;
  background: rgba(52, 199, 89, 0.06);
  border-radius: 10px;
}

.import-preview h4 {
  font-size: 13px;
  font-weight: 600;
  color: var(--accent-green);
  margin-bottom: 10px;
}

.import-preview ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.import-preview li {
  font-size: 13px;
  color: var(--text-primary);
  padding: 3px 0;
}

.import-preview li::before {
  content: '✓ ';
  color: var(--accent-green);
}

.import-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.import-error {
  font-size: 13px;
  color: var(--accent-red);
  margin-top: 10px;
  text-align: right;
}

.section {
  margin-bottom: 28px;
}

.section-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 16px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-item.full {
  grid-column: 1 / -1;
}

.form-item label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
}

select,
input[type="number"],
textarea {
  width: 100%;
  height: 40px;
  padding: 0 14px;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 10px;
  background: rgba(0, 0, 0, 0.02);
  font-size: 14px;
  font-family: inherit;
  color: var(--text-primary);
  transition: all 0.2s;
  outline: none;
}

select:focus,
input[type="number"]:focus,
textarea:focus {
  border-color: var(--accent-blue);
  background: white;
  box-shadow: 0 0 0 3px rgba(0, 113, 227, 0.1);
}

textarea {
  height: auto;
  padding: 12px 14px;
  resize: vertical;
  line-height: 1.5;
}

select {
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%2386868b' stroke-width='2'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 14px center;
  padding-right: 36px;
}

.margin-inputs {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}

.margin-field {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.margin-field span {
  font-size: 11px;
  color: var(--text-tertiary);
  text-align: center;
}

.margin-field input {
  text-align: center;
  padding: 0 8px;
}

.number-input {
  display: flex;
  align-items: center;
  gap: 10px;
}

.number-input input {
  flex: 1;
}

.hint {
  font-size: 13px;
  color: var(--text-tertiary);
  white-space: nowrap;
}

.checkbox-group {
  display: flex;
  gap: 16px;
}

.checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
  color: var(--text-primary);
}

.checkbox input[type="checkbox"] {
  width: 18px;
  height: 18px;
  border-radius: 4px;
  cursor: pointer;
  accent-color: var(--accent-blue);
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 32px;
  padding-top: 20px;
  border-top: 1px solid rgba(0, 0, 0, 0.04);
}

.btn {
  height: 40px;
  padding: 0 24px;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: var(--accent-blue);
  color: white;
}

.btn-primary:hover {
  background: var(--accent-blue-hover);
  box-shadow: 0 4px 12px rgba(0, 113, 227, 0.3);
  transform: translateY(-1px);
}

.btn-secondary {
  background: rgba(0, 0, 0, 0.04);
  color: var(--text-primary);
}

.btn-secondary:hover {
  background: rgba(0, 0, 0, 0.08);
}
</style>
