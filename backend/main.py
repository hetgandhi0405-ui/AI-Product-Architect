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
    Phase 18 - Simple Generator UI
    """
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>AI Product Architect</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 30px auto; max-width: 800px; padding: 0 20px; line-height: 1.5; color: #222; }
    h1 { margin-bottom: 8px; color: #111; }
    .subtitle { color: #666; margin-bottom: 24px; }
    label { font-weight: 600; display: block; margin-top: 16px; margin-bottom: 6px; }
    input[type="text"], textarea { width: 100%; box-sizing: border-box; padding: 10px; font-size: 15px; border: 1px solid #ccc; border-radius: 6px; }
    textarea { height: 120px; resize: vertical; }
    button { background: #0066cc; color: white; border: none; border-radius: 6px; padding: 12px 24px; font-size: 16px; font-weight: 600; cursor: pointer; margin-top: 20px; }
    button:disabled { background: #888; cursor: not-allowed; }
    .btn-download { background: #28a745; text-decoration: none; display: inline-block; padding: 12px 24px; color: white; border-radius: 6px; font-weight: 600; margin-top: 15px; }
    #status-card { margin-top: 30px; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px; background: #fafafa; display: none; }
    .status-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #eee; }
    .badge { font-weight: 700; padding: 2px 8px; border-radius: 4px; }
    .badge-APPROVED, .badge-PASS { background: #d4edda; color: #155724; }
    .badge-BLOCKED, .badge-FAIL { background: #f8d7da; color: #721c24; }
    .badge-WARN { background: #fff3cd; color: #856404; }
    #spinner { display: none; margin-top: 15px; font-weight: bold; color: #0066cc; }
  </style>
</head>
<body>
  <h1>AI Product Architect</h1>
  <div class="subtitle">Turn customer natural-language prompts into verified, downloadable software projects.</div>

  <form id="gen-form">
    <label for="project_name">Project Name (optional)</label>
    <input type="text" id="project_name" placeholder="e.g. TaskMaster Pro" />

    <label for="description">Describe your product:</label>
    <textarea id="description" required placeholder="Create a task management application where users can register, login, create tasks, update tasks, delete tasks and mark tasks as completed."></textarea>

    <button type="submit" id="submit-btn">Generate Project</button>
  </form>

  <div id="spinner">⚙️ Running AI Product Architect pipeline (Requirements → Architecture → Code Generation → Validation → Release Gate)...</div>

  <div id="status-card">
    <div class="status-row"><span><strong>Project ID:</strong></span> <span id="res-id">-</span></div>
    <div class="status-row"><span><strong>Files Generated:</strong></span> <span id="res-files">-</span></div>
    <div class="status-row"><span><strong>Generation Status:</strong></span> <span id="res-gen" class="badge badge-PASS">SUCCESS</span></div>
    <div class="status-row"><span><strong>Validation Status:</strong></span> <span id="res-val" class="badge">-</span></div>
    <div class="status-row"><span><strong>Build Status:</strong></span> <span id="res-build" class="badge">-</span></div>
    <div class="status-row"><span><strong>API Status:</strong></span> <span id="res-api" class="badge">-</span></div>
    <div class="status-row"><span><strong>Database Status:</strong></span> <span id="res-db" class="badge">-</span></div>
    <div class="status-row"><span><strong>Docker Status:</strong></span> <span id="res-docker" class="badge">-</span></div>
    <div class="status-row"><span><strong>Release Gate:</strong></span> <span id="res-gate" class="badge">-</span></div>

    <div id="download-container" style="display: none; margin-top: 20px;">
      <a id="download-link" href="#" class="btn-download">Download Project (ZIP)</a>
    </div>
  </div>

  <script>
    const form = document.getElementById('gen-form');
    const submitBtn = document.getElementById('submit-btn');
    const spinner = document.getElementById('spinner');
    const statusCard = document.getElementById('status-card');

    function setBadge(el, status) {
      el.textContent = status || 'N/A';
      el.className = 'badge badge-' + (status || '');
    }

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      submitBtn.disabled = true;
      spinner.style.display = 'block';
      statusCard.style.display = 'none';

      const payload = {
        description: document.getElementById('description').value,
        project_name: document.getElementById('project_name').value || undefined
      };

      try {
        const res = await fetch('/api/requirements/?execution_mode=QUICK', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        const resText = await res.text();
        let data = {};
        try {
          data = JSON.parse(resText);
        } catch (e) {
          alert('Server Error (' + res.status + '): ' + resText.substring(0, 200));
          return;
        }

        if (!res.ok) {
          alert('Error: ' + (data.detail || 'Generation request failed'));
          return;
        }

        statusCard.style.display = 'block';

        document.getElementById('res-id').textContent = data.project_id || '-';
        document.getElementById('res-files').textContent = data.generated_files_count || 0;

        setBadge(document.getElementById('res-val'), data.code_validation?.status);
        setBadge(document.getElementById('res-build'), data.build_validation?.status);
        setBadge(document.getElementById('res-api'), data.api_validation?.status);
        setBadge(document.getElementById('res-db'), data.database_validation?.status);
        setBadge(document.getElementById('res-docker'), data.docker_validation?.status);
        setBadge(document.getElementById('res-gate'), data.release_gate?.status);

        const dlContainer = document.getElementById('download-container');
        if (data.release_gate?.status === 'APPROVED' && data.download_url) {
          dlContainer.style.display = 'block';
          document.getElementById('download-link').href = data.download_url;
        } else {
          dlContainer.style.display = 'none';
        }
      } catch (err) {
        alert('Network error: ' + err.message);
      } finally {
        submitBtn.disabled = false;
        spinner.style.display = 'none';
      }
    });
  </script>
</body>
</html>"""
    return HTMLResponse(content=html_content)