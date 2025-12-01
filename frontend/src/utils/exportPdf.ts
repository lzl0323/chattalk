/**
 * PDF 导出工具
 * 使用 jsPDF + html2canvas 生成 PDF
 */

import jsPDF from 'jspdf'
import html2canvas from 'html2canvas'
import type { Message, PDFExportOptions } from '../types/export'

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
      minute: '2-digit'
    })
  } catch (e) {
    return timestamp
  }
}

/**
 * 创建 PDF 预览 HTML
 */
function createPdfPreviewHTML(messages: Message[], options: PDFExportOptions = {}): HTMLElement {
  const {
    title = '聊天记录',
    includeTimestamp = true
  } = options

  const container = document.createElement('div')
  container.style.cssText = `
    position: absolute;
    left: -9999px;
    top: 0;
    width: 210mm;
    padding: 20mm;
    background: white;
    font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
    color: #333;
    line-height: 1.6;
  `

  let html = ''

  // 标题
  html += `
    <div style="text-align: center; margin-bottom: 30px;">
      <h1 style="font-size: 24px; font-weight: bold; margin: 0 0 10px 0; color: #1a1a1a;">
        ${title}
      </h1>
  `

  if (includeTimestamp) {
    const exportTime = new Date().toLocaleString('zh-CN')
    html += `
      <p style="font-size: 12px; color: #666; margin: 5px 0;">
        导出时间: ${exportTime}
      </p>
      <p style="font-size: 12px; color: #666; margin: 5px 0;">
        消息数量: ${messages.length} 条
      </p>
    `
  }

  html += `
      <div style="width: 60px; height: 3px; background: #3b82f6; margin: 20px auto 0;"></div>
    </div>
  `

  // 消息列表
  messages.forEach((message, index) => {
    const isUser = message.role === 'user'
    const role = isUser ? '👤 用户' : '🤖 AI助手'
    const time = formatTime(message.timestamp || message.created_at)
    const bgColor = isUser ? '#e3f2fd' : '#f5f5f5'
    const borderColor = isUser ? '#2196f3' : '#9e9e9e'

    html += `
      <div style="margin-bottom: 25px; page-break-inside: avoid;">
        <div style="margin-bottom: 8px;">
          <span style="font-weight: bold; font-size: 14px; color: #1976d2;">
            ${role}
          </span>
          ${time ? `<span style="font-size: 12px; color: #999; margin-left: 10px;">${time}</span>` : ''}
        </div>
        <div style="
          padding: 15px;
          background: ${bgColor};
          border-left: 4px solid ${borderColor};
          border-radius: 4px;
          font-size: 13px;
          line-height: 1.8;
          white-space: pre-wrap;
          word-wrap: break-word;
        ">
          ${message.content.replace(/</g, '&lt;').replace(/>/g, '&gt;')}
        </div>
      </div>
    `

    // 每 5 条消息后添加分页提示
    if ((index + 1) % 5 === 0 && index < messages.length - 1) {
      html += `<div style="page-break-after: always;"></div>`
    }
  })

  container.innerHTML = html
  return container
}

/**
 * 导出为 PDF (方法1: 使用 html2canvas + jsPDF)
 */
export async function exportPdfWithCanvas(
  messages: Message[],
  options: PDFExportOptions = {}
): Promise<void> {
  const {
    filename = `chat-export-${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.pdf`,
    pageSize = 'A4',
    orientation = 'portrait'
  } = options

  try {
    // 创建预览容器
    const container = createPdfPreviewHTML(messages, options)
    document.body.appendChild(container)

    // 等待字体和样式加载
    await new Promise(resolve => setTimeout(resolve, 100))

    // 转换为 canvas
    const canvas = await html2canvas(container, {
      scale: 2,
      useCORS: true,
      logging: false,
      backgroundColor: '#ffffff'
    })

    // 移除预览容器
    document.body.removeChild(container)

    // 创建 PDF
    const imgData = canvas.toDataURL('image/png')
    const pdf = new jsPDF({
      orientation,
      unit: 'mm',
      format: pageSize.toLowerCase()
    })

    // A4 尺寸
    const pageWidth = pdf.internal.pageSize.getWidth()
    const pageHeight = pdf.internal.pageSize.getHeight()

    // 计算图片尺寸
    const imgWidth = pageWidth
    const imgHeight = (canvas.height * imgWidth) / canvas.width

    let heightLeft = imgHeight
    let position = 0

    // 添加第一页
    pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight)
    heightLeft -= pageHeight

    // 如果内容超过一页，添加更多页
    while (heightLeft > 0) {
      position = heightLeft - imgHeight
      pdf.addPage()
      pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight)
      heightLeft -= pageHeight
    }

    // 保存 PDF
    pdf.save(filename)
  } catch (error) {
    console.error('PDF 导出失败:', error)
    throw error
  }
}

/**
 * 导出为 PDF (方法2: 纯 jsPDF 文本模式)
 * 更快但需要手动处理中文字体
 */
export async function exportPdfWithText(
  messages: Message[],
  options: PDFExportOptions = {}
): Promise<void> {
  const {
    filename = `chat-export-${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.pdf`,
    pageSize = 'A4',
    orientation = 'portrait',
    margins = { top: 20, right: 20, bottom: 20, left: 20 }
  } = options

  try {
    const pdf = new jsPDF({
      orientation,
      unit: 'mm',
      format: pageSize.toLowerCase()
    })

    const pageWidth = pdf.internal.pageSize.getWidth()
    const pageHeight = pdf.internal.pageSize.getHeight()
    const contentWidth = pageWidth - margins.left - margins.right

    let yPosition = margins.top

    // 标题
    pdf.setFontSize(18)
    pdf.setFont('helvetica', 'bold')
    pdf.text('Chat Export', pageWidth / 2, yPosition, { align: 'center' })
    yPosition += 10

    // 导出时间
    pdf.setFontSize(10)
    pdf.setFont('helvetica', 'normal')
    const exportTime = new Date().toLocaleString('zh-CN')
    pdf.text(`Export Time: ${exportTime}`, pageWidth / 2, yPosition, { align: 'center' })
    yPosition += 5
    pdf.text(`Messages: ${messages.length}`, pageWidth / 2, yPosition, { align: 'center' })
    yPosition += 15

    // 消息
    pdf.setFontSize(11)
    messages.forEach((message) => {
      // 检查是否需要换页
      if (yPosition > pageHeight - margins.bottom - 30) {
        pdf.addPage()
        yPosition = margins.top
      }

      // 角色和时间
      const role = message.role === 'user' ? 'User' : 'AI'
      const time = formatTime(message.timestamp || message.created_at)
      
      pdf.setFont('helvetica', 'bold')
      pdf.text(`${role}`, margins.left, yPosition)
      
      if (time) {
        pdf.setFont('helvetica', 'normal')
        pdf.setFontSize(9)
        pdf.text(time, margins.left + 20, yPosition)
      }
      
      yPosition += 7

      // 内容（注意：jsPDF 对中文支持有限，这里使用基础方法）
      pdf.setFont('helvetica', 'normal')
      pdf.setFontSize(10)
      
      const lines = pdf.splitTextToSize(message.content, contentWidth)
      lines.forEach((line: string) => {
        if (yPosition > pageHeight - margins.bottom) {
          pdf.addPage()
          yPosition = margins.top
        }
        pdf.text(line, margins.left + 5, yPosition)
        yPosition += 5
      })

      yPosition += 10
    })

    pdf.save(filename)
  } catch (error) {
    console.error('PDF 导出失败:', error)
    throw error
  }
}

/**
 * 默认导出方法（使用 canvas 方式，中文支持更好）
 */
export const exportPdf = exportPdfWithCanvas
