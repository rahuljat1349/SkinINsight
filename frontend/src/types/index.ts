// Analysis Types

export interface AcneAnalysis {
  severity: 'None' | 'Mild' | 'Moderate' | 'Severe'
  count?: number | null
}

export interface SkinAnalysis {
  oiliness: number
  hydration: number
  redness: 'Low' | 'Moderate' | 'High'
  pigmentation: 'None' | 'Mild' | 'Moderate' | 'Severe'
  wrinkles: 'Minimal' | 'Mild' | 'Moderate' | 'Severe'
  pores: 'Small' | 'Medium' | 'Large'
  acne: AcneAnalysis
  texture?: number | null
  skin_tone?: string | null
}

export interface IngredientRecommendation {
  ingredient: string
  priority: 'High' | 'Medium' | 'Low'
  reason: string
  suggested_frequency?: string | null
  usage_notes?: string | null
  precautions?: string | null
}

export interface IngredientInteraction {
  ingredients: string[]
  reason: string
  suggestion: string
}

export interface AnalysisResponse {
  overall_score: number
  skin_type: 'Oily' | 'Dry' | 'Combination' | 'Normal'
  analysis: SkinAnalysis
  recommendations: IngredientRecommendation[]
  interactions: IngredientInteraction[]
  summary: string
  home_remedies: string
  wishing_message: string
  disclaimer: string
}

// Error Types

export interface ErrorDetail {
  code: string
  message: string
  user_message: string
}

export interface ErrorResponse {
  error: ErrorDetail
  success: boolean
}

// Image Validation Types

export interface ImageValidationError {
  code: string
  message: string
  userMessage: string
}

// User Info Types

export interface UserInfo {
  age_group: string
  skin_type_self: string
  gender: string
  sensitive_skin: string
}

export const AGE_GROUPS = ['18-24', '25-30', '31-40', '41-50', '50+'] as const
export const SKIN_TYPES = ['Oily', 'Dry', 'Combination'] as const
export const GENDERS = ['Male', 'Female', 'Non-binary / Other'] as const
export const SENSITIVITY_OPTIONS = ['Yes', 'No', 'Sometimes'] as const

// Form Types

export interface AnalysisForm {
  image: File | null
  isValidating: boolean
  isUploading: boolean
  error: string | null
}

// UI State Types

export interface UploadState {
  file: File | null
  previewUrl: string | null
  isDragging: boolean
  validationError: string | null
  uploadProgress: number
  isProcessing: boolean
}

export interface AnalysisState {
  data: AnalysisResponse | null
  isLoading: boolean
  error: ErrorResponse | null
  image: string | null
}
