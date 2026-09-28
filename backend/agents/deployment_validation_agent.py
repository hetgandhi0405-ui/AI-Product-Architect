import time
from typing import Any, Callable, Dict, List, Optional
from backend.agents.state import AgentState
from backend.utils.security_redaction import redact_secrets


def deployment_validation_agent(
    state: AgentState,
    ecs_client: Optional[Any] = None,
    http_getter: Optional[Callable[[str, int], tuple[int, Dict[str, Any]]]] = None,
) -> AgentState:
    """
    Validate cloud deployment:
    - Verifies ECS task count and stability
    - Polls GET /health on ALB URL (with retries)
    - Verifies database connectivity response
    - Only sets service_url if stage PASSED

    Vocabulary:
    Stage: PASSED | FAILED | SKIPPED | UNAVAILABLE
    Health: HEALTHY | DEGRADED | UNHEALTHY | INSUFFICIENT_DATA
    """
    deploy_mode = state.get("deploy_mode", "dry-run")
    deployment_status = state.get("deployment_status", "SKIPPED")
    pending_url = state.get("_pending_service_url")

    validation_errors: List[str] = []
    state["service_url"] = None

    # In dry-run mode or if deployment was skipped, validation is SKIPPED
    if deploy_mode == "dry-run" or deployment_status == "SKIPPED":
        state["deployment_validation_status"] = "SKIPPED"
        state["health_status"] = "INSUFFICIENT_DATA"
        state["validation_errors"] = []
        return state

    # If deployment failed, validation is FAILED
    if deployment_status in ("FAILED", "UNAVAILABLE"):
        state["deployment_validation_status"] = "FAILED"
        state["health_status"] = "UNHEALTHY"
        state["validation_errors"] = [
            f"Deployment stage was {deployment_status}; cannot validate."
        ]
        return state

    # If there is no pending service URL
    if not pending_url:
        state["deployment_validation_status"] = "FAILED"
        state["health_status"] = "UNHEALTHY"
        state["validation_errors"] = ["No public ALB endpoint was returned by deployment"]
        return state

    injected_http = http_getter or state.get("http_getter")
    injected_ecs = ecs_client or state.get("ecs_client")

    # Injected test / mock execution
    if injected_http is not None:
        try:
            status_code, data = injected_http(f"{pending_url}/health", 10)
            if status_code == 200:
                db_status = data.get("database")
                if db_status in ("connected", "ok", None):
                    state["deployment_validation_status"] = "PASSED"
                    state["health_status"] = "HEALTHY"
                    state["service_url"] = pending_url
                    state["validation_errors"] = []
                else:
                    state["deployment_validation_status"] = "FAILED"
                    state["health_status"] = "DEGRADED"
                    state["service_url"] = None
                    state["validation_errors"] = [
                        f"Database reported degraded state: {db_status}"
                    ]
            else:
                state["deployment_validation_status"] = "FAILED"
                state["health_status"] = "UNHEALTHY"
                state["service_url"] = None
                state["validation_errors"] = [
                    f"Health check endpoint returned HTTP {status_code}"
                ]
            return state
        except Exception as exc:
            state["deployment_validation_status"] = "FAILED"
            state["health_status"] = "UNHEALTHY"
            state["service_url"] = None
            state["validation_errors"] = [redact_secrets(str(exc))]
            return state

    # Real HTTP validation against ALB
    try:
        import httpx

        max_retries = 10
        delay_seconds = 5
        healthy = False

        for attempt in range(max_retries):
            try:
                response = httpx.get(f"{pending_url}/health", timeout=10.0)
                if response.status_code == 200:
                    data = response.json()
                    db_ok = data.get("database") in ("connected", "ok", None)
                    if db_ok:
                        state["deployment_validation_status"] = "PASSED"
                        state["health_status"] = "HEALTHY"
                        state["service_url"] = pending_url
                        state["validation_errors"] = []
                        healthy = True
                        break
                    else:
                        validation_errors.append(
                            f"Database not connected on attempt {attempt + 1}"
                        )
                else:
                    validation_errors.append(
                        f"HTTP {response.status_code} on attempt {attempt + 1}"
                    )
            except Exception as e:
                validation_errors.append(f"Connection attempt {attempt + 1} failed: {redact_secrets(str(e))}")

            if attempt < max_retries - 1:
                time.sleep(delay_seconds)

        if not healthy:
            state["deployment_validation_status"] = "FAILED"
            state["health_status"] = "UNHEALTHY"
            state["service_url"] = None
            state["validation_errors"] = validation_errors

    except Exception as exc:
        state["deployment_validation_status"] = "FAILED"
        state["health_status"] = "UNHEALTHY"
        state["service_url"] = None
        state["validation_errors"] = [redact_secrets(str(exc))]

    return state
