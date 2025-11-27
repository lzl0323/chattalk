/**
 * 对话历史状态管理
 */

import { reactive, computed } from 'vue'
import { 
  getConversations, 
  getConversationDetail, 
  createConversation, 
  updateConversationTitle,
  deleteConversationById 
} from '../services/api'

// 对话状态
const state = reactive({
  conversations: [],
  currentConversation: null,
  isLoading: false,
  error: null,
  searchQuery: ''
})

// Getters
export const conversations = computed(() => state.conversations)
export const currentConversation = computed(() => state.currentConversation)
export const isLoading = computed(() => state.isLoading)
export const conversationError = computed(() => state.error)
export const searchQuery = computed(() => state.searchQuery)

// Actions
export async function fetchConversations(search = null) {
  state.isLoading = true
  state.error = null
  
  try {
    const data = await getConversations(search)
    state.conversations = data
  } catch (error) {
    state.error = error.response?.data?.detail || '获取对话列表失败'
    console.error('Failed to fetch conversations:', error)
  } finally {
    state.isLoading = false
  }
}

export async function fetchConversationDetail(conversationId) {
  state.isLoading = true
  state.error = null
  
  try {
    const data = await getConversationDetail(conversationId)
    state.currentConversation = data
    return data
  } catch (error) {
    state.error = error.response?.data?.detail || '获取对话详情失败'
    console.error('Failed to fetch conversation detail:', error)
    return null
  } finally {
    state.isLoading = false
  }
}

export async function createNewConversation(title = null) {
  state.error = null
  
  try {
    const data = await createConversation(title)
    state.conversations.unshift(data)
    state.currentConversation = data
    return data
  } catch (error) {
    state.error = error.response?.data?.detail || '创建对话失败'
    console.error('Failed to create conversation:', error)
    return null
  }
}

export async function updateConversation(conversationId, title) {
  state.error = null
  
  try {
    const data = await updateConversationTitle(conversationId, title)
    
    // 更新列表中的对话
    const index = state.conversations.findIndex(c => c.id === conversationId)
    if (index !== -1) {
      state.conversations[index] = {
        ...state.conversations[index],
        title: data.title,
        updated_at: data.updated_at
      }
    }
    
    // 更新当前对话
    if (state.currentConversation && state.currentConversation.id === conversationId) {
      state.currentConversation = data
    }
    
    return data
  } catch (error) {
    state.error = error.response?.data?.detail || '更新对话失败'
    console.error('Failed to update conversation:', error)
    return null
  }
}

export async function deleteConversation(conversationId) {
  state.error = null
  
  try {
    await deleteConversationById(conversationId)
    
    // 从列表中移除
    state.conversations = state.conversations.filter(c => c.id !== conversationId)
    
    // 如果删除的是当前对话，清空当前对话
    if (state.currentConversation && state.currentConversation.id === conversationId) {
      state.currentConversation = null
    }
    
    return true
  } catch (error) {
    state.error = error.response?.data?.detail || '删除对话失败'
    console.error('Failed to delete conversation:', error)
    return false
  }
}

export function setCurrentConversation(conversation) {
  state.currentConversation = conversation
}

export function clearCurrentConversation() {
  state.currentConversation = null
}

export function setSearchQuery(query) {
  state.searchQuery = query
}

export function clearError() {
  state.error = null
}

export function reset() {
  state.conversations = []
  state.currentConversation = null
  state.isLoading = false
  state.error = null
  state.searchQuery = ''
}

// 导出 state 用于调试
export const conversationState = state
