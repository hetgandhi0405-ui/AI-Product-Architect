import os


DEFAULT_MODEL = "gemini-3.5-flash-lite"


def get_model(role: str = "fast") -> str:
    """
    Return the Gemini model configured for the requested role.

    Roles:
      - fast   : lower-latency agents
      - strong : higher-quality agents

    Both currently default to the existing model so behavior
    remains unchanged until different models are intentionally configured.
    """
    role = role.lower().strip()

    if role == "strong":
        return os.getenv(
            "AI_PRODUCT_ARCHITECT_STRONG_MODEL",
            DEFAULT_MODEL,
        )

    return os.getenv(
        "AI_PRODUCT_ARCHITECT_FAST_MODEL",
        DEFAULT_MODEL,
    )


def get_fast_model() -> str:
    return get_model("fast")


def get_strong_model() -> str:
    return get_model("strong")
