import api from './index'

export const uploadImage = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export const recognizeText = (data) => {
  return api.post('/process/ocr', data)
}

export const translateRegion = (data) => {
  return api.post('/process/translate', data)
}

export const translateText = (data) => {
  return api.post('/process/translate-text', data)
}

export const addText = (data) => {
  return api.post('/add-text', data)
}

export const saveImage = (data) => {
  return api.post('/save', data, {
    responseType: 'blob'
  })
}

