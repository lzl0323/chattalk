<template>
  <div class="h-full flex flex-col bg-white dark:bg-gpt-dark-700">
    <!-- 顶部栏 -->
    <div class="flex-shrink-0 flex items-center pl-14 pr-4 py-3 border-b border-gray-200 dark:border-gpt-dark-400 gap-3">
      <div class="flex items-center gap-3 flex-1">
        <button
          @click="$router.push('/')"
          class="p-2 hover:bg-gray-100 dark:hover:bg-gpt-dark-600 rounded-lg transition-colors"
          title="返回聊天"
        >
          <svg class="w-5 h-5 text-gray-700 dark:text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
        </button>
        <h1 class="text-lg font-semibold text-gray-900 dark:text-gray-100">AI 模型管理</h1>
      </div>
      
      <button
        @click="showCreateModal = true"
        class="flex items-center gap-2 px-3 py-2 bg-gpt-green-500 text-white rounded-lg hover:bg-gpt-green-600 transition-colors text-sm"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        <span>添加模型</span>
      </button>
    </div>

    <!-- 主内容区 -->
    <div class="flex-1 overflow-y-auto">
      <div class="max-w-7xl mx-auto px-6 py-8">
      <!-- 加载中 -->
      <div v-if="loading" class="text-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p class="mt-4 text-gray-600">加载中...</p>
      </div>

      <!-- 模型列表 -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="model in models"
          :key="model.id"
          class="bg-white dark:bg-gpt-dark-800 rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow border border-gray-200 dark:border-gpt-dark-600"
        >
          <!-- 模型头部 -->
          <div class="flex items-start justify-between mb-4">
            <div class="flex-1">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-1">
                {{ model.name }}
              </h3>
              <p class="text-sm text-gray-500 dark:text-gray-400">{{ model.model }}</p>
            </div>
            
            <!-- 状态徽章 -->
            <span
              v-if="model.is_active"
              class="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded"
            >
              激活
            </span>
            <span
              v-else
              class="px-2 py-1 text-xs font-medium bg-red-100 text-red-800 rounded"
            >
              禁用
            </span>
          </div>

          <!-- API 信息 -->
          <div class="space-y-2 mb-4">
            <div class="flex items-center text-sm">
              <span class="text-gray-500 w-20">API:</span>
              <span class="text-gray-700 truncate">{{ model.api_base }}</span>
            </div>
            <div class="flex items-center text-sm">
              <span class="text-gray-500 w-20">Key:</span>
              <code class="text-gray-700 bg-gray-100 px-2 py-0.5 rounded text-xs">
                {{ model.api_key_masked }}
              </code>
            </div>
          </div>

          <!-- 描述 -->
          <p v-if="model.description" class="text-sm text-gray-600 mb-4">
            {{ model.description }}
          </p>

          <!-- 配额信息 -->
          <div class="mb-4">
            <div class="flex justify-between text-sm mb-1">
              <span class="text-gray-600">配额使用</span>
              <span 
                class="font-medium"
                :class="{
                  'text-green-600': model.quota_percentage < 50,
                  'text-yellow-600': model.quota_percentage >= 50 && model.quota_percentage < 80,
                  'text-red-600': model.quota_percentage >= 80
                }"
              >
                {{ model.quota_percentage.toFixed(1) }}%
              </span>
            </div>
            
            <!-- 进度条 -->
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div
                class="h-2 rounded-full transition-all"
                :class="{
                  'bg-green-500': model.quota_percentage < 50,
                  'bg-yellow-500': model.quota_percentage >= 50 && model.quota_percentage < 80,
                  'bg-red-500': model.quota_percentage >= 80
                }"
                :style="{ width: model.quota_percentage + '%' }"
              ></div>
            </div>
            
            <div class="flex justify-between text-xs text-gray-500 mt-1">
              <span>已用: {{ formatNumber(model.quota_used) }}</span>
              <span>剩余: {{ formatNumber(model.quota_remaining) }}</span>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="flex items-center space-x-2">
            <button
              @click="editModel(model)"
              class="flex-1 px-3 py-2 text-sm text-blue-600 border border-blue-600 rounded-lg hover:bg-blue-50 transition-colors"
            >
              编辑
            </button>
            <button
              @click="resetQuota(model)"
              class="flex-1 px-3 py-2 text-sm text-green-600 border border-green-600 rounded-lg hover:bg-green-50 transition-colors"
              :disabled="model.quota_used === 0"
            >
              重置配额
            </button>
            <button
              @click="deleteModel(model)"
              class="px-3 py-2 text-sm text-red-600 border border-red-600 rounded-lg hover:bg-red-50 transition-colors"
            >
              删除
            </button>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-if="models.length === 0" class="col-span-full text-center py-12">
          <svg class="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
          <p class="text-gray-600">还没有配置任何模型</p>
          <button
            @click="showCreateModal = true"
            class="mt-4 text-blue-600 hover:text-blue-700"
          >
            添加第一个模型 →
          </button>
        </div>
      </div>
      </div>
    </div>

    <!-- 创建/编辑模态框 -->
    <div
      v-if="showCreateModal || editingModel"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="closeModal"
    >
      <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <h2 class="text-2xl font-bold text-gray-900 mb-6">
            {{ editingModel ? '编辑模型' : '添加新模型' }}
          </h2>

          <form @submit.prevent="saveModel" class="space-y-4">
            <!-- 名称 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                模型名称 <span class="text-red-500">*</span>
              </label>
              <input
                v-model="formData.name"
                type="text"
                required
                placeholder="例如: GPT-4"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <!-- 模型标识 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                模型标识 <span class="text-red-500">*</span>
              </label>
              <input
                v-model="formData.model"
                type="text"
                required
                placeholder="例如: gpt-4, deepseek-chat"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <!-- API 地址 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                API 地址 <span class="text-red-500">*</span>
              </label>
              <input
                v-model="formData.api_base"
                type="url"
                required
                placeholder="https://api.openai.com/v1"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <!-- API Key -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                API Key <span class="text-red-500">*</span>
              </label>
              <input
                v-model="formData.api_key"
                type="password"
                :required="!editingModel"
                placeholder="sk-..."
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <p v-if="editingModel" class="text-xs text-gray-500 mt-1">
                留空则不更新 API Key
              </p>
            </div>

            <!-- 描述 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                描述
              </label>
              <textarea
                v-model="formData.description"
                rows="3"
                placeholder="模型的简短描述..."
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              ></textarea>
            </div>

            <!-- 配额限制 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                配额限制 (tokens)
              </label>
              <input
                v-model.number="formData.quota_limit"
                type="number"
                min="0"
                step="1000"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <!-- 按钮 -->
            <div class="flex items-center space-x-3 pt-4">
              <button
                type="submit"
                :disabled="saving"
                class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                {{ saving ? '保存中...' : '保存' }}
              </button>
              <button
                type="button"
                @click="closeModal"
                class="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
              >
                取消
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  getModelConfigs,
  createModelConfig,
  updateModelConfig,
  deleteModelConfig,
  resetModelQuota
} from '../services/api'

const router = useRouter()

const models = ref([])
const loading = ref(true)
const showCreateModal = ref(false)
const editingModel = ref(null)
const saving = ref(false)

const formData = ref({
  name: '',
  model: '',
  api_base: '',
  api_key: '',
  description: '',
  quota_limit: 1000000
})

// 加载模型列表
async function loadModels() {
  try {
    loading.value = true
    const response = await getModelConfigs(0, 100, false)
    models.value = response.items
  } catch (error) {
    console.error('Failed to load models:', error)
    alert('加载模型列表失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 格式化数字
function formatNumber(num) {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toFixed(0)
}

// 编辑模型
function editModel(model) {
  editingModel.value = model
  formData.value = {
    name: model.name,
    model: model.model,
    api_base: model.api_base,
    api_key: '',
    description: model.description || '',
    quota_limit: model.quota_limit
  }
}

// 保存模型
async function saveModel() {
  try {
    saving.value = true
    
    const data = { ...formData.value }
    
    // 如果是编辑且没有填写 API Key，则删除该字段
    if (editingModel.value && !data.api_key) {
      delete data.api_key
    }
    
    if (editingModel.value) {
      await updateModelConfig(editingModel.value.id, data)
    } else {
      await createModelConfig(data)
    }
    
    await loadModels()
    closeModal()
  } catch (error) {
    console.error('Failed to save model:', error)
    alert('保存失败: ' + error.message)
  } finally {
    saving.value = false
  }
}

// 删除模型
async function deleteModel(model) {
  if (!confirm(`确定要删除模型 "${model.name}" 吗？`)) {
    return
  }
  
  try {
    await deleteModelConfig(model.id)
    await loadModels()
  } catch (error) {
    console.error('Failed to delete model:', error)
    alert('删除失败: ' + error.message)
  }
}

// 重置配额
async function resetQuota(model) {
  if (!confirm(`确定要重置模型 "${model.name}" 的配额吗？`)) {
    return
  }
  
  try {
    await resetModelQuota(model.id, 0)
    await loadModels()
  } catch (error) {
    console.error('Failed to reset quota:', error)
    alert('重置配额失败: ' + error.message)
  }
}

// 关闭模态框
function closeModal() {
  showCreateModal.value = false
  editingModel.value = null
  formData.value = {
    name: '',
    model: '',
    api_base: '',
    api_key: '',
    description: '',
    quota_limit: 1000000
  }
}

onMounted(() => {
  loadModels()
})
</script>

<style scoped>
/* 平滑过渡 */
.transition-all {
  transition: all 0.3s ease;
}
</style>
