export type AssetType =
  | 'SOLAR_PANEL'
  | 'WIND_TURBINE'
  | 'TRANSFORMER'
  | 'BATTERY'
  | 'SENSOR'

export type AssetStatus = 'ACTIVE' | 'INACTIVE' | 'DECOMMISSIONED' | 'MAINTENANCE' | 'ALERT'

export interface EnergyAsset {
  id: string
  name: string
  type: AssetType
  status: AssetStatus
  location: string
  ratedCapacity: number
  manufacturer: string
  model: string
  installationDate: string
  tags: string[]
  healthScore: number
  lastReading?: number
  lastReadingUnit?: string
  readingCount: number
}

export interface AssetReading {
  timestamp: string
  value: number
  unit: string
  quality: 'good' | 'suspect' | 'bad'
}

export interface MaintenanceRecord {
  id: string
  type: string
  description: string
  technician: string
  date: string
  durationHours: number
  status: 'scheduled' | 'in_progress' | 'completed' | 'cancelled'
}

export interface AssetAlert {
  id: string
  severity: 'critical' | 'warning' | 'info'
  title: string
  description: string
  timestamp: string
  acknowledged: boolean
}

export interface AssetRecommendation {
  id: string
  title: string
  priority: 'critical' | 'high' | 'medium' | 'low'
  description: string
  createdAt: string
  status: 'active' | 'implemented' | 'rejected'
}

export interface AssetDetail {
  asset: EnergyAsset
  readings: AssetReading[]
  maintenance: MaintenanceRecord[]
  alerts: AssetAlert[]
  recommendations: AssetRecommendation[]
}

export interface AssetTypeGroup {
  type: AssetType
  label: string
  count: number
  icon: string
  statusCounts: Record<AssetStatus, number>
}
