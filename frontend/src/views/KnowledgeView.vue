<template>
  <div class="h-full flex flex-col bg-gray-50 dark:bg-gpt-dark-700">
    <!-- 顶部栏 -->
    <div class="flex-shrink-0 bg-white dark:bg-gpt-dark-800 border-b border-gray-200 dark:border-gpt-dark-600 px-6 py-4">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-gray-900 dark:text-white">📚 知识库管理</h1>
          <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">管理你的文档，让 AI 更智能</p>
        </div>
        
        <button
          @click="showCreateDialog = true"
          class="px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:shadow-lg transition-all flex items-center gap-2"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          新建知识库
        </button>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="flex-1 overflow-hidden flex">
      <!-- 左侧：知识库列表 -->
      <div class="w-80 bg-white dark:bg-gpt-dark-800 border-r border-gray-200 dark:border-gpt-dark-600 overflow-y-auto">
        <div class="p-4">
          <h2 class="text-sm font-semibold text-gray-500 dark:text-gray-400 mb-3">我的知识库</h2>
          
          <!-- 加载中 -->
          <div v-if="loading" class="space-y-3">
            <div v-for="i in 3" :key="i" class="animate-pulse">
              <div class="h-20 bg-gray-200 dark:bg-gpt-dark-600 rounded-lg"></div>
            </div>
          </div>
          
          <!-- 知识库列表 -->
          <div v-else-if="knowledgeBases.length > 0" class="space-y-2">
            <div
              v-for="kb in knowledgeBases"
              :key="kb.id"
              :class="[
                'p-4 rounded-lg transition-all',
                selectedKB?.id === kb.id
                  ? 'bg-purple-50 dark:bg-purple-900/20 border-2 border-purple-500'
                  : 'bg-gray-50 dark:bg-gpt-dark-700 border-2 border-transparent'
              ]"
            >
              <div class="flex items-start justify-between">
                <div 
                  class="flex-1 min-w-0 cursor-pointer"
                  @click="selectKnowledgeBase(kb)"
                >
                  <h3 class="font-semibold text-gray-900 dark:text-white truncate">
                    {{ kb.name }}
                  </h3>
                  <p class="text-xs text-gray-500 dark:text-gray-400 mt-1 truncate">
                    {{ kb.description || '暂无描述' }}
                  </p>
                  <div class="flex items-center gap-3 mt-2 text-xs text-gray-500">
                    <span>📄 {{ kb.document_count }} 个文档</span>
                    <span>🧩 {{ kb.total_chunks }} 个片段</span>
                  </div>
                </div>
                
                <!-- 删除按钮 -->
                <button
                  @click.stop="confirmDeleteKB(kb)"
                  class="p-1.5 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded transition-colors flex-shrink-0"
                  title="删除知识库"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
          
          <!-- 空状态 -->
          <div v-else class="text-center py-12">
            <svg class="w-16 h-16 mx-auto text-gray-300 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p class="text-gray-500 dark:text-gray-400 mt-4">还没有知识库</p>
            <button
              @click="showCreateDialog = true"
              class="mt-4 text-purple-600 dark:text-purple-400 hover:underline"
            >
              创建第一个知识库
            </button>
          </div>
        </div>
      </div>

      <!-- 右侧：文档管理 -->
      <div class="flex-1 overflow-y-auto p-6">
        <!-- 未选择知识库 -->
        <div v-if="!selectedKB" class="flex items-center justify-center h-full">
          <div class="text-center">
            <svg class="w-24 h-24 mx-auto text-gray-300 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
            <h3 class="text-xl font-semibold text-gray-700 dark:text-gray-300 mt-6">选择一个知识库</h3>
            <p class="text-gray-500 dark:text-gray-400 mt-2">在左侧选择或创建一个知识库来管理文档</p>
          </div>
        </div>

        <!-- 已选择知识库 -->
        <div v-else>
          <!-- 知识库信息 -->
          <div class="bg-white dark:bg-gpt-dark-800 rounded-lg p-6 mb-6 shadow-sm">
            <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-2">{{ selectedKB.name }}</h2>
            <p class="text-gray-600 dark:text-gray-400 mb-4">{{ selectedKB.description }}</p>
            <div class="flex items-center gap-6 text-sm">
              <span class="text-gray-600 dark:text-gray-400">
                📄 <strong>{{ selectedKB.document_count }}</strong> 个文档
              </span>
              <span class="text-gray-600 dark:text-gray-400">
                🧩 <strong>{{ selectedKB.total_chunks }}</strong> 个片段
              </span>
              <span class="text-gray-600 dark:text-gray-400">
                📅 创建于 {{ formatDate(selectedKB.created_at) }}
              </span>
            </div>
          </div>

          <!-- 上传区域 -->
          <div
            @drop.prevent="handleDrop"
            @dragover.prevent="isDragging = true"
            @dragleave="isDragging = false"
            :class="[
              'border-2 border-dashed rounded-lg p-8 mb-6 text-center transition-all',
              isDragging
                ? 'border-purple-500 bg-purple-50 dark:bg-purple-900/20'
                : 'border-gray-300 dark:border-gray-600 hover:border-purple-400 dark:hover:border-purple-500'
            ]"
          >
            <input
              ref="fileInput"
              type="file"
              multiple
              accept=".txt,.md,.markdown,.pdf"
              @change="handleFileSelect"
              class="hidden"
            />
            
            <svg class="w-12 h-12 mx-auto text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            
            <p class="text-gray-700 dark:text-gray-300 font-medium mt-4">
              拖拽文件到这里，或
              <button
                @click="$refs.fileInput.click()"
                class="text-purple-600 dark:text-purple-400 hover:underline"
              >
                点击选择
              </button>
            </p>
            <p class="text-sm text-gray-500 dark:text-gray-400 mt-2">
              支持 TXT, MD, PDF 格式（最大 10MB）
            </p>
          </div>

          <!-- 上传进度 -->
          <div v-if="uploadingFiles.length > 0" class="mb-6 space-y-2">
            <div
              v-for="(file, index) in uploadingFiles"
              :key="index"
              class="bg-white dark:bg-gpt-dark-800 rounded-lg p-4 shadow-sm"
            >
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-medium text-gray-900 dark:text-white">{{ file.name }}</span>
                <span class="text-xs text-gray-500">{{ file.progress }}%</span>
              </div>
              <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div
                  class="bg-purple-600 h-2 rounded-full transition-all"
                  :style="{ width: file.progress + '%' }"
                ></div>
              </div>
            </div>
          </div>

          <!-- 文档列表 -->
          <div>
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">文档列表</h3>
            
            <!-- 加载中 -->
            <div v-if="loadingDocs" class="space-y-3">
              <div v-for="i in 3" :key="i" class="animate-pulse">
                <div class="h-16 bg-gray-200 dark:bg-gpt-dark-700 rounded-lg"></div>
              </div>
            </div>
            
            <!-- 文档卡片 -->
            <div v-else-if="documents.length > 0" class="space-y-3">
              <div
                v-for="doc in documents"
                :key="doc.id"
                class="bg-white dark:bg-gpt-dark-800 rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow"
              >
                <div class="flex items-start justify-between">
                  <div class="flex items-start gap-3 flex-1">
                    <div class="text-3xl">📄</div>
                    <div class="flex-1 min-w-0">
                      <h4 class="font-medium text-gray-900 dark:text-white truncate">{{ doc.file_name }}</h4>
                      <div class="flex items-center gap-4 mt-1 text-xs text-gray-500 dark:text-gray-400">
                        <span>🧩 {{ doc.chunk_count }} 个片段</span>
                        <span>📅 {{ formatDate(doc.created_at) }}</span>
                        <span
                          :class="[
                            'px-2 py-0.5 rounded',
                            doc.status === 'completed'
                              ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
                              : doc.status === 'failed'
                              ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
                              : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400'
                          ]"
                        >
                          {{ getStatusText(doc.status) }}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <button
                    @click="deleteDocument(doc)"
                    class="p-2 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                    title="删除文档"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
            
            <!-- 空状态 -->
            <div v-else class="text-center py-12 bg-white dark:bg-gpt-dark-800 rounded-lg">
              <svg class="w-16 h-16 mx-auto text-gray-300 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <p class="text-gray-500 dark:text-gray-400 mt-4">还没有文档</p>
              <p class="text-sm text-gray-400 dark:text-gray-500 mt-1">拖拽文件到上方上传区域</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 创建知识库对话框 -->
    <div
      v-if="showCreateDialog"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      @click.self="showCreateDialog = false"
    >
      <div class="bg-white dark:bg-gpt-dark-800 rounded-lg p-6 w-full max-w-md shadow-xl">
        <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-4">创建新知识库</h3>
        
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              知识库名称 *
            </label>
            <input
              v-model="newKB.name"
              type="text"
              placeholder="例如：技术文档库"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white dark:bg-gpt-dark-700 text-gray-900 dark:text-white"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              描述（可选）
            </label>
            <textarea
              v-model="newKB.description"
              rows="3"
              placeholder="简单描述这个知识库的用途..."
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white dark:bg-gpt-dark-700 text-gray-900 dark:text-white resize-none"
            ></textarea>
          </div>
        </div>
        
        <div class="flex justify-end gap-3 mt-6">
          <button
            @click="showCreateDialog = false"
            class="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gpt-dark-700 rounded-lg transition-colors"
          >
            取消
          </button>
          <button
            @click="createKnowledgeBase"
            :disabled="!newKB.name.trim() || creating"
            class="px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ creating ? '创建中...' : '创建' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, inject } from 'vue'
import { ragAPI } from '@/services/api'

const showToast = inject('showToast', null)

// 状态
const loading = ref(false)
const loadingDocs = ref(false)
const knowledgeBases = ref([])
const selectedKB = ref(null)
const documents = ref([])
const isDragging = ref(false)
const uploadingFiles = ref([])

// 创建对话框
const showCreateDialog = ref(false)
const creating = ref(false)
const newKB = ref({
  name: '',
  description: ''
})

const fileInput = ref(null)

// 加载知识库列表
const loadKnowledgeBases = async () => {
  loading.value = true
  try {
    knowledgeBases.value = await ragAPI.getKnowledgeBases()
  } catch (error) {
    showToast?.('加载失败：' + error.message, 'error')
  } finally {
    loading.value = false
  }
}

// 选择知识库
const selectKnowledgeBase = async (kb) => {
  selectedKB.value = kb
  await loadDocuments(kb.id)
}

// 加载文档列表
const loadDocuments = async (kbId) => {
  loadingDocs.value = true
  try {
    documents.value = await ragAPI.getDocuments(kbId)
  } catch (error) {
    showToast?.('加载文档失败：' + error.message, 'error')
  } finally {
    loadingDocs.value = false
  }
}

// 创建知识库
const createKnowledgeBase = async () => {
  if (!newKB.value.name.trim()) return
  
  creating.value = true
  try {
    await ragAPI.createKnowledgeBase(newKB.value.name, newKB.value.description)
    showToast?.('知识库创建成功！', 'success')
    showCreateDialog.value = false
    newKB.value = { name: '', description: '' }
    await loadKnowledgeBases()
  } catch (error) {
    showToast?.('创建失败：' + error.message, 'error')
  } finally {
    creating.value = false
  }
}

// 文件选择
const handleFileSelect = (event) => {
  const files = Array.from(event.target.files)
  uploadFiles(files)
  event.target.value = ''
}

// 拖拽上传
const handleDrop = (event) => {
  isDragging.value = false
  const files = Array.from(event.dataTransfer.files)
  uploadFiles(files)
}

// 上传文件
const uploadFiles = async (files) => {
  if (!selectedKB.value) {
    showToast?.('请先选择知识库', 'warning')
    return
  }
  
  for (const file of files) {
    const uploadingFile = {
      name: file.name,
      progress: 0
    }
    uploadingFiles.value.push(uploadingFile)
    
    try {
      // 模拟进度
      const interval = setInterval(() => {
        if (uploadingFile.progress < 90) {
          uploadingFile.progress += 10
        }
      }, 200)
      
      await ragAPI.uploadDocument(selectedKB.value.id, file)
      
      clearInterval(interval)
      uploadingFile.progress = 100
      
      setTimeout(() => {
        uploadingFiles.value = uploadingFiles.value.filter(f => f !== uploadingFile)
      }, 1000)
      
      showToast?.(`${file.name} 上传成功！`, 'success')
      
      // 刷新文档列表和知识库信息
      await loadDocuments(selectedKB.value.id)
      await loadKnowledgeBases()
      // 更新当前选中的知识库信息
      selectedKB.value = knowledgeBases.value.find(kb => kb.id === selectedKB.value.id)
      
    } catch (error) {
      uploadingFiles.value = uploadingFiles.value.filter(f => f !== uploadingFile)
      showToast?.(`${file.name} 上传失败：${error.message}`, 'error')
    }
  }
}

// 确认删除知识库
const confirmDeleteKB = (kb) => {
  if (confirm(`确定要删除知识库「${kb.name}」吗？\n\n⚠️ 这将删除该知识库下的所有文档和向量数据，且无法恢复！`)) {
    deleteKnowledgeBase(kb)
  }
}

// 删除知识库
const deleteKnowledgeBase = async (kb) => {
  try {
    await ragAPI.deleteKnowledgeBase(kb.id)
    showToast?.(`知识库「${kb.name}」已删除`, 'success')
    
    // 如果删除的是当前选中的知识库，清空选择
    if (selectedKB.value?.id === kb.id) {
      selectedKB.value = null
      documents.value = []
    }
    
    // 重新加载知识库列表
    await loadKnowledgeBases()
  } catch (error) {
    showToast?.('删除失败：' + error.message, 'error')
  }
}

// 删除文档
const deleteDocument = async (doc) => {
  if (!confirm(`确定要删除文档「${doc.file_name}」吗？`)) return
  
  try {
    await ragAPI.deleteDocument(selectedKB.value.id, doc.id)
    showToast?.('文档删除成功', 'success')
    await loadDocuments(selectedKB.value.id)
    await loadKnowledgeBases()
    selectedKB.value = knowledgeBases.value.find(kb => kb.id === selectedKB.value.id)
  } catch (error) {
    showToast?.('删除失败：' + error.message, 'error')
  }
}

// 格式化日期
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

// 获取状态文本
const getStatusText = (status) => {
  const statusMap = {
    completed: '已完成',
    processing: '处理中',
    failed: '失败',
    pending: '等待中'
  }
  return statusMap[status] || status
}

// 初始化
onMounted(() => {
  loadKnowledgeBases()
})
</script>

<style scoped>
/* 自定义样式 */
</style>
