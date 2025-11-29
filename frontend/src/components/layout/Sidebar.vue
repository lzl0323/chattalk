<template>
  <!-- 桌面端固定侧边栏 + 移动端抽屉 -->
  <div>
    <!-- 移动端遮罩层 -->
    <Transition name="fade">
      <div
        v-if="isOpen"
        class="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
        @click="$emit('close')"
      ></div>
    </Transition>
    
    <!-- 侧边栏主体 -->
    <aside
      :class="[
        'fixed inset-y-0 left-0 z-50',
        'w-[260px] h-full flex flex-col',
        'bg-gpt-gray-50 dark:bg-gpt-dark-800',
        'border-r border-gray-200 dark:border-gpt-dark-400',
        'transition-transform duration-300 ease-in-out',
        isOpen ? 'translate-x-0' : '-translate-x-full'
      ]"
    >
      <!-- 顶部：新建聊天按钮和收起按钮 -->
      <div class="p-3 border-b border-gray-200 dark:border-gpt-dark-400">
        <div class="flex items-center gap-2">
          <button
            @click="createNewChat"
            class="flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-lg
                   bg-white dark:bg-gpt-dark-600 hover:bg-gray-50 dark:hover:bg-gpt-dark-500
                   border border-gray-200 dark:border-gpt-dark-500
                   text-sm font-medium text-gray-900 dark:text-gray-100
                   transition-all duration-200 shadow-sm hover:shadow"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            新建聊天
          </button>
          
          <!-- 收起侧边栏按钮 -->
          <button
            @click="$emit('close')"
            class="flex-shrink-0 p-3 rounded-lg
                   hover:bg-gray-100 dark:hover:bg-gpt-dark-600
                   transition-colors"
            title="收起侧边栏"
          >
            <svg class="w-5 h-5 text-gray-700 dark:text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
            </svg>
          </button>
        </div>
      </div>
      
      <!-- 搜索框 -->
      <div class="p-3 border-b border-gray-200 dark:border-gpt-dark-400">
        <div class="relative">
          <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索对话..."
            class="w-full pl-10 pr-4 py-2 rounded-lg text-sm
                   bg-white dark:bg-gpt-dark-600
                   border border-gray-200 dark:border-gpt-dark-500
                   text-gray-900 dark:text-gray-100
                   placeholder-gray-400 dark:placeholder-gray-500
                   focus:outline-none focus:ring-2 focus:ring-gpt-green-500
                   transition-all duration-200"
          >
        </div>
      </div>
      
      <!-- 对话列表 -->
      <div class="flex-1 overflow-y-auto scrollbar-thin p-2">
        <div v-if="loading" class="flex items-center justify-center py-8">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-gpt-green-500"></div>
        </div>
        
        <div v-else-if="filteredConversations.length === 0" class="py-8 text-center">
          <p class="text-sm text-gray-500 dark:text-gray-400">
            {{ searchQuery ? '没有找到相关对话' : '暂无对话记录' }}
          </p>
        </div>
        
        <div v-else class="space-y-1">
          <div
            v-for="conversation in filteredConversations"
            :key="conversation.id"
            :class="[
              'group relative flex items-center gap-3 px-3 py-2.5 rounded-lg cursor-pointer',
              'transition-all duration-200',
              currentConversationId === conversation.id
                ? 'bg-gpt-gray-200 dark:bg-gpt-dark-600'
                : 'hover:bg-gpt-gray-100 dark:hover:bg-gpt-dark-700'
            ]"
            @click="selectConversation(conversation.id)"
          >
            <!-- 对话图标 -->
            <svg class="w-4 h-4 flex-shrink-0 text-gray-500 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
            
            <!-- 对话标题 -->
            <span class="flex-1 text-sm text-gray-900 dark:text-gray-100 truncate">
              {{ conversation.title || '新对话' }}
            </span>
            
            <!-- 操作按钮（悬停显示） -->
            <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
              <!-- 重命名 -->
              <button
                @click.stop="renameConversation(conversation)"
                class="p-1.5 rounded hover:bg-gpt-gray-300 dark:hover:bg-gpt-dark-500"
                title="重命名"
              >
                <svg class="w-4 h-4 text-gray-600 dark:text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </button>
              
              <!-- 删除 -->
              <button
                @click.stop="deleteConversation(conversation)"
                class="p-1.5 rounded hover:bg-red-100 dark:hover:bg-red-900/30"
                title="删除"
              >
                <svg class="w-4 h-4 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 底部菜单 -->
      <div class="shrink-0 border-t border-gray-200 dark:border-gpt-dark-400 p-2 space-y-1">
        <!-- 知识库管理 -->
        <router-link
          to="/knowledge"
          class="flex items-center gap-3 px-3 py-2 rounded-lg text-sm
                 text-gray-700 dark:text-gray-300
                 hover:bg-gpt-gray-100 dark:hover:bg-gpt-dark-700
                 transition-colors duration-200"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
          </svg>
          <span>知识库</span>
        </router-link>
        
        <!-- 模型管理 -->
        <router-link
          to="/models"
          class="flex items-center gap-3 px-3 py-2 rounded-lg text-sm
                 text-gray-700 dark:text-gray-300
                 hover:bg-gpt-gray-100 dark:hover:bg-gpt-dark-700
                 transition-colors duration-200"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          <span>模型管理</span>
        </router-link>
        
        <!-- 主题切换 -->
        <button
          @click="themeStore.toggleTheme()"
          class="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-left
                 text-gray-700 dark:text-gray-300
                 hover:bg-gpt-gray-100 dark:hover:bg-gpt-dark-700
                 transition-colors duration-200"
        >
          <svg v-if="themeStore.theme === 'light'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
          </svg>
          <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
          </svg>
          <span>{{ themeStore.theme === 'light' ? '深色模式' : '浅色模式' }}</span>
        </button>
        
        <!-- 用户信息 -->
        <div
          class="flex items-center justify-between gap-2 px-3 py-2 rounded-lg
                 bg-gpt-gray-100 dark:bg-gpt-dark-700
                 border border-gray-200 dark:border-gpt-dark-600"
        >
          <div class="flex items-center gap-2 flex-1 min-w-0">
            <div class="w-7 h-7 rounded-full bg-gpt-green-500 flex items-center justify-center flex-shrink-0">
              <span class="text-white text-xs font-medium">{{ userInitial }}</span>
            </div>
            <span class="text-sm text-gray-900 dark:text-gray-100 truncate">{{ userEmail }}</span>
          </div>
          <button
            @click="logout"
            class="p-1.5 rounded hover:bg-red-100 dark:hover:bg-red-900/30 transition-colors"
            title="退出登录"
          >
            <svg class="w-4 h-4 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
          </button>
        </div>
      </div>
    </aside>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, inject } from 'vue'
import { useRouter } from 'vue-router'
import { useThemeStore } from '@/stores/themeStore'
import { useAuthStore } from '@/stores/authStore'
import { useChatStore } from '@/stores/chatStore'

// Props & Emits
defineProps({
  isOpen: Boolean
})

const emit = defineEmits(['close'])

// Router & Stores
const router = useRouter()
const themeStore = useThemeStore()
const authStore = useAuthStore()
const chatStore = useChatStore()

// Toast
const showToast = inject('showToast')

// 状态
const searchQuery = ref('')
const loading = ref(false)

// 计算属性
const currentConversationId = computed(() => chatStore.currentConversation?.id)

const filteredConversations = computed(() => {
  if (!searchQuery.value) {
    return chatStore.conversations
  }
  
  const query = searchQuery.value.toLowerCase()
  return chatStore.conversations.filter(conv => 
    conv.title?.toLowerCase().includes(query)
  )
})

const userEmail = computed(() => authStore.user?.email || '')
const userInitial = computed(() => userEmail.value.charAt(0).toUpperCase())
const isAdmin = computed(() => authStore.user?.is_admin || false)

// 方法
const createNewChat = async () => {
  try {
    await chatStore.createConversation()
    // 只在移动端（屏幕宽度 < 1024px）时关闭侧边栏
    if (window.innerWidth < 1024) {
      emit('close')
    }
    router.push('/')
  } catch (error) {
    showToast?.('创建对话失败', 'error')
  }
}

const selectConversation = async (id) => {
  try {
    await chatStore.loadConversation(id)
    // 只在移动端（屏幕宽度 < 1024px）时关闭侧边栏
    if (window.innerWidth < 1024) {
      emit('close')
    }
    router.push('/')
  } catch (error) {
    showToast?.('加载对话失败', 'error')
  }
}

const renameConversation = (conversation) => {
  const newTitle = prompt('输入新标题：', conversation.title || '新对话')
  if (newTitle && newTitle.trim()) {
    chatStore.updateConversationTitle(conversation.id, newTitle.trim())
      .then(() => {
        showToast?.('重命名成功', 'success')
      })
      .catch(() => {
        showToast?.('重命名失败', 'error')
      })
  }
}

const deleteConversation = (conversation) => {
  if (confirm(`确定要删除对话"${conversation.title || '新对话'}"吗？`)) {
    // 如果是临时对话（id 为 null），直接从本地删除
    if (!conversation.id || conversation.id === 'null') {
      const index = chatStore.conversations.findIndex(c => c === conversation)
      if (index > -1) {
        chatStore.conversations.splice(index, 1)
        // 如果删除的是当前对话，切换到第一个对话或清空
        if (chatStore.currentConversation === conversation) {
          if (chatStore.conversations.length > 0) {
            chatStore.loadConversation(chatStore.conversations[0].id)
          } else {
            chatStore.currentConversation = null
            chatStore.messages = []
          }
        }
        showToast?.('删除成功', 'success')
      }
      return
    }
    
    // 真实对话，调用后端 API 删除
    chatStore.deleteConversation(conversation.id)
      .then(() => {
        showToast?.('删除成功', 'success')
      })
      .catch(() => {
        showToast?.('删除失败', 'error')
      })
  }
}

const logout = () => {
  if (confirm('确定要退出登录吗？')) {
    authStore.logout()
    router.push('/login')
  }
}

// 初始化
onMounted(async () => {
  loading.value = true
  try {
    await chatStore.fetchConversations()
  } catch (error) {
    console.error('Failed to fetch conversations:', error)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 自定义滚动条 */
.scrollbar-thin::-webkit-scrollbar {
  width: 6px;
}

.scrollbar-thin::-webkit-scrollbar-track {
  background: transparent;
}

.scrollbar-thin::-webkit-scrollbar-thumb {
  @apply bg-gray-300 dark:bg-gpt-dark-400 rounded-full;
}

.scrollbar-thin::-webkit-scrollbar-thumb:hover {
  @apply bg-gray-400 dark:bg-gpt-dark-300;
}
</style>
