from dataclasses import dataclass
from typing import FrozenSet


@dataclass(frozen=True)
class ExecutionConfig:
    """Select which optional graph nodes run for a request."""

    mode: str = "FULL"

    # QUICK omits all optional enrichment and monitoring nodes.
    optional_nodes: FrozenSet[str] = frozenset({
        "architecture_alternatives",
        "architecture_evaluator",
        "architecture_knowledge_graph",
        "digital_twin",
        "what_if_engine",
        "architecture_simulator",
        "plugin_tool",
        "monitoring",
        "failure_detection",
    })

    # TEST keeps the core pipeline but omits the heaviest simulation work.
    test_skipped_nodes: FrozenSet[str] = frozenset({
        "digital_twin",
        "what_if_engine",
        "architecture_simulator",
    })

    @property
    def is_quick(self) -> bool:
        return self.mode.upper() == "QUICK"

    @property
    def is_test(self) -> bool:
        return self.mode.upper() == "TEST"

    @property
    def is_full(self) -> bool:
        return self.mode.upper() == "FULL"

    def should_run(self, node_name: str) -> bool:
        if self.is_full:
            return True
        if self.is_quick:
            return node_name not in self.optional_nodes
        if self.is_test:
            return node_name not in self.test_skipped_nodes
        return True


def get_execution_config(mode: str = "FULL") -> ExecutionConfig:
    normalized_mode = mode.upper()
    if normalized_mode not in {"QUICK", "TEST", "FULL"}:
        raise ValueError(
            f"Invalid execution mode: {mode}. Use QUICK, TEST, or FULL."
        )
    return ExecutionConfig(mode=normalized_mode)
