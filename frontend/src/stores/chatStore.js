/**
 * 聊天管理 Store
 * 管理对话列表、消息、流式输入等聊天相关功能
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { 
  getConversations as apiGetConversations,
  getConversation as apiGetConversation,
  deleteConversation as apiDeleteConversation,
  chatStream
} from '@/services/api'

export const useChatStore = defineStore('chat', () => {
  // 状态
  const conversations = ref([])
  const currentConversation = ref(null)
  const messages = ref([])
  const isStreaming = ref(false)
  const isLoading = ref(false)
  const searchQuery = ref('')

  /**
   * 获取所有对话列表
   */
  const fetchConversations = async () => {
    isLoading.value = true
    try {
      const data = await apiGetConversations()
      conversations.value = data.sort((a, b) => 
        new Date(b.updated_at) - new Date(a.updated_at)
      )
    } catch (error) {
      console.error('Failed to fetch conversations:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 创建新对话
   */
  const createConversation = async () => {
    // 创建临时的新对话
    const newConv = {
      id: null, // 后端会在第一条消息时创建
      title: '新对话',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      messages: []
    }
    
    // 添加到列表顶部
    conversations.value.unshift(newConv)
    currentConversation.value = newConv
    messages.value = []
    
    return newConv
  }

  /**
   * 加载指定对话
   */
  const loadConversation = async (id) => {
    // 验证 ID
    if (!id || id === 'null' || id === 'undefined') {
      return
    }
    
    try {
      const conv = await apiGetConversation(id)
      currentConversation.value = conv
      messages.value = conv.messages || []
      
      // 更新列表中的对话
      const index = conversations.value.findIndex(c => c.id === id)
      if (index !== -1) {
        conversations.value[index] = conv
      }
    } catch (error) {
      console.error('Failed to load conversation:', error)
      throw error
    }
  }

  /**
   * 更新对话标题
   */
  const updateConversationTitle = async (id, title) => {
    try {
      // TODO: 调用后端 API 更新标题
      // await apiUpdateConversationTitle(id, title)
      
      // 更新本地状态
      const conv = conversations.value.find(c => c.id === id)
      if (conv) {
        conv.title = title
        conv.updated_at = new Date().toISOString()
      }
      
      if (currentConversation.value?.id === id) {
        currentConversation.value.title = title
      }
    } catch (error) {
      console.error('Failed to update conversation title:', error)
      throw error
    }
  }

  /**
   * 删除对话
   */
  const deleteConversation = async (id) => {
    try {
      await apiDeleteConversation(id)
      
      // 从列表中移除
      conversations.value = conversations.value.filter(c => c.id !== id)
      
      // 如果删除的是当前对话，清空当前状态
      if (currentConversation.value?.id === id) {
        currentConversation.value = null
        messages.value = []
      }
    } catch (error) {
      console.error('Failed to delete conversation:', error)
      throw error
    }
  }

  /**
   * 发送消息（流式）
   */
  const streamMessage = async (content, modelId, onChunk, onSuggestions, onDone, onError) => {
    isStreaming.value = true
    
    try {
      await chatStream(
        content,
        currentConversation.value?.id,
        modelId,
        // onChunk
        (chunk) => {
          onChunk?.(chunk)
        },
        // onDone
        (conversationId) => {
          isStreaming.value = false
          
          // 如果是新对话，保存 ID
          if (!currentConversation.value?.id && conversationId) {
            currentConversation.value.id = conversationId
            
            // 更新列表中的对话
            const index = conversations.value.findIndex(c => c.id === null)
            if (index !== -1) {
              conversations.value[index].id = conversationId
            }
          }
          
          // 刷新对话列表（获取最新标题）
          fetchConversations().catch(console.error)
          
          onDone?.(conversationId)
        },
        // onError
        (error) => {
          isStreaming.value = false
          onError?.(error)
        },
        // onSuggestions
        (suggestions) => {
          onSuggestions?.(suggestions)
        }
      )
    } catch (error) {
      isStreaming.value = false
      console.error('Stream message error:', error)
      throw error
    }
  }

  /**
   * 添加消息到当前对话
   */
  const addMessage = (role, content) => {
    const message = {
      role,
      content,
      timestamp: new Date().toISOString()
    }
    
    messages.value.push(message)
    
    if (currentConversation.value) {
      currentConversation.value.updated_at = message.timestamp
    }
    
    return message
  }

  /**
   * 清空当前对话
   */
  const clearMessages = () => {
    messages.value = []
  }

  /**
   * 重置所有状态
   */
  const reset = () => {
    conversations.value = []
    currentConversation.value = null
    messages.value = []
    isStreaming.value = false
    isLoading.value = false
    searchQuery.value = ''
  }

  // Getters
  const filteredConversations = computed(() => {
    if (!searchQuery.value) {
      return conversations.value
    }
    
    const query = searchQuery.value.toLowerCase()
    return conversations.value.filter(conv => 
      conv.title?.toLowerCase().includes(query)
    )
  })

  const hasMessages = computed(() => messages.value.length > 0)

  const currentConversationId = computed(() => currentConversation.value?.id)

  return {
    // State
    conversations,
    currentConversation,
    messages,
    isStreaming,
    isLoading,
    searchQuery,
    
    // Getters
    filteredConversations,
    hasMessages,
    currentConversationId,
    
    // Actions
    fetchConversations,
    createConversation,
    loadConversation,
    updateConversationTitle,
    deleteConversation,
    streamMessage,
    addMessage,
    clearMessages,
    reset,
  }
})
