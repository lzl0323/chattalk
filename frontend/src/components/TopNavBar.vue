<template>
  <header class="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between shadow-sm">
    <!-- 左侧：折叠按钮 + Logo -->
    <div class="flex items-center space-x-4">
      <button
        @click="$emit('toggle-sidebar')"
        class="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        title="切换侧边栏"
      >
        <svg class="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>
      
      <div class="flex items-center space-x-3">
        <div class="w-8 h-8 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
        </div>
        <h1 class="text-xl font-semibold text-gray-800">AI Chat</h1>
      </div>
    </div>

    <!-- 右侧：用户信息 -->
    <div class="flex items-center space-x-4">
      <!-- 用户菜单 -->
      <div class="relative">
        <button
          @click="showMenu = !showMenu"
          class="flex items-center space-x-3 p-2 hover:bg-gray-100 rounded-lg transition-colors"
          @blur="handleBlur"
        >
          <!-- 用户头像 -->
          <div 
            class="w-9 h-9 rounded-full flex items-center justify-center text-white font-semibold text-sm"
            :style="{ backgroundColor: avatarColor }"
          >
            {{ userInitial }}
          </div>
          
          <!-- 下拉箭头 -->
          <svg 
            class="w-4 h-4 text-gray-600 transition-transform"
            :class="{ 'rotate-180': showMenu }"
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        <!-- 下拉菜单 -->
        <div
          v-if="showMenu"
          class="absolute right-0 mt-2 w-64 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-50"
        >
          <!-- 用户信息 -->
          <div class="px-4 py-3 border-b border-gray-100">
            <div class="flex items-center space-x-3">
              <div 
                class="w-10 h-10 rounded-full flex items-center justify-center text-white font-semibold"
                :style="{ backgroundColor: avatarColor }"
              >
                {{ userInitial }}
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-900 truncate">
                  {{ currentUser?.email }}
                </p>
                <p class="text-xs text-gray-500">
                  已登录
                </p>
              </div>
            </div>
          </div>

          <!-- 菜单项 -->
          <div class="py-1">
            <button
              @click="goToModelConfig"
              class="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center space-x-3"
            >
              <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
              <span>模型管理</span>
            </button>
            
            <button
              @click="handleChangeAvatar"
              class="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center space-x-3"
            >
              <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              <span>更换头像</span>
            </button>
            
            <button
              class="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center space-x-3"
            >
              <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              <span>设置</span>
            </button>
          </div>

          <!-- 退出登录 -->
          <div class="border-t border-gray-100 py-1">
            <button
              @click="handleLogout"
              class="w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-red-50 flex items-center space-x-3"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              <span>退出登录</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { currentUser, logout } from '../stores/userStore'
import { reset as resetConversations } from '../stores/conversationStore'

defineEmits(['toggle-sidebar', 'new-conversation'])

const router = useRouter()
const showMenu = ref(false)

// 用户首字母
const userInitial = computed(() => {
  if (!currentUser.value?.email) return '?'
  return currentUser.value.email[0].toUpperCase()
})

// 根据邮箱生成随机颜色
const avatarColor = computed(() => {
  if (!currentUser.value?.email) return '#6366f1'
  
  // 使用邮箱生成一致的颜色
  const colors = [
    '#ef4444', '#f59e0b', '#10b981', '#3b82f6', 
    '#6366f1', '#8b5cf6', '#ec4899', '#14b8a6',
    '#f97316', '#84cc16', '#06b6d4', '#6366f1'
  ]
  
  let hash = 0
  for (let i = 0; i < currentUser.value.email.length; i++) {
    hash = currentUser.value.email.charCodeAt(i) + ((hash << 5) - hash)
  }
  
  return colors[Math.abs(hash) % colors.length]
})

function handleBlur(event) {
  // 延迟关闭，以便点击菜单项
  setTimeout(() => {
    if (!event.currentTarget.contains(document.activeElement)) {
      showMenu.value = false
    }
  }, 200)
}

function goToModelConfig() {
  showMenu.value = false
  router.push('/models')
}

function handleChangeAvatar() {
  showMenu.value = false
  alert('更换头像功能开发中...\n\n后续版本将支持：\n- 上传自定义头像\n- 选择预设头像\n- 使用 Gravatar')
}

async function handleLogout() {
  showMenu.value = false
  
  if (confirm('确定要退出登录吗？')) {
    await logout()
    resetConversations()
    router.push('/login')
  }
}
</script>

<style scoped>
/* 下拉菜单动画 */
</style>
