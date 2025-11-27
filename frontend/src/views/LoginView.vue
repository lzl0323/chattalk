<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <!-- Logo 和标题 -->
      <div class="text-center">
        <h1 class="text-4xl font-bold text-gray-900 mb-2">💬 AI Chat</h1>
        <h2 class="text-2xl font-semibold text-gray-700">
          {{ isLoginMode ? '登录' : '注册' }}
        </h2>
        <p class="mt-2 text-sm text-gray-600">
          {{ isLoginMode ? '欢迎回来！' : '创建您的账户' }}
        </p>
      </div>

      <!-- 表单 -->
      <div class="mt-8 bg-white py-8 px-6 shadow-xl rounded-lg">
        <form @submit.prevent="handleSubmit" class="space-y-6">
          <!-- 错误提示 -->
          <div v-if="authError" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            <p class="text-sm">{{ authError }}</p>
          </div>

          <!-- 邮箱输入 -->
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700 mb-2">
              邮箱地址
            </label>
            <input
              id="email"
              v-model="form.email"
              type="email"
              required
              autocomplete="email"
              class="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              placeholder="your@email.com"
              :disabled="isLoading"
            />
          </div>

          <!-- 密码输入 -->
          <div>
            <label for="password" class="block text-sm font-medium text-gray-700 mb-2">
              密码
            </label>
            <input
              id="password"
              v-model="form.password"
              type="password"
              required
              autocomplete="current-password"
              class="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              :placeholder="isLoginMode ? '输入密码' : '至少6个字符'"
              :disabled="isLoading"
            />
            <p v-if="!isLoginMode" class="mt-1 text-xs text-gray-500">
              密码长度至少6个字符
            </p>
          </div>

          <!-- 确认密码（仅注册时显示） -->
          <div v-if="!isLoginMode">
            <label for="confirmPassword" class="block text-sm font-medium text-gray-700 mb-2">
              确认密码
            </label>
            <input
              id="confirmPassword"
              v-model="form.confirmPassword"
              type="password"
              required
              autocomplete="new-password"
              class="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              placeholder="再次输入密码"
              :disabled="isLoading"
            />
          </div>

          <!-- 提交按钮 -->
          <div>
            <button
              type="submit"
              :disabled="isLoading"
              class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <span v-if="!isLoading">{{ isLoginMode ? '登录' : '注册' }}</span>
              <span v-else class="flex items-center">
                <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                处理中...
              </span>
            </button>
          </div>
        </form>

        <!-- 切换登录/注册 -->
        <div class="mt-6 text-center">
          <button
            @click="toggleMode"
            class="text-sm text-blue-600 hover:text-blue-500 font-medium"
            :disabled="isLoading"
          >
            {{ isLoginMode ? '还没有账户？立即注册' : '已有账户？立即登录' }}
          </button>
        </div>
      </div>

      <!-- 提示信息 -->
      <p class="text-center text-xs text-gray-500">
        继续使用即表示您同意我们的服务条款和隐私政策
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

const router = useRouter()
const authStore = useAuthStore()

const isLoginMode = ref(true)
const form = ref({
  email: '',
  password: '',
  confirmPassword: ''
})

// 计算属性
const isLoading = computed(() => authStore.isLoading)
const authError = computed(() => authStore.error)

function toggleMode() {
  isLoginMode.value = !isLoginMode.value
  authStore.error = null
  form.value = {
    email: '',
    password: '',
    confirmPassword: ''
  }
}

async function handleSubmit() {
  authStore.error = null
  
  // 注册时验证密码一致性
  if (!isLoginMode.value && form.value.password !== form.value.confirmPassword) {
    authStore.error = '两次输入的密码不一致'
    return
  }
  
  // 验证密码长度
  if (!isLoginMode.value && form.value.password.length < 6) {
    authStore.error = '密码长度至少6个字符'
    return
  }
  
  try {
    if (isLoginMode.value) {
      await authStore.login(form.value.email, form.value.password)
    } else {
      await authStore.register(form.value.email, form.value.password)
    }
    
    // 登录/注册成功，跳转到聊天页面
    router.push('/')
  } catch (error) {
    // 错误已由 authStore 处理
    console.error('Authentication failed:', error)
  }
}
</script>

<style scoped>
/* 自定义样式（如果需要） */
</style>
