export type AgentStatus = 'active' | 'idle' | 'busy' | 'error' | 'disabled'

export interface Agent {
  id: string
  name: string
  type: string
  status: AgentStatus
  health: number
  activeTasks: number
  totalExecutions: number
  averageRuntime: number
  successRate: number
  lastActivity: string
  version: string
  domain: string
  capabilities: string[]
}

export const DEFAULT_AGENTS: Agent[] = [
  {
    id: 'agent-planner',
    name: 'Planner Agent',
    type: 'planner',
    status: 'idle',
    health: 98,
    activeTasks: 0,
    totalExecutions: 45,
    averageRuntime: 1.2,
    successRate: 97.8,
    lastActivity: new Date(Date.now() - 2 * 60000).toISOString(),
    version: '2.1.0',
    domain: 'system',
    capabilities: ['plan_decomposition', 'goal_management', 'constraint_analysis'],
  },
  {
    id: 'agent-knowledge',
    name: 'Knowledge Agent',
    type: 'knowledge',
    status: 'idle',
    health: 95,
    activeTasks: 1,
    totalExecutions: 128,
    averageRuntime: 2.1,
    successRate: 94.5,
    lastActivity: new Date(Date.now() - 5 * 60000).toISOString(),
    version: '1.8.3',
    domain: 'knowledge',
    capabilities: ['document_retrieval', 'content_classification', 'semantic_search'],
  },
  {
    id: 'agent-evidence',
    name: 'Evidence Agent',
    type: 'evidence',
    status: 'active',
    health: 92,
    activeTasks: 2,
    totalExecutions: 89,
    averageRuntime: 3.0,
    successRate: 91.2,
    lastActivity: new Date(Date.now() - 1 * 60000).toISOString(),
    version: '1.9.1',
    domain: 'evidence',
    capabilities: ['evidence_collection', 'source_validation', 'quality_scoring'],
  },
  {
    id: 'agent-rules',
    name: 'Rules Agent',
    type: 'rules',
    status: 'idle',
    health: 99,
    activeTasks: 0,
    totalExecutions: 234,
    averageRuntime: 1.8,
    successRate: 99.1,
    lastActivity: new Date(Date.now() - 8 * 60000).toISOString(),
    version: '2.0.0',
    domain: 'rules',
    capabilities: ['rule_evaluation', 'conflict_detection', 'priority_resolution'],
  },
  {
    id: 'agent-reasoning',
    name: 'Reasoning Agent',
    type: 'reasoning',
    status: 'busy',
    health: 88,
    activeTasks: 3,
    totalExecutions: 67,
    averageRuntime: 4.2,
    successRate: 87.3,
    lastActivity: new Date(Date.now() - 0.5 * 60000).toISOString(),
    version: '1.7.2',
    domain: 'reasoning',
    capabilities: ['hypothesis_generation', 'inference_engine', 'contradiction_detection'],
  },
  {
    id: 'agent-recommendation',
    name: 'Recommendation Agent',
    type: 'recommendation',
    status: 'idle',
    health: 93,
    activeTasks: 1,
    totalExecutions: 56,
    averageRuntime: 3.5,
    successRate: 90.8,
    lastActivity: new Date(Date.now() - 3 * 60000).toISOString(),
    version: '1.6.4',
    domain: 'recommendation',
    capabilities: ['candidate_generation', 'feasibility_analysis', 'portfolio_optimization'],
  },
  {
    id: 'agent-execution',
    name: 'Execution Agent',
    type: 'execution',
    status: 'active',
    health: 96,
    activeTasks: 2,
    totalExecutions: 34,
    averageRuntime: 5.1,
    successRate: 85.7,
    lastActivity: new Date(Date.now() - 4 * 60000).toISOString(),
    version: '1.5.1',
    domain: 'execution',
    capabilities: ['task_execution', 'compensation_management', 'progress_tracking'],
  },
]
