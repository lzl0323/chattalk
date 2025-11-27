<template>
  <div class="flex flex-col h-screen bg-gray-50">
    <!-- 顶部导航栏 -->
    <TopNavBar
      @toggle-sidebar="toggleSidebar"
    />

    <!-- 主体区域：侧边栏 + 聊天区 -->
    <div class="flex flex-1 overflow-hidden">
      <!-- 侧边栏（可折叠） -->
      <transition name="slide">
        <div
          v-show="sidebarVisible"
          class="w-80 flex-shrink-0 transition-all duration-300"
        >
          <ChatSidebar
            @conversation-selected="loadConversation"
            @new-conversation="handleNewConversation"
          />
        </div>
      </transition>

      <!-- 主聊天区域 -->
      <div class="flex-1 flex flex-col min-w-0">
        <ChatContainer
          :conversation-id="currentConversationId"
          :initial-messages="currentMessages"
          @messages-updated="handleMessagesUpdated"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import TopNavBar from '../components/TopNavBar.vue'
import ChatSidebar from '../components/ChatSidebar.vue'
import ChatContainer from '../components/ChatContainer.vue'
import { getConversationDetail, createConversation } from '../services/api'
import { currentConversation, setCurrentConversation, fetchConversations } from '../stores/conversationStore'

const currentConversationId = ref(null)
const currentMessages = ref([])
const sidebarVisible = ref(true)

// 切换侧边栏显示
function toggleSidebar() {
  sidebarVisible.value = !sidebarVisible.value
}

async function loadConversation(conversation) {
  if (!conversation) {
    currentConversationId.value = null
    currentMessages.value = []
    return
  }

  try {
    const detail = await getConversationDetail(conversation.id)
    currentConversationId.value = detail.id
    currentMessages.value = detail.messages || []
  } catch (error) {
    console.error('Failed to load conversation:', error)
    currentMessages.value = []
  }
}

async function startNewConversation() {
  try {
    const newConv = await createConversation(null)
    setCurrentConversation(newConv)
    currentConversationId.value = newConv.id
    currentMessages.value = []
    
    // 刷新对话列表
    await fetchConversations()
  } catch (error) {
    console.error('Failed to create conversation:', error)
  }
}

function handleNewConversation(conversation) {
  currentConversationId.value = conversation.id
  currentMessages.value = []
}

async function handleMessagesUpdated(messages) {
  currentMessages.value = messages
  
  // 如果是新对话的第一次回复，刷新对话列表以获取后端生成的标题
  if (messages.length === 2 && currentConversation.value) {
    // 延迟一下，确保后端已经更新了标题
    setTimeout(async () => {
      await fetchConversations()
    }, 500)
  }
}

onMounted(() => {
  // 如果有当前对话，加载它
  if (currentConversation.value) {
    loadConversation(currentConversation.value)
  }
})
</script>

<style scoped>
/* 侧边栏滑动动画 */
.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
}

.slide-enter-from {
  transform: translateX(-100%);
  opacity: 0;
}

.slide-leave-to {
  transform: translateX(-100%);
  opacity: 0;
}
</style>
