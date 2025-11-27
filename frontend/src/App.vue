<template>
  <!-- ChatGPT 风格布局 -->
  <AppLayout v-if="showLayout" />
  
  <!-- 登录页面（无布局） -->
  <router-view v-else />
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import AppLayout from '@/components/layout/AppLayout.vue'

const route = useRoute()
const authStore = useAuthStore()

// 登录页不显示布局
const showLayout = computed(() => route.name !== 'Login')

// 初始化时检查登录状态
onMounted(() => {
  // 如果有 token，恢复登录状态
  if (authStore.token) {
    authStore.checkAuth().catch(() => {
      // Token 无效，忽略错误
    })
  }
})
</script>
