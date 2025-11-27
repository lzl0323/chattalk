/**
 * API 服务模块
 * 封装与后端的通信逻辑，包含认证拦截器
 */

import axios from 'axios'

// 创建 axios 实例
const apiClient = axios.create({
  baseURL: '/api',
  timeout: 300000, // 5 分钟超时
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器 - 自动添加 Token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器 - 处理认证错误
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Token 过期或无效，清除本地存储
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      // 重定向到登录页
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// ==================== 认证相关 API ====================

/**
 * 用户注册
 * @param {string} email - 邮箱
 * @param {string} password - 密码
 * @returns {Promise<Object>} Token 和用户信息
 */
export async function register(email, password) {
  const response = await axios.post('/api/auth/register', {
    email,
    password
  })
  return response.data
}

/**
 * 用户登录
 * @param {string} email - 邮箱
 * @param {string} password - 密码
 * @returns {Promise<Object>} Token 和用户信息
 */
export async function login(email, password) {
  const response = await axios.post('/api/auth/login', {
    email,
    password
  })
  return response.data
}

/**
 * 获取当前用户信息
 * @returns {Promise<Object>} 用户信息
 */
export async function getCurrentUser() {
  const response = await apiClient.get('/auth/me')
  return response.data
}

/**
 * 用户登出
 * @returns {Promise<Object>} 响应数据
 */
export async function logout() {
  const response = await apiClient.post('/auth/logout')
  return response.data
}

// ==================== 聊天相关 API ====================

/**
 * 流式聊天
 * @param {string} message - 用户消息
 * @param {string|null} conversationId - 对话 ID
 * @param {number|null} modelConfigId - 模型配置 ID
 * @param {Function} onChunk - 接收到数据块时的回调
 * @param {Function} onDone - 完成时的回调
 * @param {Function} onError - 错误时的回调
 * @param {Function} onSuggestions - 接收到推荐卡片时的回调
 * @returns {Function} 取消函数
 */
export function chatStream(message, conversationId, modelConfigId, onChunk, onDone, onError, onSuggestions) {
  const controller = new AbortController()
  const token = localStorage.getItem('token')
  
  // 使用 fetch 进行流式请求
  fetch('/api/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': token ? `Bearer ${token}` : ''
    },
    body: JSON.stringify({
      message,
      conversation_id: conversationId,
      model_config_id: modelConfigId,
      stream: true
    }),
    signal: controller.signal
  })
    .then(async (response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      
      let buffer = ''
      
      while (true) {
        const { done, value } = await reader.read()
        
        if (done) {
          break
        }
        
        // 解码数据块
        buffer += decoder.decode(value, { stream: true })
        
        // 处理 SSE 格式的数据
        const lines = buffer.split('\n')
        buffer = lines.pop() // 保留不完整的行
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6) // 移除 "data: " 前缀
            
            try {
              const chunk = JSON.parse(data)
              
              if (chunk.type === 'content' && chunk.content) {
                onChunk(chunk.content)
              } else if (chunk.type === 'suggestions' && chunk.suggestions) {
                // 处理推荐卡片
                if (onSuggestions) {
                  onSuggestions(chunk.suggestions)
                }
              } else if (chunk.type === 'done') {
                onDone(chunk.conversation_id)
              } else if (chunk.type === 'error') {
                onError(new Error(chunk.error || '未知错误'))
              }
            } catch (e) {
              console.error('Failed to parse chunk:', data, e)
            }
          }
        }
      }
    })
    .catch((error) => {
      // AbortError 也需要传递给 onError，让组件决定如何处理
      onError(error)
    })
  
  // 返回取消函数
  return () => controller.abort()
}

/**
 * 非流式聊天
 * @param {string} message - 用户消息
 * @param {string|null} conversationId - 对话 ID
 * @returns {Promise<Object>} 响应数据
 */
export async function chat(message, conversationId = null) {
  const response = await apiClient.post('/chat', {
    message,
    conversation_id: conversationId,
    stream: false
  })
  return response.data
}

/**
 * 获取对话历史
 * @param {string} conversationId - 对话 ID
 * @returns {Promise<Object>} 对话数据
 */
export async function getConversation(conversationId) {
  const response = await apiClient.get(`/conversations/${conversationId}`)
  return response.data
}

/**
 * 删除对话
 * @param {string} conversationId - 对话 ID
 * @returns {Promise<Object>} 响应数据
 */
export async function deleteConversation(conversationId) {
  const response = await apiClient.delete(`/conversations/${conversationId}`)
  return response.data
}

/**
 * 健康检查
 * @returns {Promise<Object>} 健康状态
 */
export async function healthCheck() {
  const response = await apiClient.get('/health')
  return response.data
}

// ==================== 对话历史相关 API ====================

/**
 * 创建新对话
 * @param {string|null} title - 对话标题
 * @returns {Promise<Object>} 新对话信息
 */
export async function createConversation(title = null) {
  const response = await apiClient.post('/conversations/', {
    title
  })
  return response.data
}

/**
 * 获取对话列表
 * @param {string|null} search - 搜索关键词
 * @param {number} limit - 返回数量
 * @param {number} offset - 偏移量
 * @returns {Promise<Array>} 对话列表
 */
export async function getConversations(search = null, limit = 50, offset = 0) {
  const params = { limit, offset }
  if (search) {
    params.search = search
  }
  const response = await apiClient.get('/conversations/', { params })
  return response.data
}

/**
 * 获取对话详情
 * @param {string} conversationId - 对话 ID
 * @returns {Promise<Object>} 对话详情
 */
export async function getConversationDetail(conversationId) {
  const response = await apiClient.get(`/conversations/${conversationId}`)
  return response.data
}

/**
 * 更新对话标题
 * @param {string} conversationId - 对话 ID
 * @param {string} title - 新标题
 * @returns {Promise<Object>} 更新后的对话信息
 */
export async function updateConversationTitle(conversationId, title) {
  const response = await apiClient.put(`/conversations/${conversationId}`, {
    title
  })
  return response.data
}

/**
 * 删除对话
 * @param {string} conversationId - 对话 ID
 * @returns {Promise<Object>} 响应数据
 */
export async function deleteConversationById(conversationId) {
  const response = await apiClient.delete(`/conversations/${conversationId}`)
  return response.data
}

/**
 * 添加消息到对话
 * @param {string} conversationId - 对话 ID
 * @param {string} role - 角色 (user/assistant)
 * @param {string} content - 消息内容
 * @returns {Promise<Object>} 新消息信息
 */
export async function addMessage(conversationId, role, content) {
  const response = await apiClient.post('/conversations/messages', {
    conversation_id: conversationId,
    role,
    content
  })
  return response.data
}

// ==================== 模型配置相关 API ====================

/**
 * 获取模型配置列表
 * @param {number} skip - 跳过数量
 * @param {number} limit - 限制数量
 * @param {boolean} activeOnly - 是否只返回激活的模型
 * @returns {Promise<Object>} 模型配置列表
 */
export async function getModelConfigs(skip = 0, limit = 100, activeOnly = false) {
  const response = await apiClient.get('/model-configs/', {
    params: { skip, limit, active_only: activeOnly }
  })
  return response.data
}

/**
 * 获取激活的模型列表（简化版，用于下拉框）
 * @returns {Promise<Array>} 激活的模型配置列表
 */
export async function getActiveModels() {
  const response = await apiClient.get('/model-configs/active/list')
  return response.data
}

/**
 * 获取单个模型配置
 * @param {number} configId - 配置 ID
 * @returns {Promise<Object>} 模型配置详情
 */
export async function getModelConfig(configId) {
  const response = await apiClient.get(`/model-configs/${configId}`)
  return response.data
}

/**
 * 创建模型配置
 * @param {Object} data - 模型配置数据
 * @returns {Promise<Object>} 创建的模型配置
 */
export async function createModelConfig(data) {
  const response = await apiClient.post('/model-configs/', data)
  return response.data
}

/**
 * 更新模型配置
 * @param {number} configId - 配置 ID
 * @param {Object} data - 更新数据
 * @returns {Promise<Object>} 更新后的模型配置
 */
export async function updateModelConfig(configId, data) {
  const response = await apiClient.put(`/model-configs/${configId}`, data)
  return response.data
}

/**
 * 删除模型配置
 * @param {number} configId - 配置 ID
 * @returns {Promise<Object>} 响应数据
 */
export async function deleteModelConfig(configId) {
  const response = await apiClient.delete(`/model-configs/${configId}`)
  return response.data
}

/**
 * 重置模型配额
 * @param {number} configId - 配置 ID
 * @param {number} quotaUsed - 重置后的使用量（默认 0）
 * @returns {Promise<Object>} 更新后的模型配置
 */
export async function resetModelQuota(configId, quotaUsed = 0) {
  const response = await apiClient.post(`/model-configs/${configId}/reset-quota`, {
    quota_used: quotaUsed
  })
  return response.data
}

// ==================== 推荐问题 API ====================

/**
 * 获取智能推荐问题
 * @param {number} count - 推荐数量（默认 6）
 * @returns {Promise<Array>} 推荐问题列表
 */
export async function getSuggestions(count = 6) {
  try {
    const response = await apiClient.get('/suggestions/', {
      params: { count }
    })
    return response.data.suggestions
  } catch (error) {
    console.error('Failed to get suggestions:', error)
    // 返回后备推荐
    return getFallbackSuggestions(count)
  }
}

/**
 * 获取后备推荐问题（不需要认证）
 * @param {number} count - 推荐数量（默认 6）
 * @returns {Promise<Array>} 后备推荐问题列表
 */
export async function getFallbackSuggestions(count = 6) {
  try {
    const response = await apiClient.get('/suggestions/fallback', {
      params: { count }
    })
    return response.data.suggestions
  } catch (error) {
    console.error('Failed to get fallback suggestions:', error)
    // 返回默认硬编码推荐
    return [
      { type: 'trending', title: 'GPT-4 和 Claude 3 对比', icon: 'bolt' },
      { type: 'trending', title: 'Next.js 14 新特性', icon: 'bolt' },
      { type: 'research', title: 'RAG 技术原理详解', icon: 'science' },
      { type: 'general', title: '前端性能优化技巧', icon: 'lightbulb' },
      { type: 'general', title: 'Python 异步编程指南', icon: 'code' },
      { type: 'general', title: 'Docker 容器化实践', icon: 'server' }
    ].slice(0, count)
  }
}

// ==================== OCR 相关 API ====================

/**
 * OCR API 封装
 */
export const ocrAPI = {
  /**
   * 上传文件进行 OCR 识别
   * @param {File} file - 文件对象
   * @param {string} ocrMode - OCR 模式
   * @param {number} conversationId - 对话 ID
   * @param {number} modelId - 模型 ID（可选）
   */
  async uploadFile(file, ocrMode = 'markdown', conversationId = null, modelId = null) {
    // 如果没有提供 conversationId，从 chatStore 获取
    if (!conversationId) {
      const { useChatStore } = await import('@/stores/chatStore')
      const chatStore = useChatStore()
      conversationId = chatStore.currentConversation?.id
      
      if (!conversationId) {
        // 自动创建新对话
        const newConv = await chatStore.createConversation()
        conversationId = newConv.id
        
        if (!conversationId) {
          throw new Error('Failed to create conversation')
        }
      }
    }

    const formData = new FormData()
    formData.append('file', file)
    formData.append('conversation_id', conversationId)
    formData.append('ocr_mode', ocrMode)
    
    if (modelId) {
      formData.append('model_id', modelId)
    }

    const response = await apiClient.post('/ocr/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    return response.data
  },

  /**
   * 获取可用的 OCR 模型列表
   */
  async getModels() {
    const response = await apiClient.get('/ocr/models')
    return response.data
  },

  /**
   * 获取支持的 OCR 模式列表
   */
  async getModes() {
    const response = await apiClient.get('/ocr/modes')
    return response.data
  }
}
