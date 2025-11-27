<template>
  <div
    @click="handleSelect"
    class="group relative px-3 py-2.5 rounded-lg cursor-pointer transition-all"
    :class="[
      isActive 
        ? 'bg-blue-50 border border-blue-200' 
        : 'hover:bg-gray-100 border border-transparent'
    ]"
  >
    <div class="flex items-center justify-between">
      <div class="flex-1 min-w-0 pr-2">
        <div v-if="!isEditing" class="flex items-center space-x-2">
          <svg class="w-4 h-4 text-gray-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
          <p class="text-sm font-medium text-gray-900 truncate">
            {{ displayTitle }}
          </p>
        </div>
        
        <input
          v-else
          ref="titleInput"
          v-model="editingTitle"
          type="text"
          class="w-full px-2 py-1 text-sm border border-blue-500 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
          @blur="saveTitle"
          @keyup.enter="saveTitle"
          @keyup.esc="cancelEdit"
          @click.stop
        />
        
        <div class="flex items-center mt-1 space-x-2 text-xs text-gray-500">
          <span>{{ messageCountText }}</span>
          <span>•</span>
          <span>{{ formatDate(conversation.updated_at) }}</span>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
        <button
          @click.stop="startEdit"
          class="p-1 hover:bg-gray-200 rounded transition-colors"
          title="重命名"
        >
          <svg class="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
        </button>
        
        <button
          @click.stop="handleDelete"
          class="p-1 hover:bg-red-100 rounded transition-colors"
          title="删除"
        >
          <svg class="w-4 h-4 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'

const props = defineProps({
  conversation: {
    type: Object,
    required: true
  },
  isActive: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['select', 'delete', 'rename'])

const isEditing = ref(false)
const editingTitle = ref('')
const titleInput = ref(null)

const displayTitle = computed(() => {
  return props.conversation.title || '新对话'
})

const messageCountText = computed(() => {
  const count = props.conversation.message_count || 0
  return `${count} 条消息`
})

function handleSelect() {
  if (!isEditing.value) {
    emit('select', props.conversation)
  }
}

function handleDelete() {
  emit('delete', props.conversation.id)
}

async function startEdit() {
  isEditing.value = true
  editingTitle.value = props.conversation.title || '新对话'
  await nextTick()
  titleInput.value?.focus()
  titleInput.value?.select()
}

function saveTitle() {
  if (editingTitle.value.trim() && editingTitle.value !== props.conversation.title) {
    emit('rename', props.conversation.id, editingTitle.value.trim())
  }
  isEditing.value = false
}

function cancelEdit() {
  isEditing.value = false
  editingTitle.value = ''
}

function formatDate(dateString) {
  if (!dateString) return ''
  
  const date = new Date(dateString)
  const now = new Date()
  const diff = now - date
  
  // 小于1分钟
  if (diff < 60000) {
    return '刚刚'
  }
  
  // 小于1小时
  if (diff < 3600000) {
    const minutes = Math.floor(diff / 60000)
    return `${minutes}分钟前`
  }
  
  // 小于24小时
  if (diff < 86400000) {
    const hours = Math.floor(diff / 3600000)
    return `${hours}小时前`
  }
  
  // 小于7天
  if (diff < 604800000) {
    const days = Math.floor(diff / 86400000)
    return `${days}天前`
  }
  
  // 超过7天，显示日期
  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}
</script>

<style scoped>
/* 组件特定样式 */
</style>
