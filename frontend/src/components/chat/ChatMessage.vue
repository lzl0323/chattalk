<template>
  <div
    :data-message-id="message.id"
    :class="[
      'flex gap-4 message-wrapper transition-all duration-200 rounded-lg px-3 py-2 -mx-3',
      message.role === 'user' ? 'justify-end' : 'justify-start',
      isSelected && 'message-selected'
    ]"
    @click="handleMessageClick"
    @contextmenu="handleContextMenu"
  >
    <!-- AI 头像 -->
    <div
      v-if="message.role === 'assistant'"
      class="w-8 h-8 rounded-full bg-gpt-green-500 flex items-center justify-center flex-shrink-0"
    >
      <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
      </svg>
    </div>
    
    <!-- 消息内容 -->
    <div :class="['flex flex-col gap-2', message.role === 'user' ? 'items-end' : 'items-start', 'max-w-[75%]']">
      <!-- 气泡 -->
      <div
        :class="[
          'rounded-2xl px-4 py-3',
          message.role === 'user'
            ? 'bg-gpt-gray-100 dark:bg-gpt-dark-500 text-gray-900 dark:text-gray-100'
            : 'bg-transparent text-gray-900 dark:text-gray-100'
        ]"
      >
        <!-- 用户消息 -->
        <div v-if="message.role === 'user'">
          <!-- 文件消息 -->
          <div v-if="message.message_type === 'image' && message.file_url" class="file-message">
            <!-- PDF 文件 -->
            <div v-if="isPDF(message.file_name)" class="pdf-file-display">
              <div class="flex items-center gap-3 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-blue-400 dark:hover:border-blue-500 transition-colors cursor-pointer"
                   @click="openFile(message.file_url)">
                <!-- PDF 图标 -->
                <div class="flex-shrink-0">
                  <svg class="w-10 h-10 text-red-500" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18.5,9H13V3.5L18.5,9M6,20V4H12V10H18V20H6M7.5,13H9.5V15H11V18H9.5V16.5H7.5V18H6V13H7.5V13M10.5,13H13.5C14.3,13 15,13.7 15,14.5V16.5C15,17.3 14.3,18 13.5,18H10.5V13M12,16.5H13.5V14.5H12V16.5M16.5,13H18V15H19.5V13H21V18H19.5V16.5H16.5V18H15V13H16.5V13Z"/>
                  </svg>
                </div>
                <!-- 文件信息 -->
                <div class="flex-1 min-w-0">
                  <div class="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                    {{ message.file_name }}
                  </div>
                  <div class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    PDF 文档
                  </div>
                </div>
                <!-- 下载图标 -->
                <div class="flex-shrink-0">
                  <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                </div>
              </div>
            </div>
            
            <!-- 图片文件 -->
            <div v-else class="image-message">
              <img
                :src="getImageUrl(message.file_url)"
                :alt="message.file_name || '上传的图片'"
                class="uploaded-image"
                @click="previewImage(message.file_url)"
                @error="handleImageError"
              />
            </div>
          </div>
          
          <!-- 普通文本消息 -->
          <div v-else class="whitespace-pre-wrap break-words">
            {{ message.content }}
          </div>
        </div>
        
        <!-- AI 消息（Markdown 渲染） -->
        <div
          v-else
          class="markdown-body prose dark:prose-dark max-w-none"
          v-html="renderedContent"
        ></div>
        
        <!-- 流式输入光标 -->
        <span v-if="isStreaming" class="inline-block w-2 h-4 ml-1 bg-gpt-green-500 animate-pulse"></span>
      </div>
      
      <!-- 操作按钮（仅 AI 消息） -->
      <div
        v-if="message.role === 'assistant' && !isStreaming"
        class="flex items-center gap-2 px-2 opacity-0 group-hover:opacity-100 transition-opacity"
      >
        <button
          @click="$emit('copy')"
          class="p-1.5 rounded hover:bg-gray-100 dark:hover:bg-gpt-dark-600 transition-colors"
          title="复制"
        >
          <svg class="w-4 h-4 text-gray-500 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
        </button>
        
        <button
          @click="$emit('regenerate')"
          class="p-1.5 rounded hover:bg-gray-100 dark:hover:bg-gpt-dark-600 transition-colors"
          title="重新生成"
        >
          <svg class="w-4 h-4 text-gray-500 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
        
        <button
          @click="$emit('delete')"
          class="p-1.5 rounded hover:bg-red-100 dark:hover:bg-red-900/30 transition-colors"
          title="删除"
        >
          <svg class="w-4 h-4 text-red-500 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </button>
      </div>
      
      <!-- 时间戳 -->
      <span class="text-xs text-gray-400 dark:text-gray-500 px-2">
        {{ formatTime(message.created_at || message.timestamp) }}
      </span>
    </div>
    
    <!-- 用户头像 -->
    <div
      v-if="message.role === 'user'"
      class="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center flex-shrink-0"
    >
      <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
      </svg>
    </div>
  </div>
  
  <!-- 图片预览模态框 -->
  <Teleport to="body">
    <div
      v-if="showImagePreview"
      class="image-preview-modal"
      @click="closePreview"
    >
      <div class="preview-content" @click.stop>
        <button class="close-btn" @click="closePreview">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
        <img :src="previewImageUrl" alt="预览图片" class="preview-image" />
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { computed, ref } from 'vue'
import { marked } from 'marked'
import hljs from 'highlight.js/lib/core'
// 导入常用语言
import javascript from 'highlight.js/lib/languages/javascript'
import python from 'highlight.js/lib/languages/python'
import java from 'highlight.js/lib/languages/java'
import cpp from 'highlight.js/lib/languages/cpp'
import sql from 'highlight.js/lib/languages/sql'
import json from 'highlight.js/lib/languages/json'
import xml from 'highlight.js/lib/languages/xml'
import css from 'highlight.js/lib/languages/css'
import 'highlight.js/styles/atom-one-dark.css'

// 注册语言
hljs.registerLanguage('javascript', javascript)
hljs.registerLanguage('python', python)
hljs.registerLanguage('java', java)
hljs.registerLanguage('cpp', cpp)
hljs.registerLanguage('sql', sql)
hljs.registerLanguage('json', json)
hljs.registerLanguage('xml', xml)
hljs.registerLanguage('css', css)

// Props
const props = defineProps({
  message: {
    type: Object,
    required: true
  },
  isStreaming: {
    type: Boolean,
    default: false
  },
  isSelected: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['copy', 'regenerate', 'delete', 'messageClick', 'messageContextMenu'])

// 图片预览
const showImagePreview = ref(false)
const previewImageUrl = ref('')

// 判断是否是 PDF 文件
const isPDF = (fileName) => {
  if (!fileName) return false
  return fileName.toLowerCase().endsWith('.pdf')
}

// 获取图片 URL
const getImageUrl = (fileUrl) => {
  if (!fileUrl) return ''
  
  // 替换反斜杠为正斜杠（兼容 Windows 路径）
  let url = fileUrl.replace(/\\/g, '/')
  
  // 如果已经是完整URL，直接返回
  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url
  }
  
  // 使用当前域名和端口构建URL
  // 优先使用环境变量配置的后端地址（支持局域网访问）
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL
  const baseUrl = API_BASE_URL || window.location.origin
  
  // 兼容旧格式：如果路径以 /ocr/ 开头但不是 /uploads/ocr/，添加 /uploads 前缀
  if (url.startsWith('/ocr/')) {
    return `${baseUrl}/uploads${url}`
  }
  
  // 如果以 / 开头，说明是相对于根路径的
  if (url.startsWith('/')) {
    return `${baseUrl}${url}`
  }
  
  // 如果以 uploads/ 开头，添加根路径和斜杠
  if (url.startsWith('uploads/')) {
    return `${baseUrl}/${url}`
  }
  
  // 如果以 ocr/ 开头（旧格式），添加 /uploads/ 前缀
  if (url.startsWith('ocr/')) {
    return `${baseUrl}/uploads/${url}`
  }
  
  // 否则添加 /uploads/ 前缀
  return `${baseUrl}/uploads/${url}`
}

// 消息点击处理
const handleMessageClick = (event) => {
  emit('messageClick', props.message.id, event)
}

// 右键菜单处理
const handleContextMenu = (event) => {
  emit('messageContextMenu', props.message.id, event)
}

// 打开文件（在新标签页）
const openFile = (fileUrl) => {
  const url = getImageUrl(fileUrl)
  window.open(url, '_blank')
}

const previewImage = (fileUrl) => {
  previewImageUrl.value = getImageUrl(fileUrl)
  showImagePreview.value = true
}

const closePreview = () => {
  showImagePreview.value = false
  previewImageUrl.value = ''
}

const handleImageError = (event) => {
  console.error('图片加载失败:', {
    src: event.target.src,
    message_type: props.message.message_type,
    file_url: props.message.file_url,
    file_name: props.message.file_name,
    computed_url: getImageUrl(props.message.file_url)
  })
}

// 配置 marked
marked.setOptions({
  highlight: (code, lang) => {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(code, { language: lang }).value
      } catch (err) {
        console.error('Highlight error:', err)
      }
    }
    return hljs.highlightAuto(code).value
  },
  breaks: true,
  gfm: true
})

// 渲染 Markdown
const renderedContent = computed(() => {
  if (props.message.role === 'assistant') {
    try {
      return marked.parse(props.message.content || '')
    } catch (error) {
      console.error('Markdown parse error:', error)
      return props.message.content
    }
  }
  return props.message.content
})

// 格式化时间
const formatTime = (timestamp) => {
  if (!timestamp) return ''
  
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date
  
  // 小于 1 分钟
  if (diff < 60000) {
    return '刚刚'
  }
  
  // 小于 1 小时
  if (diff < 3600000) {
    return `${Math.floor(diff / 60000)} 分钟前`
  }
  
  // 小于 24 小时
  if (diff < 86400000) {
    return `${Math.floor(diff / 3600000)} 小时前`
  }
  
  // 显示具体时间
  return date.toLocaleString('zh-CN', {
    month: 'numeric',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style>
/* Markdown 样式 */
.markdown-body {
  @apply text-gray-900 dark:text-gray-100;
}

.markdown-body p {
  @apply mb-4 leading-relaxed;
}

.markdown-body h1,
.markdown-body h2,
.markdown-body h3,
.markdown-body h4 {
  @apply font-semibold mt-6 mb-4;
}

.markdown-body h1 {
  @apply text-2xl;
}

.markdown-body h2 {
  @apply text-xl;
}

.markdown-body h3 {
  @apply text-lg;
}

.markdown-body ul,
.markdown-body ol {
  @apply ml-6 mb-4 space-y-2;
}

.markdown-body li {
  @apply leading-relaxed;
}

.markdown-body code {
  @apply px-1.5 py-0.5 rounded bg-gpt-gray-100 dark:bg-gpt-dark-600 text-sm font-mono;
}

.markdown-body pre {
  @apply my-4 rounded-lg overflow-x-auto bg-gpt-dark-800;
}

.markdown-body pre code {
  @apply block p-4 bg-transparent text-gray-100;
}

.markdown-body blockquote {
  @apply pl-4 border-l-4 border-gray-300 dark:border-gpt-dark-400 text-gray-600 dark:text-gray-400 italic my-4;
}

.markdown-body table {
  @apply w-full border-collapse my-4;
}

.markdown-body th,
.markdown-body td {
  @apply border border-gray-300 dark:border-gpt-dark-400 px-4 py-2;
}

.markdown-body th {
  @apply bg-gpt-gray-50 dark:bg-gpt-dark-600 font-semibold;
}

.markdown-body a {
  @apply text-gpt-green-500 hover:underline;
}

.markdown-body strong {
  @apply font-semibold;
}

.markdown-body em {
  @apply italic;
}

/* 文件消息样式 */
.file-message {
  @apply max-w-md;
}

/* PDF 文件显示 */
.pdf-file-display {
  @apply relative;
}

.pdf-file-display .flex {
  @apply transition-all duration-200;
}

.pdf-file-display .flex:hover {
  @apply shadow-md;
}

/* 图片消息样式 */
.image-message {
  @apply relative overflow-hidden rounded-lg;
}

.uploaded-image {
  @apply max-w-sm max-h-80 object-contain cursor-pointer rounded-lg;
  @apply transition-transform duration-200 hover:scale-[1.02];
  @apply shadow-md hover:shadow-lg;
}

/* 图片预览模态框 */
.image-preview-modal {
  @apply fixed inset-0 z-50;
  @apply bg-black bg-opacity-90;
  @apply flex items-center justify-center;
  @apply backdrop-blur-sm;
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.preview-content {
  @apply relative max-w-[90vw] max-h-[90vh];
  @apply flex items-center justify-center;
  animation: zoomIn 0.3s ease-out;
}

@keyframes zoomIn {
  from {
    transform: scale(0.8);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

.preview-image {
  @apply max-w-full max-h-[90vh] object-contain;
  @apply rounded-lg shadow-2xl;
}

.close-btn {
  @apply absolute top-4 right-4 z-10;
  @apply w-10 h-10 rounded-full;
  @apply bg-white dark:bg-gray-800;
  @apply text-gray-700 dark:text-gray-300;
  @apply flex items-center justify-center;
  @apply hover:bg-gray-100 dark:hover:bg-gray-700;
  @apply transition-colors duration-200;
  @apply shadow-lg;
}

.close-btn:hover {
  @apply transform scale-110;
}

/* 消息选中状态样式 */
.message-wrapper {
  cursor: pointer;
  user-select: none;
}

.message-wrapper:hover {
  background-color: rgba(0, 0, 0, 0.02);
}

.dark .message-wrapper:hover {
  background-color: rgba(255, 255, 255, 0.05);
}

.message-selected {
  background-color: rgba(33, 150, 243, 0.1) !important;
  border: 1px solid rgba(33, 150, 243, 0.3);
}

.dark .message-selected {
  background-color: rgba(33, 150, 243, 0.15) !important;
  border-color: rgba(33, 150, 243, 0.4);
}
</style>
