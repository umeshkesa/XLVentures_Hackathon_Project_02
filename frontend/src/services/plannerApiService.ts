import { useQuery } from '@tanstack/react-query'
import { apiGet } from '@/api/client'
import type { Plan, Workflow } from '@/types/planner'

interface PlansResponse {
  plans: Plan[]
  total: number
}

interface WorkflowsResponse {
  workflows: Workflow[]
  total: number
}

export function usePlans() {
  return useQuery({
    queryKey: ['planner', 'plans'],
    queryFn: async () => {
      const { data } = await apiGet<PlansResponse>('/planner/plans')
      return data?.plans ?? []
    },
    staleTime: 30_000,
    retry: 2,
  })
}

export function usePlanById(planId: string) {
  return useQuery({
    queryKey: ['planner', 'plans', planId],
    queryFn: async () => {
      const { data } = await apiGet<Plan>(`/planner/plans/${planId}`)
      return data
    },
    enabled: !!planId,
    retry: 2,
  })
}

export function useWorkflows() {
  return useQuery({
    queryKey: ['planner', 'workflows'],
    queryFn: async () => {
      const { data } = await apiGet<WorkflowsResponse>('/workflow/workflows')
      return data?.workflows ?? []
    },
    staleTime: 30_000,
    retry: 2,
  })
}

export function useWorkflowById(workflowId: string) {
  return useQuery({
    queryKey: ['planner', 'workflows', workflowId],
    queryFn: async () => {
      const { data } = await apiGet<Workflow>(`/workflow/workflows/${workflowId}`)
      return data
    },
    enabled: !!workflowId,
    retry: 2,
  })
}
