# ================================================================
# 1. Section: Functions
# ================================================================
class PipelineError(ValueError):
    """The pipeline file is malformed."""


class RunnerError(ValueError):
    """The runner found a mistake."""
