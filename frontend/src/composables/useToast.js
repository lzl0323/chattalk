/**
 * Toast 提示 Hook
 */
import { ref } from 'vue'

const toasts = ref([])

export function useToast() {
  const showToast = (message, type = 'info', duration = 3000) => {
    const id = Date.now()
    
    toasts.value.push({
      id,
      message,
      type, // 'success', 'error', 'info', 'warning'
      duration
    })

    // 自动移除
    setTimeout(() => {
      removeToast(id)
    }, duration)
  }

  const removeToast = (id) => {
    const index = toasts.value.findIndex(t => t.id === id)
    if (index > -1) {
      toasts.value.splice(index, 1)
    }
  }

  return {
    toasts,
    showToast,
    removeToast
  }
}
