from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from backend.routes import requirements, projects


app = FastAPI(
    title="AI Product Architect API",
    description="Backend API for AI-powered cloud product generation",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    requirements.router,
    prefix="/api"
)

app.include_router(
    projects.router,
    prefix="/api"
)


@app.get("/")
def root():
    return {
        "project": "AI Product Architect",
        "member": "Member 2",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/ui", response_class=HTMLResponse)
@app.get("/generator", response_class=HTMLResponse)
def generator_ui():
    """
    Autonomous AI Product-to-Cloud Deployment & Optimization Platform Dashboard.
    Renders interactive UI covering all 12 pipeline sections.
    """
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Autonomous AI Product-to-Cloud Platform</title>
  <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
  <style>
    :root {
      --bg: #0f172a;
      --card-bg: #1e293b;
      --border: #334155;
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --primary: #3b82f6;
      --primary-hover: #2563eb;
      --success: #22c55e;
      --warning: #eab308;
      --danger: #ef4444;
      --accent: #a855f7;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.6;
      padding: 24px;
      max-width: 1280px;
      margin: 0 auto;
    }
    header {
      margin-bottom: 24px;
      border-bottom: 1px solid var(--border);
      padding-bottom: 16px;
    }
    h1 { font-size: 28px; font-weight: 700; color: #fff; }
    .subtitle { color: var(--text-muted); font-size: 14px; margin-top: 4px; }
    .badge-mode {
      background: var(--accent);
      color: #fff;
      font-size: 11px;
      padding: 3px 8px;
      border-radius: 12px;
      font-weight: 700;
      vertical-align: middle;
      margin-left: 8px;
    }
    
    .card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 20px;
      margin-bottom: 20px;
    }
    .card-title {
      font-size: 16px;
      font-weight: 700;
      color: var(--primary);
      margin-bottom: 12px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    
    label { font-weight: 600; font-size: 13px; color: var(--text-muted); display: block; margin-bottom: 6px; }
    input[type="text"], textarea, select {
      width: 100%;
      background: #0f172a;
      color: #fff;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 10px 14px;
      font-size: 14px;
      margin-bottom: 12px;
    }
    textarea { height: 100px; resize: vertical; }
    
    .btn-group { display: flex; gap: 12px; }
    button {
      background: var(--primary);
      color: #fff;
      border: none;
      border-radius: 8px;
      padding: 12px 24px;
      font-size: 15px;
      font-weight: 600;
      cursor: pointer;
      transition: background 0.2s;
    }
    button:hover { background: var(--primary-hover); }
    button:disabled { opacity: 0.5; cursor: not-allowed; }
    
    .btn-success { background: var(--success); text-decoration: none; color: white; padding: 10px 18px; border-radius: 6px; font-weight: 600; font-size: 13px; display: inline-block; }
    
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px; }
    .grid-4 { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; }
    
    .stat-box {
      background: #0f172a;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 12px 16px;
    }
    .stat-label { font-size: 12px; color: var(--text-muted); }
    .stat-value { font-size: 18px; font-weight: 700; color: #fff; margin-top: 4px; }
    
    .status-badge {
      font-size: 11px;
      font-weight: 700;
      padding: 2px 8px;
      border-radius: 4px;
      text-transform: uppercase;
    }
    .status-APPROVED, .status-PASS, .status-passed, .status-HEALTHY { background: rgba(34, 197, 94, 0.2); color: var(--success); border: 1px solid var(--success); }
    .status-BLOCKED, .status-FAIL, .status-failed, .status-UNHEALTHY { background: rgba(239, 68, 68, 0.2); color: var(--danger); border: 1px solid var(--danger); }
    .status-WARN, .status-DEGRADED { background: rgba(234, 179, 8, 0.2); color: var(--warning); border: 1px solid var(--warning); }
    .status-SKIPPED, .status-UNAVAILABLE { background: rgba(148, 163, 184, 0.2); color: var(--text-muted); border: 1px solid var(--text-muted); }
    
    pre {
      background: #0f172a;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 12px;
      font-family: 'Fira Code', monospace;
      font-size: 12px;
      overflow-x: auto;
      max-height: 250px;
    }
    
    #results-area { display: none; }
    #loading-overlay {
      display: none;
      text-align: center;
      padding: 40px;
      background: var(--card-bg);
      border-radius: 12px;
      border: 1px solid var(--border);
      margin-bottom: 20px;
    }
    .spinner-anim {
      width: 40px;
      height: 40px;
      border: 4px solid var(--border);
      border-top-color: var(--primary);
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin: 0 auto 16px;
    }
    @keyframes spin { to { transform: rotate(360deg); } }
    
    .mermaid { background: #0f172a; padding: 16px; border-radius: 8px; border: 1px solid var(--border); overflow-x: auto; text-align: center; }
  </style>
</head>
<body>
  <header>
    <h1>Autonomous AI Product-to-Cloud Platform <span class="badge-mode">Phase 1-20 Active</span></h1>
    <div class="subtitle">Execute full pipeline: Prompt → Product Generation → Product Validation → Cloud Architecture → Terraform → Validation → Monitoring → Agentic RL Optimization</div>
  </header>

  <!-- Input Form -->
  <div class="card">
    <div class="card-title">1. Product Requirement Prompt</div>
    <form id="gen-form">
      <div class="grid">
        <div>
          <label for="project_name">Project Name (Optional)</label>
          <input type="text" id="project_name" placeholder="e.g. TaskMaster Platform" />
        </div>
        <div>
          <label for="execution_mode">Execution Mode</label>
          <select id="execution_mode">
            <option value="QUICK" selected>QUICK (Fast Local Synthesis & Validation)</option>
            <option value="FULL">FULL (Deep Simulation & Gemini AI LLM Inference)</option>
          </select>
        </div>
      </div>

      <label for="description">Natural Language Product Requirement Prompt</label>
      <textarea id="description" required placeholder="Build a task management platform for small businesses. Users should be able to register and login, create teams, projects and tasks, comment on tasks, receive notifications, and view a dashboard. Use PostgreSQL. The system should support 10,000 users and require high availability."></textarea>

      <div class="btn-group">
        <button type="submit" id="submit-btn">🚀 Execute Autonomous Pipeline</button>
      </div>
    </form>
  </div>

  <!-- Loading State -->
  <div id="loading-overlay">
    <div class="spinner-anim"></div>
    <h3 style="color:#fff;">Executing Autonomous AI Product-to-Cloud Pipeline...</h3>
    <p style="color:var(--text-muted); margin-top:8px;" id="loading-step">Analyzing requirements → Planning Product → Generating Code → Validating Product → Inferring Cloud Architecture → Generating Terraform → Evaluating RL Policy...</p>
  </div>

  <!-- Results Dashboard -->
  <div id="results-area">
    <!-- Quick Status Bar -->
    <div class="card" style="border-left: 4px solid var(--primary);">
      <div class="card-title">
        <span>Pipeline Execution Summary</span>
        <div id="action-links" style="display:flex; gap:10px;"></div>
      </div>
      <div class="grid-4">
        <div class="stat-box"><div class="stat-label">Project ID</div><div class="stat-value" id="stat-pid" style="font-size:14px; word-break:break-all;">-</div></div>
        <div class="stat-box"><div class="stat-label">Release Gate</div><div class="stat-value" id="stat-gate">-</div></div>
        <div class="stat-box"><div class="stat-label">Deployment Ready</div><div class="stat-value" id="stat-ready">-</div></div>
        <div class="stat-box"><div class="stat-label">Monthly Cost Est.</div><div class="stat-value" id="stat-cost">-</div></div>
      </div>
    </div>

    <!-- Product Metadata & Spec -->
    <div class="grid">
      <div class="card">
        <div class="card-title">2. Inferred Product Metadata</div>
        <div class="grid-4" style="margin-bottom:12px;">
          <div class="stat-box"><div class="stat-label">Frontend</div><div class="stat-value" id="meta-fe">-</div></div>
          <div class="stat-box"><div class="stat-label">Backend</div><div class="stat-value" id="meta-be">-</div></div>
          <div class="stat-box"><div class="stat-label">Database</div><div class="stat-value" id="meta-db">-</div></div>
          <div class="stat-box"><div class="stat-label">Scale Users</div><div class="stat-value" id="meta-users">-</div></div>
        </div>
        <div class="stat-label">Generated Project Files (<span id="meta-file-count">0</span> total):</div>
        <pre id="meta-files-list">-</pre>
      </div>

      <div class="card">
        <div class="card-title">3. Inferred Cloud Architecture Spec</div>
        <div class="grid-4" style="margin-bottom:12px;">
          <div class="stat-box"><div class="stat-label">Compute Service</div><div class="stat-value" id="cloud-compute">-</div></div>
          <div class="stat-box"><div class="stat-label">RDS Instance</div><div class="stat-value" id="cloud-rds">-</div></div>
          <div class="stat-box"><div class="stat-label">Multi-AZ</div><div class="stat-value" id="cloud-multiaz">-</div></div>
          <div class="stat-box"><div class="stat-label">ElastiCache Redis</div><div class="stat-value" id="cloud-redis">-</div></div>
        </div>
        <div class="stat-label">JSON Infrastructure State:</div>
        <pre id="infra-state-json">-</pre>
      </div>
    </div>

    <!-- Architecture Diagram -->
    <div class="card">
      <div class="card-title">4. Dynamic Cloud Architecture Diagram (Mermaid)</div>
      <div id="mermaid-container">
        <div class="mermaid" id="mermaid-graph">flowchart LR\n  USER["User"] --> ALB["Load Balancer"]\n  ALB --> APP["ECS App"]\n  APP --> DB["PostgreSQL"]</div>
      </div>
    </div>

    <!-- Validations & Security -->
    <div class="grid">
      <div class="card">
        <div class="card-title">5. Unified Product Validation Report</div>
        <div class="grid-4" style="margin-bottom:12px;">
          <div class="stat-box"><div class="stat-label">Gates Passed</div><div class="stat-value" id="val-gates-count">-</div></div>
          <div class="stat-box"><div class="stat-label">Code Syntax</div><div class="stat-value" id="val-gate-code">-</div></div>
          <div class="stat-box"><div class="stat-label">API Contract</div><div class="stat-value" id="val-gate-api">-</div></div>
          <div class="stat-box"><div class="stat-label">Database Schema</div><div class="stat-value" id="val-gate-db">-</div></div>
        </div>
        <div class="stat-label">Validation Summary:</div>
        <pre id="val-summary-text">-</pre>
      </div>

      <div class="card">
        <div class="card-title">6. Terraform HCL Infrastructure</div>
        <div class="grid-4" style="margin-bottom:12px;">
          <div class="stat-box"><div class="stat-label">Status</div><div class="stat-value" id="tf-status">-</div></div>
          <div class="stat-box"><div class="stat-label">HCL Files Count</div><div class="stat-value" id="tf-file-count">-</div></div>
          <div class="stat-box" style="grid-column: span 2;"><div class="stat-label">Download Package</div><div id="tf-dl-btn" style="margin-top:4px;">-</div></div>
        </div>
        <div class="stat-label">Generated Terraform Files:</div>
        <pre id="tf-files-list">-</pre>
      </div>
    </div>

    <!-- RL Evaluation & Dataset Record -->
    <div class="grid">
      <div class="card">
        <div class="card-title">7. RL-Based Evaluation Scoring</div>
        <div class="grid-4" style="margin-bottom:12px;">
          <div class="stat-box"><div class="stat-label">Reward Score</div><div class="stat-value" id="rl-reward">-</div></div>
          <div class="stat-box"><div class="stat-label">Policy Safe</div><div class="stat-value" id="rl-safe">-</div></div>
          <div class="stat-box"><div class="stat-label">Recommendation</div><div class="stat-value" id="rl-accepted">-</div></div>
          <div class="stat-box"><div class="stat-label">Fine-tune Record</div><div class="stat-value" id="rl-ft-id">-</div></div>
        </div>
        <div class="stat-label">RL Evaluation Summary:</div>
        <pre id="rl-summary-text">-</pre>
      </div>
    </div>

  </div>

  <script>
    mermaid.initialize({ startOnLoad: false, theme: 'dark' });

    const form = document.getElementById('gen-form');
    const submitBtn = document.getElementById('submit-btn');
    const loadingOverlay = document.getElementById('loading-overlay');
    const resultsArea = document.getElementById('results-area');

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      submitBtn.disabled = true;
      loadingOverlay.style.display = 'block';
      resultsArea.style.display = 'none';

      const payload = {
        description: document.getElementById('description').value,
        project_name: document.getElementById('project_name').value || undefined,
        execution_mode: document.getElementById('execution_mode').value
      };

      try {
        const res = await fetch('/api/requirements/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        const data = await res.json();

        if (!res.ok) {
          alert('Error: ' + (data.detail || 'Generation request failed'));
          return;
        }

        renderDashboard(data);
        resultsArea.style.display = 'block';
      } catch (err) {
        alert('Network or execution error: ' + err.message);
      } finally {
        submitBtn.disabled = false;
        loadingOverlay.style.display = 'none';
      }
    });

    function renderDashboard(data) {
      // 1. Status Bar
      document.getElementById('stat-pid').textContent = data.project_id || '-';
      
      const gateStatus = data.release_gate?.status || 'UNKNOWN';
      document.getElementById('stat-gate').innerHTML = `<span class="status-badge status-${gateStatus}">${gateStatus}</span>`;

      const ready = data.validation_report?.deployment_ready ?? false;
      document.getElementById('stat-ready').innerHTML = ready ?
        `<span class="status-badge status-passed">YES (Ready)</span>` :
        `<span class="status-badge status-failed">NO (Blocked)</span>`;

      const cost = data.cloud_architecture_spec?.estimated_metrics?.monthly_cost_usd;
      document.getElementById('stat-cost').textContent = cost ? `$${cost}/mo` : 'N/A';

      // Action Download Links
      const actionLinks = document.getElementById('action-links');
      actionLinks.innerHTML = '';
      if (data.download_url) {
        actionLinks.innerHTML += `<a href="${data.download_url}" class="btn-success">📦 Download Project ZIP</a>`;
      }
      if (data.project_id) {
        actionLinks.innerHTML += `<a href="/api/requirements/terraform/${data.project_id}" class="btn-success" style="background:#0066cc;">🛠️ Download Terraform ZIP</a>`;
      }

      // 2. Product Metadata
      const pm = data.product_metadata || {};
      document.getElementById('meta-fe').textContent = pm.frontend?.framework || 'react';
      document.getElementById('meta-be').textContent = pm.backend?.framework || 'fastapi';
      document.getElementById('meta-db').textContent = pm.database?.engine || 'postgresql';
      document.getElementById('meta-users').textContent = pm.scalability?.target_users?.toLocaleString() || '1,000';
      document.getElementById('meta-file-count').textContent = data.generated_files_count || 0;

      const manifestFiles = data.file_manifest?.files || [];
      document.getElementById('meta-files-list').textContent = manifestFiles.map(f => `📄 ${f.path}`).join('\n') || 'None';

      // 3. Cloud Spec & Infra State
      const cs = data.cloud_architecture_spec || {};
      document.getElementById('cloud-compute').textContent = cs.compute?.service || 'ecs_fargate';
      document.getElementById('cloud-rds').textContent = cs.database?.instance_class || 'db.t3.medium';
      document.getElementById('cloud-multiaz').textContent = cs.database?.multi_az ? 'YES' : 'NO';
      document.getElementById('cloud-redis').textContent = cs.cache?.enabled ? 'YES' : 'NO';

      document.getElementById('infra-state-json').textContent = JSON.stringify(data.infrastructure_state || {}, null, 2);

      // 4. Architecture Diagram
      const rawDiagram = data.architecture_diagram || `flowchart LR\\n  USER["User"] --> ALB["Load Balancer"]\\n  ALB --> APP["FastAPI Backend"]\\n  APP --> DB["PostgreSQL Database"]`;
      const mermaidDiv = document.getElementById('mermaid-graph');
      mermaidDiv.removeAttribute('data-processed');
      mermaidDiv.textContent = rawDiagram;
      mermaid.contentLoaded();

      // 5. Validation Report
      const vr = data.validation_report || {};
      document.getElementById('val-gates-count').textContent = `${vr.gates_passed || 0}/${vr.gates_total || 8}`;
      document.getElementById('val-gate-code').innerHTML = `<span class="status-badge status-${data.code_validation?.status}">${data.code_validation?.status || 'N/A'}</span>`;
      document.getElementById('val-gate-api').innerHTML = `<span class="status-badge status-${data.api_validation?.status}">${data.api_validation?.status || 'N/A'}</span>`;
      document.getElementById('val-gate-db').innerHTML = `<span class="status-badge status-${data.database_validation?.status}">${data.database_validation?.status || 'N/A'}</span>`;

      document.getElementById('val-summary-text').textContent = vr.summary || 'All validation checks completed.';

      // 6. Terraform
      const tf = data.terraform_generation || {};
      document.getElementById('tf-status').innerHTML = `<span class="status-badge status-${data.terraform_validation?.status || 'passed'}">${data.terraform_validation?.status || 'PASSED'}</span>`;
      document.getElementById('tf-file-count').textContent = tf.file_count || 0;
      document.getElementById('tf-dl-btn').innerHTML = data.project_id ? `<a href="/api/requirements/terraform/${data.project_id}" class="btn-success" style="font-size:11px; padding:4px 8px;">Download Terraform ZIP</a>` : '-';
      document.getElementById('tf-files-list').textContent = Object.keys(tf.files || {}).map(f => `🛠️ infrastructure/terraform/${f}`).join('\n') || 'None';

      // 7. RL Evaluation
      const rl = data.rl_evaluation || {};
      document.getElementById('rl-reward').textContent = rl.reward !== undefined ? rl.reward : '0.0';
      document.getElementById('rl-safe').textContent = rl.is_policy_safe ? 'YES' : 'NO';
      document.getElementById('rl-accepted').textContent = rl.recommendation_accepted ? 'ACCEPTED' : 'PAUSED';
      document.getElementById('rl-ft-id').textContent = data.finetuning_dataset_record?.record_id || 'N/A';
      document.getElementById('rl-summary-text').textContent = rl.summary || 'RL evaluation complete.';
    }
  </script>
</body>
</html>"""
    return HTMLResponse(content=html_content)