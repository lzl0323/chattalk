<template>
  <div class="search-mode-selector flex items-center gap-2">
    <!-- 联网搜索按钮 -->
    <button
      @click="selectMode('web')"
      :class="[
        'mode-button',
        mode === 'web' ? 'active' : 'inactive'
      ]"
      :title="mode === 'web' ? '联网搜索已开启' : '点击开启联网搜索'"
    >
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
      <span class="mode-label">联网搜索</span>
      <span class="status-badge">{{ mode === 'web' ? 'ON' : 'OFF' }}</span>
    </button>

    <!-- 深度搜索按钮 -->
    <button
      @click="selectMode('rag')"
      :class="[
        'mode-button',
        mode === 'rag' ? 'active' : 'inactive'
      ]"
      :disabled="!hasKnowledgeBase"
      :title="getTooltip('rag')"
    >
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
      </svg>
      <span class="mode-label">深度搜索</span>
      <span class="status-badge">{{ mode === 'rag' ? 'ON' : 'OFF' }}</span>
    </button>

    <!-- 提示信息 -->
    <transition name="fade">
      <div v-if="showHint" class="mode-hint">
        {{ hintText }}
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: 'normal' // normal, web, rag
  },
  hasKnowledgeBase: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

const mode = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const showHint = ref(false)
const hintText = ref('')

const selectMode = (newMode) => {
  // 如果点击当前模式，则关闭
  if (mode.value === newMode) {
    mode.value = 'normal'
    hintText.value = '已切换到普通模式'
  } else {
    // 切换到新模式
    if (newMode === 'rag' && !props.hasKnowledgeBase) {
      hintText.value = '请先在知识库管理页面上传文档'
      showHint.value = true
      setTimeout(() => {
        showHint.value = false
      }, 3000)
      return
    }
    
    mode.value = newMode
    hintText.value = newMode === 'web' 
      ? '联网搜索已开启，将搜索互联网最新信息'
      : '深度搜索已开启，将检索知识库文档'
  }
  
  showHint.value = true
  setTimeout(() => {
    showHint.value = false
  }, 2000)
}

const getTooltip = (modeType) => {
  if (modeType === 'rag' && !props.hasKnowledgeBase) {
    return '请先上传文档到知识库'
  }
  return mode.value === modeType 
    ? '深度搜索已开启' 
    : '点击开启深度搜索'
}

watch(() => props.modelValue, (newVal) => {
  console.log('搜索模式:', newVal === 'normal' ? '普通' : newVal === 'web' ? '联网搜索' : '深度搜索')
})
</script>

<style scoped>
.search-mode-selector {
  position: relative;
}

.mode-button {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border: 1.5px solid;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

/* 激活状态 */
.mode-button.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: #667eea;
  color: white;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.mode-button.active:hover {
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  transform: translateY(-1px);
}

/* 未激活状态 */
.mode-button.inactive {
  background: white;
  border-color: #e5e7eb;
  color: #6b7280;
}

.mode-button.inactive:hover {
  background: #f9fafb;
  border-color: #d1d5db;
}

/* 禁用状态 */
.mode-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.mode-button:disabled:hover {
  transform: none;
  box-shadow: none;
}

/* 暗色模式 */
.dark .mode-button.inactive {
  background: #374151;
  border-color: #4b5563;
  color: #9ca3af;
}

.dark .mode-button.inactive:hover {
  background: #4b5563;
  border-color: #6b7280;
}

/* 标签 */
.mode-label {
  font-weight: 600;
}

/* 状态标识 */
.status-badge {
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.active .status-badge {
  background: rgba(255, 255, 255, 0.25);
  color: white;
}

.inactive .status-badge {
  background: rgba(0, 0, 0, 0.05);
  color: #9ca3af;
}

/* 提示信息 */
.mode-hint {
  position: absolute;
  top: 100%;
  left: 0;
  margin-top: 8px;
  padding: 8px 12px;
  background: rgba(0, 0, 0, 0.85);
  color: white;
  border-radius: 6px;
  font-size: 12px;
  white-space: nowrap;
  z-index: 1000;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: all 0.2s ease;
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(-4px);
}

.fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
