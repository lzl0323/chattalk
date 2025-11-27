<template>
  <div
    class="flex mb-4 animate-fadeIn"
    :class="isUser ? 'justify-end' : 'justify-start'"
  >
    <div
      class="max-w-[75%] rounded-2xl px-4 py-3 shadow-sm"
      :class="messageClass"
    >
      <!-- 消息头部：角色标识 -->
      <div class="flex items-center mb-1.5">
        <div
          class="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold mr-2"
          :class="avatarClass"
        >
          {{ isUser ? '我' : 'AI' }}
        </div>
        <span class="text-xs text-gray-500">
          {{ formattedTime }}
        </span>
      </div>
      
      <!-- 消息内容 -->
      <div
        v-if="isUser"
        class="text-white whitespace-pre-wrap break-words"
      >
        {{ content }}
      </div>
      <div
        v-else
        class="markdown-content prose prose-sm max-w-none"
        v-html="renderedContent"
      ></div>
      
      <!-- 流式加载指示器 -->
      <div
        v-if="isStreaming"
        class="inline-block w-1 h-4 bg-gray-400 animate-pulse ml-0.5"
      ></div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  role: {
    type: String,
    required: true,
    validator: (value) => ['user', 'assistant'].includes(value)
  },
  content: {
    type: String,
    required: true
  },
  timestamp: {
    type: Date,
    default: () => new Date()
  },
  isStreaming: {
    type: Boolean,
    default: false
  }
})

const isUser = computed(() => props.role === 'user')

const messageClass = computed(() => {
  return isUser.value
    ? 'bg-primary-500 text-white'
    : 'bg-white border border-gray-200'
})

const avatarClass = computed(() => {
  return isUser.value
    ? 'bg-primary-600 text-white'
    : 'bg-green-500 text-white'
})

const formattedTime = computed(() => {
  if (!props.timestamp) return ''
  
  const date = new Date(props.timestamp)
  const hours = date.getHours().toString().padStart(2, '0')
  const minutes = date.getMinutes().toString().padStart(2, '0')
  
  return `${hours}:${minutes}`
})

// 简单的 Markdown 渲染
const renderedContent = computed(() => {
  let html = props.content
  
  // 转义 HTML
  html = html.replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
  
  // 代码块
  html = html.replace(/```(\w+)?\n([\s\S]*?)```/g, (match, lang, code) => {
    return `<pre><code class="language-${lang || 'plaintext'}">${code.trim()}</code></pre>`
  })
  
  // 行内代码
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>')
  
  // 标题
  html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>')
  html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>')
  html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>')
  
  // 粗体
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
  
  // 斜体
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>')
  
  // 无序列表
  html = html.replace(/^\- (.+)$/gm, '<li>$1</li>')
  html = html.replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>')
  
  // 有序列表
  html = html.replace(/^\d+\. (.+)$/gm, '<li>$1</li>')
  
  // 引用
  html = html.replace(/^&gt; (.+)$/gm, '<blockquote>$1</blockquote>')
  
  // 链接
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>')
  
  // 段落
  html = html.split('\n\n').map(para => {
    if (!para.trim()) return ''
    if (para.startsWith('<')) return para
    return `<p>${para}</p>`
  }).join('\n')
  
  return html
})
</script>

<style scoped>
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fadeIn {
  animation: fadeIn 0.3s ease-out;
}
</style>
