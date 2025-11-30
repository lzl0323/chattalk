<template>
  <div class="voice-input-container">
    <!-- 麦克风按钮 -->
    <button
      @click="toggleRecording"
      :disabled="!isSupported"
      :class="[
        'voice-button',
        { 
          'recording': isRecording,
          'disabled': !isSupported
        }
      ]"
      :title="buttonTitle"
    >
      <!-- 麦克风图标 -->
      <svg
        class="mic-icon"
        fill="currentColor"
        viewBox="0 0 24 24"
      >
        <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
        <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
      </svg>
    </button>
    
    <!-- 录音状态提示（类似 ChatGPT） -->
    <Transition name="slide-up">
      <div v-if="isRecording" class="listening-tooltip">
        正在聆听...
      </div>
    </Transition>
    
    <!-- 错误提示 -->
    <Transition name="fade">
      <div v-if="statusMessage && statusType === 'error'" class="error-tooltip">
        {{ statusMessage }}
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const emit = defineEmits(['transcript'])

// 状态
const isRecording = ref(false)
const isSupported = ref(false)
const statusMessage = ref('')
const statusType = ref('info') // 'info' | 'error' | 'success'
const recognition = ref(null)

// 按钮提示文本
const buttonTitle = computed(() => {
  if (!isSupported.value) return '您的浏览器不支持语音识别'
  return isRecording.value ? '点击停止录音' : '点击开始语音输入'
})

// 初始化 Web Speech API
const initSpeechRecognition = () => {
  // 检查浏览器兼容性
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
  
  if (!SpeechRecognition) {
    console.warn('浏览器不支持 Web Speech API')
    isSupported.value = false
    return
  }
  
  isSupported.value = true
  
  // 创建识别实例
  recognition.value = new SpeechRecognition()
  
  // 配置参数
  recognition.value.continuous = true // 连续识别
  recognition.value.interimResults = true // 返回临时结果
  recognition.value.lang = 'zh-CN' // 中文识别
  recognition.value.maxAlternatives = 1 // 最多返回 1 个识别结果
  
  // 识别结果事件
  recognition.value.onresult = (event) => {
    let finalTranscript = ''
    
    // 遍历识别结果，只处理最终结果
    for (let i = event.resultIndex; i < event.results.length; i++) {
      if (event.results[i].isFinal) {
        finalTranscript += event.results[i][0].transcript
      }
    }
    
    // 如果有最终结果，发送给父组件
    if (finalTranscript) {
      console.log('✅ 识别成功:', finalTranscript)
      emit('transcript', finalTranscript)
    }
  }
  
  // 识别开始
  recognition.value.onstart = () => {
    console.log('✅ 语音识别已启动')
    isRecording.value = true
  }
  
  // 识别结束
  recognition.value.onend = () => {
    console.log('语音识别已停止')
    isRecording.value = false
    
    // 清除状态提示
    setTimeout(() => {
      if (statusType.value === 'info') {
        statusMessage.value = ''
      }
    }, 1000)
  }
  
  // 识别错误
  recognition.value.onerror = (event) => {
    console.error('语音识别错误:', event.error)
    
    let errorMsg = '识别失败'
    
    switch (event.error) {
      case 'no-speech':
        errorMsg = '未检测到语音，请再说一遍'
        break
      case 'audio-capture':
        errorMsg = '无法访问麦克风，请检查权限'
        break
      case 'not-allowed':
        errorMsg = '麦克风权限被拒绝'
        break
      case 'network':
        errorMsg = '网络错误，请检查网络连接'
        break
      case 'aborted':
        errorMsg = '识别被中止'
        break
      default:
        errorMsg = `识别错误: ${event.error}`
    }
    
    showStatus(errorMsg, 'error')
    isRecording.value = false
    
    // 3秒后清除错误提示
    setTimeout(() => {
      statusMessage.value = ''
    }, 3000)
  }
  
  // 没有匹配结果
  recognition.value.onnomatch = () => {
    showStatus('未听清，请再说一遍', 'error')
  }
}

// 切换录音状态
const toggleRecording = () => {
  if (!isSupported.value || !recognition.value) return
  
  if (isRecording.value) {
    // 停止录音
    stopRecording()
  } else {
    // 开始录音
    startRecording()
  }
}

// 开始录音
const startRecording = async () => {
  try {
    // 检查 navigator.mediaDevices 是否可用
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      throw new Error('您的浏览器不支持麦克风访问，请使用 HTTPS 或 localhost')
    }
    
    // 先请求麦克风权限，这会弹出浏览器的权限请求窗口
    console.log('🎤 请求麦克风权限...')
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    console.log('✅ 麦克风权限已授予')
    
    // 停止测试流（我们只需要权限）
    stream.getTracks().forEach(track => track.stop())
    
    // 权限授予后，启动语音识别
    console.log('🎤 启动语音识别...')
    recognition.value.start()
    // isRecording 会在 onstart 事件中设置
    console.log('✅ 语音识别已启动')
  } catch (error) {
    console.error('❌ 启动失败:', {
      name: error.name,
      message: error.message,
      error: error
    })
    
    // 根据不同的错误类型显示友好提示
    if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
      showStatus('⚠️ 麦克风权限被拒绝\n请点击地址栏左侧🔒图标，允许麦克风访问后刷新页面', 'error')
    } else if (error.name === 'NotFoundError') {
      showStatus('❌ 未找到麦克风设备\n请检查麦克风是否连接', 'error')
    } else if (error.name === 'NotReadableError') {
      showStatus('⚠️ 麦克风被占用\n请关闭其他使用麦克风的程序', 'error')
    } else if (error.name === 'InvalidStateError') {
      showStatus('⚠️ 语音识别已在运行\n请稍后再试', 'error')
    } else if (error.message && error.message.includes('HTTPS')) {
      showStatus('⚠️ 需要 HTTPS 或 localhost\n请使用 http://localhost:5173 访问', 'error')
    } else {
      showStatus(`❌ 启动失败: ${error.message || '未知错误'}\n请查看控制台了解详情`, 'error')
    }
    
    // 5秒后清除错误提示
    setTimeout(() => {
      statusMessage.value = ''
    }, 5000)
  }
}

// 停止录音
const stopRecording = () => {
  try {
    recognition.value.stop()
    isRecording.value = false
  } catch (error) {
    console.error('停止语音识别失败:', error)
  }
}

// 显示状态信息
const showStatus = (message, type = 'info') => {
  statusMessage.value = message
  statusType.value = type
}

// 组件挂载
onMounted(() => {
  initSpeechRecognition()
})

// 组件卸载
onUnmounted(() => {
  if (recognition.value && isRecording.value) {
    recognition.value.stop()
  }
})

// 暴露方法
defineExpose({
  startRecording,
  stopRecording,
  isRecording: computed(() => isRecording.value)
})
</script>

<style scoped>
.voice-input-container {
  position: relative;
  display: inline-flex;
  align-items: center;
}

/* 麦克风按钮 - ChatGPT 风格 */
.voice-button {
  position: relative;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: none;
  background: #000;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: none;
  flex-shrink: 0;
}

.voice-button:hover:not(.disabled):not(.recording) {
  background: #2d2d2d;
  transform: scale(1.05);
}

.voice-button.recording {
  background: #ef4444;
  animation: pulse 1.5s ease-in-out infinite;
}

.voice-button.disabled {
  cursor: not-allowed;
  opacity: 0.4;
  background: #9ca3af;
}

/* 脉冲动画 */
@keyframes pulse {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4);
  }
  50% {
    box-shadow: 0 0 0 8px rgba(239, 68, 68, 0);
  }
}

/* 麦克风图标 */
.mic-icon {
  width: 16px;
  height: 16px;
  color: white;
  transition: transform 0.2s ease;
}

.voice-button:active:not(.disabled) .mic-icon {
  transform: scale(0.95);
}

/* 录音提示框 - ChatGPT 风格 */
.listening-tooltip {
  position: absolute;
  bottom: calc(100% + 12px);
  left: 50%;
  transform: translateX(-50%);
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(8px);
  color: #1f2937;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  white-space: nowrap;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12), 0 0 0 1px rgba(0, 0, 0, 0.05);
  z-index: 1000;
}

/* 添加小三角 */
.listening-tooltip::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 6px solid transparent;
  border-right: 6px solid transparent;
  border-top: 6px solid rgba(255, 255, 255, 0.95);
}

/* 错误提示 */
.error-tooltip {
  position: absolute;
  bottom: calc(100% + 12px);
  left: 50%;
  transform: translateX(-50%);
  background: #fef2f2;
  color: #dc2626;
  padding: 10px 16px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 500;
  white-space: pre-line;
  max-width: 280px;
  text-align: center;
  line-height: 1.5;
  box-shadow: 0 4px 16px rgba(239, 68, 68, 0.15), 0 0 0 1px rgba(239, 68, 68, 0.1);
  z-index: 1000;
}

.error-tooltip::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 6px solid transparent;
  border-right: 6px solid transparent;
  border-top: 6px solid #fef2f2;
}

/* 向上滑入动画 */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-up-enter-from {
  opacity: 0;
  transform: translateX(-50%) translateY(4px);
}

.slide-up-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-4px);
}

.slide-up-enter-to,
.slide-up-leave-from {
  opacity: 1;
  transform: translateX(-50%) translateY(0);
}

/* 淡入淡出动画 */
.fade-enter-active,
.fade-leave-active {
  transition: all 0.25s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(4px);
}

.fade-enter-to,
.fade-leave-from {
  opacity: 1;
  transform: translateX(-50%) translateY(0);
}

/* 深色模式适配 */
@media (prefers-color-scheme: dark) {
  .voice-button:not(.recording):not(.disabled) {
    background: #374151;
  }
  
  .voice-button:hover:not(.disabled):not(.recording) {
    background: #4b5563;
  }
  
  .listening-tooltip {
    background: rgba(31, 41, 55, 0.95);
    color: #f9fafb;
  }
  
  .listening-tooltip::after {
    border-top-color: rgba(31, 41, 55, 0.95);
  }
}

/* 响应式 */
@media (max-width: 640px) {
  .voice-button {
    width: 32px;
    height: 32px;
  }
  
  .mic-icon {
    width: 16px;
    height: 16px;
  }
  
  .listening-tooltip,
  .error-tooltip {
    font-size: 12px;
    padding: 6px 12px;
  }
}
</style>
