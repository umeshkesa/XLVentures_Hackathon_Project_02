import { useState } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { useRecommendationById } from '@/services/recommendationApiService'
import { useReasoningById } from '@/services/reasoningApiService'
import {
  Database, BookOpen, Scale, BrainCircuit, Lightbulb, ArrowDown, ChevronDown, ChevronRight, Clock, BarChart3, Shield, Target
} from 'lucide-react'

const STAGES = [
  { id: 'evidence', label: 'Evidence Collection', icon: Database, color: 'border-purple-500', bg: 'bg-purple-500/10', text: 'text-purple-600' },
  { id: 'knowledge', label: 'Knowledge Retrieved', icon: BookOpen, color: 'border-yellow-500', bg: 'bg-yellow-500/10', text: 'text-yellow-600' },
  { id: 'rules', label: 'Business Rules Applied', icon: Scale, color: 'border-orange-500', bg: 'bg-orange-500/10', text: 'text-orange-600' },
  { id: 'reasoning', label: 'Reasoning Engine', icon: BrainCircuit, color: 'border-blue-500', bg: 'bg-blue-500/10', text: 'text-blue-600' },
  { id: 'recommendation', label: 'Recommendation', icon: Lightbulb, color: 'border-green-500', bg: 'bg-green-500/10', text: 'text-green-600' },
]

export default function ReasoningPipeline() {
  const [searchParams] = useSearchParams()
  const recommendationId = searchParams.get('recommendationId') || ''

  const { data: rec, isLoading: recLoading } = useRecommendationById(recommendationId)
  const { data: reasoning, isLoading: reasoningLoading } = useReasoningById(rec?.reasoningId || '')

  const [expandedStage, setExpandedStage] = useState<string | null>('evidence')

  const toggleStage = (stageId: string) => {
    setExpandedStage(expandedStage === stageId ? null : stageId)
  }

  if (!recommendationId) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Reasoning Pipeline</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Visualize the complete decision-making process from evidence to recommendation.
          </p>
        </div>
        <div className="bg-card rounded-xl border p-8 text-center">
          <BrainCircuit className="h-12 w-12 mx-auto text-muted-foreground mb-3" />
          <h2 className="text-lg font-semibold mb-1">Select a Recommendation</h2>
          <p className="text-sm text-muted-foreground">
            Navigate to a recommendation detail and click "View Reasoning Pipeline" to see the full decision flow.
          </p>
          <Link to="/recommendations" className="inline-block mt-4 px-4 py-2 bg-primary text-primary-foreground text-sm rounded-lg hover:bg-primary/90">
            Go to Recommendations
          </Link>
        </div>
      </div>
    )
  }

  if (recLoading || reasoningLoading) {
    return (
      <div className="flex justify-center py-12">
        <LoadingSpinner size="lg" label="Loading pipeline..." />
      </div>
    )
  }

  if (!rec) {
    return (
      <div className="bg-card rounded-xl border p-8 text-center">
        <h2 className="text-lg font-semibold text-foreground">Recommendation not found</h2>
        <p className="text-sm text-muted-foreground mt-1">Recommendation {recommendationId} does not exist.</p>
      </div>
    )
  }

  const stageContent: Record<string, { title: string; description: string; items: { label: string; value: string; icon?: React.ReactNode }[]; details: string[]; confidence?: number; processingTimeMs?: number }> = {
    evidence: {
      title: 'Evidence Collection',
      description: 'Relevant evidence gathered from sensors, incidents, customer feedback, and other sources.',
      items: (rec.evidenceIds || []).map((eid: string) => ({ label: 'Evidence', value: eid, icon: <Database className="h-3.5 w-3.5 text-purple-500" /> })),
      details: [
        `${(rec.evidenceIds || []).length} evidence sources collected`,
        `Priority: ${rec.priority}`,
        `Risk level assessed: ${rec.riskLevel}`,
      ],
      confidence: rec.confidence * 0.9,
    },
    knowledge: {
      title: 'Knowledge Retrieved',
      description: 'Related knowledge documents, manuals, SOPs, and historical records retrieved.',
      items: (rec.knowledgeIds || []).map((kid: string) => ({ label: 'Knowledge', value: kid, icon: <BookOpen className="h-3.5 w-3.5 text-yellow-500" /> })),
      details: [
        `${(rec.knowledgeIds || []).length} knowledge sources retrieved`,
        `Domain: ${rec.source}`,
      ],
      confidence: rec.confidence * 0.85,
    },
    rules: {
      title: 'Business Rules Applied',
      description: 'Applicable business rules, compliance policies, and SLAs evaluated.',
      items: (rec.ruleIds || []).map((rid: string) => ({ label: 'Rule', value: rid, icon: <Scale className="h-3.5 w-3.5 text-orange-500" /> })),
      details: [
        `${(rec.ruleIds || []).length} business rules triggered`,
        `Source: ${rec.source.replace(/_/g, ' ')}`,
      ],
      confidence: rec.confidence * 0.88,
    },
    reasoning: {
      title: 'Reasoning Engine',
      description: 'AI reasoning process evaluating evidence against knowledge and rules.',
      items: [
        { label: 'Reasoning Session', value: rec.reasoningId || 'N/A', icon: <BrainCircuit className="h-3.5 w-3.5 text-blue-500" /> },
        { label: 'Strategy', value: reasoning?.strategy || 'N/A', icon: <Target className="h-3.5 w-3.5 text-blue-500" /> },
        { label: 'Domain', value: reasoning?.domain || 'N/A', icon: <Shield className="h-3.5 w-3.5 text-blue-500" /> },
      ],
      details: [
        `Confidence: ${((reasoning?.confidence || rec.confidence) * 100).toFixed(0)}%`,
        `Risk score: ${reasoning?.riskScore || 'N/A'}`,
        `Processing time: ${reasoning?.processingTimeMs ? `${reasoning.processingTimeMs}ms` : 'N/A'}`,
        `Steps: ${reasoning?.steps?.length || 0}`,
      ],
      confidence: reasoning?.confidence || rec.confidence,
      processingTimeMs: reasoning?.processingTimeMs,
    },
    recommendation: {
      title: 'Recommendation Generated',
      description: 'Final recommendation with confidence scoring, business impact, and action plan.',
      items: [
        { label: 'Recommendation ID', value: rec.id, icon: <Lightbulb className="h-3.5 w-3.5 text-green-500" /> },
        { label: 'Priority', value: rec.priority, icon: <BarChart3 className="h-3.5 w-3.5 text-green-500" /> },
        { label: 'Business Impact', value: rec.businessImpact, icon: <Target className="h-3.5 w-3.5 text-green-500" /> },
      ],
      details: [
        `Confidence score: ${(rec.confidence * 100).toFixed(0)}%`,
        `Estimated cost: $${(rec.estimatedCost || 0).toLocaleString()}`,
        `Estimated savings: $${(rec.estimatedSavings || 0).toLocaleString()}`,
        `Timeline: ${rec.timeline}`,
      ],
      confidence: rec.confidence,
    },
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Reasoning Pipeline</h1>
        <p className="text-sm text-muted-foreground mt-1">
          End-to-end decision flow for recommendation <span className="font-mono font-medium text-foreground">{rec.id}</span>
        </p>
      </div>

      {/* Header Card */}
      <div className="bg-card rounded-xl border p-5 space-y-2">
        <div className="flex items-center justify-between">
          <h2 className="font-semibold text-lg text-foreground">{rec.title}</h2>
          <Link to={`/recommendations?id=${rec.id}`} className="text-xs text-primary hover:underline">View Recommendation</Link>
        </div>
        <p className="text-sm text-muted-foreground line-clamp-2">{rec.description}</p>
        <div className="flex flex-wrap gap-2 pt-1">
          <span className={`text-[10px] px-2 py-0.5 rounded font-bold uppercase ${rec.priority === 'critical' ? 'bg-red-500 text-white' : rec.priority === 'high' ? 'bg-orange-500 text-white' : rec.priority === 'medium' ? 'bg-yellow-500 text-slate-900' : 'bg-slate-500 text-white'}`}>{rec.priority}</span>
          <span className="text-xs px-2 py-0.5 rounded bg-muted text-muted-foreground">Overall Confidence: {(rec.confidence * 100).toFixed(0)}%</span>
        </div>
      </div>

      {/* Pipeline Flow */}
      <div className="space-y-0">
        {STAGES.map((stage, idx) => {
          const content = stageContent[stage.id]
          const isExpanded = expandedStage === stage.id
          const StageIcon = stage.icon

          return (
            <div key={stage.id} className="relative">
              {/* Connector line */}
              {idx < STAGES.length - 1 && (
                <div className="absolute left-6 top-12 bottom-0 w-px bg-border z-0">
                  <ArrowDown className="h-4 w-4 text-muted-foreground mx-auto -ml-[7.5px] mt-1" />
                </div>
              )}

              {/* Stage Card */}
              <div className="relative z-10 ml-0">
                <div
                  onClick={() => toggleStage(stage.id)}
                  className={`bg-card rounded-xl border-l-4 ${stage.color} shadow-xs hover:shadow-md transition-all cursor-pointer p-4 ${isExpanded ? 'rounded-b-none' : ''}`}
                >
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg ${stage.bg}`}>
                      <StageIcon className={`h-5 w-5 ${stage.text}`} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-sm text-foreground">{stage.label}</h3>
                      <p className="text-xs text-muted-foreground">{content.description}</p>
                    </div>
                    <div className="flex items-center gap-3 text-xs text-muted-foreground">
                      {content.confidence !== undefined && (
                        <div className="flex items-center gap-1">
                          <BarChart3 className="h-3 w-3" />
                          {(content.confidence * 100).toFixed(0)}%
                        </div>
                      )}
                      {content.processingTimeMs !== undefined && (
                        <div className="flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          {content.processingTimeMs}ms
                        </div>
                      )}
                      {isExpanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                    </div>
                  </div>
                </div>

                {/* Expanded Content */}
                {isExpanded && (
                  <div className="bg-card border-x border-b rounded-b-xl p-4 space-y-4">
                    {/* Items */}
                    {content.items.length > 0 && (
                      <div className="space-y-2">
                        <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Sources Used</h4>
                        <div className="flex flex-wrap gap-2">
                          {content.items.map((item, i) => (
                            <div key={i} className="flex items-center gap-1.5 px-3 py-1.5 bg-muted rounded-lg text-xs text-foreground">
                              {item.icon}
                              <span className="font-medium">{item.label}:</span>
                              <span className="text-muted-foreground">{item.value}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Details */}
                    <div className="space-y-1">
                      <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Processing Summary</h4>
                      <div className="grid grid-cols-2 gap-2">
                        {content.details.map((d, i) => (
                          <div key={i} className="text-xs text-foreground bg-muted/50 px-3 py-1.5 rounded-lg">{d}</div>
                        ))}
                      </div>
                    </div>

                    {/* Confidence bar */}
                    {content.confidence !== undefined && (
                      <div className="space-y-1">
                        <div className="flex justify-between text-xs">
                          <span className="text-muted-foreground">Stage Confidence</span>
                          <span className="font-medium text-foreground">{(content.confidence * 100).toFixed(0)}%</span>
                        </div>
                        <div className="w-full h-2 bg-secondary rounded-full overflow-hidden">
                          <div
                            className="h-full rounded-full transition-all"
                            style={{
                              width: `${content.confidence * 100}%`,
                              backgroundColor: stage.id === 'evidence' ? '#a855f7' : stage.id === 'knowledge' ? '#eab308' : stage.id === 'rules' ? '#f97316' : stage.id === 'reasoning' ? '#3b82f6' : '#22c55e',
                            }}
                          />
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>

      {/* Related Links */}
      {reasoning && (
        <div className="flex gap-2 pt-2">
          <Link to={`/reasoning/${rec.reasoningId}`} className="flex items-center gap-1.5 px-3 py-2 bg-card border rounded-lg text-xs hover:border-blue-500/40 transition-all">
            <BrainCircuit className="h-3.5 w-3.5 text-blue-500" />
            View Reasoning Session
          </Link>
          <Link to={`/evidence?q=${rec.id}`} className="flex items-center gap-1.5 px-3 py-2 bg-card border rounded-lg text-xs hover:border-purple-500/40 transition-all">
            <Database className="h-3.5 w-3.5 text-purple-500" />
            View Related Evidence
          </Link>
          <Link to={`/explainability?id=${rec.id}`} className="flex items-center gap-1.5 px-3 py-2 bg-card border rounded-lg text-xs hover:border-green-500/40 transition-all">
            <Lightbulb className="h-3.5 w-3.5 text-green-500" />
            View Explainability
          </Link>
        </div>
      )}
    </div>
  )
}
