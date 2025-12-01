<template>
  <Teleport to="body">
    <Transition name="menu-fade">
      <div
        v-if="show && position"
        class="context-menu"
        :style="menuStyle"
        @click.stop
      >
        <div class="menu-header">
          <span class="menu-title">已选择 {{ selectedCount }} 条消息</span>
        </div>
        
        <div class="menu-divider"></div>
        
        <button
          class="menu-item"
          @click="handleExportMarkdown"
          :disabled="exporting"
        >
          <svg class="menu-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <span>导出为 Markdown</span>
          <kbd class="menu-shortcut">Ctrl+M</kbd>
        </button>

        <button
          class="menu-item"
          @click="handleExportPdf"
          :disabled="exporting"
        >
          <svg class="menu-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
          </svg>
          <span>导出为 PDF</span>
          <kbd class="menu-shortcut">Ctrl+P</kbd>
        </button>

        <div class="menu-divider"></div>

        <button
          class="menu-item menu-item-danger"
          @click="handleClearSelection"
        >
          <svg class="menu-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
          <span>取消选择</span>
          <kbd class="menu-shortcut">Esc</kbd>
        </button>

        <!-- 加载提示 -->
        <div v-if="exporting" class="menu-loading">
          <div class="loading-spinner"></div>
          <span>正在导出...</span>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'

interface Props {
  show: boolean
  position: { x: number; y: number } | null
  selectedCount: number
}

interface Emits {
  (e: 'exportMarkdown'): void
  (e: 'exportPdf'): void
  (e: 'clearSelection'): void
  (e: 'close'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const exporting = ref(false)

/**
 * 菜单位置样式
 */
const menuStyle = computed(() => {
  if (!props.position) return {}

  const { x, y } = props.position
  const menuWidth = 260
  const menuHeight = 240

  // 防止菜单超出视口
  const viewportWidth = window.innerWidth
  const viewportHeight = window.innerHeight

  let left = x
  let top = y

  if (x + menuWidth > viewportWidth) {
    left = viewportWidth - menuWidth - 10
  }

  if (y + menuHeight > viewportHeight) {
    top = viewportHeight - menuHeight - 10
  }

  return {
    left: `${left}px`,
    top: `${top}px`
  }
})

/**
 * 导出 Markdown
 */
const handleExportMarkdown = async () => {
  if (exporting.value) return
  exporting.value = true
  
  try {
    emit('exportMarkdown')
    // 延迟关闭，让用户看到操作反馈
    setTimeout(() => {
      exporting.value = false
      emit('close')
    }, 500)
  } catch (error) {
    console.error('Markdown 导出失败:', error)
    exporting.value = false
  }
}

/**
 * 导出 PDF
 */
const handleExportPdf = async () => {
  if (exporting.value) return
  exporting.value = true
  
  try {
    emit('exportPdf')
    // PDF 生成可能需要更长时间
    setTimeout(() => {
      exporting.value = false
      emit('close')
    }, 1000)
  } catch (error) {
    console.error('PDF 导出失败:', error)
    exporting.value = false
  }
}

/**
 * 清除选择
 */
const handleClearSelection = () => {
  emit('clearSelection')
  emit('close')
}

/**
 * 监听快捷键
 */
watch(() => props.show, (show) => {
  if (show) {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey || e.metaKey) {
        if (e.key === 'm' || e.key === 'M') {
          e.preventDefault()
          handleExportMarkdown()
        } else if (e.key === 'p' || e.key === 'P') {
          e.preventDefault()
          handleExportPdf()
        }
      }
    }

    document.addEventListener('keydown', handleKeyDown)

    return () => {
      document.removeEventListener('keydown', handleKeyDown)
    }
  }
})
</script>

<style scoped>
.context-menu {
  position: fixed;
  z-index: 9999;
  min-width: 260px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12),
              0 2px 8px rgba(0, 0, 0, 0.08);
  padding: 8px;
  border: 1px solid rgba(0, 0, 0, 0.08);
  user-select: none;
}

.dark .context-menu {
  background: #2d2d2d;
  border-color: rgba(255, 255, 255, 0.1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4),
              0 2px 8px rgba(0, 0, 0, 0.3);
}

.menu-header {
  padding: 10px 12px;
}

.menu-title {
  font-size: 12px;
  font-weight: 600;
  color: #666;
}

.dark .menu-title {
  color: #aaa;
}

.menu-divider {
  height: 1px;
  background: #e5e7eb;
  margin: 6px 0;
}

.dark .menu-divider {
  background: rgba(255, 255, 255, 0.1);
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 10px 12px;
  border: none;
  background: transparent;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  color: #1f2937;
  transition: all 0.2s;
  position: relative;
}

.dark .menu-item {
  color: #e5e7eb;
}

.menu-item:hover:not(:disabled) {
  background: #f3f4f6;
}

.dark .menu-item:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.1);
}

.menu-item:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.menu-item-danger {
  color: #ef4444;
}

.dark .menu-item-danger {
  color: #f87171;
}

.menu-item-danger:hover:not(:disabled) {
  background: #fef2f2;
}

.dark .menu-item-danger:hover:not(:disabled) {
  background: rgba(239, 68, 68, 0.1);
}

.menu-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.menu-shortcut {
  margin-left: auto;
  font-size: 11px;
  padding: 2px 6px;
  background: #f3f4f6;
  border-radius: 4px;
  color: #6b7280;
  font-family: monospace;
}

.dark .menu-shortcut {
  background: rgba(255, 255, 255, 0.1);
  color: #9ca3af;
}

.menu-loading {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.95);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  border-radius: 12px;
  backdrop-filter: blur(4px);
}

.dark .menu-loading {
  background: rgba(45, 45, 45, 0.95);
}

.loading-spinner {
  width: 24px;
  height: 24px;
  border: 3px solid #e5e7eb;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.dark .loading-spinner {
  border-color: rgba(255, 255, 255, 0.1);
  border-top-color: #60a5fa;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 菜单淡入淡出动画 */
.menu-fade-enter-active,
.menu-fade-leave-active {
  transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1);
}

.menu-fade-enter-from,
.menu-fade-leave-to {
  opacity: 0;
  transform: scale(0.95) translateY(-10px);
}

.menu-fade-enter-to,
.menu-fade-leave-from {
  opacity: 1;
  transform: scale(1) translateY(0);
}
</style>
