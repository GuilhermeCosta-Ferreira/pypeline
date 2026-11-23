# ================================================================
# 0. Section: IMPORTS
# ================================================================
from ..step import Step
from .registry import Registry


# ================================================================
# 1. Section: Functions
# ================================================================
class StepRegistry(Registry[Step]):
    """Registry of the steps a pipeline file can use, by `name`.

    Examples:
        >>> @StepRegistry.register("blur")
        ... @dataclass
        ... class Blur(Step[Image, Image]):
        ...     radius: int = 2
        ...     ...

        The registry key is the step's `name` in the pipeline file, and its fields are
        the other keys:

            steps:
              - name: blur
                radius: 3
    """
