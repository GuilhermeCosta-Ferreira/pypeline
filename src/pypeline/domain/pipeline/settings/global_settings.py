# ================================================================
# 0. Section: IMPORTS
# ================================================================
from dataclasses import dataclass


# ================================================================
# 1. Section: Functions
# ================================================================
@dataclass(frozen=True)
class GlobalSettings:
    """The `global` section of a pipeline file.

    Attributes:
        pipeline_name: Name of the pipeline.
        check_scope: Not used yet.
        save_all_intermediates: Not used yet.
    """
    pipeline_name: str
    check_scope: bool
    save_all_intermediates: bool
