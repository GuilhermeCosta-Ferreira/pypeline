# ================================================================
# 0. Section: IMPORTS
# ================================================================
import yaml

from pathlib import Path

from pypeline.errors import PipelineError

from ..domain.pipeline import PipelineDraft


# ================================================================
# 1. Section: Functions
# ================================================================
class PipelineLoader:
    """Reads a pipeline YAML file into an unchecked `PipelineDraft`."""

    def read(self, path: Path) -> PipelineDraft:
        """Parse `path` as YAML.

        Raises:
            PipelineError: If the file's top level is not a mapping.
        """
        with path.open() as f:
            data = yaml.safe_load(f)

        # 1. An empty file loads as None, a bare list or scalar is not a pipeline
        if not isinstance(data, dict):
            raise PipelineError(f"[{path}] expected a mapping of sections")
        return PipelineDraft(data)
