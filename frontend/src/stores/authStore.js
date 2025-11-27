/**
 * 用户认证 Store
 * 管理用户登录、注册、登出等认证相关功能
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as apiLogin, register as apiRegister, getCurrentUser } from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || null)
  const isAuthenticated = ref(!!token.value)
  const isLoading = ref(false)
  const error = ref(null)

  /**
   * 用户登录
   */
  const login = async (email, password) => {
    isLoading.value = true
    error.value = null
    
    try {
      const data = await apiLogin(email, password)
      
      // 保存 Token 和用户信息
      token.value = data.access_token
      user.value = data.user
      isAuthenticated.value = true
      
      // 持久化到 localStorage
      localStorage.setItem('token', data.access_token)
      
      return data
    } catch (err) {
      console.error('Login failed:', err)
      error.value = err.response?.data?.detail || err.message || '登录失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 用户注册
   */
  const register = async (email, password) => {
    isLoading.value = true
    error.value = null
    
    try {
      const data = await apiRegister(email, password)
      
      // 注册成功后自动登录
      token.value = data.access_token
      user.value = data.user
      isAuthenticated.value = true
      
      localStorage.setItem('token', data.access_token)
      
      return data
    } catch (err) {
      error.value = err.message || '注册失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 用户登出
   */
  const logout = () => {
    user.value = null
    token.value = null
    isAuthenticated.value = false
    error.value = null
    
    // 清除持久化数据
    localStorage.removeItem('token')
  }

  /**
   * 检查认证状态（用于页面刷新后恢复登录状态）
   */
  const checkAuth = async () => {
    if (!token.value) {
      return false
    }
    
    try {
      const userData = await getCurrentUser()
      user.value = userData
      isAuthenticated.value = true
      return true
    } catch (err) {
      // Token 无效，清除登录状态
      logout()
      return false
    }
  }

  /**
   * 刷新用户信息
   */
  const refreshUser = async () => {
    if (!isAuthenticated.value) return
    
    try {
      const userData = await getCurrentUser()
      user.value = userData
    } catch (err) {
      console.error('Failed to refresh user:', err)
    }
  }

  // Getters
  const userEmail = computed(() => user.value?.email || '')
  const isAdmin = computed(() => user.value?.is_admin || false)
  const userId = computed(() => user.value?.id)

  return {
    // State
    user,
    token,
    isAuthenticated,
    isLoading,
    error,
    
    // Getters
    userEmail,
    isAdmin,
    userId,
    
    // Actions
    login,
    register,
    logout,
    checkAuth,
    refreshUser,
  }
})
