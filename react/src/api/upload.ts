import { compressImageFile } from '@/utils/imageUtils'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

export async function uploadImage(
  file: File,
  onProgress?: (progress: number) => void
): Promise<{ file_id?: string; url: string; width?: number; height?: number }> {
  const formData = new FormData()
  formData.append('file', file)

  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest()

    xhr.upload.onprogress = (event) => {
      if (event.lengthComputable && onProgress) {
        const progress = Math.round((event.loaded * 100) / event.total)
        onProgress(progress)
      }
    }

    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve(JSON.parse(xhr.responseText))
      } else {
        reject(new Error(xhr.statusText))
      }
    }

    xhr.onerror = () => {
      reject(new Error('Network error'))
    }

    xhr.open('POST', `${API_BASE_URL}/api/upload`, true)
    xhr.send(formData)
  })
}
