import { createBrowserRouter, Navigate } from 'react-router-dom'
import { AppLayout } from '@/layouts/AppLayout'
import Dashboard from '@/pages/Dashboard'
import CustomersList from '@/pages/CustomersList'
import CustomerDetail from '@/pages/CustomerDetail'
import AssetsList from '@/pages/AssetsList'
import AssetDetail from '@/pages/AssetDetail'
import ImportCenter from '@/pages/ImportCenter'
import ImportReport from '@/pages/ImportReport'
import InteractionsList from '@/pages/InteractionsList'
import InteractionDetail from '@/pages/InteractionDetail'
import KnowledgeCenter from '@/pages/KnowledgeCenter'
import KnowledgeDetail from '@/pages/KnowledgeDetail'
import EvidenceList from '@/pages/EvidenceList'
import EvidenceDetail from '@/pages/EvidenceDetail'
import ReasoningCenter from '@/pages/ReasoningCenter'
import ReasoningDetail from '@/pages/ReasoningDetail'
import ReasoningPipeline from '@/pages/ReasoningPipeline'
import RecommendationCenter from '@/pages/RecommendationCenter'
import RecommendationAnalytics from '@/pages/RecommendationAnalytics'
import ExplainabilityCenter from '@/pages/ExplainabilityCenter'
import ReviewCenter from '@/pages/ReviewCenter'
import ActionsCenter from '@/pages/ActionsCenter'
import AICopilot from '@/pages/AICopilot'
import PlannerVisualization from '@/pages/PlannerVisualization'
import AgentMonitor from '@/pages/AgentMonitor'
import CapabilityRegistry from '@/pages/CapabilityRegistry'
import PlatformHealth from '@/pages/PlatformHealth'
import SettingsPage from '@/pages/SettingsPage'
import ExecutiveAnalytics from '@/pages/ExecutiveAnalytics'
import TraceabilityView from '@/components/TraceabilityView'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <AppLayout />,
    children: [
      { index: true, element: <Navigate to="/dashboard" replace /> },
      { path: 'dashboard', element: <Dashboard /> },
      { path: 'customers', element: <CustomersList /> },
      { path: 'customers/:id', element: <CustomerDetail /> },
      { path: 'assets', element: <AssetsList /> },
      { path: 'assets/:id', element: <AssetDetail /> },
      { path: 'import', element: <ImportCenter /> },
      { path: 'import/report/:jobId', element: <ImportReport /> },
      { path: 'interactions', element: <InteractionsList /> },
      { path: 'interactions/:id', element: <InteractionDetail /> },
      { path: 'knowledge', element: <KnowledgeCenter /> },
      { path: 'knowledge/:id', element: <KnowledgeDetail /> },
      { path: 'evidence', element: <EvidenceList /> },
      { path: 'evidence/:id', element: <EvidenceDetail /> },
      { path: 'reasoning', element: <ReasoningCenter /> },
      { path: 'reasoning/:id', element: <ReasoningDetail /> },
      { path: 'reasoning/pipeline', element: <ReasoningPipeline /> },
      { path: 'recommendations', element: <RecommendationCenter /> },
      { path: 'recommendations/analytics', element: <RecommendationAnalytics /> },
      { path: 'explainability', element: <ExplainabilityCenter /> },
      { path: 'review', element: <ReviewCenter /> },
      { path: 'actions', element: <ActionsCenter /> },
      { path: 'traceability', element: <TraceabilityView /> },
      { path: 'copilot', element: <AICopilot /> },
      { path: 'planner', element: <PlannerVisualization /> },
      { path: 'agents', element: <AgentMonitor /> },
      { path: 'plugins', element: <CapabilityRegistry /> },
      { path: 'health', element: <PlatformHealth /> },
      { path: 'settings', element: <SettingsPage /> },
      { path: 'analytics', element: <ExecutiveAnalytics /> },
    ],
  },
])
