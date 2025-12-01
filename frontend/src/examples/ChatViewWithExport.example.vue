<template>
  <div class="chat-view-container">
    <!-- 消息列表容器 -->
    <div
      ref="messagesContainerRef"
      class="messages-container relative"
      @mousedown="handleMouseDown"
      @mousemove="handleMouseMove"
      @mouseup="handleMouseUp"
      @mouseleave="handleMouseUp"
    >
      <!-- 选择框图层 -->
      <SelectionLayer
        :is-selecting="isSelecting"
        :selection-rect="selectionRect"
      />

      <!-- 消息列表 -->
      <div class="messages-list">
        <ChatMessage
          v-for="message in messages"
          :key="message.id"
          :message="message"
          :is-selected="isMessageSelected(message.id)"
          @message-click="toggleMessageSelection"
          @message-context-menu="showContextMenu"
        />
      </div>
    </div>

    <!-- 右键菜单 -->
    <ChatContextMenu
      :show="!!contextMenuPosition"
      :position="contextMenuPosition"
      :selected-count="selectedCount"
      @export-markdown="handleExportMarkdown"
      @export-pdf="handleExportPdf"
      @clear-selection="clearSelection"
      @close="hideContextMenu"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import ChatMessage from '@/components/chat/ChatMessage.vue'
import SelectionLayer from '@/components/chat/SelectionLayer.vue'
import ChatContextMenu from '@/components/chat/ChatContextMenu.vue'
import { useSelection } from '@/composables/useSelection'
import { exportMarkdown } from '@/utils/exportMarkdown'
import { exportPdf } from '@/utils/exportPdf'
import type { Message } from '@/types/export'

// 示例消息数据
const messages = ref<Message[]>([
  {
    id: '1',
    role: 'user',
    content: '你好！请介绍一下 Vue 3。',
    timestamp: '2025-03-02 18:30:00'
  },
  {
    id: '2',
    role: 'assistant',
    content: 'Vue 3 是一个渐进式 JavaScript 框架，用于构建用户界面。它具有以下特点：\n\n1. **性能优化**：更快的虚拟 DOM\n2. **Composition API**：更灵活的代码组织\n3. **TypeScript 支持**：更好的类型推断\n4. **树摇优化**：更小的打包体积',
    timestamp: '2025-03-02 18:30:05'
  },
  {
    id: '3',
    role: 'user',
    content: '能详细说说 Composition API 吗？',
    timestamp: '2025-03-02 18:31:00'
  },
  {
    id: '4',
    role: 'assistant',
    content: 'Composition API 是 Vue 3 引入的新特性：\n\n```javascript\nimport { ref, computed } from "vue"\n\nexport function useCounter() {\n  const count = ref(0)\n  const double = computed(() => count.value * 2)\n  \n  function increment() {\n    count.value++\n  }\n  \n  return { count, double, increment }\n}\n```\n\n主要优势：\n- 更好的代码复用\n- 更清晰的逻辑组织\n- 更好的 TypeScript 支持',
    timestamp: '2025-03-02 18:31:10'
  }
])

// 消息容器引用
const messagesContainerRef = ref<HTMLElement | null>(null)

// 使用选择功能
const {
  isSelecting,
  selectionRect,
  contextMenuPosition,
  selectedCount,
  selectedIdList,
  startSelection,
  updateSelection,
  endSelection,
  toggleMessageSelection,
  showContextMenu: showCtxMenu,
  hideContextMenu,
  clearSelection,
  isMessageSelected
} = useSelection(messagesContainerRef)

/**
 * 鼠标按下 - 开始框选
 */
const handleMouseDown = (e: MouseEvent) => {
  startSelection(e)
}

/**
 * 鼠标移动 - 更新框选区域
 */
const handleMouseMove = (e: MouseEvent) => {
  updateSelection(e)
}

/**
 * 鼠标松开 - 结束框选
 */
const handleMouseUp = () => {
  endSelection()
}

/**
 * 显示右键菜单
 */
const showContextMenu = (messageId: string, e: MouseEvent) => {
  showCtxMenu(e, messageId)
}

/**
 * 获取选中的消息
 */
const getSelectedMessages = (): Message[] => {
  return messages.value.filter(msg => selectedIdList.value.includes(msg.id))
}

/**
 * 导出 Markdown
 */
const handleExportMarkdown = () => {
  const selectedMessages = getSelectedMessages()
  if (selectedMessages.length === 0) return

  exportMarkdown(selectedMessages, {
    title: '聊天记录导出',
    filename: `chat-export-${Date.now()}.md`,
    includeTimestamp: true
  })

  console.log(`已导出 ${selectedMessages.length} 条消息为 Markdown`)
}

/**
 * 导出 PDF
 */
const handleExportPdf = async () => {
  const selectedMessages = getSelectedMessages()
  if (selectedMessages.length === 0) return

  try {
    await exportPdf(selectedMessages, {
      title: '聊天记录',
      filename: `chat-export-${Date.now()}.pdf`,
      pageSize: 'A4',
      orientation: 'portrait',
      includeTimestamp: true
    })

    console.log(`已导出 ${selectedMessages.length} 条消息为 PDF`)
  } catch (error) {
    console.error('PDF 导出失败:', error)
    alert('PDF 导出失败，请查看控制台')
  }
}
</script>

<style scoped>
.chat-view-container {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f9fafb;
}

.dark .chat-view-container {
  background: #1a1a1a;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  position: relative;
}

.messages-list {
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 自定义滚动条 */
.messages-container::-webkit-scrollbar {
  width: 6px;
}

.messages-container::-webkit-scrollbar-track {
  background: transparent;
}

.messages-container::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 3px;
}

.dark .messages-container::-webkit-scrollbar-thumb {
  background: #4b5563;
}

.messages-container::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}

.dark .messages-container::-webkit-scrollbar-thumb:hover {
  background: #6b7280;
}
</style>
