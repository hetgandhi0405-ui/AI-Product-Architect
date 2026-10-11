/**
 * API client connecting frontend to backend AI Product Architect pipeline.
 */

const API_BASE = window.location.origin;

export async function checkHealth() {
  const response = await fetch(`${API_BASE}/health`);
  return await response.json();
}

export async function processRequirements({ description, project_name, execution_mode = 'QUICK' }) {
  const response = await fetch(`${API_BASE}/api/requirements/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      description,
      project_name: project_name || undefined,
      execution_mode,
    }),
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || 'Pipeline execution failed');
  }

  return data;
}

export function getExportUrl(projectId) {
  return `${API_BASE}/api/requirements/export/${projectId}`;
}

export function getTerraformExportUrl(projectId) {
  return `${API_BASE}/api/requirements/terraform/${projectId}`;
}
