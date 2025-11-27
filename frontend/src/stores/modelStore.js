/**
 * 模型管理 Store
 * 管理 AI 模型列表、选择、配额等功能
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getActiveModels } from '@/services/api'

export const useModelStore = defineStore('model', () => {
  // 状态
  const models = ref([])
  const selectedModelId = ref(null)
  const isLoading = ref(false)
  const error = ref(null)
  const lastFetchTime = ref(null)

  /**
   * 获取模型列表
   */
  const fetchModels = async (forceRefresh = false) => {
    // 缓存 30 秒，避免频繁请求
    const now = Date.now()
    if (!forceRefresh && lastFetchTime.value && (now - lastFetchTime.value < 30000)) {
      return models.value
    }

    isLoading.value = true
    error.value = null
    
    try {
      const data = await getActiveModels()
      // 只保留聊天模型，过滤掉 OCR 模型
      models.value = (data || []).filter(m => m.model_type !== 'ocr')
      lastFetchTime.value = now
      
      // 如果还没选择模型，自动选择第一个可用的
      if (!selectedModelId.value && models.value.length > 0) {
        const availableModel = models.value.find(m => 
          m.is_active && m.quota_remaining > 0
        )
        selectedModelId.value = availableModel?.id || models.value[0]?.id
      }
      
      // 检查当前选中的模型是否还可用
      if (selectedModelId.value) {
        const currentModel = models.value.find(m => m.id === selectedModelId.value)
        if (!currentModel || !currentModel.is_active || currentModel.quota_remaining <= 0) {
          // 切换到可用模型
          const fallbackModel = models.value.find(m => 
            m.is_active && m.quota_remaining > 0
          )
          if (fallbackModel) {
            selectedModelId.value = fallbackModel.id
          }
        }
      }
      
      return models.value
    } catch (err) {
      error.value = err.message || '获取模型列表失败'
      console.error('Failed to fetch models:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 选择模型
   */
  const selectModel = (id) => {
    const model = models.value.find(m => m.id === id)
    
    if (!model) {
      console.warn('Model not found:', id)
      return false
    }
    
    // 检查模型是否可用
    if (!model.is_active) {
      error.value = '该模型已被禁用'
      return false
    }
    
    if (model.quota_remaining <= 0) {
      error.value = '该模型配额已用完'
      return false
    }
    
    selectedModelId.value = id
    error.value = null
    
    // 保存到 localStorage
    localStorage.setItem('selectedModelId', id.toString())
    
    return true
  }

  /**
   * 检查模型配额
   */
  const checkQuota = (modelId) => {
    const model = models.value.find(m => m.id === modelId)
    
    if (!model) {
      return { available: false, reason: '模型不存在' }
    }
    
    if (!model.is_active) {
      return { available: false, reason: '模型已禁用' }
    }
    
    if (model.quota_remaining <= 0) {
      return { available: false, reason: '配额已用完' }
    }
    
    return { available: true, remaining: model.quota_remaining }
  }

  /**
   * 刷新模型配额信息
   */
  const refreshQuotas = async () => {
    await fetchModels(true)
  }

  /**
   * 从 localStorage 恢复选择
   */
  const restoreSelection = () => {
    const savedId = localStorage.getItem('selectedModelId')
    if (savedId) {
      const model = models.value.find(m => m.id === parseInt(savedId))
      if (model && model.is_active && model.quota_remaining > 0) {
        selectedModelId.value = parseInt(savedId)
      }
    }
  }

  /**
   * 重置状态
   */
  const reset = () => {
    models.value = []
    selectedModelId.value = null
    isLoading.value = false
    error.value = null
    lastFetchTime.value = null
  }

  // Getters
  const currentModel = computed(() => {
    if (!selectedModelId.value) return null
    return models.value.find(m => m.id === selectedModelId.value)
  })

  const availableModels = computed(() => {
    return models.value.filter(m => 
      m.is_active && m.quota_remaining > 0
    )
  })

  const unavailableModels = computed(() => {
    return models.value.filter(m => 
      !m.is_active || m.quota_remaining <= 0
    )
  })

  const hasAvailableModels = computed(() => {
    return availableModels.value.length > 0
  })

  const currentQuota = computed(() => {
    if (!currentModel.value) return null
    return {
      used: currentModel.value.quota_used || 0,
      limit: currentModel.value.quota_limit || 0,
      remaining: currentModel.value.quota_remaining || 0,
      percentage: currentModel.value.quota_limit > 0
        ? Math.round((currentModel.value.quota_used / currentModel.value.quota_limit) * 100)
        : 0
    }
  })

  const isCurrentModelAvailable = computed(() => {
    if (!currentModel.value) return false
    return currentModel.value.is_active && currentModel.value.quota_remaining > 0
  })

  return {
    // State
    models,
    selectedModelId,
    isLoading,
    error,
    
    // Getters
    currentModel,
    availableModels,
    unavailableModels,
    hasAvailableModels,
    currentQuota,
    isCurrentModelAvailable,
    
    // Actions
    fetchModels,
    selectModel,
    checkQuota,
    refreshQuotas,
    restoreSelection,
    reset,
  }
})
