import { useState, useEffect } from 'react'
import { DEFAULT_SETTINGS } from '@/types/settings'
import type { AppSettings } from '@/types/settings'
import { useTheme } from '@/hooks/useTheme'
import { cn } from '@/lib/utils'
import {
  Save, Settings, Bot, Palette, Upload, BrainCircuit,
  ThumbsUp, User, ChevronDown, ChevronRight, RefreshCw, Server,
} from 'lucide-react'
import { Card } from '@/components/Card'
import { Button } from '@/components/Button'

const STORAGE_KEY = 'adip_settings'

function loadSettings(): AppSettings {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) return { ...DEFAULT_SETTINGS, ...JSON.parse(raw) }
  } catch { /* ignore */ }
  return DEFAULT_SETTINGS
}

function saveSettings(settings: AppSettings) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(settings))
}

type SectionKey = 'general' | 'llm' | 'api' | 'theme' | 'import' | 'reasoning' | 'recommendations' | 'user'

const SECTIONS: { key: SectionKey; label: string; icon: React.ReactNode }[] = [
  { key: 'general', label: 'General', icon: <Settings className="h-4 w-4" /> },
  { key: 'llm', label: 'LLM Provider', icon: <Bot className="h-4 w-4" /> },
  { key: 'api', label: 'API Configuration', icon: <Server className="h-4 w-4" /> },
  { key: 'theme', label: 'Theme', icon: <Palette className="h-4 w-4" /> },
  { key: 'import', label: 'Import Settings', icon: <Upload className="h-4 w-4" /> },
  { key: 'reasoning', label: 'Reasoning Configuration', icon: <BrainCircuit className="h-4 w-4" /> },
  { key: 'recommendations', label: 'Recommendation Threshold', icon: <ThumbsUp className="h-4 w-4" /> },
  { key: 'user', label: 'User Preferences', icon: <User className="h-4 w-4" /> },
]

export default function SettingsPage() {
  const [settings, setSettings] = useState<AppSettings>(loadSettings)
  const [saved, setSaved] = useState(false)
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['general']))
  const { theme, setTheme } = useTheme()

  useEffect(() => { if (theme) setSettings(prev => ({ ...prev, theme: { ...prev.theme, mode: theme } })) }, [theme])

  const update = <K extends keyof AppSettings>(section: K, values: Partial<AppSettings[K]>) => {
    setSettings(prev => ({ ...prev, [section]: { ...prev[section], ...values } }))
  }

  const handleSave = () => {
    saveSettings(settings)
    if (settings.theme.mode !== theme && (settings.theme.mode === 'light' || settings.theme.mode === 'dark')) setTheme(settings.theme.mode)
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  const handleReset = () => {
    setSettings(DEFAULT_SETTINGS)
    saveSettings(DEFAULT_SETTINGS)
  }

  const toggleSection = (key: string) => {
    setExpandedSections(prev => {
      const next = new Set(prev)
      if (next.has(key)) next.delete(key); else next.add(key)
      return next
    })
  }

  const renderField = (label: string, desc: string, children: React.ReactNode) => (
    <div className="flex items-start justify-between py-3">
      <div className="space-y-0.5 flex-1">
        <label className="text-sm font-medium">{label}</label>
        <p className="text-xs text-muted-foreground">{desc}</p>
      </div>
      <div className="shrink-0 ml-4">{children}</div>
    </div>
  )

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Settings</h1>
          <p className="text-sm text-muted-foreground mt-1">Platform configuration and preferences</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={handleReset} className="text-xs">
            <RefreshCw className="h-3.5 w-3.5" /> Reset
          </Button>
          <Button size="sm" onClick={handleSave} className="text-xs">
            <Save className="h-3.5 w-3.5" /> {saved ? 'Saved!' : 'Save Changes'}
          </Button>
        </div>
      </div>

      <div className="space-y-3">
        {SECTIONS.map(section => {
          const isExpanded = expandedSections.has(section.key)
          return (
            <Card key={section.key} className="overflow-hidden">
              <button onClick={() => toggleSection(section.key)}
                className="w-full flex items-center justify-between p-4 hover:bg-muted/30 transition-colors text-left">
                <div className="flex items-center gap-3">
                  <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10 text-primary">
                    {section.icon}
                  </div>
                  <span className="text-sm font-semibold">{section.label}</span>
                </div>
                {isExpanded ? <ChevronDown className="h-4 w-4 text-muted-foreground" /> : <ChevronRight className="h-4 w-4 text-muted-foreground" />}
              </button>
              {isExpanded && (
                <div className="px-4 pb-4 border-t border-border divide-y divide-border/50">
                  {section.key === 'general' && (
                    <>
                      {renderField('Platform Name', 'The display name for this platform instance',
                        <input type="text" value={settings.general.platformName} onChange={e => update('general', { platformName: e.target.value })}
                          className="w-48 bg-background border rounded-lg px-3 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-primary/30" />)}
                      {renderField('Timezone', 'Default timezone for date/time display',
                        <select value={settings.general.timezone} onChange={e => update('general', { timezone: e.target.value })}
                          className="bg-background border rounded-lg px-3 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-primary/30">
                          <option>UTC</option><option>America/New_York</option><option>America/Chicago</option><option>America/Denver</option><option>America/Los_Angeles</option>
                        </select>)}
                      {renderField('Date Format', 'Format for date display across the platform',
                        <select value={settings.general.dateFormat} onChange={e => update('general', { dateFormat: e.target.value })}
                          className="bg-background border rounded-lg px-3 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-primary/30">
                          <option>YYYY-MM-DD</option><option>MM/DD/YYYY</option><option>DD/MM/YYYY</option>
                        </select>)}
                      {renderField('Language', 'Platform language preference',
                        <select value={settings.general.language} onChange={e => update('general', { language: e.target.value })}
                          className="bg-background border rounded-lg px-3 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-primary/30">
                          <option>en-US</option><option>en-GB</option><option>es</option><option>fr</option><option>de</option>
                        </select>)}
                      {renderField('Notifications', 'Enable in-platform notifications',
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input type="checkbox" checked={settings.general.notificationsEnabled} onChange={e => update('general', { notificationsEnabled: e.target.checked })} className="sr-only peer" />
                          <div className="w-9 h-5 bg-muted rounded-full peer peer-checked:bg-primary peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all" />
                        </label>)}
                    </>
                  )}
                  {section.key === 'llm' && (
                    <>
                      {renderField('Provider', 'AI provider for the Copilot',
                        <select value={settings.llm.provider} onChange={e => update('llm', { provider: e.target.value })}
                          className="bg-background border rounded-lg px-3 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-primary/30">
                          <option>OpenAI</option><option>Anthropic</option><option>Azure OpenAI</option><option>Local</option>
                        </select>)}
                      {renderField('Model', 'Model identifier',
                        <input type="text" value={settings.llm.model} onChange={e => update('llm', { model: e.target.value })}
                          className="w-48 bg-background border rounded-lg px-3 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-primary/30" />)}
                      {renderField('Temperature', 'Response creativity (0 = deterministic, 1 = creative)',
                        <input type="number" min="0" max="2" step="0.1" value={settings.llm.temperature} onChange={e => update('llm', { temperature: parseFloat(e.target.value) || 0.7 })}
                          className="w-20 bg-background border rounded-lg px-3 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-primary/30" />)}
                      {renderField('Max Tokens', 'Maximum response length',
                        <input type="number" value={settings.llm.maxTokens} onChange={e => update('llm', { maxTokens: parseInt(e.target.value) || 2048 })}
                          className="w-20 bg-background border rounded-lg px-3 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-primary/30" />)}
                    </>
                  )}
                  {section.key === 'api' && (
                    <>
                      {renderField('Base URL', 'Backend API endpoint',
                        <input type="text" value={settings.api.baseUrl} onChange={e => update('api', { baseUrl: e.target.value })}
                          className="w-64 bg-background border rounded-lg px-3 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-primary/30" />)}
                      {renderField('Timeout', 'Request timeout in seconds',
                        <input type="number" value={settings.api.timeout} onChange={e => update('api', { timeout: parseInt(e.target.value) || 30 })}
                          className="w-20 bg-background border rounded-lg px-3 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-primary/30" />)}
                      {renderField('Retry Count', 'Number of retry attempts on failure',
                        <input type="number" min="0" max="10" value={settings.api.retryCount} onChange={e => update('api', { retryCount: parseInt(e.target.value) || 3 })}
                          className="w-20 bg-background border rounded-lg px-3 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-primary/30" />)}
                    </>
                  )}
                  {section.key === 'theme' && (
                    <>
                      {renderField('Theme Mode', 'Choose between light or dark mode',
                        <div className="flex gap-1">
                          {(['light', 'dark'] as const).map(m => (
                            <button key={m} onClick={() => { update('theme', { mode: m }); setTheme(m) }}
                              className={cn('px-3 py-1.5 text-xs rounded-lg border capitalize transition-colors', settings.theme.mode === m ? 'bg-primary text-primary-foreground border-primary' : 'bg-card text-muted-foreground hover:text-foreground')}>
                              {m}
                            </button>
                          ))}
                        </div>)}
                      {renderField('Primary Color', 'Platform accent color',
                        <div className="flex gap-1">
                          {['blue', 'violet', 'emerald', 'amber', 'rose'].map(c => (
                            <button key={c} onClick={() => update('theme', { primaryColor: c })}
                              className={cn('h-6 w-6 rounded-full border-2 transition-all', settings.theme.primaryColor === c ? 'border-foreground scale-110' : 'border-transparent')}
                              style={{ backgroundColor: c === 'blue' ? '#3b82f6' : c === 'violet' ? '#8b5cf6' : c === 'emerald' ? '#10b981' : c === 'amber' ? '#f59e0b' : '#f43f5e' }} />
                          ))}
                        </div>)}
                      {renderField('Sidebar', 'Default sidebar state',
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input type="checkbox" checked={!settings.theme.sidebarCollapsed} onChange={e => update('theme', { sidebarCollapsed: !e.target.checked })} className="sr-only peer" />
                          <div className="w-9 h-5 bg-muted rounded-full peer peer-checked:bg-primary peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all" />
                        </label>)}
                      {renderField('Font Size', 'Content font size preference',
                        <select value={settings.theme.fontSize} onChange={e => update('theme', { fontSize: e.target.value as 'small' | 'medium' | 'large' })}
                          className="bg-background border rounded-lg px-3 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-primary/30">
                          <option value="small">Small</option><option value="medium">Medium</option><option value="large">Large</option>
                        </select>)}
                    </>
                  )}
                  {section.key === 'import' && (
                    <>
                      {renderField('Default Delimiter', 'CSV delimiter character',
                        <input type="text" value={settings.import.defaultDelimiter} onChange={e => update('import', { defaultDelimiter: e.target.value })}
                          className="w-16 bg-background border rounded-lg px-3 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-primary/30" />)}
                      {renderField('Max File Size', 'Maximum upload file size in MB',
                        <input type="number" value={settings.import.maxFileSize} onChange={e => update('import', { maxFileSize: parseInt(e.target.value) || 50 })}
                          className="w-20 bg-background border rounded-lg px-3 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-primary/30" />)}
                      {renderField('Auto-Classify', 'Automatically classify uploaded files',
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input type="checkbox" checked={settings.import.autoClassify} onChange={e => update('import', { autoClassify: e.target.checked })} className="sr-only peer" />
                          <div className="w-9 h-5 bg-muted rounded-full peer peer-checked:bg-primary peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all" />
                        </label>)}
                      {renderField('Run Post-Import', 'Execute post-import pipeline',
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input type="checkbox" checked={settings.import.runPostImport} onChange={e => update('import', { runPostImport: e.target.checked })} className="sr-only peer" />
                          <div className="w-9 h-5 bg-muted rounded-full peer peer-checked:bg-primary peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all" />
                        </label>)}
                    </>
                  )}
                  {section.key === 'reasoning' && (
                    <>
                      {renderField('Default Strategy', 'Reasoning strategy for new sessions',
                        <select value={settings.reasoning.defaultStrategy} onChange={e => update('reasoning', { defaultStrategy: e.target.value })}
                          className="bg-background border rounded-lg px-3 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-primary/30">
                          <option value="analytical">Analytical</option><option value="deductive">Deductive</option><option value="inductive">Inductive</option><option value="abductive">Abductive</option>
                        </select>)}
                      {renderField('Max Hypotheses', 'Maximum hypotheses per session',
                        <input type="number" min="1" max="20" value={settings.reasoning.maxHypotheses} onChange={e => update('reasoning', { maxHypotheses: parseInt(e.target.value) || 5 })}
                          className="w-20 bg-background border rounded-lg px-3 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-primary/30" />)}
                      {renderField('Confidence Threshold', 'Minimum confidence for accepted hypotheses',
                        <input type="number" min="0" max="1" step="0.05" value={settings.reasoning.confidenceThreshold} onChange={e => update('reasoning', { confidenceThreshold: parseFloat(e.target.value) || 0.6 })}
                          className="w-20 bg-background border rounded-lg px-3 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-primary/30" />)}
                      {renderField('Contradiction Detection', 'Enable automatic contradiction detection',
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input type="checkbox" checked={settings.reasoning.enableContradictionDetection} onChange={e => update('reasoning', { enableContradictionDetection: e.target.checked })} className="sr-only peer" />
                          <div className="w-9 h-5 bg-muted rounded-full peer peer-checked:bg-primary peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all" />
                        </label>)}
                    </>
                  )}
                  {section.key === 'recommendations' && (
                    <>
                      {renderField('Confidence Threshold', 'Minimum confidence for active recommendations',
                        <input type="number" min="0" max="1" step="0.05" value={settings.recommendations.confidenceThreshold} onChange={e => update('recommendations', { confidenceThreshold: parseFloat(e.target.value) || 0.65 })}
                          className="w-20 bg-background border rounded-lg px-3 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-primary/30" />)}
                      {renderField('Risk Threshold', 'Maximum acceptable risk level',
                        <input type="number" min="0" max="1" step="0.05" value={settings.recommendations.riskThreshold} onChange={e => update('recommendations', { riskThreshold: parseFloat(e.target.value) || 0.5 })}
                          className="w-20 bg-background border rounded-lg px-3 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-primary/30" />)}
                      {renderField('Max Alternatives', 'Maximum alternatives per recommendation',
                        <input type="number" min="1" max="10" value={settings.recommendations.maxAlternatives} onChange={e => update('recommendations', { maxAlternatives: parseInt(e.target.value) || 3 })}
                          className="w-20 bg-background border rounded-lg px-3 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-primary/30" />)}
                      {renderField('Portfolio Optimization', 'Enable portfolio-level optimization',
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input type="checkbox" checked={settings.recommendations.enablePortfolioOptimization} onChange={e => update('recommendations', { enablePortfolioOptimization: e.target.checked })} className="sr-only peer" />
                          <div className="w-9 h-5 bg-muted rounded-full peer peer-checked:bg-primary peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all" />
                        </label>)}
                    </>
                  )}
                  {section.key === 'user' && (
                    <>
                      {renderField('Show Notifications', 'Display notification badges and alerts',
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input type="checkbox" checked={settings.user.showNotifications} onChange={e => update('user', { showNotifications: e.target.checked })} className="sr-only peer" />
                          <div className="w-9 h-5 bg-muted rounded-full peer peer-checked:bg-primary peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all" />
                        </label>)}
                      {renderField('Email Digest', 'Receive daily email digest of platform activity',
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input type="checkbox" checked={settings.user.emailDigest} onChange={e => update('user', { emailDigest: e.target.checked })} className="sr-only peer" />
                          <div className="w-9 h-5 bg-muted rounded-full peer peer-checked:bg-primary peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all" />
                        </label>)}
                      {renderField('Dashboard Refresh', 'Dashboard auto-refresh interval in seconds',
                        <input type="number" min="10" max="300" step="10" value={settings.user.dashboardRefreshInterval} onChange={e => update('user', { dashboardRefreshInterval: parseInt(e.target.value) || 30 })}
                          className="w-20 bg-background border rounded-lg px-3 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-primary/30" />)}
                    </>
                  )}
                </div>
              )}
            </Card>
          )
        })}
      </div>
    </div>
  )
}
