export function triggerDashboardRefresh() {
  window.dispatchEvent(new CustomEvent('dashboard-refresh'))
}
