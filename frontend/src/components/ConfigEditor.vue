<template>
  <div class="config-editor">
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
import { ref, computed } from 'vue'

const props = defineProps({
  config: { type: Object, required: true }
})

const emit = defineEmits(['save', 'cancel'])

const form = ref(JSON.parse(JSON.stringify(props.config)))

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

const handleSave = () => emit('save', form.value)
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
