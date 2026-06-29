import { createBrowserRouter, Navigate } from 'react-router-dom'
import { useAuth } from '@/store/auth'

function RootRedirect() {
  const { isCustomer } = useAuth()
  return <Navigate to={isCustomer ? '/customer' : '/dashboard'} replace />
}
import { AppLayout } from '@/layouts/AppLayout'
import Login from '@/pages/Login'
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

/* ── Customer Pages ─────────────────────────────────────────── */
import CustomerDashboard from '@/pages/CustomerDashboard'
import CustomerAssets from '@/pages/CustomerAssets'
import CustomerInteractions from '@/pages/CustomerInteractions'
import CustomerKnowledge from '@/pages/CustomerKnowledge'
import CustomerEvidence from '@/pages/CustomerEvidence'
import CustomerRecommendations from '@/pages/CustomerRecommendations'
import CustomerSupport from '@/pages/CustomerSupport'
import CustomerProfile from '@/pages/CustomerProfile'

export const router = createBrowserRouter([
  {
    path: '/login',
    element: <Login />,
  },
  {
    path: '/',
    element: <AppLayout />,
    children: [
      { index: true, element: <RootRedirect /> },

      /* ── Admin Pages ──────────────────────────────────── */
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

      /* ── Customer Pages ───────────────────────────────── */
      { path: 'customer', element: <CustomerDashboard /> },
      { path: 'customer/assets', element: <CustomerAssets /> },
      { path: 'customer/interactions', element: <CustomerInteractions /> },
      { path: 'customer/knowledge', element: <CustomerKnowledge /> },
      { path: 'customer/evidence', element: <CustomerEvidence /> },
      { path: 'customer/recommendations', element: <CustomerRecommendations /> },
      { path: 'customer/support', element: <CustomerSupport /> },
      { path: 'customer/profile', element: <CustomerProfile /> },
    ],
  },
])
