/**
 * 导出功能相关类型定义
 */

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp?: string
  created_at?: string
}

export interface SelectionRect {
  startX: number
  startY: number
  endX: number
  endY: number
}

export interface ContextMenuPosition {
  x: number
  y: number
}

export interface ExportOptions {
  title?: string
  filename?: string
  includeTimestamp?: boolean
}

export interface PDFExportOptions extends ExportOptions {
  pageSize?: 'A4' | 'Letter'
  orientation?: 'portrait' | 'landscape'
  margins?: {
    top: number
    right: number
    bottom: number
    left: number
  }
}

export type ExportFormat = 'markdown' | 'pdf'
