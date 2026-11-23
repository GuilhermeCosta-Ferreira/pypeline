# ================================================================
# 0. Section: IMPORTS
# ================================================================
from dataclasses import dataclass
from functools import cached_property

from .settings import SavePoint
from ..step import Step, StepScope
from .settings import InputSettings
from .settings import OutputSettings
from .settings import GlobalSettings
from .wave import Wave, build_waves
from ..registries import StepRegistry


# ================================================================
# 1. Section: Functions
# ================================================================
@dataclass(frozen=True)
class Pipeline:
    """A pipeline's settings and its steps in order.

    Build it with `PipelineBuilder`.
    """

    global_settings: GlobalSettings
    input_settings: InputSettings
    output_settings: OutputSettings
    steps: list[Step]

    # ================================================================
    # 2. Section: Cached Propeties
    # ================================================================
    @cached_property
    def steps_names(self) -> list[str]:
        return [StepRegistry.key_of(step) for step in self.steps]

    @cached_property
    def steps_scope(self) -> list[StepScope]:
        return [step.scope for step in self.steps]

    @cached_property
    def save_points(self) -> dict[int, list[SavePoint]]:
        points: dict[int, list[SavePoint]] = {}
        for point in self.output_settings.save_points:
            positions = [i for i, n in enumerate(self.steps_names) if n == point.after]
            points.setdefault(positions[point.occurrence - 1], []).append(point)
        return points

    @cached_property
    def waves(self) -> list[Wave]:
        return build_waves(self.steps)

    # ================================================================
    # 3. Section: Methods
    # ================================================================
    def get_save_points_after(self, idx: int) -> list[SavePoint]:
        return self.save_points.get(idx, [])
