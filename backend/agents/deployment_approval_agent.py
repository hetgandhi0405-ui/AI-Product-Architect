"""
Phase 8 — Deployment Approval & Controlled Rollback Agent
===========================================================
Manages user approval workflow and rollback snapshots for cloud deployments.

Flow:
  PLAN → APPROVAL GATE → APPLY → VERIFY → (ROLLBACK IF FAILED)

Functions:
  1. Record approval decisions (user_id, approved: bool, timestamp, deploy_mode)
  2. Snapshot current infrastructure_state as rollback_state before applying changes
  3. Validate approval requirements before real infrastructure mutations occur
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from backend.agents.state import AgentState


def deployment_approval_agent(state: AgentState) -> AgentState:
    """
    Process approval decision and snapshot rollback state prior to cloud deployment.
    """
    deploy_mode = state.get("deploy_mode", "dry-run")
    infra_state = state.get("infrastructure_state", {})
    approved_flag = state.get("approved") is True

    # 1. Capture current known-good snapshot into rollback_state
    if infra_state:
        state["rollback_state"] = {
            "snapshot_id": f"snap-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "infrastructure_state": infra_state,
        }

    # 2. Build deployment_approval state
    approval_record: Dict[str, Any] = {
        "deploy_mode": deploy_mode,
        "approved": approved_flag if deploy_mode == "real" else True,
        "approver": state.get("approver", "system-dryrun" if deploy_mode == "dry-run" else "user"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "requires_approval": deploy_mode == "real",
        "status": "APPROVED" if (deploy_mode == "dry-run" or approved_flag) else "PENDING_APPROVAL",
    }

    state["deployment_approval"] = approval_record

    # 3. Append to deployment history
    history = state.get("deployment_history", [])
    history.append({
        "timestamp": approval_record["timestamp"],
        "deploy_mode": deploy_mode,
        "status": approval_record["status"],
        "architecture_id": infra_state.get("architecture_id", "ARCH-000"),
    })
    state["deployment_history"] = history

    return state


def execute_rollback(state: AgentState) -> AgentState:
    """
    Restore previous known-good infrastructure_state from rollback_state snapshot.
    """
    rollback = state.get("rollback_state", {})
    saved_infra = rollback.get("infrastructure_state")

    if not saved_infra:
        state["rollback_status"] = {
            "status": "FAILED",
            "reason": "No rollback_state snapshot available in project state",
        }
        return state

    # Restore previous state
    state["infrastructure_state"] = saved_infra
    state["rollback_status"] = {
        "status": "SUCCESS",
        "snapshot_id": rollback.get("snapshot_id"),
        "restored_at": datetime.now(timezone.utc).isoformat(),
    }

    arch = state.get("architecture", {})
    arch["infrastructure_state"] = saved_infra
    state["architecture"] = arch

    return state
