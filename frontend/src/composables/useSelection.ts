/**
 * 消息选择功能 Composable
 * 模仿微信 PC 端的消息框选和多选逻辑
 */

import { ref, computed, onMounted, onUnmounted } from 'vue'
import type { Message, SelectionRect } from '@/types/export'

export function useSelection(containerRef: any) {
  // 选中的消息 ID 集合
  const selectedIds = ref<Set<string>>(new Set())
  
  // 是否正在框选
  const isSelecting = ref(false)
  
  // 选择矩形坐标
  const selectionRect = ref<SelectionRect | null>(null)
  
  // 右键菜单位置
  const contextMenuPosition = ref<{ x: number; y: number } | null>(null)

  // 框选起始点
  let startX = 0
  let startY = 0

  /**
   * 开始框选
   */
  const startSelection = (e: MouseEvent) => {
    // 只响应左键
    if (e.button !== 0) return
    
    // 如果点击的是消息元素或其内部，不启动框选（让消息自己的点击事件处理）
    const target = e.target as HTMLElement
    if (target.closest('[data-message-id]')) return

    isSelecting.value = true
    const container = containerRef.value
    const rect = container.getBoundingClientRect()
    
    startX = e.clientX - rect.left + container.scrollLeft
    startY = e.clientY - rect.top + container.scrollTop
    
    selectionRect.value = {
      startX,
      startY,
      endX: startX,
      endY: startY
    }

    // 如果不是 Ctrl/Cmd 或 Shift，清空之前的选择
    if (!e.ctrlKey && !e.metaKey && !e.shiftKey) {
      selectedIds.value.clear()
    }
  }

  /**
   * 更新框选区域
   */
  const updateSelection = (e: MouseEvent) => {
    if (!isSelecting.value || !selectionRect.value) return

    const container = containerRef.value
    const rect = container.getBoundingClientRect()
    
    selectionRect.value.endX = e.clientX - rect.left + container.scrollLeft
    selectionRect.value.endY = e.clientY - rect.top + container.scrollTop

    // 实时计算框选范围内的消息
    updateSelectedMessages()
  }

  /**
   * 结束框选
   */
  const endSelection = () => {
    if (!isSelecting.value) return
    
    isSelecting.value = false
    // 保留选中状态，但清除选择框
    setTimeout(() => {
      selectionRect.value = null
    }, 100)
  }

  /**
   * 更新选中的消息（框选模式）
   */
  const updateSelectedMessages = () => {
    if (!selectionRect.value || !containerRef.value) return

    const rect = selectionRect.value
    const minX = Math.min(rect.startX, rect.endX)
    const maxX = Math.max(rect.startX, rect.endX)
    const minY = Math.min(rect.startY, rect.endY)
    const maxY = Math.max(rect.startY, rect.endY)

    // 查找所有消息元素
    const messageElements = containerRef.value.querySelectorAll('[data-message-id]')
    
    messageElements.forEach((el: HTMLElement) => {
      const messageRect = el.getBoundingClientRect()
      const containerRect = containerRef.value.getBoundingClientRect()
      
      const scrollLeft = containerRef.value.scrollLeft
      const scrollTop = containerRef.value.scrollTop
      
      const elemTop = messageRect.top - containerRect.top + scrollTop
      const elemBottom = messageRect.bottom - containerRect.top + scrollTop
      const elemLeft = messageRect.left - containerRect.left + scrollLeft
      const elemRight = messageRect.right - containerRect.left + scrollLeft

      // 判断是否相交
      const isIntersecting = !(
        elemRight < minX ||
        elemLeft > maxX ||
        elemBottom < minY ||
        elemTop > maxY
      )

      const messageId = el.getAttribute('data-message-id')
      if (messageId && isIntersecting) {
        selectedIds.value.add(messageId)
      }
    })
  }

  /**
   * 点击选择消息（支持 Ctrl/Shift）
   */
  const toggleMessageSelection = (messageId: string, e: MouseEvent) => {
    if (e.ctrlKey || e.metaKey) {
      // Ctrl/Cmd + 点击：切换单个选中状态
      if (selectedIds.value.has(messageId)) {
        selectedIds.value.delete(messageId)
      } else {
        selectedIds.value.add(messageId)
      }
    } else if (e.shiftKey && selectedIds.value.size > 0) {
      // Shift + 点击：范围选择
      // TODO: 实现范围选择逻辑
      selectedIds.value.add(messageId)
    } else {
      // 普通点击：单选
      selectedIds.value.clear()
      selectedIds.value.add(messageId)
    }
  }

  /**
   * 显示右键菜单
   */
  const showContextMenu = (e: MouseEvent, messageId?: string) => {
    e.preventDefault()
    
    // 如果右键的消息未被选中，则选中它
    if (messageId && !selectedIds.value.has(messageId)) {
      selectedIds.value.clear()
      selectedIds.value.add(messageId)
    }

    // 如果没有选中任何消息，不显示菜单
    if (selectedIds.value.size === 0) return

    contextMenuPosition.value = {
      x: e.clientX,
      y: e.clientY
    }
  }

  /**
   * 隐藏右键菜单
   */
  const hideContextMenu = () => {
    contextMenuPosition.value = null
  }

  /**
   * 清空选择
   */
  const clearSelection = () => {
    selectedIds.value.clear()
    selectionRect.value = null
    isSelecting.value = false
    hideContextMenu()
  }

  /**
   * 判断消息是否被选中
   */
  const isMessageSelected = (messageId: string) => {
    return selectedIds.value.has(messageId)
  }

  /**
   * 获取选中的消息数量
   */
  const selectedCount = computed(() => selectedIds.value.size)

  /**
   * 获取选中的消息 ID 列表
   */
  const selectedIdList = computed(() => Array.from(selectedIds.value))

  // 监听全局点击，关闭右键菜单
  const handleGlobalClick = (e: MouseEvent) => {
    const target = e.target as HTMLElement
    if (!target.closest('.context-menu')) {
      hideContextMenu()
    }
  }

  // 监听 Escape 键，清空选择
  const handleEscape = (e: KeyboardEvent) => {
    if (e.key === 'Escape') {
      clearSelection()
    }
  }

  // 挂载时添加事件监听
  onMounted(() => {
    document.addEventListener('click', handleGlobalClick)
    document.addEventListener('keydown', handleEscape)
  })

  // 卸载时移除事件监听
  onUnmounted(() => {
    document.removeEventListener('click', handleGlobalClick)
    document.removeEventListener('keydown', handleEscape)
  })

  return {
    // 状态
    selectedIds,
    selectedIdList,
    selectedCount,
    isSelecting,
    selectionRect,
    contextMenuPosition,

    // 方法
    startSelection,
    updateSelection,
    endSelection,
    toggleMessageSelection,
    showContextMenu,
    hideContextMenu,
    clearSelection,
    isMessageSelected
  }
}
