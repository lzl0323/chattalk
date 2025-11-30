<template>
  <div class="file-upload-container">
    <!-- OCR 模式选择器 -->
    <div v-if="showModeSelector" class="ocr-mode-selector">
      <div class="mode-header">
        <h3>选择 OCR 模式</h3>
        <button @click="showModeSelector = false" class="close-btn">✕</button>
      </div>
      <div class="mode-grid">
        <button
          v-for="mode in ocrModes"
          :key="mode.value"
          @click="selectMode(mode.value)"
          :class="['mode-card', { active: selectedMode === mode.value }]"
        >
          <span class="mode-icon">{{ mode.icon }}</span>
          <span class="mode-label">{{ mode.label }}</span>
          <span class="mode-desc">{{ mode.description }}</span>
        </button>
      </div>
    </div>

    <!-- 文件上传按钮 -->
    <button
      @click="triggerFileUpload"
      :disabled="uploading"
      class="upload-btn"
      title="上传图片或 PDF"
    >
      <svg v-if="!uploading" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
              d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
      </svg>
      <div v-else class="spinner"></div>
    </button>

    <!-- 隐藏的文件输入 -->
    <input
      ref="fileInput"
      type="file"
      accept="image/jpeg,image/jpg,image/png,application/pdf"
      @change="handleFileSelect"
      style="display: none"
    />

    <!-- 上传进度提示 -->
    <div v-if="uploading" class="upload-progress">
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: `${uploadProgress}%` }"></div>
      </div>
      <span class="progress-text">正在识别... {{ uploadProgress }}%</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ocrAPI } from '@/services/api'
import { useToast } from '@/composables/useToast'

const emit = defineEmits(['upload-success', 'upload-error'])

const fileInput = ref(null)
const uploading = ref(false)
const uploadProgress = ref(0)
const showModeSelector = ref(false)
const selectedMode = ref('markdown')
const ocrModes = ref([])
const pendingFile = ref(null)

const { showToast } = useToast()

// 获取 OCR 模式列表
onMounted(async () => {
  try {
    const response = await ocrAPI.getModes()
    ocrModes.value = response.modes
  } catch (error) {
    console.error('Failed to load OCR modes:', error)
  }
})

// 触发文件选择
const triggerFileUpload = () => {
  if (!uploading.value) {
    fileInput.value?.click()
  }
}

// 文件选择处理
const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (!file) return

  // 验证文件大小 (最大 10MB)
  if (file.size > 10 * 1024 * 1024) {
    showToast('文件大小不能超过 10MB', 'error')
    return
  }

  // 验证文件类型
  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf']
  if (!allowedTypes.includes(file.type)) {
    showToast('只支持 JPG、PNG 和 PDF 文件', 'error')
    return
  }

  // 保存文件并显示模式选择器
  pendingFile.value = file
  showModeSelector.value = true
}

// 选择 OCR 模式
const selectMode = (mode) => {
  selectedMode.value = mode
  showModeSelector.value = false
  
  if (pendingFile.value) {
    uploadFile(pendingFile.value, mode)
  }
}

// 上传文件
const uploadFile = async (file, mode) => {
  uploading.value = true
  uploadProgress.value = 0

  try {
    // 模拟进度
    const progressInterval = setInterval(() => {
      if (uploadProgress.value < 90) {
        uploadProgress.value += 10
      }
    }, 200)

    const result = await ocrAPI.uploadFile(file, mode)

    clearInterval(progressInterval)
    uploadProgress.value = 100

    // 延迟一下让用户看到 100%
    setTimeout(() => {
      emit('upload-success', result)
      showToast('文件识别成功', 'success')
      uploading.value = false
      uploadProgress.value = 0
      pendingFile.value = null
      
      // 清空文件输入
      if (fileInput.value) {
        fileInput.value.value = ''
      }
    }, 300)

  } catch (error) {
    uploading.value = false
    uploadProgress.value = 0
    pendingFile.value = null

    const errorMsg = error.response?.data?.detail?.message || error.message || '文件上传失败'
    
    if (error.response?.data?.detail?.error === 'MODEL_USAGE_EXCEEDED') {
      showToast('OCR 模型配额已用尽，请联系管理员', 'error')
    } else {
      showToast(errorMsg, 'error')
    }
    
    emit('upload-error', error)
  }
}
</script>

<style scoped>
.file-upload-container {
  position: relative;
}

.upload-btn {
  padding: 0.5rem;
  border-radius: 0.5rem;
  transition: all 0.2s;
  background-color: transparent;
  color: #6b7280;
  border: none;
  cursor: pointer;
}

.upload-btn:hover:not(:disabled) {
  background-color: #f3f4f6;
}

.upload-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.dark .upload-btn {
  color: #9ca3af;
}

.dark .upload-btn:hover:not(:disabled) {
  background-color: #374151;
}

.spinner {
  width: 1rem;
  height: 1rem;
  border: 2px solid #e5e7eb;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.upload-progress {
  position: fixed;
  bottom: 100px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(10px);
  padding: 16px 24px;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  border: 1px solid rgba(139, 92, 246, 0.2);
  min-width: 280px;
  z-index: 1000;
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: rgba(139, 92, 246, 0.1);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 10px;
  position: relative;
}

.progress-bar::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, 
    transparent 0%, 
    rgba(255, 255, 255, 0.3) 50%, 
    transparent 100%
  );
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #8b5cf6, #a78bfa);
  border-radius: 4px;
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 0 10px rgba(139, 92, 246, 0.5);
}

.progress-text {
  font-size: 0.875rem;
  color: #6b7280;
  font-weight: 500;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.progress-text::before {
  content: '✨';
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.6;
    transform: scale(1.2);
  }
}

.dark .upload-progress {
  background: rgba(31, 41, 55, 0.98);
  border-color: rgba(139, 92, 246, 0.3);
}

.dark .progress-text {
  color: #d1d5db;
}

.ocr-mode-selector {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1), 0 10px 10px -5px rgba(0,0,0,0.04);
  padding: 24px;
  z-index: 1000;
  max-width: 600px;
  width: 90%;
}

.dark .ocr-mode-selector {
  background: #1f2937;
}

.mode-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.mode-header h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
}

.dark .mode-header h3 {
  color: #f9fafb;
}

.close-btn {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: none;
  background: #f3f4f6;
  color: #6b7280;
  font-size: 1.25rem;
  cursor: pointer;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #e5e7eb;
}

.mode-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.mode-card {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 16px;
  border-radius: 12px;
  border: 2px solid #e5e7eb;
  background: #f9fafb;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
}

.mode-card:hover {
  border-color: #8b5cf6;
  background: #f5f3ff;
}

.mode-card.active {
  border-color: #8b5cf6;
  background: #8b5cf6;
  color: white;
}

.mode-icon {
  font-size: 1.5rem;
  margin-bottom: 8px;
}

.mode-label {
  font-weight: 600;
  font-size: 0.875rem;
  margin-bottom: 4px;
}

.mode-desc {
  font-size: 0.75rem;
  opacity: 0.8;
}

.dark .mode-card {
  background: #374151;
  border-color: #4b5563;
}

.dark .mode-card:hover {
  background: #4c1d95;
  border-color: #8b5cf6;
}
</style>
