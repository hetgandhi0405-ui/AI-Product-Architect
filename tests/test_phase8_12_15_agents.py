"""
Tests for Phase 8 (Deployment Approval & Rollback), Phase 12 (RL Evaluation), and Phase 15 (Fine-Tuning Dataset).
"""
import pytest
from backend.agents.deployment_approval_agent import deployment_approval_agent, execute_rollback
from backend.agents.rl_evaluation_agent import rl_evaluation_agent
from backend.agents.finetuning_dataset_agent import finetuning_dataset_agent


def _make_state(**kwargs):
    state = {
        "project_id": "test-proj-01",
        "project_name": "Task Management App",
        "requirements": "Build a task management platform with PostgreSQL",
        "deploy_mode": "dry-run",
        "infrastructure_state": {
            "architecture_id": "ARCH-001",
            "resources": [{"id": "vpc-1", "type": "aws_vpc"}],
            "expected_metrics": {"monthly_cost_usd": 150.0, "latency_p95_ms": 200.0},
        },
        "optimization_candidates": [
            {
                "candidate_id": "CAND-001",
                "estimated_cost_usd": 120.0,
                "estimated_latency_p95_ms": 150.0,
                "estimated_sla": 99.99,
                "risk_score": 0.2,
                "changes": ["Enable Redis caching"],
            }
        ],
        "optimization_recommendation": {
            "recommended_action": "APPLY_CANDIDATE",
            "summary": "Add ElastiCache Redis",
        },
        "release_gate": {"approved": True},
        "validation_report": {"deployment_ready": True},
    }
    state.update(kwargs)
    return state


# ─── Phase 8: Deployment Approval & Rollback ──────────────────────────────────

class TestDeploymentApprovalAgent:
    def test_dry_run_auto_approved(self):
        state = _make_state(deploy_mode="dry-run")
        result = deployment_approval_agent(state)
        approval = result["deployment_approval"]
        assert approval["status"] == "APPROVED"
        assert approval["approved"] is True
        assert "rollback_state" in result

    def test_real_mode_pending_without_flag(self):
        state = _make_state(deploy_mode="real", approved=False)
        result = deployment_approval_agent(state)
        approval = result["deployment_approval"]
        assert approval["status"] == "PENDING_APPROVAL"
        assert approval["approved"] is False

    def test_execute_rollback_restores_snapshot(self):
        state = _make_state()
        state = deployment_approval_agent(state)
        state["infrastructure_state"] = {"architecture_id": "ARCH-MUTATED"}
        result = execute_rollback(state)
        assert result["rollback_status"]["status"] == "SUCCESS"
        assert result["infrastructure_state"]["architecture_id"] == "ARCH-001"


# ─── Phase 12: RL Evaluation ──────────────────────────────────────────────────

class TestRLEvaluationAgent:
    def test_positive_reward_for_good_candidate(self):
        state = _make_state()
        result = rl_evaluation_agent(state)
        rl_eval = result["rl_evaluation"]
        assert "reward" in rl_eval
        assert rl_eval["is_policy_safe"] is True
        assert rl_eval["recommendation_accepted"] is True
        assert result["rl_policy_validated"] is True

    def test_no_change_when_candidates_empty(self):
        state = _make_state(optimization_candidates=[], optimization_recommendation={})
        result = rl_evaluation_agent(state)
        rl_eval = result["rl_evaluation"]
        assert rl_eval["reward"] == 0.0
        assert rl_eval["recommendation_accepted"] is False


# ─── Phase 15: Fine-Tuning Dataset ───────────────────────────────────────────

class TestFineTuningDatasetAgent:
    def test_generates_valid_dataset_record(self):
        state = _make_state()
        state = rl_evaluation_agent(state)
        result = finetuning_dataset_agent(state)
        rec = result["finetuning_dataset_record"]
        assert rec["record_id"] == "rec-test-proj-01"
        assert "requirements" in rec["input"]
        assert "infrastructure_state" in rec["target_outputs"]
        assert "rl_evaluation" in rec["target_outputs"]
        assert rec["metadata"]["quality_score"] > 0.0
