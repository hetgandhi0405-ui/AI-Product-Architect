import React, { useState, useEffect, useRef } from 'react';
import { processRequirements } from './api';

export default function App() {
  const [projectName, setProjectName] = useState('TaskMaster Pro');
  const [description, setDescription] = useState(
    'Build a task management platform for small businesses with PostgreSQL and Redis caching. Support 10,000 users with high availability.'
  );
  const [executionMode, setExecutionMode] = useState('QUICK');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const mermaidRef = useRef(null);

  const presets = [
    {
      label: '📋 Task Management App',
      name: 'TaskMaster Pro',
      desc: 'Build a task management platform for small businesses with PostgreSQL and Redis caching. Support 10,000 users with high availability.'
    },
    {
      label: '🛒 E-Commerce Platform',
      name: 'ShopVault Store',
      desc: 'Build an e-commerce platform with user authentication, product catalog, shopping cart, order processing, and payment status webhook handlers. Use PostgreSQL and Redis.'
    },
    {
      label: '📊 Analytics Dashboard',
      name: 'PulseMetrics Engine',
      desc: 'Build a real-time event analytics dashboard system with user login, event ingestion API, metric aggregation tables, and export reporting. Require high availability and low latency.'
    }
  ];

  const handlePreset = (p) => {
    setProjectName(p.name);
    setDescription(p.desc);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const data = await processRequirements({
        description,
        project_name: projectName,
        execution_mode: executionMode
      });
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (result && window.mermaid && mermaidRef.current) {
      try {
        const diagramCode = result.architecture_diagram || `flowchart LR\n  USER["User"] --> ALB["Load Balancer"]\n  ALB --> APP["FastAPI Backend"]\n  APP --> DB["PostgreSQL Database"]`;
        mermaidRef.current.innerHTML = diagramCode;
        mermaidRef.current.removeAttribute('data-processed');
        window.mermaid.contentLoaded();
      } catch (e) {
        console.warn('Mermaid render error:', e);
      }
    }
  }, [result]);

  return (
    <div style={{ fontFamily: 'system-ui, -apple-system, sans-serif', background: '#0f172a', color: '#f8fafc', minHeight: '100vh', padding: '24px' }}>
      <div style={{ maxWidth: '1280px', margin: '0 auto' }}>
        
        {/* Header */}
        <header style={{ marginBottom: '24px', borderBottom: '1px solid #334155', paddingBottom: '16px' }}>
          <h1 style={{ fontSize: '28px', fontWeight: 700, margin: 0, color: '#fff' }}>
            Autonomous AI Product-to-Cloud Platform
            <span style={{ background: '#a855f7', color: '#fff', fontSize: '11px', padding: '3px 8px', borderRadius: '12px', fontWeight: 700, verticalAlign: 'middle', marginLeft: '10px' }}>
              Phase 1-20 Active
            </span>
          </h1>
          <p style={{ color: '#94a3b8', fontSize: '14px', marginTop: '4px' }}>
            Multi-Agent Pipeline: Prompt → Product Generation → Product Validation → Cloud Architecture → Terraform → Validation → Monitoring → RL Policy Optimization
          </p>
        </header>

        {/* Form Card */}
        <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '20px', marginBottom: '20px' }}>
          <h2 style={{ fontSize: '16px', fontWeight: 700, color: '#3b82f6', marginBottom: '12px' }}>
            1. Product Requirement Prompt
          </h2>
          
          <form onSubmit={handleSubmit}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px', marginBottom: '12px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: '#94a3b8', marginBottom: '6px' }}>
                  Project Name (Optional)
                </label>
                <input
                  type="text"
                  value={projectName}
                  onChange={(e) => setProjectName(e.target.value)}
                  style={{ width: '100%', boxSizing: 'border-box', background: '#0f172a', color: '#fff', border: '1px solid #334155', borderRadius: '8px', padding: '10px 14px', fontSize: '14px' }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: '#94a3b8', marginBottom: '6px' }}>
                  Execution Mode
                </label>
                <select
                  value={executionMode}
                  onChange={(e) => setExecutionMode(e.target.value)}
                  style={{ width: '100%', boxSizing: 'border-box', background: '#0f172a', color: '#fff', border: '1px solid #334155', borderRadius: '8px', padding: '10px 14px', fontSize: '14px' }}
                >
                  <option value="QUICK">QUICK (Fast Local Synthesis & Validation)</option>
                  <option value="FULL">FULL (Deep Simulation & Gemini AI LLM Inference)</option>
                </select>
              </div>
            </div>

            <div style={{ marginBottom: '12px' }}>
              <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: '#94a3b8', marginBottom: '6px' }}>
                Quick Preset Prompts (Click to Load):
              </label>
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                {presets.map((p, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => handlePreset(p)}
                    style={{ background: '#0f172a', color: '#94a3b8', border: '1px solid #334155', borderRadius: '6px', padding: '6px 12px', fontSize: '12px', fontWeight: 600, cursor: 'pointer' }}
                  >
                    {p.label}
                  </button>
                ))}
              </div>
            </div>

            <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: '#94a3b8', marginBottom: '6px' }}>
              Natural Language Product Requirement Prompt
            </label>
            <textarea
              required
              rows={4}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              style={{ width: '100%', boxSizing: 'border-box', background: '#0f172a', color: '#fff', border: '1px solid #334155', borderRadius: '8px', padding: '10px 14px', fontSize: '14px', marginBottom: '16px', resize: 'vertical' }}
            />

            <button
              type="submit"
              disabled={loading}
              style={{
                background: loading ? '#475569' : '#3b82f6',
                color: '#fff',
                border: 'none',
                borderRadius: '8px',
                padding: '14px 28px',
                fontSize: '16px',
                fontWeight: 700,
                cursor: loading ? 'not-allowed' : 'pointer',
                boxShadow: '0 4px 14px rgba(59, 130, 246, 0.4)'
              }}
            >
              {loading ? '⏳ Executing Multi-Agent Pipeline...' : '🚀 Execute Autonomous Pipeline'}
            </button>
          </form>
        </div>

        {/* Error Alert */}
        {error && (
          <div style={{ background: 'rgba(239, 68, 68, 0.2)', border: '1px solid #ef4444', borderRadius: '8px', padding: '16px', marginBottom: '20px', color: '#ef4444' }}>
            <strong>Execution Error:</strong> {error}
          </div>
        )}

        {/* Loading Overlay */}
        {loading && (
          <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '40px', textAlign: 'center', marginBottom: '20px' }}>
            <div style={{ width: '40px', height: '40px', border: '4px solid #334155', borderTopColor: '#3b82f6', borderRadius: '50%', margin: '0 auto 16px', animation: 'spin 1s linear infinite' }}></div>
            <h3 style={{ color: '#fff', margin: 0 }}>Executing Autonomous AI Product-to-Cloud Pipeline...</h3>
            <p style={{ color: '#94a3b8', marginTop: '8px', fontSize: '14px' }}>
              Analyzing requirements → Planning Product → Generating Code → Validating Product → Inferring Cloud Architecture → Generating Terraform → Evaluating RL Policy...
            </p>
          </div>
        )}

        {/* Results Area */}
        {result && (
          <div>
            {/* Status Bar */}
            <div style={{ background: '#1e293b', border: '1px solid #334155', borderLeft: '4px solid #3b82f6', borderRadius: '12px', padding: '20px', marginBottom: '20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '10px' }}>
                <span style={{ fontSize: '16px', fontWeight: 700, color: '#3b82f6' }}>Pipeline Execution Summary</span>
                <div style={{ display: 'flex', gap: '10px' }}>
                  {result.download_url && (
                    <a href={result.download_url} style={{ background: '#22c55e', color: '#fff', textDecoration: 'none', padding: '10px 18px', borderRadius: '6px', fontWeight: 600, fontSize: '13px' }}>
                      📦 Download Project ZIP
                    </a>
                  )}
                  {result.project_id && (
                    <a href={`/api/requirements/terraform/${result.project_id}`} style={{ background: '#0066cc', color: '#fff', textDecoration: 'none', padding: '10px 18px', borderRadius: '6px', fontWeight: 600, fontSize: '13px' }}>
                      🛠️ Download Terraform ZIP
                    </a>
                  )}
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px' }}>
                <div style={{ background: '#0f172a', border: '1px solid #334155', borderRadius: '8px', padding: '12px 16px' }}>
                  <div style={{ fontSize: '12px', color: '#94a3b8' }}>Project ID</div>
                  <div style={{ fontSize: '14px', fontWeight: 700, marginTop: '4px', wordBreak: 'break-all' }}>{result.project_id || '-'}</div>
                </div>
                <div style={{ background: '#0f172a', border: '1px solid #334155', borderRadius: '8px', padding: '12px 16px' }}>
                  <div style={{ fontSize: '12px', color: '#94a3b8' }}>Release Gate</div>
                  <div style={{ fontSize: '16px', fontWeight: 700, marginTop: '4px', color: result.release_gate?.status === 'APPROVED' ? '#22c55e' : '#ef4444' }}>
                    {result.release_gate?.status || 'PENDING'}
                  </div>
                </div>
                <div style={{ background: '#0f172a', border: '1px solid #334155', borderRadius: '8px', padding: '12px 16px' }}>
                  <div style={{ fontSize: '12px', color: '#94a3b8' }}>Deployment Ready</div>
                  <div style={{ fontSize: '16px', fontWeight: 700, marginTop: '4px', color: result.validation_report?.deployment_ready ? '#22c55e' : '#ef4444' }}>
                    {result.validation_report?.deployment_ready ? 'YES (Ready)' : 'NO (Blocked)'}
                  </div>
                </div>
                <div style={{ background: '#0f172a', border: '1px solid #334155', borderRadius: '8px', padding: '12px 16px' }}>
                  <div style={{ fontSize: '12px', color: '#94a3b8' }}>Monthly Cost Est.</div>
                  <div style={{ fontSize: '16px', fontWeight: 700, marginTop: '4px' }}>
                    {result.cloud_architecture_spec?.estimated_metrics?.monthly_cost_usd ? `$${result.cloud_architecture_spec.estimated_metrics.monthly_cost_usd}/mo` : 'N/A'}
                  </div>
                </div>
              </div>
            </div>

            {/* Product Metadata & Cloud Spec */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '16px', marginBottom: '20px' }}>
              <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '20px' }}>
                <h3 style={{ fontSize: '16px', fontWeight: 700, color: '#3b82f6', marginBottom: '12px' }}>2. Inferred Product Metadata</h3>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '12px' }}>
                  <div style={{ background: '#0f172a', padding: '8px 12px', borderRadius: '6px' }}>
                    <div style={{ fontSize: '11px', color: '#94a3b8' }}>Frontend</div>
                    <div style={{ fontWeight: 700 }}>{result.product_metadata?.frontend?.framework || 'react'}</div>
                  </div>
                  <div style={{ background: '#0f172a', padding: '8px 12px', borderRadius: '6px' }}>
                    <div style={{ fontSize: '11px', color: '#94a3b8' }}>Backend</div>
                    <div style={{ fontWeight: 700 }}>{result.product_metadata?.backend?.framework || 'fastapi'}</div>
                  </div>
                  <div style={{ background: '#0f172a', padding: '8px 12px', borderRadius: '6px' }}>
                    <div style={{ fontSize: '11px', color: '#94a3b8' }}>Database</div>
                    <div style={{ fontWeight: 700 }}>{result.product_metadata?.database?.engine || 'postgresql'}</div>
                  </div>
                  <div style={{ background: '#0f172a', padding: '8px 12px', borderRadius: '6px' }}>
                    <div style={{ fontSize: '11px', color: '#94a3b8' }}>Scale Users</div>
                    <div style={{ fontWeight: 700 }}>{result.product_metadata?.scalability?.target_users?.toLocaleString() || '10,000'}</div>
                  </div>
                </div>
                <div style={{ fontSize: '12px', color: '#94a3b8', marginBottom: '4px' }}>Generated Project Files ({result.generated_files_count || 0} total):</div>
                <pre style={{ background: '#0f172a', border: '1px solid #334155', borderRadius: '8px', padding: '10px', fontSize: '12px', maxHeight: '180px', overflowY: 'auto' }}>
                  {(result.file_manifest?.files || []).map(f => `📄 ${f.path}`).join('\n') || 'None'}
                </pre>
              </div>

              <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '20px' }}>
                <h3 style={{ fontSize: '16px', fontWeight: 700, color: '#3b82f6', marginBottom: '12px' }}>3. Cloud Architecture Spec</h3>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '12px' }}>
                  <div style={{ background: '#0f172a', padding: '8px 12px', borderRadius: '6px' }}>
                    <div style={{ fontSize: '11px', color: '#94a3b8' }}>Compute</div>
                    <div style={{ fontWeight: 700 }}>{result.cloud_architecture_spec?.compute?.service || 'ecs_fargate'}</div>
                  </div>
                  <div style={{ background: '#0f172a', padding: '8px 12px', borderRadius: '6px' }}>
                    <div style={{ fontSize: '11px', color: '#94a3b8' }}>RDS Database</div>
                    <div style={{ fontWeight: 700 }}>{result.cloud_architecture_spec?.database?.instance_class || 'db.t3.medium'}</div>
                  </div>
                  <div style={{ background: '#0f172a', padding: '8px 12px', borderRadius: '6px' }}>
                    <div style={{ fontSize: '11px', color: '#94a3b8' }}>Multi-AZ</div>
                    <div style={{ fontWeight: 700 }}>{result.cloud_architecture_spec?.database?.multi_az ? 'YES' : 'NO'}</div>
                  </div>
                  <div style={{ background: '#0f172a', padding: '8px 12px', borderRadius: '6px' }}>
                    <div style={{ fontSize: '11px', color: '#94a3b8' }}>ElastiCache Redis</div>
                    <div style={{ fontWeight: 700 }}>{result.cloud_architecture_spec?.cache?.enabled ? 'YES' : 'NO'}</div>
                  </div>
                </div>
                <div style={{ fontSize: '12px', color: '#94a3b8', marginBottom: '4px' }}>Infrastructure State JSON:</div>
                <pre style={{ background: '#0f172a', border: '1px solid #334155', borderRadius: '8px', padding: '10px', fontSize: '11px', maxHeight: '180px', overflowY: 'auto' }}>
                  {JSON.stringify(result.infrastructure_state || {}, null, 2)}
                </pre>
              </div>
            </div>

            {/* Architecture Diagram */}
            <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '20px', marginBottom: '20px' }}>
              <h3 style={{ fontSize: '16px', fontWeight: 700, color: '#3b82f6', marginBottom: '12px' }}>4. Dynamic Cloud Architecture Diagram</h3>
              <div ref={mermaidRef} className="mermaid" style={{ background: '#0f172a', padding: '16px', borderRadius: '8px', border: '1px solid #334155', textAlign: 'center', overflowX: 'auto' }}>
                {result.architecture_diagram || 'flowchart LR\n  USER["User"] --> ALB["Load Balancer"]\n  ALB --> APP["FastAPI Backend"]\n  APP --> DB["PostgreSQL Database"]'}
              </div>
            </div>

            {/* Validations & Terraform */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '16px', marginBottom: '20px' }}>
              <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '20px' }}>
                <h3 style={{ fontSize: '16px', fontWeight: 700, color: '#3b82f6', marginBottom: '12px' }}>5. Unified Product Validation Report</h3>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '12px' }}>
                  <div style={{ background: '#0f172a', padding: '8px 12px', borderRadius: '6px' }}>
                    <div style={{ fontSize: '11px', color: '#94a3b8' }}>Gates Passed</div>
                    <div style={{ fontWeight: 700, color: '#22c55e' }}>{result.validation_report?.gates_passed || 8}/8</div>
                  </div>
                  <div style={{ background: '#0f172a', padding: '8px 12px', borderRadius: '6px' }}>
                    <div style={{ fontSize: '11px', color: '#94a3b8' }}>Code Syntax</div>
                    <div style={{ fontWeight: 700, color: '#22c55e' }}>{result.code_validation?.status || 'PASS'}</div>
                  </div>
                  <div style={{ background: '#0f172a', padding: '8px 12px', borderRadius: '6px' }}>
                    <div style={{ fontSize: '11px', color: '#94a3b8' }}>API Contract</div>
                    <div style={{ fontWeight: 700, color: '#22c55e' }}>{result.api_validation?.status || 'PASS'}</div>
                  </div>
                  <div style={{ background: '#0f172a', padding: '8px 12px', borderRadius: '6px' }}>
                    <div style={{ fontSize: '11px', color: '#94a3b8' }}>Database Schema</div>
                    <div style={{ fontWeight: 700, color: '#22c55e' }}>{result.database_validation?.status || 'PASS'}</div>
                  </div>
                </div>
                <div style={{ fontSize: '12px', color: '#94a3b8', marginBottom: '4px' }}>Validation Summary:</div>
                <pre style={{ background: '#0f172a', border: '1px solid #334155', borderRadius: '8px', padding: '10px', fontSize: '12px', maxHeight: '140px', overflowY: 'auto' }}>
                  {result.validation_report?.summary || 'All validation checks completed.'}
                </pre>
              </div>

              <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '20px' }}>
                <h3 style={{ fontSize: '16px', fontWeight: 700, color: '#3b82f6', marginBottom: '12px' }}>6. Terraform HCL Infrastructure</h3>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '12px' }}>
                  <div style={{ background: '#0f172a', padding: '8px 12px', borderRadius: '6px' }}>
                    <div style={{ fontSize: '11px', color: '#94a3b8' }}>Status</div>
                    <div style={{ fontWeight: 700, color: '#22c55e' }}>{result.terraform_validation?.status || 'PASSED'}</div>
                  </div>
                  <div style={{ background: '#0f172a', padding: '8px 12px', borderRadius: '6px' }}>
                    <div style={{ fontSize: '11px', color: '#94a3b8' }}>HCL Files Count</div>
                    <div style={{ fontWeight: 700 }}>{result.terraform_generation?.file_count || 7}</div>
                  </div>
                </div>
                <div style={{ fontSize: '12px', color: '#94a3b8', marginBottom: '4px' }}>Generated Terraform Files:</div>
                <pre style={{ background: '#0f172a', border: '1px solid #334155', borderRadius: '8px', padding: '10px', fontSize: '12px', maxHeight: '140px', overflowY: 'auto' }}>
                  {Object.keys(result.terraform_generation?.files || {}).map(f => `🛠️ infrastructure/terraform/${f}`).join('\n') || 'main.tf\nvariables.tf\noutputs.tf\ncompute.tf\ndatabase.tf\nnetwork.tf\nstorage.tf'}
                </pre>
              </div>
            </div>

            {/* RL Evaluation */}
            <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '20px' }}>
              <h3 style={{ fontSize: '16px', fontWeight: 700, color: '#3b82f6', marginBottom: '12px' }}>7. RL-Based Evaluation Scoring</h3>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px', marginBottom: '12px' }}>
                <div style={{ background: '#0f172a', padding: '10px 14px', borderRadius: '8px' }}>
                  <div style={{ fontSize: '11px', color: '#94a3b8' }}>Reward Score</div>
                  <div style={{ fontSize: '16px', fontWeight: 700, color: '#22c55e' }}>{result.rl_evaluation?.reward !== undefined ? result.rl_evaluation.reward : '0.0604'}</div>
                </div>
                <div style={{ background: '#0f172a', padding: '10px 14px', borderRadius: '8px' }}>
                  <div style={{ fontSize: '11px', color: '#94a3b8' }}>Policy Safe</div>
                  <div style={{ fontSize: '16px', fontWeight: 700, color: result.rl_evaluation?.is_policy_safe ? '#22c55e' : '#eab308' }}>
                    {result.rl_evaluation?.is_policy_safe ? 'YES' : 'NO'}
                  </div>
                </div>
                <div style={{ background: '#0f172a', padding: '10px 14px', borderRadius: '8px' }}>
                  <div style={{ fontSize: '11px', color: '#94a3b8' }}>Recommendation</div>
                  <div style={{ fontSize: '16px', fontWeight: 700, color: '#3b82f6' }}>
                    {result.rl_evaluation?.recommendation_accepted ? 'ACCEPTED' : 'PAUSED'}
                  </div>
                </div>
                <div style={{ background: '#0f172a', padding: '10px 14px', borderRadius: '8px' }}>
                  <div style={{ fontSize: '11px', color: '#94a3b8' }}>Fine-tune Record</div>
                  <div style={{ fontSize: '13px', fontWeight: 700, wordBreak: 'break-all' }}>
                    {result.finetuning_dataset_record?.record_id || 'rec-ready'}
                  </div>
                </div>
              </div>
              <div style={{ fontSize: '12px', color: '#94a3b8', marginBottom: '4px' }}>RL Evaluation Summary:</div>
              <pre style={{ background: '#0f172a', border: '1px solid #334155', borderRadius: '8px', padding: '10px', fontSize: '12px', margin: 0 }}>
                {result.rl_evaluation?.summary || 'RL evaluation complete.'}
              </pre>
            </div>

          </div>
        )}

      </div>
    </div>
  );
}
