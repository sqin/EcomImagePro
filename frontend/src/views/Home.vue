<template>
  <div class="home-container">
    <div class="donate-entry">
      <el-button type="danger" round @click="handleLogout" style="margin-right: 10px;">
        登出
      </el-button>
      <el-button type="primary" round @click="showDonateDialog = true">
        请我喝杯咖啡
      </el-button>
    </div>
    <el-row :gutter="20">
      <!-- 左侧工具栏 -->
      <el-col :span="6">
        <el-card class="tool-panel">
          <template #header>
            <span>操作面板</span>
          </template>
          
          <!-- 图片上传 -->
          <div class="upload-section">
            <el-upload
              class="upload-demo"
              :auto-upload="true"
              :on-success="handleUploadSuccess"
              :on-error="handleUploadError"
              :before-upload="beforeUpload"
              :action="uploadAction"
              :headers="uploadHeaders"
              :show-file-list="false"
            >
              <el-button type="primary" :icon="Upload">上传图片</el-button>
            </el-upload>
          </div>

          <!-- 操作类型选择 -->
          <div class="operation-section" v-if="currentImage">
            <el-divider>操作类型</el-divider>
            
            <el-radio-group v-model="operationType" @change="handleOperationChange">
              <el-radio label="select">识别与翻译</el-radio>
              <el-radio label="erase">擦除文字</el-radio>
              <el-radio label="text">添加文字</el-radio>
            </el-radio-group>

            <!-- 识别文字选项（在选择区域后显示） -->
            <div v-if="selectedRegion && operationType === 'select'" class="ocr-options">
              <el-divider></el-divider>
              <el-checkbox v-model="showOCR" @change="handleOCRChange">
                识别文字
              </el-checkbox>
              <div v-if="showOCR" class="ocr-result" style="margin-top: 10px;">
                <el-input
                  v-model="ocrText"
                  type="textarea"
                  :rows="4"
                  placeholder="OCR识别结果将显示在这里..."
                  :disabled="isRecognizing"
                  readonly
                ></el-input>
                <el-button
                  type="primary"
                  @click="handleRecognize"
                  :loading="isRecognizing"
                  :disabled="!selectedRegion"
                  style="width: 100%; margin-top: 10px;"
                >
                  {{ isRecognizing ? '识别中...' : '开始识别' }}
                </el-button>

                <!-- 翻译模块 -->
                <div v-if="ocrText" class="translate-options" style="margin-top: 16px;">
                  <el-select v-model="translateSource" placeholder="源语言" style="width: 100%; margin-top: 10px;">
                    <el-option label="中文" value="zh"></el-option>
                    <el-option label="英文" value="en"></el-option>
                    <el-option label="俄文" value="ru"></el-option>
                  </el-select>
                  <el-select v-model="translateTarget" placeholder="目标语言" style="width: 100%; margin-top: 10px;">
                    <el-option label="中文" value="zh"></el-option>
                    <el-option label="英文" value="en"></el-option>
                    <el-option label="俄文" value="ru"></el-option>
                  </el-select>
                  <el-button 
                    type="primary" 
                    @click="handleTranslate()" 
                    :loading="isTranslating"
                    :disabled="translateSource === translateTarget || !ocrText"
                    style="width: 100%; margin-top: 10px;"
                  >
                    {{ isTranslating ? '翻译中...' : '执行翻译' }}
                  </el-button>
                  <el-input
                    v-if="translationResult"
                    v-model="translationResult"
                    type="textarea"
                    :rows="4"
                    placeholder="翻译结果将显示在这里..."
                    readonly
                    style="margin-top: 10px;"
                  ></el-input>
                </div>
              </div>
            </div>

            <!-- 擦除文字选项 -->
            <div v-if="operationType === 'erase'" class="erase-options">
              <el-divider></el-divider>
              <div style="margin-top: 10px; margin-bottom: 10px; color: #909399; font-size: 12px;">
                <el-icon><InfoFilled /></el-icon>
                提示：在图片上选择要擦除的区域
              </div>
              <div v-if="eraseRegion" style="margin-bottom: 10px; padding: 8px; background-color: #fff3cd; border-radius: 4px; font-size: 12px; color: #856404;">
                <el-icon><Check /></el-icon>
                已选择区域：X={{ eraseRegion.x }}, Y={{ eraseRegion.y }}, 宽={{ eraseRegion.width }}, 高={{ eraseRegion.height }}
              </div>
              <el-button 
                type="warning" 
                @click="handleEraseText" 
                :disabled="!eraseRegion"
                style="width: 100%; margin-top: 10px;"
              >
                擦除文字
              </el-button>
            </div>

            <!-- 文字样式设置（独立添加文字模式） -->
            <div v-if="operationType === 'text'" class="text-options">
              <el-divider></el-divider>
              <div style="margin-top: 10px; margin-bottom: 10px; color: #909399; font-size: 12px;">
                <el-icon><InfoFilled /></el-icon>
                提示：在图片上选择区域以确定文字位置
              </div>
              <div v-if="textPositionRegion" style="margin-bottom: 10px; padding: 8px; background-color: #f0f9ff; border-radius: 4px; font-size: 12px; color: #409EFF;">
                <el-icon><Check /></el-icon>
                已选择位置：X={{ textPositionRegion.x }}, Y={{ textPositionRegion.y }}, 宽={{ textPositionRegion.width }}, 高={{ textPositionRegion.height }}
              </div>
              <el-input 
                v-model="textContent" 
                placeholder="输入文字" 
                style="margin-top: 10px;"
              ></el-input>
              <el-input-number 
                v-model="textSize" 
                :min="12" 
                :max="100" 
                label="字体大小"
                style="width: 100%; margin-top: 10px;"
              ></el-input-number>
              <el-select v-model="textFont" placeholder="选择字体" style="width: 100%; margin-top: 10px;">
                <el-option label="Arial" value="arial.ttf"></el-option>
                <el-option label="Times New Roman" value="times.ttf"></el-option>
                <el-option label="Courier New" value="courier.ttf"></el-option>
              </el-select>
              <el-select v-model="textAlign" placeholder="对齐方式" style="width: 100%; margin-top: 10px;">
                <el-option label="左对齐" value="left"></el-option>
                <el-option label="居中" value="center"></el-option>
                <el-option label="右对齐" value="right"></el-option>
              </el-select>
              <el-color-picker v-model="textColor" style="margin-top: 10px;"></el-color-picker>
              <el-button 
                type="primary" 
                @click="handleAddText" 
                :disabled="!textContent"
                style="width: 100%; margin-top: 10px;"
              >
                添加文字
              </el-button>
            </div>

          </div>

          <!-- 保存按钮 -->
          <div class="save-section" v-if="processedImageUrl">
            <el-divider></el-divider>
            <el-button 
              type="success" 
              @click="handleSave" 
              style="width: 100%;"
            >
              保存图片
            </el-button>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧图片编辑区域 -->
      <el-col :span="18">
        <el-card>
          <template #header>
            <span>图片编辑</span>
          </template>
          
          <div class="image-editor-container">
            <ImageEditor
              v-if="currentImage"
              :image-url="currentImage.url"
              :image-id="currentImage.id"
              :operation-type="operationType"
              @region-selected="handleRegionSelected"
            />
            
            <div v-else class="empty-state">
              <el-empty description="请先上传图片"></el-empty>
            </div>
          </div>

          <!-- 处理后的图片预览 -->
          <div v-if="processedImageUrl" class="processed-preview">
            <el-divider>处理结果</el-divider>
            <img :src="processedImageUrl" alt="处理后的图片" class="processed-image" />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-dialog
      v-model="showDonateDialog"
      width="380px"
      :close-on-click-modal="true"
      :show-close="true"
      custom-class="donate-dialog"
    >
      <div class="donate-dialog-content">
        <img src="/donation/alipay.png" alt="Alipay QR" class="donate-qr" />
        <p class="donate-desc">使用支付宝扫码请我喝杯咖啡 ☕️</p>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload, InfoFilled, Check } from '@element-plus/icons-vue'
import ImageEditor from '../components/ImageEditor.vue'
import { uploadImage, recognizeText, translateText, eraseText, addText, saveImage } from '../api/image'
import { logout } from '../api/auth'

const router = useRouter()
const currentImage = ref(null)
const operationType = ref('select')
const selectedRegion = ref(null)
const eraseRegion = ref(null) // 擦除文字的区域
const textPositionRegion = ref(null) // 文字添加时的位置区域（填充区域）
const processedImageUrl = ref(null)
const processedImageId = ref(null)

// OCR识别相关
const showOCR = ref(false)
const ocrText = ref('')
const isRecognizing = ref(false)
const translationResult = ref('')
const isTranslating = ref(false)
const showDonateDialog = ref(false)

// 翻译相关
const translateSource = ref('zh')
const translateTarget = ref('en')

// 文字相关
const textContent = ref('')
const textSize = ref(24)
const textFont = ref('arial.ttf')
const textColor = ref('#000000')
const textAlign = ref('left')

// 上传配置
const uploadAction = '/api/upload'
const uploadHeaders = {}

const beforeUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  return true
}

const handleUploadSuccess = (response) => {
  currentImage.value = {
    id: response.image_id,
    url: response.url,
    filename: response.filename
  }
  processedImageUrl.value = null
  selectedRegion.value = null
  eraseRegion.value = null
  textPositionRegion.value = null
  ElMessage.success('图片上传成功!')
}

const handleUploadError = () => {
  ElMessage.error('图片上传失败!')
}

const handleOperationChange = () => {
  if (operationType.value === 'select') {
    // 切换到选择区域模式时，清除其他操作相关的区域
    eraseRegion.value = null
    textPositionRegion.value = null
  } else if (operationType.value === 'erase') {
    // 切换到擦除文字模式时，清除OCR相关状态和其他区域
    showOCR.value = false
    ocrText.value = ''
    translationResult.value = ''
    textPositionRegion.value = null
  } else if (operationType.value === 'text') {
    // 切换到文字添加模式时，不清除textPositionRegion（保留用户选择）
    // 清除OCR相关状态和其他区域
    showOCR.value = false
    ocrText.value = ''
    translationResult.value = ''
    eraseRegion.value = null
  } else {
    // 切换操作类型时，清除所有相关状态
    showOCR.value = false
    ocrText.value = ''
    translationResult.value = ''
    eraseRegion.value = null
    textPositionRegion.value = null
  }
}

const handleOCRChange = (checked) => {
  if (!checked) {
    ocrText.value = ''
    translationResult.value = ''
  }
}

const handleRecognize = async () => {
  if (!selectedRegion.value) {
    ElMessage.warning('请先选择要识别的区域!')
    return
  }

  try {
    isRecognizing.value = true
    ElMessage.info('正在识别文字，请稍候...')
    const response = await recognizeText({
      image_id: currentImage.value.id,
      region: {
        x: selectedRegion.value.x,
        y: selectedRegion.value.y,
        width: selectedRegion.value.width,
        height: selectedRegion.value.height
      }
    })
    
    if (response.text) {
      ocrText.value = response.text
      translationResult.value = ''
      ElMessage.success('识别完成!')
    } else {
      ocrText.value = ''
      translationResult.value = ''
      ElMessage.warning('未识别到文字')
    }
  } catch (error) {
    ElMessage.error('识别失败: ' + (error.response?.data?.detail || error.message))
    ocrText.value = ''
  } finally {
    isRecognizing.value = false
  }
}

const handleRegionSelected = (region) => {
  if (operationType.value === 'erase') {
    // 擦除文字模式：保存为擦除区域
    eraseRegion.value = region
  } else if (operationType.value === 'text') {
    // 文字添加模式：保存为填充区域
    textPositionRegion.value = region
    ElMessage.success('已选择填充区域，可以添加文字了')
  } else {
    // 选择区域模式：保存为选择区域
    selectedRegion.value = region
    // 选择新区域时，重置OCR相关状态
    showOCR.value = false
    ocrText.value = ''
    translationResult.value = ''
  }
}

const handleTranslate = async (auto = false) => {
  const text = ocrText.value.trim()
  if (!text) {
    translationResult.value = ''
    if (!auto) {
      ElMessage.warning('请先识别文字!')
    }
    return
  }

  if (translateSource.value === translateTarget.value) {
    if (!auto) {
      ElMessage.warning('源语言和目标语言不能相同!')
    }
    return
  }

  try {
    isTranslating.value = true
    if (!auto) {
      ElMessage.info('正在翻译，请稍候...')
    }
    const response = await translateText({
      text,
      source_lang: translateSource.value,
      target_lang: translateTarget.value
    })
    
    if (response.translated_text) {
      translationResult.value = response.translated_text
      if (!auto) {
        ElMessage.success('翻译完成!')
      }
    } else {
      translationResult.value = ''
      if (!auto) {
        ElMessage.warning(response.message || '未获取到翻译结果')
      }
    }
  } catch (error) {
    translationResult.value = ''
    if (!auto) {
      ElMessage.error('翻译失败: ' + (error.response?.data?.detail || error.message))
    }
  } finally {
    isTranslating.value = false
  }
}

watch([ocrText, translateSource, translateTarget], () => {
  translationResult.value = ''
})

const handleEraseText = async () => {
  if (!eraseRegion.value) {
    ElMessage.warning('请先选择要擦除的区域!')
    return
  }

  try {
    ElMessage.info('正在擦除文字...')
    const response = await eraseText({
      image_id: currentImage.value.id,
      region: {
        x: eraseRegion.value.x,
        y: eraseRegion.value.y,
        width: eraseRegion.value.width,
        height: eraseRegion.value.height
      }
    })
    
    processedImageUrl.value = response.url
    processedImageId.value = response.processed_id
    currentImage.value.url = response.url
    currentImage.value.id = response.processed_id
    eraseRegion.value = null
    ElMessage.success('文字擦除成功!')
  } catch (error) {
    ElMessage.error('擦除文字失败: ' + (error.response?.data?.detail || error.message))
  }
}

const handleAddText = async () => {
  if (!textContent.value) {
    ElMessage.warning('请输入文字内容!')
    return
  }

  // 准备添加文字的参数
  const params = {
    image_id: currentImage.value.id,
    text: textContent.value,
    font_size: textSize.value,
    font_family: textFont.value,
    color: textColor.value,
    align: textAlign.value
  }

  // 添加文字模式：使用textPositionRegion填充
  if (textPositionRegion.value) {
    // 设置填充区域
    params.x = textPositionRegion.value.x
    params.y = textPositionRegion.value.y
    params.width = textPositionRegion.value.width
    params.height = textPositionRegion.value.height
  } else {
    // 默认位置
    params.x = 100
    params.y = 100
    ElMessage.warning('建议先选择区域，将使用默认位置添加')
  }

  try {
    ElMessage.info('正在添加文字...')
    const response = await addText(params)
    
    processedImageUrl.value = response.url
    processedImageId.value = response.processed_id
    currentImage.value.url = response.url
    currentImage.value.id = response.processed_id
    textContent.value = ''
    // 清除区域选择，方便下次使用
    textPositionRegion.value = null
    ElMessage.success('文字添加成功!')
  } catch (error) {
    ElMessage.error('添加文字失败: ' + (error.response?.data?.detail || error.message))
  }
}

const handleSave = async () => {
  if (!processedImageId.value) {
    ElMessage.warning('没有可保存的图片!')
    return
  }

  try {
    const response = await saveImage({
      processed_id: processedImageId.value
    })
    
    // 创建下载链接
    const blob = new Blob([response], { type: 'image/jpeg' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `processed_${processedImageId.value}.jpg`
    link.click()
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('图片保存成功!')
  } catch (error) {
    ElMessage.error('保存失败: ' + (error.message || '未知错误'))
  }
}

const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要登出吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    const token = localStorage.getItem('auth_token')
    if (token) {
      try {
        await logout(token)
      } catch (error) {
        // 即使登出API失败，也清除本地token
        console.error('登出API调用失败:', error)
      }
    }
    
    // 清除本地token
    localStorage.removeItem('auth_token')
    ElMessage.success('已登出')
    // 跳转到登录页
    router.push('/login')
  } catch (error) {
    // 用户取消登出
    if (error !== 'cancel') {
      console.error('登出失败:', error)
    }
  }
}
</script>

<style scoped>
.home-container {
  width: 100%;
}

.donate-entry {
  position: fixed;
  top: 12px;
  right: 24px;
  z-index: 1000;
}

.tool-panel {
  height: fit-content;
}

.upload-section {
  margin-bottom: 20px;
}

.operation-section {
  margin-top: 20px;
}

.translate-options,
.text-options,
.ocr-options {
  margin-top: 15px;
}

.ocr-result {
  animation: slideDown 0.3s ease-out;
}

.donate-dialog .el-dialog__body {
  padding-top: 10px;
}

.donate-dialog-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.donate-qr {
  width: 260px;
  border-radius: 16px;
  box-shadow: 0 10px 35px rgba(0, 0, 0, 0.15);
}

.donate-desc {
  font-size: 14px;
  color: #606266;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.save-section {
  margin-top: 20px;
}

.image-editor-container {
  width: 100%;
  min-height: 500px;
  height: 70vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #fafafa;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 10px;
}

.empty-state {
  width: 100%;
  height: 400px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.processed-preview {
  margin-top: 20px;
}

.processed-image {
  max-width: 100%;
  height: auto;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
}
</style>

