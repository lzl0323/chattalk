<template>
  <div
    v-if="isSelecting && selectionRect"
    class="selection-layer"
    :style="selectionStyle"
  >
    <div class="selection-box"></div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { SelectionRect } from '../../types/export'

interface Props {
  isSelecting: boolean
  selectionRect: SelectionRect | null
}

const props = defineProps<Props>()

/**
 * 计算选择框样式
 */
const selectionStyle = computed(() => {
  if (!props.selectionRect) return {}

  const { startX, startY, endX, endY } = props.selectionRect

  const left = Math.min(startX, endX)
  const top = Math.min(startY, endY)
  const width = Math.abs(endX - startX)
  const height = Math.abs(endY - startY)

  return {
    left: `${left}px`,
    top: `${top}px`,
    width: `${width}px`,
    height: `${height}px`
  }
})
</script>

<style scoped>
.selection-layer {
  position: absolute;
  pointer-events: none;
  z-index: 1000;
}

.selection-box {
  width: 100%;
  height: 100%;
  border: 2px solid #2196f3;
  background-color: rgba(33, 150, 243, 0.1);
  border-radius: 2px;
  animation: selection-pulse 0.3s ease-out;
}

@keyframes selection-pulse {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* 选择框四个角的标记 */
.selection-box::before,
.selection-box::after {
  content: '';
  position: absolute;
  width: 8px;
  height: 8px;
  border: 2px solid #2196f3;
  background: white;
}

.selection-box::before {
  top: -4px;
  left: -4px;
  border-right: none;
  border-bottom: none;
}

.selection-box::after {
  bottom: -4px;
  right: -4px;
  border-left: none;
  border-top: none;
}
</style>
