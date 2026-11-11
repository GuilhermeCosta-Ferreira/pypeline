# ================================================================
# 0. Section: IMPORTS
# ================================================================
from dataclasses import dataclass

from ..step import Step
from .settings import InputSettings
from .settings import OutputSettings
from .settings import GlobalSettings
from ..registries import StepRegistry


# ================================================================
# 1. Section: Functions
# ================================================================
@dataclass(frozen=True)
class Protocol:
    global_settings: GlobalSettings
    input_settings: InputSettings
    output_settings: OutputSettings
    steps: list[Step]

    @property
    def steps_names(self) -> list[str]:
        return [StepRegistry.key_of(step) for step in self.steps]
