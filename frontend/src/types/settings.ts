export interface AppSettings {
  general: GeneralSettings
  llm: LLMSettings
  api: APISettings
  theme: ThemeSettings
  import: ImportSettings
  reasoning: ReasoningSettings
  recommendations: RecommendationSettings
  user: UserPreferences
}

export interface GeneralSettings {
  platformName: string
  timezone: string
  dateFormat: string
  language: string
  notificationsEnabled: boolean
}

export interface LLMSettings {
  provider: string
  model: string
  temperature: number
  maxTokens: number
  apiEndpoint: string
}

export interface APISettings {
  baseUrl: string
  timeout: number
  retryCount: number
}

export interface ThemeSettings {
  mode: 'light' | 'dark' | 'system'
  primaryColor: string
  sidebarCollapsed: boolean
  fontSize: 'small' | 'medium' | 'large'
}

export interface ImportSettings {
  defaultDelimiter: string
  maxFileSize: number
  autoClassify: boolean
  runPostImport: boolean
  generateRecommendations: boolean
}

export interface ReasoningSettings {
  defaultStrategy: string
  maxHypotheses: number
  confidenceThreshold: number
  enableContradictionDetection: boolean
}

export interface RecommendationSettings {
  confidenceThreshold: number
  riskThreshold: number
  maxAlternatives: number
  enablePortfolioOptimization: boolean
}

export interface UserPreferences {
  showNotifications: boolean
  emailDigest: boolean
  dashboardRefreshInterval: number
}

export const DEFAULT_SETTINGS: AppSettings = {
  general: {
    platformName: 'ADIP Platform',
    timezone: 'UTC',
    dateFormat: 'YYYY-MM-DD',
    language: 'en-US',
    notificationsEnabled: true,
  },
  llm: {
    provider: 'OpenAI',
    model: 'gpt-4o',
    temperature: 0.7,
    maxTokens: 2048,
    apiEndpoint: 'https://api.openai.com/v1',
  },
  api: {
    baseUrl: 'http://localhost:8000/api/v1',
    timeout: 30,
    retryCount: 3,
  },
  theme: {
    mode: 'light',
    primaryColor: 'blue',
    sidebarCollapsed: false,
    fontSize: 'medium',
  },
  import: {
    defaultDelimiter: ',',
    maxFileSize: 50,
    autoClassify: true,
    runPostImport: true,
    generateRecommendations: true,
  },
  reasoning: {
    defaultStrategy: 'analytical',
    maxHypotheses: 5,
    confidenceThreshold: 0.6,
    enableContradictionDetection: true,
  },
  recommendations: {
    confidenceThreshold: 0.65,
    riskThreshold: 0.5,
    maxAlternatives: 3,
    enablePortfolioOptimization: true,
  },
  user: {
    showNotifications: true,
    emailDigest: false,
    dashboardRefreshInterval: 30,
  },
}
