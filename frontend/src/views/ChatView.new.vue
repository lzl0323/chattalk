<template>
  <div class="h-full flex flex-col bg-white dark:bg-gpt-dark-700">
    <!-- 顶部栏 -->
    <div class="flex-shrink-0 flex items-center pl-14 pr-4 py-3 border-b border-gray-200 dark:border-gpt-dark-400 gap-3">
      <!-- 对话标题（可编辑） -->
      <div class="flex items-center gap-3 flex-1 min-w-0">
        <input
          v-if="isEditingTitle"
          v-model="editedTitle"
          @blur="saveTitle"
          @keyup.enter="saveTitle"
          @keyup.esc="cancelEditTitle"
          ref="titleInput"
          class="flex-1 px-3 py-1 text-lg font-semibold rounded
                 bg-white dark:bg-gpt-dark-600
                 border border-gray-300 dark:border-gpt-dark-500
                 text-gray-900 dark:text-gray-100
                 focus:outline-none focus:ring-2 focus:ring-gpt-green-500"
        >
        <div v-else class="flex items-center gap-2 flex-1 min-w-0">
          <h1 class="text-lg font-semibold text-gray-900 dark:text-gray-100 truncate">
            {{ conversationTitle }}
          </h1>
          <button
            @click="startEditTitle"
            class="p-1.5 rounded hover:bg-gray-100 dark:hover:bg-gpt-dark-600 transition-colors"
            title="编辑标题"
          >
            <svg class="w-4 h-4 text-gray-500 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </button>
        </div>
      </div>
      
      <!-- 模型选择器 -->
      <div class="flex-shrink-0">
        <select
          v-model="selectedModelId"
          @change="handleModelChange"
          class="px-3 py-2 rounded-lg text-sm font-medium
                 bg-gpt-gray-100 dark:bg-gpt-dark-600
                 border border-gray-200 dark:border-gpt-dark-500
                 text-gray-900 dark:text-gray-100
                 hover:bg-gpt-gray-200 dark:hover:bg-gpt-dark-500
                 focus:outline-none focus:ring-2 focus:ring-gpt-green-500
                 cursor-pointer transition-all duration-200"
        >
          <option
            v-for="model in models"
            :key="model.id"
            :value="model.id"
            :disabled="!model.is_active || model.quota_remaining <= 0"
            :class="{
              'text-red-500': !model.is_active || model.quota_remaining <= 0
            }"
          >
            {{ model.name }} - {{ model.quota_remaining > 0 ? `剩余 ${formatQuota(model.quota_remaining)}` : '已用尽' }}
          </option>
        </select>
      </div>
    </div>
    
    <!-- 配额警告横幅 -->
    <Transition name="slide-down">
      <div
        v-if="showQuotaWarning"
        class="warning-banner"
      >
        <svg class="w-5 h-5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
        </svg>
        <p class="flex-1">当前模型流量已用完，请切换其他模型继续对话</p>
        <button
          @click="showQuotaWarning = false"
          class="p-1 hover:bg-yellow-100 dark:hover:bg-yellow-800 rounded"
        >
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
        </button>
      </div>
    </Transition>
    
    <!-- 消息区域 -->
    <div
      ref="messagesContainer"
      class="flex-1 overflow-y-auto px-4 py-6 relative"
      @scroll="handleScroll"
      @mousedown="startSelection"
      @mousemove="updateSelection"
      @mouseup="endSelection"
      @mouseleave="endSelection"
    >
      <!-- 选择框图层 -->
      <SelectionLayer
        :is-selecting="isSelecting"
        :selection-rect="selectionRect"
      />
      <!-- 空状态：欢迎界面 -->
      <div v-if="messages.length === 0" class="flex-1 flex flex-col items-center justify-center px-4 pb-32">
        <div class="text-center max-w-3xl w-full">
          <!-- 大标题 -->
          <h1 class="text-4xl md:text-5xl font-medium text-gray-800 dark:text-gray-100 mb-12">
            你在忙什么？
          </h1>
          
          <!-- 推荐问题卡片 -->
          <div v-if="!loadingSuggestions && initialSuggestions.length > 0" class="mt-8">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-4xl mx-auto">
              <button
                v-for="(suggestion, index) in initialSuggestions"
                :key="index"
                @click="handleSuggestionClick(suggestion.title)"
                class="group relative p-5 rounded-2xl border border-gray-200 dark:border-gpt-dark-500
                       bg-white dark:bg-gpt-dark-800/50 hover:bg-gray-50 dark:hover:bg-gpt-dark-700/50
                       hover:shadow-md dark:hover:shadow-xl
                       transition-all duration-300 text-left"
              >
                <div class="flex items-start gap-3">
                  <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500 dark:from-purple-600 dark:to-pink-600
                              flex items-center justify-center flex-shrink-0 shadow-sm">
                    <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                  <span class="text-sm font-medium text-gray-700 dark:text-gray-200 leading-relaxed">
                    {{ suggestion.title }}
                  </span>
                </div>
              </button>
            </div>
          </div>
          
          <!-- 加载状态 -->
          <div v-if="loadingSuggestions" class="mt-8 flex justify-center">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500"></div>
          </div>
        </div>
      </div>
      
      <!-- 消息列表 -->
      <div v-else class="max-w-3xl mx-auto space-y-6">
        <ChatMessage
          v-for="(message, index) in messages"
          :key="message.id"
          :message="message"
          :is-streaming="message.isStreaming"
          :is-selected="isMessageSelected(message.id)"
          @regenerate="regenerateMessage(index)"
          @copy="copyMessage(message.content)"
          @delete="deleteMessage(index)"
          @message-click="toggleMessageSelection"
          @message-context-menu="handleShowContextMenu"
        />
        
        <!-- 推荐问题卡片 -->
        <div
          v-for="(suggestion, sIdx) in suggestionsList"
          :key="`suggestion-${sIdx}`"
          class="my-6"
        >
          <div class="flex items-center gap-2 mb-3">
            <svg class="w-4 h-4 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            <span class="text-sm font-medium text-gray-700 dark:text-gray-300">你可能感兴趣的问题</span>
          </div>
          <div class="grid grid-cols-1 gap-3">
            <button
              v-for="(item, iIdx) in suggestion.suggestions"
              :key="iIdx"
              @click="handleSuggestionClick(item.title)"
              class="group flex items-center gap-3 p-3 rounded-lg border border-gray-200 dark:border-gpt-dark-400
                     bg-white dark:bg-gpt-dark-600 hover:bg-purple-50 dark:hover:bg-gpt-dark-500
                     hover:border-purple-200 dark:hover:border-purple-500
                     transition-all duration-200 text-left"
            >
              <div class="w-8 h-8 rounded-lg bg-purple-50 dark:bg-purple-900/30 group-hover:bg-purple-100 dark:group-hover:bg-purple-900/50
                          flex items-center justify-center flex-shrink-0 transition-colors">
                <svg class="w-4 h-4 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <span class="text-sm text-gray-700 dark:text-gray-300 group-hover:text-gray-900 dark:group-hover:text-gray-100">
                {{ item.title }}
              </span>
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 输入区域 -->
    <div class="flex-shrink-0 bg-gradient-to-t from-white to-white/80 dark:from-gpt-dark-700 dark:to-gpt-dark-700/80 backdrop-blur-sm p-6">
      <div class="max-w-4xl mx-auto">
        <!-- 搜索模式选择器 -->
        <div class="mb-3">
          <SearchModeSelector 
            v-model="searchMode"
            :hasKnowledgeBase="hasKnowledgeBase"
          />
        </div>
        
        <!-- 输入框容器 -->
        <div class="relative bg-white dark:bg-gpt-dark-800 rounded-2xl shadow-md dark:shadow-xl border border-gray-200 dark:border-gpt-dark-600">
          <div class="flex items-center gap-1.5 p-2">
            <!-- 文件上传组件 -->
            <FileUpload 
              @upload-success="handleFileUpload"
              @upload-error="handleFileUploadError"
            />
            
            <!-- 输入框 -->
            <div class="flex-1 relative">
              <textarea
                v-model="inputMessage"
                @keydown.enter.exact.prevent="sendMessage"
                @keydown.enter.shift.exact="handleShiftEnter"
                ref="inputTextarea"
                rows="1"
                placeholder="发送消息..."
                :disabled="isLoading"
                class="w-full px-3 py-2 pr-14 rounded-xl resize-none
                       bg-transparent
                       text-gray-900 dark:text-gray-100 text-base
                       placeholder-gray-400 dark:placeholder-gray-500
                       focus:outline-none
                       disabled:opacity-50
                       transition-all
                       custom-scrollbar"
                style="max-height: 200px; min-height: 24px;"
              ></textarea>
              
              <!-- 语音输入按钮 -->
              <div class="absolute top-1/2 right-3 -translate-y-1/2">
                <VoiceInput @transcript="handleVoiceTranscript" />
              </div>
            </div>
            
            <!-- 发送/停止按钮 -->
            <button
              @click="isLoading ? stopGeneration() : sendMessage()"
              :disabled="!canSend && !isLoading"
              class="p-2 rounded-full transition-all duration-200"
              :class="isLoading
                ? 'bg-gray-800 hover:bg-gray-900 dark:bg-gray-700 dark:hover:bg-gray-600 text-white'
                : canSend 
                  ? 'bg-black hover:bg-gray-800 dark:bg-white dark:hover:bg-gray-100 text-white dark:text-black shadow-sm' 
                  : 'bg-gray-100 dark:bg-gpt-dark-700 text-gray-300 dark:text-gray-600 cursor-not-allowed'"
              :title="isLoading ? '停止生成' : '发送消息'"
            >
              <!-- 停止图标 -->
              <svg v-if="isLoading" class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                <path d="M6 6h12v12H6z" />
              </svg>
              <!-- 发送图标 -->
              <svg v-else class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
              </svg>
            </button>
          </div>
          
          <!-- 字符计数（内嵌） -->
          <div v-if="inputMessage.length > 0" class="px-3 pb-1.5">
            <div class="text-xs text-gray-400 dark:text-gray-500 text-right">
              {{ inputMessage.length }} / 4000
            </div>
          </div>
        </div>
        
        <!-- 提示文本 -->
        <p class="text-xs text-gray-400 dark:text-gray-500 mt-3 text-center">
          ChatTalk 可能会犯错。请核查重要信息。
        </p>
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

<script setup>
import { ref, computed, nextTick, watch, inject, onMounted } from 'vue'
import { useChatStore } from '@/stores/chatStore'
import { useModelStore } from '@/stores/modelStore'
import { getSuggestions, chatStream } from '@/services/api'
import ChatMessage from '@/components/chat/ChatMessage.vue'
import FileUpload from '@/components/chat/FileUpload.vue'
import SearchModeSelector from '@/components/chat/SearchModeSelector.vue'
import VoiceInput from '@/components/chat/VoiceInput.vue'
import SelectionLayer from '@/components/chat/SelectionLayer.vue'
import ChatContextMenu from '@/components/chat/ChatContextMenu.vue'
import { useSelection } from '@/composables/useSelection'
import { exportMarkdown } from '@/utils/exportMarkdown'
import { exportPdf } from '@/utils/exportPdf'

// Stores
const chatStore = useChatStore()
const modelStore = useModelStore()

// Toast & Sidebar
const showToast = inject('showToast', null)
const toggleSidebar = inject('toggleSidebar', null)

// Refs
const messagesContainer = ref(null)
const inputTextarea = ref(null)
const titleInput = ref(null)

// 消息选择功能
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
} = useSelection(messagesContainer)

// 状态
const inputMessage = ref('')
const isLoading = ref(false)
const selectedModelId = ref(null)
const isEditingTitle = ref(false)
const editedTitle = ref('')
const showQuotaWarning = ref(false)
const suggestionsList = ref([])
const initialSuggestions = ref([])
const loadingSuggestions = ref(false)
const cancelStream = ref(null)

// 搜索模式状态（从 localStorage 恢复）
const searchMode = ref(localStorage.getItem('chatSearchMode') || 'normal')  // normal, web, rag
const hasKnowledgeBase = ref(false)  // 是否有知识库
const knowledgeBaseId = ref('default')  // 知识库ID

// 监听搜索模式变化，保存到 localStorage
watch(searchMode, (newMode) => {
  localStorage.setItem('chatSearchMode', newMode)
  console.log('💾 搜索模式已保存:', newMode)
})

// 计算属性
const messages = computed(() => {
  // 过滤掉包含 OCR 标签的用户消息（自动发送给模型的 OCR 内容）
  const filtered = chatStore.messages.filter(msg => {
    if (msg.role === 'user' && msg.content) {
      // 检查是否包含 OCR 标签
      return !msg.content.includes('<|ref]>') && !msg.content.includes('<|det]>')
    }
    return true
  })
  
  // 确保每条消息都有唯一的 id
  return filtered.map((msg, index) => {
    if (!msg.id) {
      // 如果消息没有 id，生成一个唯一 id
      return {
        ...msg,
        id: `msg-${chatStore.currentConversation?.id || 'temp'}-${index}-${msg.created_at || Date.now()}`
      }
    }
    return msg
  })
})
const models = computed(() => modelStore.models)
const currentModel = computed(() => 
  models.value.find(m => m.id === selectedModelId.value)
)

const conversationTitle = computed(() => 
  chatStore.currentConversation?.title || '新对话'
)

const canSend = computed(() => 
  inputMessage.value.trim().length > 0 && 
  !isLoading.value &&
  currentModel.value?.is_active &&
  currentModel.value?.quota_remaining > 0
)

// 方法
const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

// 保存滚动位置（防抖）
let scrollSaveTimer = null
const handleScroll = () => {
  if (!chatStore.currentConversation?.id) return
  
  // 使用防抖避免频繁保存
  clearTimeout(scrollSaveTimer)
  scrollSaveTimer = setTimeout(() => {
    const scrollTop = messagesContainer.value?.scrollTop
    if (scrollTop !== undefined) {
      const key = `scroll_${chatStore.currentConversation.id}`
      localStorage.setItem(key, scrollTop.toString())
    }
  }, 200)
}

// 恢复滚动位置
const restoreScrollPosition = () => {
  if (!chatStore.currentConversation?.id) return
  
  nextTick(() => {
    const key = `scroll_${chatStore.currentConversation.id}`
    const savedPosition = localStorage.getItem(key)
    
    if (savedPosition && messagesContainer.value) {
      messagesContainer.value.scrollTop = parseInt(savedPosition)
    }
  })
}

const autoResizeTextarea = () => {
  nextTick(() => {
    if (inputTextarea.value) {
      inputTextarea.value.style.height = 'auto'
      inputTextarea.value.style.height = inputTextarea.value.scrollHeight + 'px'
    }
  })
}

const handleShiftEnter = () => {
  // Shift+Enter 允许换行
  autoResizeTextarea()
}

// 处理语音识别结果
const handleVoiceTranscript = (transcript) => {
  // 将识别的文本追加到输入框
  if (inputMessage.value) {
    inputMessage.value += ' ' + transcript
  } else {
    inputMessage.value = transcript
  }
  
  // 调整输入框高度
  autoResizeTextarea()
  
  // 聚焦输入框
  nextTick(() => {
    inputTextarea.value?.focus()
  })
}

const sendMessage = async () => {
  if (!canSend.value) {
    if (!currentModel.value?.is_active || currentModel.value?.quota_remaining <= 0) {
      showQuotaWarning.value = true
      showToast?.('当前模型流量已用完，请切换其他模型', 'warning')
    }
    return
  }
  
  const message = inputMessage.value.trim()
  if (!message) return
  
  // 清空输入框
  inputMessage.value = ''
  autoResizeTextarea()
  
  // 添加用户消息
  chatStore.messages.push({
    role: 'user',
    content: message,
    timestamp: new Date()
  })
  
  scrollToBottom()
  
  // 准备接收 AI 回复
  const assistantIndex = chatStore.messages.length
  chatStore.messages.push({
    role: 'assistant',
    content: '',
    timestamp: new Date(),
    isStreaming: true
  })
  
  isLoading.value = true
  
  // 调用流式 API 并保存取消函数
  cancelStream.value = chatStream(
    message,
    chatStore.currentConversation?.id,
    selectedModelId.value,
    // onChunk
    (chunk) => {
      console.log('💬 收到内容块:', chunk)
      const msg = chatStore.messages[assistantIndex]
      if (msg) {
        msg.content += chunk
        scrollToBottom()
      } else {
        console.error('❌ 找不到assistant消息:', assistantIndex)
      }
    },
    // onDone
    (conversationId) => {
      console.log('✅ 对话完成:', conversationId)
      const msg = chatStore.messages[assistantIndex]
      if (msg) {
        msg.isStreaming = false
        console.log('📝 最终内容:', msg.content)
      }
      isLoading.value = false
      cancelStream.value = null
      scrollToBottom()
      inputTextarea.value?.focus()
      
      // 更新对话 ID
      if (!chatStore.currentConversation?.id && conversationId) {
        chatStore.currentConversation.id = conversationId
      }
    },
    // onError
    (error) => {
      isLoading.value = false
      cancelStream.value = null
      const msg = chatStore.messages[assistantIndex]
      
      // 如果是用户中断，保留已生成的内容
      if (error?.name === 'AbortError') {
        if (msg) {
          msg.isStreaming = false
        }
        showToast?.('已停止生成', 'info')
      } else {
        // 其他错误，删除空消息
        if (msg && !msg.content) {
          chatStore.messages.splice(assistantIndex, 1)
        }
        showToast?.(error?.message || '发送失败', 'error')
      }
    },
    // onSuggestions
    (suggestions) => {
      suggestionsList.value.push({ suggestions })
      scrollToBottom()
    },
    true, // saveUserMessage
    searchMode.value !== 'normal', // useRag (web或rag模式都启用)
    searchMode.value === 'web' ? 'web_search' : knowledgeBaseId.value // knowledgeBaseId
  )
  
  // 打印调试信息
  console.log('🔍 搜索模式:', searchMode.value, 'useRag:', searchMode.value !== 'normal', 'knowledgeBaseId:', searchMode.value === 'web' ? 'web_search' : knowledgeBaseId.value)
}

// 停止生成
const stopGeneration = () => {
  if (cancelStream.value) {
    cancelStream.value()
    cancelStream.value = null
    isLoading.value = false
    
    // 更新最后一条消息的流式状态
    const lastMsg = chatStore.messages[chatStore.messages.length - 1]
    if (lastMsg && lastMsg.isStreaming) {
      lastMsg.isStreaming = false
    }
  }
}

const handleSuggestionClick = async (title) => {
  console.log('推荐问题被点击:', title)
  inputMessage.value = title
  
  // 使用 nextTick 确保 inputMessage 已更新
  await nextTick()
  
  console.log('准备发送消息:', {
    message: inputMessage.value,
    conversationId: chatStore.currentConversation?.id,
    modelId: selectedModelId.value
  })
  
  // 直接调用发送逻辑，不依赖 inputMessage
  if (!canSend.value) {
    if (!currentModel.value?.is_active || currentModel.value?.quota_remaining <= 0) {
      showQuotaWarning.value = true
      showToast?.('当前模型流量已用完，请切换其他模型', 'warning')
    }
    return
  }
  
  const message = title.trim()  // 直接使用传入的 title
  if (!message) return
  
  console.log('✅ 实际发送的消息:', message)
  
  // 清空输入框
  inputMessage.value = ''
  autoResizeTextarea()
  
  // 添加用户消息
  chatStore.messages.push({
    role: 'user',
    content: message,
    timestamp: new Date()
  })
  
  scrollToBottom()
  
  // 准备接收 AI 回复
  const assistantIndex = chatStore.messages.length
  chatStore.messages.push({
    role: 'assistant',
    content: '',
    timestamp: new Date(),
    isStreaming: true
  })
  
  isLoading.value = true
  
  // 调用流式 API（支持 RAG）
  cancelStream.value = chatStream(
    message,
    chatStore.currentConversation?.id,
    selectedModelId.value,
    // onChunk
    (chunk) => {
      console.log('💬 收到内容块:', chunk)
      const msg = chatStore.messages[assistantIndex]
      if (msg) {
        msg.content += chunk
        scrollToBottom()
      }
    },
    // onDone
    (conversationId) => {
      console.log('✅ 对话完成:', conversationId)
      const msg = chatStore.messages[assistantIndex]
      if (msg) {
        msg.isStreaming = false
        console.log('📝 最终内容:', msg.content)
      }
      isLoading.value = false
      cancelStream.value = null
      scrollToBottom()
      inputTextarea.value?.focus()
      
      if (!chatStore.currentConversation?.id && conversationId) {
        chatStore.currentConversation.id = conversationId
      }
    },
    // onError
    (error) => {
      isLoading.value = false
      cancelStream.value = null
      const msg = chatStore.messages[assistantIndex]
      
      if (error?.name === 'AbortError') {
        if (msg) {
          msg.isStreaming = false
        }
        showToast?.('已停止生成', 'info')
      } else {
        if (msg && !msg.content) {
          chatStore.messages.splice(assistantIndex, 1)
        }
        showToast?.(error?.message || '发送失败', 'error')
      }
    },
    // onSuggestions
    (suggestions) => {
      suggestionsList.value.push({ suggestions })
      scrollToBottom()
    },
    true, // saveUserMessage
    searchMode.value !== 'normal', // useRag (web或rag模式都启用)
    searchMode.value === 'web' ? 'web_search' : knowledgeBaseId.value // knowledgeBaseId
  )
}

const regenerateMessage = async (index) => {
  // TODO: 实现重新生成消息
  showToast?.('重新生成功能开发中', 'info')
}

const copyMessage = (content) => {
  navigator.clipboard.writeText(content)
    .then(() => {
      showToast?.('已复制到剪贴板', 'success')
    })
    .catch(() => {
      showToast?.('复制失败', 'error')
    })
}

const deleteMessage = (index) => {
  if (confirm('确定要删除这条消息吗？')) {
    chatStore.messages.splice(index, 1)
    showToast?.('已删除', 'success')
  }
}

const startEditTitle = () => {
  isEditingTitle.value = true
  editedTitle.value = conversationTitle.value
  nextTick(() => {
    titleInput.value?.focus()
    titleInput.value?.select()
  })
}

const saveTitle = async () => {
  if (editedTitle.value.trim() && editedTitle.value !== conversationTitle.value) {
    try {
      await chatStore.updateConversationTitle(
        chatStore.currentConversation.id,
        editedTitle.value.trim()
      )
      showToast?.('标题已更新', 'success')
    } catch (error) {
      showToast?.('更新失败', 'error')
    }
  }
  isEditingTitle.value = false
}

const cancelEditTitle = () => {
  isEditingTitle.value = false
  editedTitle.value = ''
}

const handleModelChange = () => {
  modelStore.selectModel(selectedModelId.value)
  
  // 检查配额
  const model = currentModel.value
  if (!model.is_active || model.quota_remaining <= 0) {
    showQuotaWarning.value = true
  } else {
    showQuotaWarning.value = false
  }
}

const formatQuota = (quota) => {
  if (quota >= 1000000) {
    const value = quota / 1000000
    return value % 1 === 0 ? `${Math.floor(value)}M` : `${value.toFixed(1)}M`
  } else if (quota >= 1000) {
    const value = quota / 1000
    return value % 1 === 0 ? `${Math.floor(value)}K` : `${value.toFixed(1)}K`
  }
  return quota.toString()
}

// 监听输入变化，自动调整高度
watch(inputMessage, () => {
  autoResizeTextarea()
})

// 监听对话切换，恢复滚动位置
watch(() => chatStore.currentConversation?.id, (newId, oldId) => {
  if (newId && newId !== oldId) {
    // 对话切换时，恢复该对话的滚动位置
    restoreScrollPosition()
    
    // 如果切换到新对话且消息为空，加载推荐问题
    if (messages.value.length === 0 && !loadingSuggestions.value && initialSuggestions.value.length === 0) {
      loadInitialSuggestions()
    }
  }
})

// 监听消息列表变化，当消息为空时加载推荐问题
watch(() => messages.value.length, (newLength, oldLength) => {
  // 只在消息从有到无时触发（比如新建对话），避免初始化时重复加载
  if (newLength === 0 && oldLength > 0 && !loadingSuggestions.value && initialSuggestions.value.length === 0) {
    loadInitialSuggestions()
  }
}, { flush: 'post' })

// 加载推荐问题
const loadInitialSuggestions = async () => {
  loadingSuggestions.value = true
  try {
    const response = await getSuggestions(4)
    // getSuggestions 已经返回了 suggestions 数组，不需要再取 .suggestions
    initialSuggestions.value = Array.isArray(response) ? response : (response?.suggestions || [])
  } catch (error) {
    console.error('Failed to load suggestions:', error)
    // 失败时使用默认推荐
    initialSuggestions.value = [
      { type: 'trending', title: 'TypeScript 5.3 新特性', icon: 'bolt' },
      { type: 'research', title: 'RAG 技术原理与应用', icon: 'science' },
      { type: 'general', title: '前端性能优化指南', icon: 'lightbulb' },
      { type: 'general', title: 'Python 异步编程实战', icon: 'code' }
    ]
  } finally {
    loadingSuggestions.value = false
  }
}

// OCR 文件上传成功处理
const handleFileUpload = async (result) => {
  console.log('File uploaded successfully:', result)
  
  // 刷新消息列表 - 重新加载当前对话，显示上传的图片
  if (chatStore.currentConversation?.id) {
    await chatStore.loadConversation(chatStore.currentConversation.id)
  }
  
  // 滚动到底部
  await nextTick()
  scrollToBottom()
  
  // 将 OCR 识别的内容静默发送给聊天模型（不显示原始 OCR 内容）
  if (result.content_markdown) {
    console.log('OCR content received, sending to chat model silently...')
    
    // 稍微延迟一下，确保页面完全渲染完毕
    setTimeout(async () => {
      // 准备 AI 回复消息槽位
      const assistantIndex = chatStore.messages.length
      chatStore.messages.push({
        role: 'assistant',
        content: '',
        timestamp: new Date(),
        isStreaming: true
      })
      
      isLoading.value = true
      
      // 直接调用流式 API，将 OCR 内容作为消息发送
      cancelStream.value = chatStream(
        result.content_markdown,  // OCR 识别的内容
        chatStore.currentConversation?.id,
        selectedModelId.value,
        // onChunk
        (chunk) => {
          const msg = chatStore.messages[assistantIndex]
          if (msg) {
            msg.content += chunk
            scrollToBottom()
          }
        },
        // onDone
        (data) => {
          const msg = chatStore.messages[assistantIndex]
          if (msg) {
            msg.isStreaming = false
            
            // 更新对话 ID（如果是新对话）
            if (data.conversation_id && !chatStore.currentConversation?.id) {
              chatStore.currentConversation.id = data.conversation_id
              
              const index = chatStore.conversations.findIndex(c => c.id === null)
              if (index !== -1) {
                chatStore.conversations[index].id = data.conversation_id
              }
            }
          }
          
          isLoading.value = false
          cancelStream.value = null
          scrollToBottom()
        },
        // onError
        (error) => {
          console.error('Stream error:', error)
          const msg = chatStore.messages[assistantIndex]
          if (msg) {
            msg.isStreaming = false
            msg.content = '抱歉，发生了错误：' + (error.message || '未知错误')
          }
          
          isLoading.value = false
          cancelStream.value = null
        },
        // onSuggestions
        null,
        // saveUserMessage - OCR 内容不保存到数据库
        false
      )
    }, 100)
  }
}

// OCR 文件上传失败处理
const handleFileUploadError = (error) => {
  console.error('File upload failed:', error)
}

// 检查知识库状态
const checkKnowledgeBaseStatus = async () => {
  try {
    const { ragAPI } = await import('@/services/api')
    const status = await ragAPI.checkStatus()
    
    // 只要有知识库就认为可用（不强制要求有文档）
    hasKnowledgeBase.value = status.knowledge_bases && status.knowledge_bases.length > 0
    
    if (hasKnowledgeBase.value) {
      knowledgeBaseId.value = status.knowledge_bases[0].id
      console.log('✅ 知识库可用:', {
        count: status.knowledge_bases.length,
        id: knowledgeBaseId.value,
        documents: status.total_documents
      })
    } else {
      console.log('❌ 未找到知识库')
    }
  } catch (error) {
    console.error('检查知识库状态失败:', error)
    hasKnowledgeBase.value = false
  }
}

// 消息导出功能
const handleShowContextMenu = (messageId, e) => {
  showCtxMenu(e, messageId)
}

const getSelectedMessages = () => {
  return messages.value.filter(msg => selectedIdList.value.includes(msg.id))
}

const handleExportMarkdown = () => {
  const selectedMessages = getSelectedMessages()
  if (selectedMessages.length === 0) {
    showToast?.('请先选择要导出的消息', 'warning')
    return
  }

  try {
    exportMarkdown(selectedMessages, {
      title: conversationTitle.value,
      filename: `${conversationTitle.value}-${Date.now()}.md`,
      includeTimestamp: true
    })
    showToast?.(`已导出 ${selectedMessages.length} 条消息为 Markdown`, 'success')
  } catch (error) {
    console.error('Markdown 导出失败:', error)
    showToast?.('导出失败，请查看控制台', 'error')
  }
}

const handleExportPdf = async () => {
  const selectedMessages = getSelectedMessages()
  if (selectedMessages.length === 0) {
    showToast?.('请先选择要导出的消息', 'warning')
    return
  }

  try {
    showToast?.('正在生成 PDF，请稍候...', 'info')
    await exportPdf(selectedMessages, {
      title: conversationTitle.value,
      filename: `${conversationTitle.value}-${Date.now()}.pdf`,
      pageSize: 'A4',
      orientation: 'portrait',
      includeTimestamp: true
    })
    showToast?.(`已导出 ${selectedMessages.length} 条消息为 PDF`, 'success')
  } catch (error) {
    console.error('PDF 导出失败:', error)
    showToast?.('PDF 导出失败，请查看控制台', 'error')
  }
}

// 初始化
onMounted(async () => {
  // 加载模型列表
  await modelStore.fetchModels()
  
  // 设置默认模型
  if (modelStore.models.length > 0) {
    const availableModel = modelStore.models.find(m => m.is_active && m.quota_remaining > 0)
    selectedModelId.value = availableModel?.id || modelStore.models[0].id
  }
  
  // 检查知识库状态
  await checkKnowledgeBaseStatus()
  
  // 恢复上次打开的对话
  await chatStore.restoreLastConversation()
  
  // 如果恢复了对话，恢复滚动位置
  if (chatStore.currentConversation) {
    restoreScrollPosition()
  } else {
    // 如果没有恢复到对话，加载推荐问题
    loadInitialSuggestions()
  }
  
  // 聚焦输入框
  inputTextarea.value?.focus()
})
</script>

<style scoped>
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
}

.slide-down-enter-from {
  transform: translateY(-100%);
  opacity: 0;
}

.slide-down-leave-to {
  transform: translateY(-100%);
  opacity: 0;
}

/* 自定义滚动条样式 */
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 3px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}

/* 深色模式 */
:deep(.dark) .custom-scrollbar::-webkit-scrollbar-thumb {
  background: #4b5563;
}

:deep(.dark) .custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #6b7280;
}

/* Firefox */
.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: #d1d5db transparent;
}

:deep(.dark) .custom-scrollbar {
  scrollbar-color: #4b5563 transparent;
}
</style>
