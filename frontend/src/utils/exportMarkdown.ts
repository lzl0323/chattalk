/**
 * Markdown 导出工具
 */

import type { Message, ExportOptions } from '../types/export'

/**
 * 格式化时间
 */
function formatTime(timestamp?: string): string {
  if (!timestamp) return ''
  
  try {
    const date = new Date(timestamp)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  } catch (e) {
    return timestamp
  }
}

/**
 * 生成 Markdown 内容
 */
export function generateMarkdown(messages: Message[], options: ExportOptions = {}): string {
  const {
    title = '聊天记录导出',
    includeTimestamp = true
  } = options

  let markdown = ''

  // 添加标题
  markdown += `# ${title}\n\n`

  // 添加导出时间
  if (includeTimestamp) {
    const exportTime = new Date().toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
    markdown += `**导出时间**: ${exportTime}\n\n`
    markdown += `**消息数量**: ${messages.length} 条\n\n`
    markdown += '---\n\n'
  }

  // 添加消息内容
  messages.forEach((message, index) => {
    const role = message.role === 'user' ? '👤 用户' : '🤖 AI助手'
    const time = formatTime(message.timestamp || message.created_at)
    
    markdown += `## ${role}\n\n`
    
    if (time) {
      markdown += `*${time}*\n\n`
    }
    
    // 消息内容使用引用格式
    const contentLines = message.content.split('\n')
    contentLines.forEach(line => {
      markdown += `> ${line}\n`
    })
    
    markdown += '\n'
    
    // 最后一条消息不添加分隔线
    if (index < messages.length - 1) {
      markdown += '---\n\n'
    }
  })

  return markdown
}

/**
 * 导出 Markdown 文件
 */
export function exportMarkdown(messages: Message[], options: ExportOptions = {}): void {
  const {
    filename = `chat-export-${Date.now()}.md`
  } = options

  const markdown = generateMarkdown(messages, options)

  // 创建 Blob
  const blob = new Blob([markdown], { type: 'text/markdown;charset=utf-8' })

  // 创建下载链接
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  
  // 触发下载
  document.body.appendChild(link)
  link.click()
  
  // 清理
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

/**
 * 复制 Markdown 到剪贴板
 */
export async function copyMarkdownToClipboard(messages: Message[], options: ExportOptions = {}): Promise<boolean> {
  try {
    const markdown = generateMarkdown(messages, options)
    await navigator.clipboard.writeText(markdown)
    return true
  } catch (error) {
    console.error('复制到剪贴板失败:', error)
    return false
  }
}
