<template>
  <div class="rag-toggle-container">
    <button
      @click="toggleRag"
      :class="[
        'rag-toggle-button',
        isRagEnabled ? 'rag-enabled' : 'rag-disabled'
      ]"
      :title="isRagEnabled ? '深度搜索已开启' : '深度搜索已关闭'"
    >
      <!-- 图标 -->
      <svg
        class="rag-icon"
        :class="{ 'icon-active': isRagEnabled }"
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M21 21L16.65 16.65M19 11C19 15.4183 15.4183 19 11 19C6.58172 19 3 15.4183 3 11C3 6.58172 6.58172 3 11 3C15.4183 3 19 6.58172 19 11Z"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
        <path
          v-if="isRagEnabled"
          d="M11 8V14M8 11H14"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
        />
      </svg>
      
      <!-- 文字 -->
      <span class="rag-label">联网搜索</span>
      
      <!-- 状态指示器 -->
      <span
        :class="[
          'rag-status',
          isRagEnabled ? 'status-on' : 'status-off'
        ]"
      >
        {{ isRagEnabled ? 'ON' : 'OFF' }}
      </span>
    </button>
    
    <!-- 提示文字 -->
    <transition name="fade">
      <div v-if="showHint" class="rag-hint">
        <svg class="hint-icon" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
        </svg>
        <span>{{ hintText }}</span>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

const isRagEnabled = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const showHint = ref(false)
const hintText = computed(() => {
  if (props.disabled) {
    return '搜索功能暂时不可用'
  }
  return isRagEnabled.value
    ? '实时搜索互联网最新信息'
    : '普通对话模式'
})

const toggleRag = () => {
  if (props.disabled) {
    showHint.value = true
    setTimeout(() => {
      showHint.value = false
    }, 3000)
    return
  }
  
  isRagEnabled.value = !isRagEnabled.value
  showHint.value = true
  setTimeout(() => {
    showHint.value = false
  }, 2000)
}

// 监听状态变化
watch(() => props.modelValue, (newVal) => {
  console.log('RAG 模式:', newVal ? '开启' : '关闭')
})
</script>

<style scoped>
.rag-toggle-container {
  position: relative;
  display: inline-flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
}

.rag-toggle-button {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border: 2px solid transparent;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.rag-toggle-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, transparent 0%, rgba(255,255,255,0.1) 100%);
  opacity: 0;
  transition: opacity 0.3s;
}

.rag-toggle-button:hover::before {
  opacity: 1;
}

/* 禁用状态 */
.rag-disabled {
  background: #f3f4f6;
  color: #6b7280;
  border-color: #e5e7eb;
}

.rag-disabled:hover {
  background: #e5e7eb;
  border-color: #d1d5db;
}

/* 启用状态 */
.rag-enabled {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.rag-enabled:hover {
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
  transform: translateY(-1px);
}

/* 图标 */
.rag-icon {
  width: 20px;
  height: 20px;
  transition: transform 0.3s;
}

.rag-toggle-button:hover .rag-icon {
  transform: scale(1.1);
}

.icon-active {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

/* 文字 */
.rag-label {
  font-weight: 600;
  letter-spacing: 0.3px;
}

/* 状态指示器 */
.rag-status {
  padding: 2px 8px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-off {
  background: rgba(0, 0, 0, 0.1);
  color: #6b7280;
}

.status-on {
  background: rgba(255, 255, 255, 0.3);
  color: white;
}

/* 提示框 */
.rag-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  border-radius: 8px;
  font-size: 12px;
  white-space: nowrap;
  position: absolute;
  top: 100%;
  left: 0;
  margin-top: 8px;
  z-index: 1000;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.hint-icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: all 0.3s ease;
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(-8px);
}

.fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* 暗色模式 */
.dark .rag-disabled {
  background: #374151;
  color: #9ca3af;
  border-color: #4b5563;
}

.dark .rag-disabled:hover {
  background: #4b5563;
  border-color: #6b7280;
}
</style>
