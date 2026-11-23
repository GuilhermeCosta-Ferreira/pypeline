# ================================================================
# 1. Section: Functions
# ================================================================
class PipelineError(ValueError):
    """The pipeline file or its steps are invalid; raised while building, before
    anything runs."""


class RunnerError(ValueError):
    """The pipeline failed while running, after it was built and validated."""
