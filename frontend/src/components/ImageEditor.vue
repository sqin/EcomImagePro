<template>
  <div class="image-editor">
    <canvas
      ref="canvasRef"
      @mousedown="handleMouseDown"
      @mousemove="handleMouseMove"
      @mouseup="handleMouseUp"
      @mouseleave="handleMouseLeave"
    ></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'

const props = defineProps({
  imageUrl: {
    type: String,
    required: true
  },
  imageId: {
    type: String,
    required: true
  },
  operationType: {
    type: String,
    default: 'select'
  }
})

const emit = defineEmits(['region-selected'])

const canvasRef = ref(null)
const image = ref(null)
const scale = ref(1)
const isDrawing = ref(false)
const startX = ref(0)
const startY = ref(0)
const currentRegion = ref(null) // 正在绘制的区域
const selectedRegion = ref(null) // 已选择并确认的区域
const canvasWidth = ref(0)
const canvasHeight = ref(0)

const loadImage = () => {
  const img = new Image()
  img.crossOrigin = 'anonymous'
  img.onload = () => {
    image.value = img
    drawImage()
  }
  img.onerror = () => {
    console.error('图片加载失败')
  }
  // 使用完整URL
  const baseUrl = window.location.origin
  img.src = baseUrl + props.imageUrl
}

// 计算并设置 canvas 尺寸（只在必要时调用）
const calculateCanvasSize = () => {
  const canvas = canvasRef.value
  if (!canvas || !image.value) return

  const container = canvas.parentElement
  // 使用容器的实际可用空间
  const containerWidth = container.clientWidth - 20
  const containerHeight = container.clientHeight - 20

  // 计算缩放比例
  const imgAspect = image.value.width / image.value.height
  const containerAspect = containerWidth / containerHeight

  let drawWidth, drawHeight
  
  // 计算缩放比例，使图片尽可能大地显示在容器中，同时保持原比例
  if (imgAspect > containerAspect) {
    // 图片更宽，以宽度为准，填满容器宽度
    drawWidth = containerWidth
    drawHeight = drawWidth / imgAspect
  } else {
    // 图片更高，以高度为准，填满容器高度
    drawHeight = containerHeight
    drawWidth = drawHeight * imgAspect
  }

  // 确保不超过容器尺寸
  drawWidth = Math.min(drawWidth, containerWidth)
  drawHeight = Math.min(drawHeight, containerHeight)

  scale.value = image.value.width / drawWidth
  canvasWidth.value = drawWidth
  canvasHeight.value = drawHeight

  canvas.width = drawWidth
  canvas.height = drawHeight
}

// 重新绘制内容（不改变尺寸）
const redraw = () => {
  const canvas = canvasRef.value
  if (!canvas || !image.value) return

  const ctx = canvas.getContext('2d')

  // 绘制图片
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  ctx.drawImage(image.value, 0, 0, canvasWidth.value, canvasHeight.value)

  // 绘制已选择的区域（半透明蓝色）
  if (selectedRegion.value) {
    drawRegion(ctx, selectedRegion.value, 'rgba(0, 123, 255, 0.3)')
  }

  // 绘制当前正在选择的区域（更亮的蓝色）
  if (currentRegion.value) {
    drawRegion(ctx, currentRegion.value, 'rgba(0, 123, 255, 0.5)')
  }
}

// 初始化或重新计算尺寸并绘制
const drawImage = () => {
  calculateCanvasSize()
  redraw()
}

const drawRegion = (ctx, region, color) => {
  ctx.fillStyle = color
  ctx.fillRect(region.x, region.y, region.width, region.height)
  ctx.strokeStyle = '#409EFF'
  ctx.lineWidth = 2
  ctx.strokeRect(region.x, region.y, region.width, region.height)
}

const getCanvasCoordinates = (event) => {
  const canvas = canvasRef.value
  if (!canvas) return { x: 0, y: 0 }
  
  const rect = canvas.getBoundingClientRect()
  // Canvas 的实际显示尺寸和内部尺寸可能不同，需要计算缩放比例
  const scaleX = canvas.width / rect.width
  const scaleY = canvas.height / rect.height
  
  // 计算相对于 canvas 的坐标
  let x = (event.clientX - rect.left) * scaleX
  let y = (event.clientY - rect.top) * scaleY
  
  // 限制在 canvas 范围内
  x = Math.max(0, Math.min(x, canvas.width))
  y = Math.max(0, Math.min(y, canvas.height))
  
  return { x, y }
}

const handleMouseDown = (event) => {
  if (props.operationType !== 'select' && props.operationType !== 'translate' && props.operationType !== 'text') {
    return
  }

  event.preventDefault()
  event.stopPropagation()
  
  // 开始新的选择时，清除之前选择的区域
  selectedRegion.value = null
  
  isDrawing.value = true
  const coords = getCanvasCoordinates(event)
  startX.value = coords.x
  startY.value = coords.y
  currentRegion.value = {
    x: coords.x,
    y: coords.y,
    width: 0,
    height: 0
  }
  
  // 添加全局鼠标事件监听
  document.addEventListener('mousemove', handleDocumentMouseMove)
  document.addEventListener('mouseup', handleDocumentMouseUp)
}

const handleMouseMove = (event) => {
  if (!isDrawing.value || !currentRegion.value) return
  handleDocumentMouseMove(event)
}

const handleDocumentMouseMove = (event) => {
  if (!isDrawing.value || !currentRegion.value) return

  const canvas = canvasRef.value
  if (!canvas) return
  
  const rect = canvas.getBoundingClientRect()
  const scaleX = canvas.width / rect.width
  const scaleY = canvas.height / rect.height
  
  // 计算相对于 canvas 的坐标
  let x = (event.clientX - rect.left) * scaleX
  let y = (event.clientY - rect.top) * scaleY
  
  // 限制在 canvas 范围内
  x = Math.max(0, Math.min(x, canvas.width))
  y = Math.max(0, Math.min(y, canvas.height))
  
  const coords = { x, y }
  
  const width = coords.x - startX.value
  const height = coords.y - startY.value

  currentRegion.value = {
    x: Math.min(startX.value, coords.x),
    y: Math.min(startY.value, coords.y),
    width: Math.abs(width),
    height: Math.abs(height)
  }

  redraw()
}

const handleMouseUp = (event) => {
  handleDocumentMouseUp(event)
}

const handleDocumentMouseUp = (event) => {
  if (!isDrawing.value) return

  isDrawing.value = false
  
  // 移除全局事件监听
  document.removeEventListener('mousemove', handleDocumentMouseMove)
  document.removeEventListener('mouseup', handleDocumentMouseUp)

  if (currentRegion.value && currentRegion.value.width > 5 && currentRegion.value.height > 5) {
    // 保存已选择的区域（Canvas坐标）
    selectedRegion.value = {
      x: currentRegion.value.x,
      y: currentRegion.value.y,
      width: currentRegion.value.width,
      height: currentRegion.value.height
    }

    // 转换为原始图片坐标并发送事件
    const originalRegion = {
      x: Math.round(currentRegion.value.x * scale.value),
      y: Math.round(currentRegion.value.y * scale.value),
      width: Math.round(currentRegion.value.width * scale.value),
      height: Math.round(currentRegion.value.height * scale.value)
    }

    emit('region-selected', originalRegion)
  }

  // 清除正在绘制的区域，但保留已选择的区域
  currentRegion.value = null
  redraw()
}

const handleMouseLeave = () => {
  // 不在这里处理，让全局事件处理
  // 这样可以确保即使鼠标移出canvas也能继续绘制
}

watch(() => props.imageUrl, () => {
  loadImage()
})

watch(() => props.operationType, () => {
  currentRegion.value = null
  selectedRegion.value = null
})

onMounted(() => {
  loadImage()
  window.addEventListener('resize', drawImage)
})

// 组件卸载时清理事件监听
onUnmounted(() => {
  document.removeEventListener('mousemove', handleDocumentMouseMove)
  document.removeEventListener('mouseup', handleDocumentMouseUp)
  window.removeEventListener('resize', drawImage)
})
</script>

<style scoped>
.image-editor {
  width: 100%;
  height: 100%;
  min-height: 500px;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: auto;
  padding: 10px;
}

canvas {
  cursor: crosshair;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: #fff;
  display: block;
  /* 确保 canvas 的显示尺寸和内部尺寸一致 */
  max-width: 100%;
  height: auto;
}
</style>

