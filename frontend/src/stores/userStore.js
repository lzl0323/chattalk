/**
 * 用户状态管理
 * 使用 Reactive API 实现简单的状态管理
 */

import { reactive, computed } from 'vue'
import { login as apiLogin, register as apiRegister, logout as apiLogout, getCurrentUser } from '../services/api'

// 用户状态
const state = reactive({
  user: null,
  token: null,
  isLoading: false,
  error: null
})

// 从 localStorage 恢复状态
function restoreState() {
  const token = localStorage.getItem('token')
  const user = localStorage.getItem('user')
  
  if (token && user) {
    state.token = token
    try {
      state.user = JSON.parse(user)
    } catch (e) {
      console.error('Failed to parse user data:', e)
      localStorage.removeItem('user')
    }
  }
}

// 初始化时恢复状态
restoreState()

// Getters
export const isAuthenticated = computed(() => !!state.token && !!state.user)
export const currentUser = computed(() => state.user)
export const isLoading = computed(() => state.isLoading)
export const authError = computed(() => state.error)

// Actions
export async function login(email, password) {
  state.isLoading = true
  state.error = null
  
  try {
    const response = await apiLogin(email, password)
    
    // 保存 token 和用户信息
    state.token = response.access_token
    state.user = response.user
    
    localStorage.setItem('token', response.access_token)
    localStorage.setItem('user', JSON.stringify(response.user))
    
    return true
  } catch (error) {
    state.error = error.response?.data?.detail || '登录失败'
    return false
  } finally {
    state.isLoading = false
  }
}

export async function register(email, password) {
  state.isLoading = true
  state.error = null
  
  try {
    const response = await apiRegister(email, password)
    
    // 保存 token 和用户信息
    state.token = response.access_token
    state.user = response.user
    
    localStorage.setItem('token', response.access_token)
    localStorage.setItem('user', JSON.stringify(response.user))
    
    return true
  } catch (error) {
    state.error = error.response?.data?.detail || '注册失败'
    return false
  } finally {
    state.isLoading = false
  }
}

export async function logout() {
  try {
    await apiLogout()
  } catch (error) {
    console.error('Logout error:', error)
  } finally {
    // 清除状态
    state.user = null
    state.token = null
    state.error = null
    
    // 清除本地存储
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }
}

export async function fetchCurrentUser() {
  if (!state.token) {
    return false
  }
  
  state.isLoading = true
  
  try {
    const user = await getCurrentUser()
    state.user = user
    localStorage.setItem('user', JSON.stringify(user))
    return true
  } catch (error) {
    console.error('Failed to fetch user:', error)
    // Token 可能已过期
    await logout()
    return false
  } finally {
    state.isLoading = false
  }
}

export function clearError() {
  state.error = null
}

// 导出 state 用于调试
export const userState = state
