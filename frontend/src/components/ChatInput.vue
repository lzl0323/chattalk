<template>
  <div class="border-t border-gray-200 bg-white p-4">
    <div class="max-w-4xl mx-auto">
      <div class="flex items-end gap-3">
        <!-- 输入框 -->
        <div class="flex-1 relative">
          <textarea
            ref="textareaRef"
            v-model="inputMessage"
            :disabled="disabled"
            :placeholder="placeholder"
            class="w-full px-4 py-3 pr-12 border border-gray-300 rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed transition-all"
            :class="{ 'border-red-500': error }"
            rows="1"
            @keydown.enter.exact.prevent="handleSend"
            @keydown.shift.enter="handleNewLine"
            @input="adjustHeight"
          ></textarea>
          
          <!-- 字符计数 -->
          <div
            v-if="inputMessage.length > 0"
            class="absolute bottom-2 right-2 text-xs"
            :class="inputMessage.length > 4000 ? 'text-red-500' : 'text-gray-400'"
          >
            {{ inputMessage.length }} / 4000
          </div>
        </div>
        
        <!-- 发送按钮 -->
        <button
          @click="handleSend"
          :disabled="!canSend"
          class="px-6 py-3 bg-primary-500 text-white rounded-xl font-medium hover:bg-primary-600 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:bg-gray-300 disabled:cursor-not-allowed transition-all flex items-center gap-2"
        >
          <svg
            v-if="!disabled"
            class="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
            />
          </svg>
          <svg
            v-else
            class="w-5 h-5 animate-spin"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              class="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              stroke-width="4"
            ></circle>
            <path
              class="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            ></path>
          </svg>
          <span>{{ disabled ? '发送中...' : '发送' }}</span>
        </button>
      </div>
      
      <!-- 错误提示 -->
      <div v-if="error" class="mt-2 text-sm text-red-500">
        {{ error }}
      </div>
      
      <!-- 提示信息 -->
      <div class="mt-2 text-xs text-gray-500 flex items-center justify-between">
        <span>按 Enter 发送，Shift + Enter 换行</span>
        <button
          v-if="showClear"
          @click="$emit('clear')"
          class="text-primary-500 hover:text-primary-600 transition-colors"
        >
          清空对话
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'

const props = defineProps({
  disabled: {
    type: Boolean,
    default: false
  },
  placeholder: {
    type: String,
    default: '输入消息...'
  },
  showClear: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['send', 'clear'])

const inputMessage = ref('')
const textareaRef = ref(null)
const error = ref('')

const canSend = computed(() => {
  return !props.disabled &&
    inputMessage.value.trim().length > 0 &&
    inputMessage.value.length <= 4000
})

// 调整文本框高度
const adjustHeight = () => {
  const textarea = textareaRef.value
  if (!textarea) return
  
  textarea.style.height = 'auto'
  const newHeight = Math.min(textarea.scrollHeight, 200) // 最大高度 200px
  textarea.style.height = `${newHeight}px`
}

// 处理发送
const handleSend = () => {
  const message = inputMessage.value.trim()
  
  // 验证
  if (!message) {
    error.value = '消息不能为空'
    return
  }
  
  if (message.length > 4000) {
    error.value = '消息过长，最多 4000 字符'
    return
  }
  
  if (props.disabled) {
    return
  }
  
  // 清除错误
  error.value = ''
  
  // 发送消息
  emit('send', message)
  
  // 清空输入
  inputMessage.value = ''
  
  // 重置高度
  nextTick(() => {
    if (textareaRef.value) {
      textareaRef.value.style.height = 'auto'
    }
  })
}

// 处理换行
const handleNewLine = () => {
  inputMessage.value += '\n'
  nextTick(adjustHeight)
}

// 清除错误提示
watch(inputMessage, () => {
  if (error.value && inputMessage.value.length <= 4000) {
    error.value = ''
  }
})

// 暴露焦点方法
const focus = () => {
  textareaRef.value?.focus()
}

defineExpose({ focus })
</script>
