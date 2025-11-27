<template>
  <div class="h-screen flex overflow-hidden bg-white dark:bg-gpt-dark-700 transition-colors duration-200">
    <!-- 展开侧边栏按钮（侧边栏关闭时显示） -->
    <Transition name="fade">
      <button
        v-if="!isSidebarOpen"
        @click="toggleSidebar"
        class="fixed left-2 top-2 z-[60] p-2.5 rounded-lg
               bg-white dark:bg-gpt-dark-800
               border border-gray-200 dark:border-gpt-dark-600
               hover:bg-gray-50 dark:hover:bg-gpt-dark-700
               shadow-md hover:shadow-lg
               transition-all duration-200"
        title="展开侧边栏"
      >
        <svg class="w-5 h-5 text-gray-700 dark:text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>
    </Transition>
    
    <!-- 侧边栏 -->
    <Sidebar 
      :is-open="isSidebarOpen"
      @close="closeSidebar"
    />
    
    <!-- 主内容区 -->
    <div 
      class="flex-1 flex flex-col overflow-hidden transition-all duration-300"
      :style="{ marginLeft: isSidebarOpen ? '0px' : '0px' }"
    >
      <!-- 路由内容 -->
      <main class="flex-1 overflow-hidden">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
    
    <!-- Toast 通知容器 -->
    <Teleport to="body">
      <div class="fixed bottom-4 right-4 z-50 flex flex-col gap-2">
        <TransitionGroup name="toast">
          <div
            v-for="toast in toasts"
            :key="toast.id"
            :class="[
              'toast',
              `toast-${toast.type}`,
              'min-w-[300px] max-w-md'
            ]"
          >
            <div class="flex items-center gap-3">
              <!-- 图标 -->
              <div class="flex-shrink-0">
                <svg v-if="toast.type === 'success'" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                </svg>
                <svg v-else-if="toast.type === 'error'" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                </svg>
                <svg v-else-if="toast.type === 'warning'" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                </svg>
                <svg v-else class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                </svg>
              </div>
              
              <!-- 消息 -->
              <p class="flex-1">{{ toast.message }}</p>
              
              <!-- 关闭按钮 -->
              <button
                @click="removeToast(toast.id)"
                class="flex-shrink-0 hover:opacity-75 transition-opacity"
              >
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </button>
            </div>
          </div>
        </TransitionGroup>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, onMounted, provide } from 'vue'
import { useThemeStore } from '@/stores/themeStore'
import Sidebar from './Sidebar.vue'

// Store
const themeStore = useThemeStore()

// 侧边栏状态（桌面端默认打开，移动端默认关闭）
const isSidebarOpen = ref(window.innerWidth >= 1024)

const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value
}

const closeSidebar = () => {
  isSidebarOpen.value = false
}

// Toast 通知系统
const toasts = ref([])
let toastId = 0

const showToast = (message, type = 'info', duration = 3000) => {
  const id = toastId++
  const toast = { id, message, type }
  
  toasts.value.push(toast)
  
  if (duration > 0) {
    setTimeout(() => {
      removeToast(id)
    }, duration)
  }
  
  return id
}

const removeToast = (id) => {
  const index = toasts.value.findIndex(t => t.id === id)
  if (index > -1) {
    toasts.value.splice(index, 1)
  }
}

// 提供给子组件使用
provide('showToast', showToast)
provide('toggleSidebar', toggleSidebar)

// 初始化
onMounted(() => {
  themeStore.initTheme()
})
</script>

<style scoped>
/* 页面切换动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Toast 动画 */
.toast-enter-active {
  animation: slideIn 0.3s ease-out;
}

.toast-leave-active {
  animation: slideOut 0.3s ease-in;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@keyframes slideOut {
  from {
    transform: translateX(0);
    opacity: 1;
  }
  to {
    transform: translateX(100%);
    opacity: 0;
  }
}
</style>
