"""
Phase 15 — Fine-Tuning Dataset Generator Agent
===============================================
Formats the completed pipeline state into a standardized JSONL training record.
Enables fine-tuning custom models on full application-to-cloud transformation trajectories.

Dataset Record Schema:
{
  "project_id": "...",
  "prompt": "...",
  "product_metadata": {...},
  "cloud_architecture_spec": {...},
  "infrastructure_state": {...},
  "validation_report": {...},
  "optimization_recommendation": {...},
  "rl_evaluation": {...},
  "quality_score": 1.0
}
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from backend.agents.state import AgentState


def finetuning_dataset_agent(state: AgentState) -> AgentState:
    """
    Format pipeline state into a fine-tuning dataset record and append to dataset JSONL file.
    """
    project_id = state.get("project_id", "proj-unknown")
    requirements = state.get("requirements", "")
    prod_meta = state.get("product_metadata", {})
    cloud_spec = state.get("cloud_architecture_spec", {})
    infra_state = state.get("infrastructure_state", {})
    val_report = state.get("validation_report", {})
    opt_rec = state.get("optimization_recommendation", {})
    rl_eval = state.get("rl_evaluation", {})
    release_gate = state.get("release_gate", {})

    # Compute trajectory quality score (0.0 to 1.0)
    is_approved = release_gate.get("approved", False)
    val_passed = val_report.get("deployment_ready", False)
    rl_accepted = rl_eval.get("recommendation_accepted", True)

    quality_score = 1.0 if (is_approved and val_passed) else (0.7 if is_approved else 0.4)
    if rl_eval.get("reward", 0) > 0.1:
        quality_score = min(1.0, quality_score + 0.1)

    record = {
        "record_id": f"rec-{project_id}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "input": {
            "requirements": requirements,
            "project_name": state.get("project_name", ""),
        },
        "target_outputs": {
            "product_metadata": prod_meta,
            "cloud_architecture_spec": cloud_spec,
            "infrastructure_state": infra_state,
            "validation_report": val_report,
            "optimization_recommendation": opt_rec,
            "rl_evaluation": rl_eval,
        },
        "metadata": {
            "execution_mode": state.get("execution_mode", "QUICK"),
            "quality_score": round(quality_score, 2),
            "approved": is_approved,
            "deployment_ready": val_passed,
        }
    }

    state["finetuning_dataset_record"] = record

    # Append to local dataset JSONL store
    dataset_dir_env = os.environ.get("AI_PRODUCT_ARCHITECT_DATASET_DIR")
    if dataset_dir_env:
        ds_dir = Path(dataset_dir_env).resolve()
    else:
        ds_dir = (Path(__file__).resolve().parents[2] / "data" / "finetuning").resolve()

    try:
        ds_dir.mkdir(parents=True, exist_ok=True)
        ds_file = ds_dir / "dataset.jsonl"
        with open(ds_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    except Exception:
        # Non-critical write failure
        pass

    return state
