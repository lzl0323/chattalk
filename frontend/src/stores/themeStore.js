/**
 * 主题管理 Store
 * 支持 Light/Dark 模式切换
 */
import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  // 状态
  const theme = ref('light') // 'light' | 'dark'
  const isTransitioning = ref(false)

  /**
   * 初始化主题
   * 优先级：localStorage > 系统偏好 > 默认 light
   */
  const initTheme = () => {
    const savedTheme = localStorage.getItem('theme')
    
    if (savedTheme) {
      theme.value = savedTheme
    } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      theme.value = 'dark'
    }
    
    applyTheme(theme.value)
  }

  /**
   * 应用主题到 DOM
   */
  const applyTheme = (newTheme) => {
    const root = document.documentElement
    
    if (newTheme === 'dark') {
      root.classList.add('dark')
    } else {
      root.classList.remove('dark')
    }
  }

  /**
   * 切换主题
   */
  const toggleTheme = () => {
    isTransitioning.value = true
    theme.value = theme.value === 'light' ? 'dark' : 'light'
    
    // 过渡动画结束后重置标志
    setTimeout(() => {
      isTransitioning.value = false
    }, 300)
  }

  /**
   * 设置指定主题
   */
  const setTheme = (newTheme) => {
    if (newTheme !== 'light' && newTheme !== 'dark') {
      console.warn('Invalid theme:', newTheme)
      return
    }
    
    theme.value = newTheme
  }

  // 监听主题变化，自动应用并保存
  watch(theme, (newTheme) => {
    applyTheme(newTheme)
    localStorage.setItem('theme', newTheme)
  })

  // 监听系统主题变化
  if (window.matchMedia) {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      // 仅在用户未手动设置时跟随系统
      if (!localStorage.getItem('theme')) {
        theme.value = e.matches ? 'dark' : 'light'
      }
    })
  }

  return {
    // State
    theme,
    isTransitioning,
    
    // Getters
    isDark: () => theme.value === 'dark',
    isLight: () => theme.value === 'light',
    
    // Actions
    initTheme,
    toggleTheme,
    setTheme,
  }
})
