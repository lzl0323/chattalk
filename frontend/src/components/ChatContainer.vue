<template>
  <div class="flex flex-col h-full bg-white">
    <!-- 消息列表 -->
    <main
      ref="messagesContainer"
      class="flex-1 overflow-y-auto custom-scrollbar px-6 py-6"
    >
      <div class="max-w-4xl mx-auto">
        <!-- 欢迎消息 -->
        <div v-if="messages.length === 0" class="text-center py-12">
          <div class="w-20 h-20 mx-auto mb-6 bg-gradient-to-br from-primary-100 to-primary-200 rounded-full flex items-center justify-center">
            <svg class="w-10 h-10 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
          </div>
          <h2 class="text-2xl font-bold text-gray-800 mb-2">欢迎使用 AI 对话助手</h2>
          <p class="text-gray-600 mb-8">我可以帮助你解答问题、提供建议、进行创意讨论等</p>
          
          <!-- 示例问题 -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-2xl mx-auto">
            <!-- 加载状态 -->
            <div v-if="loadingSuggestions" class="col-span-full text-center py-8">
              <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
              <p class="text-sm text-gray-500 mt-2">正在生成推荐问题...</p>
            </div>
            
            <!-- 推荐问题 -->
            <button
              v-for="example in exampleQuestions"
              :key="example"
              @click="handleExampleClick(example)"
              class="p-4 bg-white border border-gray-200 rounded-xl hover:border-primary-500 hover:shadow-md transition-all text-left group"
            >
              <div class="flex items-start gap-3">
                <svg class="w-5 h-5 text-primary-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                <span class="text-sm text-gray-700 group-hover:text-gray-900">{{ example }}</span>
              </div>
            </button>
          </div>
        </div>
        
        <!-- 消息列表 -->
        <div v-else>
          <template v-for="(msg, index) in messages" :key="index">
            <!-- 普通消息 -->
            <ChatMessage
              v-if="msg.role !== 'suggestions'"
              :role="msg.role"
              :content="msg.content"
              :timestamp="msg.timestamp"
              :is-streaming="msg.isStreaming"
            />
            
            <!-- 推荐卡片 -->
            <div v-else class="max-w-2xl mx-auto my-6">
              <div class="flex items-center gap-2 mb-3">
                <svg class="w-4 h-4 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                <span class="text-sm font-medium text-gray-700">你可能感兴趣的问题</span>
              </div>
              <div class="grid grid-cols-1 gap-3">
                <button
                  v-for="(suggestion, sIndex) in msg.suggestions"
                  :key="sIndex"
                  @click="handleExampleClick(suggestion.title)"
                  class="group flex items-center gap-3 p-3 rounded-lg border border-gray-200 bg-white hover:bg-purple-50 hover:border-purple-200 transition-all duration-200 text-left"
                >
                  <div class="w-8 h-8 rounded-lg bg-purple-50 group-hover:bg-purple-100 flex items-center justify-center flex-shrink-0">
                    <svg class="w-4 h-4 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                  <span class="text-sm text-gray-700 group-hover:text-gray-900">{{ suggestion.title }}</span>
                </button>
              </div>
            </div>
          </template>
        </div>
        
        <!-- 错误提示 -->
        <div
          v-if="errorMessage"
          class="max-w-2xl mx-auto mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3"
        >
          <svg class="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div class="flex-1">
            <p class="text-sm text-red-800">{{ errorMessage }}</p>
          </div>
          <button
            @click="errorMessage = ''"
            class="text-red-500 hover:text-red-700"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
    </main>
    
    <!-- 底部区域：模型选择 + 输入框 -->
    <div class="border-t border-gray-200 bg-white">
      <!-- 模型选择器 -->
      <div v-if="availableModels.length > 0" class="px-6 py-2 border-b border-gray-100">
        <div class="max-w-4xl mx-auto flex items-center space-x-3">
          <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
          <select
            v-model="selectedModelId"
            class="flex-1 text-sm border-0 focus:ring-0 text-gray-700 cursor-pointer"
          >
            <option
              v-for="model in availableModels"
              :key="model.id"
              :value="model.id"
            >
              {{ model.name }} (剩余: {{ formatQuota(model.quota_remaining) }})
            </option>
          </select>
          <span v-if="selectedModel" class="text-xs text-gray-500">
            {{ selectedModel.quota_percentage.toFixed(0) }}% 已用
          </span>
        </div>
      </div>
      
      <!-- 输入框 -->
      <ChatInput
        ref="chatInputRef"
        :disabled="isLoading"
        :show-clear="messages.length > 0"
        @send="handleSendMessage"
        @clear="handleClear"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted, watch } from 'vue'
import ChatMessage from './ChatMessage.vue'
import ChatInput from './ChatInput.vue'
import { chatStream, getActiveModels, getSuggestions } from '../services/api'

// Props
const props = defineProps({
  conversationId: {
    type: String,
    default: null
  },
  initialMessages: {
    type: Array,
    default: () => []
  }
})

// Emits
const emit = defineEmits(['messages-updated'])

// 状态
const messages = ref([])
const isLoading = ref(false)
const conversationId = ref(props.conversationId)
const errorMessage = ref('')
const messagesContainer = ref(null)
const chatInputRef = ref(null)

// 模型相关状态
const availableModels = ref([])
const selectedModelId = ref(null)

// 计算当前选中的模型
const selectedModel = computed(() => {
  return availableModels.value.find(m => m.id === selectedModelId.value)
})

// 格式化配额显示
const formatQuota = (quota) => {
  if (quota >= 1000000) {
    return (quota / 1000000).toFixed(1) + 'M'
  } else if (quota >= 1000) {
    return (quota / 1000).toFixed(1) + 'K'
  }
  return quota.toFixed(0)
}

// 监听 props 变化
watch(() => props.conversationId, (newId, oldId) => {
  conversationId.value = newId
  // 如果切换了对话，清空错误消息
  if (newId !== oldId) {
    errorMessage.value = ''
  }
})

watch(() => props.initialMessages, (newMessages) => {
  messages.value = newMessages && newMessages.length > 0 ? [...newMessages] : []
  nextTick(() => {
    scrollToBottom()
  })
}, { immediate: true, deep: true })

// 推荐问题
const exampleQuestions = ref([])
const loadingSuggestions = ref(false)

// 加载推荐问题
const loadSuggestions = async () => {
  try {
    loadingSuggestions.value = true
    const suggestions = await getSuggestions(4)
    exampleQuestions.value = suggestions.map(s => s.title)
  } catch (error) {
    console.error('Failed to load suggestions:', error)
    // 使用默认推荐
    exampleQuestions.value = [
      '请介绍一下 Vue 3 的主要特性',
      '如何优化网站性能？',
      '请解释一下机器学习的基本概念',
      '给我推荐一些学习编程的资源'
    ]
  } finally {
    loadingSuggestions.value = false
  }
}

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

// 处理发送消息
const handleSendMessage = (message) => {
  // 添加用户消息
  messages.value.push({
    role: 'user',
    content: message,
    timestamp: new Date()
  })
  
  scrollToBottom()
  
  // 准备接收助手回复
  const assistantMessageIndex = messages.value.length
  messages.value.push({
    role: 'assistant',
    content: '',
    timestamp: new Date(),
    isStreaming: true
  })
  
  isLoading.value = true
  errorMessage.value = ''
  
  // 流式请求
  chatStream(
    message,
    conversationId.value,
    selectedModelId.value,  // 传递选中的模型 ID
    // onChunk: 接收到内容块
    (chunk) => {
      const msg = messages.value[assistantMessageIndex]
      if (msg) {
        msg.content += chunk
        scrollToBottom()
      }
    },
    // onDone: 完成
    (newConversationId) => {
      isLoading.value = false
      const msg = messages.value[assistantMessageIndex]
      if (msg) {
        msg.isStreaming = false
      }
      
      // 保存对话 ID
      if (newConversationId) {
        conversationId.value = newConversationId
      }
      
      // 通知父组件消息已更新
      emit('messages-updated', messages.value)
      
      scrollToBottom()
      
      // 聚焦输入框
      chatInputRef.value?.focus()
    },
    // onError: 错误
    (error) => {
      isLoading.value = false
      const msg = messages.value[assistantMessageIndex]
      if (msg) {
        msg.isStreaming = false
      }
      
      errorMessage.value = `发送失败: ${error.message || '未知错误'}`
      console.error('Chat error:', error)
      
      // 移除空的助手消息
      if (msg && !msg.content) {
        messages.value.splice(assistantMessageIndex, 1)
      }
    },
    // onSuggestions: 接收到推荐卡片
    (suggestions) => {
      // 将推荐卡片插入到消息流中
      messages.value.push({
        role: 'suggestions',
        suggestions: suggestions,
        timestamp: new Date()
      })
      scrollToBottom()
    }
  )
}

// 处理示例问题点击
const handleExampleClick = (question) => {
  handleSendMessage(question)
}

// 清空对话
const handleClear = () => {
  if (confirm('确定要清空对话吗？')) {
    messages.value = []
    conversationId.value = null
    errorMessage.value = ''
    emit('messages-updated', [])
    chatInputRef.value?.focus()
  }
}

// 加载可用模型
const loadModels = async () => {
  try {
    availableModels.value = await getActiveModels()
    if (availableModels.value.length > 0 && !selectedModelId.value) {
      selectedModelId.value = availableModels.value[0].id
    }
  } catch (error) {
    console.error('Failed to load models:', error)
  }
}

// 挂载时加载模型、推荐问题并聚焦输入框
onMounted(() => {
  loadModels()
  loadSuggestions()
  chatInputRef.value?.focus()
})
</script>
