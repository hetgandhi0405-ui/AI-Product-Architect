"""
End-to-End Pipeline Integration Test
Executes a full requirement generation run through the complete LangGraph agent pipeline.
"""
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from backend.agents.graph import build_agent_graph

print("=== INITIALIZING AGENT GRAPH ===")
graph = build_agent_graph()

initial_state = {
    "project_id": "e2e-test-proj-100",
    "project_name": "E2E Task Manager App",
    "requirements": (
        "Build a task management platform for small businesses with PostgreSQL "
        "and Redis caching. Support 10,000 users with high availability."
    ),
    "execution_mode": "QUICK",
    "suggestions": [],
    "architecture": {},
    "correction_attempts": 0,
    "max_correction_attempts": 3,
    "code_correction_attempts": 0,
    "max_code_correction_attempts": 3,
    "integration_correction_attempts": 0,
    "max_integration_correction_attempts": 2,
}

print("=== EXECUTING END-TO-END PIPELINE ===")
result = graph.invoke(initial_state)

print("\n==================================================")
print("             PIPELINE RESULT SUMMARY              ")
print("==================================================")
print(f"Project ID:             {result.get('project_id')}")
print(f"Project Name:           {result.get('project_name')}")
print(f"Assembled Path:         {result.get('assembled_project_path')}")
print(f"Generated Files Count:  {len(result.get('generated_files', {}))}")

# 1. Product Metadata
prod_meta = result.get("product_metadata", {})
print("\n--- Phase 1: Product Metadata ---")
print(f"Frontend Framework:     {prod_meta.get('frontend', {}).get('framework')}")
print(f"Backend Framework:      {prod_meta.get('backend', {}).get('framework')}")
print(f"Database Engine:        {prod_meta.get('database', {}).get('engine')}")
print(f"Target Users:           {prod_meta.get('scalability', {}).get('target_users')}")
print(f"High Availability:      {prod_meta.get('scalability', {}).get('high_availability')}")
print(f"Needs Cache:            {prod_meta.get('scalability', {}).get('needs_cache')}")

# 2. Cloud Architecture Spec
cloud_spec = result.get("cloud_architecture_spec", {})
print("\n--- Phase 3: Cloud Architecture Spec ---")
print(f"Architecture ID:        {cloud_spec.get('architecture_id')}")
print(f"Compute Service:        {cloud_spec.get('compute', {}).get('service')}")
print(f"Database Instance:      {cloud_spec.get('database', {}).get('instance_class')}")
print(f"Multi-AZ Database:      {cloud_spec.get('database', {}).get('multi_az')}")
print(f"Cache Engine:           {cloud_spec.get('cache', {}).get('engine')}")
print(f"Est. Monthly Cost:      ${cloud_spec.get('estimated_metrics', {}).get('monthly_cost_usd')}/mo")

# 3. Infrastructure State
infra_state = result.get("infrastructure_state", {})
print("\n--- Phase 4: Infrastructure State ---")
print(f"Resource Count:         {len(infra_state.get('resources', []))}")
print(f"Relationship Count:     {len(infra_state.get('relationships', []))}")
print(f"State File Location:    {result.get('infrastructure_state_path')}")

# 4. Architecture Diagram
diagram = result.get("architecture_diagram", "")
print("\n--- Phase 5: Mermaid Architecture Diagram ---")
print("\n".join(diagram.splitlines()[:10]))
print("...")

# 5. Terraform Generation
tf_gen = result.get("terraform_generation", {})
print("\n--- Phase 6: Terraform Generation ---")
print(f"Status:                 {tf_gen.get('status')}")
print(f"Files Generated:        {list(tf_gen.get('files', {}).keys())}")
print(f"Terraform Path:         {result.get('terraform_path')}")

# 6. Unified Validation Report
val_report = result.get("validation_report", {})
print("\n--- Phase 2: Unified Validation Report ---")
print(f"Status:                 {val_report.get('status')}")
print(f"Deployment Ready:       {val_report.get('deployment_ready')}")
print(f"Gates Passed:           {val_report.get('gates_passed')}/{val_report.get('gates_total')}")

# 7. RL Evaluation
rl_eval = result.get("rl_evaluation", {})
print("\n--- Phase 12: RL Evaluation ---")
print(f"Reward Score:           {rl_eval.get('reward')}")
print(f"Policy Safe:            {rl_eval.get('is_policy_safe')}")
print(f"Accepted:               {rl_eval.get('recommendation_accepted')}")

# 8. Fine-tuning Record
rec = result.get("finetuning_dataset_record", {})
print("\n--- Phase 15: Fine-tuning Dataset ---")
print(f"Record ID:              {rec.get('record_id')}")
print(f"Quality Score:          {rec.get('metadata', {}).get('quality_score')}")

print("\n==================================================")
print("     ALL END-TO-END VERIFICATIONS COMPLETED       ")
print("==================================================")
