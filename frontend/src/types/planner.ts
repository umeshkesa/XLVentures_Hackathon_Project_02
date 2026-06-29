export interface Plan {
  plan_id: string
  title: string
  status: 'draft' | 'active' | 'completed' | 'failed'
  description: string
  stages: PlanStage[]
  created_at: string
  updated_at: string
  confidence: number
}

export interface PlanStage {
  name: string
  status: 'pending' | 'in_progress' | 'completed' | 'failed' | 'skipped'
  duration: number
  confidence: number
  input_summary: string
  output_summary: string
  logs: string[]
  agents: string[]
}

export interface Workflow {
  workflow_id: string
  name: string
  status: 'pending' | 'active' | 'completed' | 'failed'
  stages: WorkflowStage[]
  created_at: string
}

export interface WorkflowStage {
  name: string
  agent: string
  status: 'pending' | 'active' | 'completed' | 'failed'
  duration: number
}

export interface OrchestrationStage {
  id: string
  label: string
  icon: string
  agents: string[]
  description: string
  color: string
  status: 'pending' | 'in_progress' | 'completed' | 'failed' | 'skipped'
  duration: number
  confidence: number
  input: string
  output: string
  logs: string[]
}

export const ORCHESTRATION_PIPELINE: OrchestrationStage[] = [
  {
    id: 'user-request',
    label: 'User Request',
    icon: 'User',
    agents: [],
    description: 'Initial user query or trigger event',
    color: 'slate',
    status: 'completed',
    duration: 0,
    confidence: 1,
    input: 'Natural language query',
    output: 'Parse intent and extract parameters',
    logs: [],
  },
  {
    id: 'planner-agent',
    label: 'Planner Agent',
    icon: 'ClipboardList',
    agents: ['Planner Agent'],
    description: 'Decompose request into a structured plan',
    color: 'blue',
    status: 'completed',
    duration: 1.2,
    confidence: 0.95,
    input: 'User request with parameters',
    output: 'Structured plan with goal, constraints, and strategy',
    logs: [],
  },
  {
    id: 'capability-discovery',
    label: 'Capability Discovery',
    icon: 'Search',
    agents: ['Registry Agent'],
    description: 'Discover available capabilities and plugins',
    color: 'cyan',
    status: 'completed',
    duration: 0.8,
    confidence: 0.92,
    input: 'Plan requirements',
    output: 'Matched capabilities and plugins',
    logs: [],
  },
  {
    id: 'workflow-engine',
    label: 'Workflow Engine',
    icon: 'GitBranch',
    agents: ['Workflow Agent'],
    description: 'Orchestrate the execution workflow',
    color: 'indigo',
    status: 'completed',
    duration: 1.5,
    confidence: 0.90,
    input: 'Plan + capabilities',
    output: 'Executable workflow with stage dependencies',
    logs: [],
  },
  {
    id: 'knowledge-agent',
    label: 'Knowledge Agent',
    icon: 'BookOpen',
    agents: ['Knowledge Agent'],
    description: 'Retrieve relevant knowledge documents',
    color: 'emerald',
    status: 'completed',
    duration: 2.1,
    confidence: 0.88,
    input: 'Domain context and query parameters',
    output: 'Matched knowledge documents with relevance scores',
    logs: [],
  },
  {
    id: 'evidence-agent',
    label: 'Evidence Agent',
    icon: 'FileSearch',
    agents: ['Evidence Agent'],
    description: 'Collect and analyze evidence',
    color: 'amber',
    status: 'completed',
    duration: 3.0,
    confidence: 0.91,
    input: 'Evidence collection request',
    output: 'Collected evidence with quality scores',
    logs: [],
  },
  {
    id: 'rules-agent',
    label: 'Rules Agent',
    icon: 'Scale',
    agents: ['Rules Agent'],
    description: 'Evaluate business rules',
    color: 'rose',
    status: 'completed',
    duration: 1.8,
    confidence: 0.94,
    input: 'Context + evidence summary',
    output: 'Triggered rules with impact assessment',
    logs: [],
  },
  {
    id: 'energy-agent',
    label: 'Energy Agent',
    icon: 'Zap',
    agents: ['Energy Agent'],
    description: 'Analyze energy domain data',
    color: 'yellow',
    status: 'completed',
    duration: 2.3,
    confidence: 0.87,
    input: 'Asset data + sensor readings',
    output: 'Energy health assessment and insights',
    logs: [],
  },
  {
    id: 'reasoning-engine',
    label: 'Reasoning Engine',
    icon: 'BrainCircuit',
    agents: ['Reasoning Agent'],
    description: 'Apply reasoning to generate decisions',
    color: 'violet',
    status: 'completed',
    duration: 4.2,
    confidence: 0.85,
    input: 'Knowledge + evidence + rules + energy data',
    output: 'Reasoning path with hypothesis and inference',
    logs: [],
  },
  {
    id: 'recommendation-engine',
    label: 'Recommendation Engine',
    icon: 'ThumbsUp',
    agents: ['Recommendation Agent'],
    description: 'Generate actionable recommendations',
    color: 'orange',
    status: 'completed',
    duration: 3.5,
    confidence: 0.86,
    input: 'Reasoning output + feasibility analysis',
    output: 'Ranked recommendations with confidence',
    logs: [],
  },
  {
    id: 'human-review',
    label: 'Human Review',
    icon: 'ClipboardCheck',
    agents: ['Review Agent'],
    description: 'Human-in-the-loop review and approval',
    color: 'pink',
    status: 'pending',
    duration: 0,
    confidence: 0,
    input: 'Recommendation package',
    output: 'Approved, rejected, or modified decision',
    logs: [],
  },
  {
    id: 'action-execution',
    label: 'Action Execution',
    icon: 'Zap',
    agents: ['Execution Agent'],
    description: 'Execute approved actions',
    color: 'green',
    status: 'pending',
    duration: 0,
    confidence: 0,
    input: 'Approved decision',
    output: 'Executed action with completion report',
    logs: [],
  },
]
