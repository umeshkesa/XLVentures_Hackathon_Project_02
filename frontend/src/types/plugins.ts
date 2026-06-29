export type PluginStatus = 'active' | 'inactive' | 'error' | 'installing'

export interface PluginItem {
  id: string
  name: string
  description: string
  version: string
  status: PluginStatus
  type: string
  domain: string
  capabilities: string[]
  author: string
  installed_at: string
  health: number
  dependencies: string[]
}

export interface PluginCapability {
  name: string
  description: string
  plugin_id: string
  domain: string
  parameters: Record<string, string>
}

export interface RegistryEntry {
  registry_id: string
  name: string
  type: string
  domain: string
  version: string
  status: string
  description: string
  tags: string[]
}

export const DEFAULT_PLUGINS: PluginItem[] = [
  {
    id: 'plg-energy-core',
    name: 'Energy Core Plugin',
    description: 'Core energy domain functionality including asset management, sensor data processing, and topology analysis.',
    version: '2.3.1',
    status: 'active',
    type: 'domain',
    domain: 'energy',
    capabilities: ['asset_management', 'sensor_processing', 'topology_analysis', 'alarm_correlation'],
    author: 'ADIP Engineering',
    installed_at: '2026-01-15T08:00:00Z',
    health: 97,
    dependencies: ['plg-registry-base'],
  },
  {
    id: 'plg-knowledge-base',
    name: 'Knowledge Base Plugin',
    description: 'Document management, content classification, and knowledge retrieval capabilities.',
    version: '1.8.3',
    status: 'active',
    type: 'domain',
    domain: 'knowledge',
    capabilities: ['document_ingestion', 'content_classification', 'semantic_retrieval', 'version_management'],
    author: 'ADIP Engineering',
    installed_at: '2026-01-10T10:00:00Z',
    health: 95,
    dependencies: ['plg-registry-base'],
  },
  {
    id: 'plg-evidence-engine',
    name: 'Evidence Engine Plugin',
    description: 'Evidence collection, validation, fusion, and traceability capabilities.',
    version: '1.9.1',
    status: 'active',
    type: 'domain',
    domain: 'evidence',
    capabilities: ['evidence_collection', 'source_validation', 'conflict_detection', 'traceability'],
    author: 'ADIP Engineering',
    installed_at: '2026-02-01T09:00:00Z',
    health: 92,
    dependencies: ['plg-registry-base', 'plg-knowledge-base'],
  },
  {
    id: 'plg-rules-engine',
    name: 'Rules Engine Plugin',
    description: 'Business rule evaluation, conflict resolution, and policy enforcement.',
    version: '2.0.0',
    status: 'active',
    type: 'domain',
    domain: 'rules',
    capabilities: ['rule_evaluation', 'conflict_detection', 'policy_enforcement', 'priority_resolution'],
    author: 'ADIP Engineering',
    installed_at: '2026-01-20T11:00:00Z',
    health: 99,
    dependencies: ['plg-registry-base'],
  },
  {
    id: 'plg-reasoning-core',
    name: 'Reasoning Core Plugin',
    description: 'Hypothesis generation, inference engine, and contradiction detection for decision intelligence.',
    version: '1.7.2',
    status: 'active',
    type: 'domain',
    domain: 'reasoning',
    capabilities: ['hypothesis_generation', 'inference_engine', 'contradiction_detection', 'decision_alternatives'],
    author: 'ADIP Engineering',
    installed_at: '2026-02-15T14:00:00Z',
    health: 88,
    dependencies: ['plg-registry-base', 'plg-knowledge-base', 'plg-evidence-engine'],
  },
  {
    id: 'plg-recommendation',
    name: 'Recommendation Engine Plugin',
    description: 'Recommendation generation, feasibility analysis, and portfolio optimization.',
    version: '1.6.4',
    status: 'active',
    type: 'domain',
    domain: 'recommendation',
    capabilities: ['candidate_generation', 'feasibility_analysis', 'cost_analysis', 'portfolio_optimization'],
    author: 'ADIP Engineering',
    installed_at: '2026-03-01T08:00:00Z',
    health: 93,
    dependencies: ['plg-registry-base', 'plg-reasoning-core'],
  },
  {
    id: 'plg-execution',
    name: 'Execution Plugin',
    description: 'Task execution, compensation management, and progress tracking.',
    version: '1.5.1',
    status: 'active',
    type: 'domain',
    domain: 'execution',
    capabilities: ['task_execution', 'compensation_management', 'progress_tracking', 'audit_logging'],
    author: 'ADIP Engineering',
    installed_at: '2026-03-15T10:00:00Z',
    health: 96,
    dependencies: ['plg-registry-base'],
  },
  {
    id: 'plg-registry-base',
    name: 'Registry Base Plugin',
    description: 'Core service registry and capability discovery infrastructure.',
    version: '1.2.0',
    status: 'active',
    type: 'infrastructure',
    domain: 'system',
    capabilities: ['service_registration', 'capability_discovery', 'domain_mapping', 'version_tracking'],
    author: 'ADIP Infrastructure',
    installed_at: '2026-01-01T00:00:00Z',
    health: 100,
    dependencies: [],
  },
  {
    id: 'plg-sandbox',
    name: 'Plugin Sandbox',
    description: 'Isolated execution environment for third-party plugins with resource limits and security policies.',
    version: '1.1.0',
    status: 'inactive',
    type: 'infrastructure',
    domain: 'system',
    capabilities: ['namespace_isolation', 'resource_limiting', 'permission_enforcement', 'audit_trail'],
    author: 'ADIP Security',
    installed_at: '2026-01-05T12:00:00Z',
    health: 100,
    dependencies: ['plg-registry-base'],
  },
  {
    id: 'plg-energy-solar',
    name: 'Solar Domain Extension',
    description: 'Specialized solar energy analytics, panel monitoring, and irradiance forecasting.',
    version: '1.3.0',
    status: 'active',
    type: 'domain',
    domain: 'energy',
    capabilities: ['panel_monitoring', 'irradiance_forecasting', 'solar_analytics', 'inverter_management'],
    author: 'ADIP Energy Team',
    installed_at: '2026-02-10T09:00:00Z',
    health: 94,
    dependencies: ['plg-energy-core'],
  },
]

export const DEFAULT_CAPABILITIES: PluginCapability[] = [
  { name: 'asset_management', description: 'Manage energy assets lifecycle', plugin_id: 'plg-energy-core', domain: 'energy', parameters: {} },
  { name: 'sensor_processing', description: 'Process sensor readings and telemetry', plugin_id: 'plg-energy-core', domain: 'energy', parameters: {} },
  { name: 'document_ingestion', description: 'Ingest knowledge documents', plugin_id: 'plg-knowledge-base', domain: 'knowledge', parameters: {} },
  { name: 'evidence_collection', description: 'Collect evidence from multiple sources', plugin_id: 'plg-evidence-engine', domain: 'evidence', parameters: {} },
  { name: 'rule_evaluation', description: 'Evaluate business rules against context', plugin_id: 'plg-rules-engine', domain: 'rules', parameters: {} },
  { name: 'hypothesis_generation', description: 'Generate reasoning hypotheses', plugin_id: 'plg-reasoning-core', domain: 'reasoning', parameters: {} },
  { name: 'candidate_generation', description: 'Generate recommendation candidates', plugin_id: 'plg-recommendation', domain: 'recommendation', parameters: {} },
  { name: 'task_execution', description: 'Execute approved actions', plugin_id: 'plg-execution', domain: 'execution', parameters: {} },
  { name: 'service_registration', description: 'Register services in the platform registry', plugin_id: 'plg-registry-base', domain: 'system', parameters: {} },
  { name: 'panel_monitoring', description: 'Monitor solar panel performance', plugin_id: 'plg-energy-solar', domain: 'energy', parameters: {} },
]

export const DOMAIN_PLUGIN_COLORS: Record<string, string> = {
  energy: 'text-yellow-500 bg-yellow-500/10 border-yellow-500/30',
  knowledge: 'text-emerald-500 bg-emerald-500/10 border-emerald-500/30',
  evidence: 'text-amber-500 bg-amber-500/10 border-amber-500/30',
  rules: 'text-rose-500 bg-rose-500/10 border-rose-500/30',
  reasoning: 'text-violet-500 bg-violet-500/10 border-violet-500/30',
  recommendation: 'text-orange-500 bg-orange-500/10 border-orange-500/30',
  execution: 'text-green-500 bg-green-500/10 border-green-500/30',
  system: 'text-cyan-500 bg-cyan-500/10 border-cyan-500/30',
}
