import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 120000,
})

// 获取配置列表
export const listConfigs = () => api.get('/configs')

// 获取配置
export const getConfig = (name) => api.get(`/config/${name}`)

// 更新配置
export const updateConfig = (name, config) => api.put(`/config/${name}`, config)

// 恢复默认配置
export const resetConfig = (name) => api.post(`/config/${name}/reset`)

// 检查文档
export const checkDocument = (file, configName) => {
  const formData = new FormData()
  formData.append('file', file)
  const params = configName ? { config_name: configName } : {}
  return api.post('/check', formData, {
    params,
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

// 修复文档
export const fixDocument = (fileId, configName) => {
  const params = configName ? { config_name: configName } : {}
  return api.post(`/fix/${fileId}`, null, { params })
}

// 下载修复后的文件
export const downloadFixed = (fileId) => {
  return api.get(`/download/${fileId}`, { responseType: 'blob' })
}

// 清理文件
export const cleanupFiles = (fileId) => api.delete(`/cleanup/${fileId}`)

// 从文本导入配置
export const importConfig = (text) => api.post('/config/import', { text })

export default api
