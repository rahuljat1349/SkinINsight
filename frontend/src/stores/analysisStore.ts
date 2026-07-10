import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { AnalysisResponse, ErrorResponse, UploadState, AnalysisState, UserInfo } from '@/types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

// Error codes that indicate image validation failures
const IMAGE_ERROR_CODES = [
  'no_face_detected',
  'multiple_faces_detected',
  'face_too_small',
  'poor_lighting',
  'excessive_blur',
  'unsupported_image_format',
  'image_too_large',
  'low_resolution'
]

export const useAnalysisStore = defineStore('analysis', () => {
  // State
  const uploadState = ref<UploadState>({
    file: null,
    previewUrl: null,
    isDragging: false,
    validationError: null,
    uploadProgress: 0,
    isProcessing: false
  })

  const analysisState = ref<AnalysisState>({
    data: null,
    isLoading: false,
    error: null,
    image: null
  })

  const userInfo = ref<UserInfo>({
    age_group: '',
    skin_type_self: '',
    gender: '',
    sensitive_skin: ''
  })

  const showQuestions = ref(false)
  const triggerShowQuestions = () => { showQuestions.value = true }

  // Actions
  const setFile = (file: File | null) => {
    uploadState.value.file = file
    uploadState.value.previewUrl = file ? URL.createObjectURL(file) : null
    uploadState.value.validationError = null
    uploadState.value.uploadProgress = 0
    if (!file) showQuestions.value = false
  }

  const setDragging = (isDragging: boolean) => {
    uploadState.value.isDragging = isDragging
  }

  const setValidationError = (error: string | null) => {
    uploadState.value.validationError = error
  }

  const setProcessing = (isProcessing: boolean) => {
    uploadState.value.isProcessing = isProcessing
  }

  const setUploadProgress = (progress: number) => {
    uploadState.value.uploadProgress = progress
  }

  const setAnalysisLoading = (isLoading: boolean) => {
    analysisState.value.isLoading = isLoading
  }

  const setAnalysisError = (error: ErrorResponse | null) => {
    analysisState.value.error = error
  }

  const setUserInfo = (info: UserInfo) => {
    userInfo.value = info
  }

  const setAnalysisData = (data: AnalysisResponse | null, image?: string | null) => {
    analysisState.value.data = data
    analysisState.value.image = image || null
    if (data) {
      analysisState.value.error = null
    }
  }

  const clear = () => {
    uploadState.value = {
      file: null,
      previewUrl: null,
      isDragging: false,
      validationError: null,
      uploadProgress: 0,
      isProcessing: false
    }
    analysisState.value = {
      data: null,
      isLoading: false,
      error: null,
      image: null
    }
    userInfo.value = {
      age_group: '',
      skin_type_self: '',
      gender: '',
      sensitive_skin: ''
    }
    showQuestions.value = false
  }

  // Image validation
  const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB
  const SUPPORTED_FORMATS = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']

  const validateImage = (file: File): { valid: boolean; error: string | null } => {
    // Check file type
    if (!SUPPORTED_FORMATS.includes(file.type)) {
      return {
        valid: false,
        error: 'Unsupported image format. Please upload JPG, JPEG, PNG, or WEBP.'
      }
    }

    // Check file size
    if (file.size > MAX_FILE_SIZE) {
      return {
        valid: false,
        error: 'Image is too large. Maximum size is 10MB.'
      }
    }

    return { valid: true, error: null }
  }

  // Analyze image
  const analyzeImage = async (): Promise<AnalysisResponse> => {
    if (!uploadState.value.file) {
      throw new Error('No file selected')
    }

    if (!userInfo.value.age_group || !userInfo.value.skin_type_self || !userInfo.value.gender || !userInfo.value.sensitive_skin) {
      throw new Error('Please complete all questions about yourself before analyzing.')
    }

    setProcessing(true)
    setAnalysisLoading(true)
    setAnalysisError(null)

    try {
      const formData = new FormData()
      formData.append('file', uploadState.value.file)
      formData.append('age_group', userInfo.value.age_group)
      formData.append('skin_type_self', userInfo.value.skin_type_self)
      formData.append('gender', userInfo.value.gender)
      formData.append('sensitive_skin', userInfo.value.sensitive_skin)

      // Simulate upload progress (actual progress events not supported by all browsers)
      setUploadProgress(10)

      const response = await fetch(`${API_BASE_URL}/v1/analyze`, {
        method: 'POST',
        body: formData,
        // Headers are automatically set by browser for FormData
      })

      setUploadProgress(90)

      if (!response.ok) {
        const errorData: ErrorResponse = await response.json().catch(() => ({
          error: {
            code: 'unknown_error',
            message: `HTTP ${response.status}`,
            user_message: 'An error occurred while processing your image.'
          },
          success: false
        }))
        
        setAnalysisError(errorData)
        
        // If it's an image validation error, show it in the upload state
        if (errorData.error && IMAGE_ERROR_CODES.includes(errorData.error.code)) {
          setValidationError(errorData.error.user_message)
        }
        
        throw new Error(errorData.error?.user_message || 'Analysis failed')
      }

      const result: AnalysisResponse = await response.json()
      setUploadProgress(100)
      
      // Store the result
      setAnalysisData(result, URL.createObjectURL(uploadState.value.file))
      
      return result
    } catch (error) {
      console.error('Analysis error:', error)
      // Only set generic network error if no specific error was already set
      if (!analysisState.value.error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error'
        setAnalysisError({
          error: {
            code: 'network_error',
            message: errorMessage,
            user_message: 'Failed to connect to the analysis service. Please try again.'
          },
          success: false
        })
      }
      throw error
    } finally {
      setProcessing(false)
      setAnalysisLoading(false)
    }
  }

  return {
    // State
    uploadState,
    analysisState,
    userInfo,
    showQuestions,
    
    // Actions
    setFile,
    setDragging,
    setValidationError,
    setProcessing,
    setUploadProgress,
    setAnalysisLoading,
    setAnalysisError,
    setUserInfo,
    setAnalysisData,
    clear,
    triggerShowQuestions,
    
    // Methods
    validateImage,
    analyzeImage
  }
})
