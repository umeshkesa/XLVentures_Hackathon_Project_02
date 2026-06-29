import type { EnergyAsset, AssetDetail, AssetReading, MaintenanceRecord, AssetAlert, AssetRecommendation } from '@/types/assets'

const types: EnergyAsset['type'][] = ['SOLAR_PANEL', 'WIND_TURBINE', 'TRANSFORMER', 'BATTERY', 'SENSOR']
const statuses: EnergyAsset['status'][] = ['ACTIVE', 'ACTIVE', 'ACTIVE', 'MAINTENANCE', 'ALERT', 'INACTIVE']

const mockAssets: EnergyAsset[] = Array.from({ length: 100 }, (_, i) => {
  const type = types[i % 5]
  const baseNames: Record<string, string> = {
    SOLAR_PANEL: 'Solar Panel',
    WIND_TURBINE: 'Wind Turbine',
    TRANSFORMER: 'Transformer',
    BATTERY: 'Battery Bank',
    SENSOR: 'Sensor',
  }
  return {
    id: `${type === 'SOLAR_PANEL' ? 'SP' : type === 'WIND_TURBINE' ? 'WT' : type === 'TRANSFORMER' ? 'TF' : type === 'BATTERY' ? 'BB' : 'SN'}-${String(100 + i).padStart(3, '0')}`,
    name: `${baseNames[type]} #${String(100 + i)}`,
    type,
    status: statuses[i % 6],
    location: ['Zone A', 'Zone B', 'Zone C', 'Zone D', 'Zone E'][i % 5],
    ratedCapacity: [100, 250, 500, 50, 10, 1000][i % 6],
    manufacturer: ['Siemens', 'GE', 'ABB', 'Schneider', 'SMA', 'Huawei'][i % 6],
    model: `Model-${String(2000 + i)}`,
    installationDate: new Date(2020 + (i % 4), i % 12, 1).toISOString(),
    tags: [type.toLowerCase(), 'monitored', 'critical'],
    healthScore: Math.round((85 + Math.random() * 15) * 10) / 10,
    lastReading: Math.round((100 + Math.random() * 900) * 100) / 100,
    lastReadingUnit: type === 'BATTERY' ? 'kWh' : type === 'SENSOR' ? '°C' : 'kW',
    readingCount: Math.floor(1000 + Math.random() * 9000),
  }
})

function mockReadings(_assetId: string): AssetReading[] {
  return Array.from({ length: 24 }, (_, i) => ({
    timestamp: new Date(Date.now() - i * 3600000).toISOString(),
    value: Math.round((100 + Math.sin(i * 0.5) * 50 + Math.random() * 20) * 100) / 100,
    unit: 'kW',
    quality: (['good', 'good', 'good', 'suspect'] as const)[i % 4],
  }))
}

function mockMaintenance(assetId: string): MaintenanceRecord[] {
  return [
    { id: `M-${assetId}-1`, type: 'Routine Inspection', description: 'Quarterly inspection and cleaning', technician: 'John Smith', date: new Date(Date.now() - 86400000 * 30).toISOString(), durationHours: 4, status: 'completed' },
    { id: `M-${assetId}-2`, type: 'Calibration', description: 'Sensor recalibration', technician: 'Lisa Wang', date: new Date(Date.now() - 86400000 * 60).toISOString(), durationHours: 2, status: 'completed' },
    { id: `M-${assetId}-3`, type: 'Preventive Maintenance', description: 'Component replacement', technician: 'John Smith', date: new Date(Date.now() + 86400000 * 14).toISOString(), durationHours: 8, status: 'scheduled' },
  ]
}

function mockAlerts(assetId: string): AssetAlert[] {
  return [
    { id: `A-${assetId}-1`, severity: 'warning', title: 'Efficiency Drop Detected', description: 'Output efficiency dropped below 85% threshold', timestamp: new Date(Date.now() - 3600000 * 3).toISOString(), acknowledged: false },
    { id: `A-${assetId}-2`, severity: 'info', title: 'Scheduled Maintenance Due', description: 'Routine maintenance scheduled within 7 days', timestamp: new Date(Date.now() - 3600000 * 12).toISOString(), acknowledged: true },
    { id: `A-${assetId}-3`, severity: 'critical', title: 'Vibration Threshold Exceeded', description: 'Vibration levels exceed safe operating parameters', timestamp: new Date(Date.now() - 3600000 * 48).toISOString(), acknowledged: false },
  ]
}

function mockRecommendations(assetId: string): AssetRecommendation[] {
  return [
    { id: `R-${assetId}-1`, title: 'Optimize Operating Schedule', priority: 'high', description: 'Adjust operating hours to match peak demand periods', createdAt: new Date(Date.now() - 86400000 * 5).toISOString(), status: 'active' },
    { id: `R-${assetId}-2`, title: 'Replace Worn Components', priority: 'medium', description: 'Identified 3 components approaching end of life', createdAt: new Date(Date.now() - 86400000 * 12).toISOString(), status: 'active' },
    { id: `R-${assetId}-3`, title: 'Upgrade Control Firmware', priority: 'low', description: 'New firmware version available with efficiency improvements', createdAt: new Date(Date.now() - 86400000 * 20).toISOString(), status: 'implemented' },
  ]
}

export interface AssetService {
  list(params: { type?: string; status?: string; search?: string; page: number; limit: number }): Promise<{ assets: EnergyAsset[]; total: number }>
  getById(id: string): Promise<AssetDetail | null>
  getByType(type: string): Promise<{ assets: EnergyAsset[]; total: number }>
}

export function useAssetService(): AssetService {
  return {
    async list({ type, status, search, page, limit }) {
      let filtered = [...mockAssets]
      if (type) filtered = filtered.filter((a) => a.type === type)
      if (status) filtered = filtered.filter((a) => a.status === status)
      if (search) {
        const q = search.toLowerCase()
        filtered = filtered.filter((a) => a.name.toLowerCase().includes(q) || a.id.toLowerCase().includes(q) || a.location.toLowerCase().includes(q))
      }
      const total = filtered.length
      const start = (page - 1) * limit
      const assets = filtered.slice(start, start + limit)
      return { assets, total }
    },
    async getById(id: string) {
      const asset = mockAssets.find((a) => a.id === id)
      if (!asset) return null
      return {
        asset,
        readings: mockReadings(asset.id),
        maintenance: mockMaintenance(asset.id),
        alerts: mockAlerts(asset.id),
        recommendations: mockRecommendations(asset.id),
      }
    },
    async getByType(type: string) {
      const assets = mockAssets.filter((a) => a.type === type)
      return { assets, total: assets.length }
    },
  }
}
