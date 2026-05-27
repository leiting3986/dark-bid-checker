<template>
  <div class="config-editor">
    <el-form :model="form" label-width="120px" label-position="left">
      <!-- 页面设置 -->
      <el-divider content-position="left">页面设置</el-divider>

      <el-form-item label="纸张大小">
        <el-select v-model="form.requirements.page.size" style="width: 100%">
          <el-option label="A4" value="A4" />
          <el-option label="A3" value="A3" />
          <el-option label="B5" value="B5" />
        </el-select>
      </el-form-item>

      <el-form-item label="页边距 (cm)">
        <el-row :gutter="12">
          <el-col :span="6">
            <el-input v-model.number="form.requirements.page.margins.top_cm" placeholder="上">
              <template #prepend>上</template>
            </el-input>
          </el-col>
          <el-col :span="6">
            <el-input v-model.number="form.requirements.page.margins.bottom_cm" placeholder="下">
              <template #prepend>下</template>
            </el-input>
          </el-col>
          <el-col :span="6">
            <el-input v-model.number="form.requirements.page.margins.left_cm" placeholder="左">
              <template #prepend>左</template>
            </el-input>
          </el-col>
          <el-col :span="6">
            <el-input v-model.number="form.requirements.page.margins.right_cm" placeholder="右">
              <template #prepend>右</template>
            </el-input>
          </el-col>
        </el-row>
      </el-form-item>

      <el-form-item label="页眉页脚">
        <el-checkbox v-model="form.requirements.page.noHeader">禁止页眉</el-checkbox>
        <el-checkbox v-model="form.requirements.page.noFooter">禁止页脚</el-checkbox>
        <el-checkbox v-model="form.requirements.page.noPageNumber">禁止页码</el-checkbox>
      </el-form-item>

      <!-- 正文格式 -->
      <el-divider content-position="left">正文格式</el-divider>

      <el-form-item label="字体">
        <el-select v-model="form.requirements.text.font" style="width: 100%">
          <el-option label="宋体" value="宋体" />
          <el-option label="仿宋" value="仿宋" />
          <el-option label="黑体" value="黑体" />
          <el-option label="楷体" value="楷体" />
          <el-option label="微软雅黑" value="微软雅黑" />
        </el-select>
      </el-form-item>

      <el-form-item label="字号 (磅)">
        <el-input-number v-model="form.requirements.text.fontSize_pt" :min="8" :max="36" :step="0.5" />
        <span class="hint">{{ fontSizeName }}</span>
      </el-form-item>

      <el-form-item label="字体颜色">
        <el-color-picker v-model="fontColorHex" />
        <span class="hint">#{{ form.requirements.text.fontColor }}</span>
      </el-form-item>

      <el-form-item label="行距 (磅)">
        <el-input-number v-model="form.requirements.text.lineSpacing.value_pt" :min="12" :max="60" :step="1" />
        <span class="hint">固定值</span>
      </el-form-item>

      <el-form-item label="段间距 (磅)">
        <el-input-number v-model="form.requirements.text.paragraphSpacing_pt" :min="0" :max="36" :step="1" />
      </el-form-item>

      <!-- 表格格式 -->
      <el-divider content-position="left">表格格式</el-divider>

      <el-form-item label="表格字体">
        <el-select v-model="form.requirements.table.font" style="width: 100%">
          <el-option label="仿宋" value="仿宋" />
          <el-option label="宋体" value="宋体" />
          <el-option label="黑体" value="黑体" />
          <el-option label="楷体" value="楷体" />
        </el-select>
      </el-form-item>

      <el-form-item label="表格字号 (磅)">
        <el-input-number v-model="form.requirements.table.fontSize_pt" :min="8" :max="24" :step="0.5" />
        <span class="hint">{{ tableFontSizeName }}</span>
      </el-form-item>

      <!-- 禁止内容 -->
      <el-divider content-position="left">禁止内容</el-divider>

      <el-form-item label="投标人名称">
        <el-input
          v-model="forbiddenText"
          type="textarea"
          :rows="4"
          placeholder="每行一个投标人名称，检查时将禁止出现这些内容"
        />
      </el-form-item>
    </el-form>

    <div class="dialog-footer">
      <el-button @click="$emit('cancel')">取消</el-button>
      <el-button type="primary" @click="handleSave">保存配置</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  config: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['save', 'cancel'])

const form = ref(JSON.parse(JSON.stringify(props.config)))

// 字号名称映射
const fontSizeMap = {
  42: '初号',
  36: '小初',
  26: '一号',
  24: '小一',
  22: '二号',
  18: '小二',
  16: '三号',
  15: '小三',
  14: '四号',
  12: '小四',
  10.5: '五号',
  9: '小五',
  7.5: '六号',
  6.5: '小六',
  5.5: '七号',
  5: '八号',
}

const fontSizeName = computed(() => {
  const pt = form.value.requirements.text.fontSize_pt
  return fontSizeMap[pt] || ''
})

const tableFontSizeName = computed(() => {
  const pt = form.value.requirements.table.fontSize_pt
  return fontSizeMap[pt] || ''
})

// 颜色处理
const fontColorHex = computed({
  get: () => '#' + form.value.requirements.text.fontColor,
  set: (val) => {
    form.value.requirements.text.fontColor = val.replace('#', '')
  },
})

// 禁止内容处理
const forbiddenText = computed({
  get: () => {
    const names = form.value.requirements.forbiddenContent.bidderNames || []
    const companies = form.value.requirements.forbiddenContent.companyNames || []
    return [...new Set([...names, ...companies])].join('\n')
  },
  set: (val) => {
    const lines = val.split('\n').filter((l) => l.trim())
    form.value.requirements.forbiddenContent.bidderNames = lines
    form.value.requirements.forbiddenContent.companyNames = lines
  },
})

const handleSave = () => {
  emit('save', form.value)
}
</script>

<style scoped>
.config-editor {
  max-height: 600px;
  overflow-y: auto;
  padding-right: 16px;
}

.hint {
  margin-left: 12px;
  color: #909399;
  font-size: 14px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}

:deep(.el-divider__text) {
  font-weight: 600;
  color: #303133;
}
</style>
