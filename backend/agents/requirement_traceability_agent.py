from typing import Any, Dict, List


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().lower()


def _extract_requirements(architecture: Dict[str, Any]) -> List[Any]:
    for key in [
        "functional_requirements",
        "requirements",
        "features",
        "product_requirements",
    ]:
        candidate = architecture.get(key)
        if isinstance(candidate, list):
            return candidate
        if isinstance(candidate, str) and candidate.strip():
            return [x.strip() for x in candidate.split("\n") if x.strip()]
    return []


def _extract_features(architecture: Dict[str, Any]) -> List[Any]:
    features = architecture.get("features", [])
    if isinstance(features, list):
        return features
    if isinstance(features, str) and features.strip():
        return [x.strip() for x in features.split("\n") if x.strip()]
    return []


def _extract_components(architecture: Dict[str, Any]) -> List[Dict[str, Any]]:
    components = architecture.get("components")
    if isinstance(components, list):
        return [
            x if isinstance(x, dict) else {"name": str(x)}
            for x in components
        ]

    components = architecture.get("architecture_components", [])
    if isinstance(components, list):
        return [
            x if isinstance(x, dict) else {"name": str(x)}
            for x in components
        ]

    return []


def _extract_tests(architecture: Dict[str, Any]) -> List[Any]:
    tests = architecture.get("tests")
    if isinstance(tests, list):
        return tests

    strategy = architecture.get("testing_strategy")
    if isinstance(strategy, list):
        return strategy
    if isinstance(strategy, str) and strategy.strip():
        return [strategy]

    return []


def _keywords(text: str) -> set:
    stop_words = {
        "the", "a", "an", "and", "or", "to", "of", "for",
        "with", "must", "should", "system", "application",
        "users", "user",
    }

    return {
        word
        for word in _normalize_text(text)
        .replace(",", " ")
        .replace(".", " ")
        .split()
        if len(word) > 2 and word not in stop_words
    }


def _match_score(requirement: str, candidate: str) -> float:
    required = _keywords(requirement)
    available = _keywords(candidate)

    if not required or not available:
        return 0.0

    return round(
        len(required.intersection(available))
        / len(required)
        * 100,
        2,
    )


def _best_matches(
    requirement: str,
    candidates: List[str],
    minimum_score: float = 20.0,
) -> List[Dict[str, Any]]:
    matches = []

    for candidate in candidates:
        score = _match_score(requirement, candidate)
        if score >= minimum_score:
            matches.append({
                "name": candidate,
                "match_score": score,
            })

    return sorted(
        matches,
        key=lambda x: x["match_score"],
        reverse=True,
    )


def requirement_traceability_agent(
    state: Dict[str, Any],
) -> Dict[str, Any]:

    architecture = state.get("architecture", {})

    if not isinstance(architecture, dict):
        architecture = {}

    requirements = _extract_requirements(architecture)
    features = _extract_features(architecture)
    components = _extract_components(architecture)
    tests = _extract_tests(architecture)

    feature_names = [
        str(x.get("name", ""))
        if isinstance(x, dict)
        else str(x)
        for x in features
        if str(x).strip()
    ]

    component_names = [
        str(x.get("name", ""))
        for x in components
        if x.get("name")
    ]

    test_names = [
        str(x.get("name", x))
        if isinstance(x, dict)
        else str(x)
        for x in tests
        if str(x).strip()
    ]

    matrix = []

    for index, requirement in enumerate(requirements, start=1):

        if isinstance(requirement, dict):
            text = requirement.get(
                "description",
                requirement.get("text", ""),
            )
        else:
            text = str(requirement)

        text = str(text).strip()

        if not text:
            continue

        feature_matches = _best_matches(
            text,
            feature_names,
        )

        component_matches = _best_matches(
            text,
            component_names,
        )

        test_matches = _best_matches(
            text,
            test_names,
        )

        satisfied = bool(
            feature_matches
            or component_matches
            or test_matches
        )

        matrix.append({
            "requirement_id": f"REQ-{index:03d}",
            "requirement": text,
            "features": feature_matches,
            "architecture_components": component_matches,
            "tests": test_matches,
            "status": (
                "SATISFIED"
                if satisfied
                else "UNSATISFIED"
            ),
        })

    total = len(matrix)

    satisfied = sum(
        1
        for item in matrix
        if item["status"] == "SATISFIED"
    )

    coverage = (
        round((satisfied / total) * 100, 2)
        if total
        else 0.0
    )

    if coverage >= 90:
        status = "EXCELLENT"
    elif coverage >= 75:
        status = "GOOD"
    elif coverage >= 50:
        status = "PARTIAL"
    else:
        status = "LOW"

    result = {
        "status": status,
        "requirement_count": total,
        "satisfied_requirements": satisfied,
        "unsatisfied_requirements": total - satisfied,
        "coverage_percent": coverage,
        "traceability_matrix": matrix,
    }

    architecture["requirement_traceability"] = result

    state["architecture"] = architecture
    state["requirement_traceability"] = result

    return state
