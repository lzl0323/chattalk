<template>
  <div class="flex flex-col h-full bg-gray-50 border-r border-gray-200">
    <!-- 顶部：新建对话按钮 -->
    <div class="p-4 border-b border-gray-200 bg-white">
      <button
        @click="createNewChat"
        class="w-full flex items-center justify-center space-x-2 px-4 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium shadow-sm"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        <span>新建对话</span>
      </button>
    </div>

    <!-- 搜索框 -->
    <div class="p-4">
      <div class="relative">
        <input
          v-model="searchInput"
          type="text"
          placeholder="搜索对话..."
          class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
          @input="handleSearch"
        />
        <svg class="absolute left-3 top-2.5 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      </div>
    </div>

    <!-- 对话列表 -->
    <div class="flex-1 overflow-y-auto px-2">
      <div v-if="isLoading && conversations.length === 0" class="text-center py-8 text-gray-500">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
        <p class="mt-2 text-sm">加载中...</p>
      </div>

      <div v-else-if="conversations.length === 0" class="text-center py-8 text-gray-500">
        <svg class="w-16 h-16 mx-auto text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>
        <p class="mt-2 text-sm">暂无对话历史</p>
        <p class="text-xs text-gray-400 mt-1">点击上方按钮创建新对话</p>
      </div>

      <div v-else class="space-y-1 pb-4">
        <ChatListItem
          v-for="conversation in conversations"
          :key="conversation.id"
          :conversation="conversation"
          :is-active="currentConversation?.id === conversation.id"
          @select="selectConversation"
          @delete="deleteChat"
          @rename="renameChat"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import ChatListItem from './ChatListItem.vue'
import { 
  conversations, 
  currentConversation,
  isLoading,
  fetchConversations,
  createNewConversation,
  deleteConversation,
  updateConversation,
  setCurrentConversation,
  clearCurrentConversation
} from '../stores/conversationStore'

const emit = defineEmits(['conversation-selected', 'new-conversation'])

const searchInput = ref('')

onMounted(async () => {
  await fetchConversations()
})

async function createNewChat() {
  const newConv = await createNewConversation()
  if (newConv) {
    emit('new-conversation', newConv)
  }
}

function selectConversation(conversation) {
  setCurrentConversation(conversation)
  emit('conversation-selected', conversation)
}

async function deleteChat(conversationId) {
  if (confirm('确定要删除这个对话吗？')) {
    const success = await deleteConversation(conversationId)
    if (success && currentConversation.value?.id === conversationId) {
      clearCurrentConversation()
      emit('conversation-selected', null)
    }
  }
}

async function renameChat(conversationId, newTitle) {
  await updateConversation(conversationId, newTitle)
}

let searchTimeout = null
function handleSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(async () => {
    await fetchConversations(searchInput.value || null)
  }, 300)
}
</script>

<style scoped>
/* 滚动条样式 */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: transparent;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #cbd5e0;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #a0aec0;
}
</style>
