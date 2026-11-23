# ================================================================
# 0. Section: IMPORTS
# ================================================================
from typing import Any
from pathlib import Path
from dacite import Config, DaciteError, from_dict

from pypeline.errors import PipelineError

from ..step import Step
from .pipeline import Pipeline
from ..registries import StepRegistry
from .pipeline_draft import PipelineDraft
from .settings import GlobalSettings, InputSettings, OutputSettings

KNOWN_SECTIONS: frozenset[str] = frozenset({"global", "input", "steps", "output"})
CONFIG = Config(strict=True, type_hooks={Path: Path})


# ================================================================
# 1. Section: Functions
# ================================================================
class PipelineBuilder:
    """Turn an unchecked PipelineDraft into a validated, ready-to-run Pipeline."""

    def build(self, draft: PipelineDraft) -> Pipeline:
        """Build a Pipeline from a draft and check it is runnable before returning it.

        Raises:
            PipelineError: If a section, step or save point is invalid, or the steps
                cannot run in the given order.
        """
        _validate_keys(draft.data)

        # 1. Builds the settings
        global_settings = self.build_section(
            GlobalSettings, draft.data["global"], "global"
        )
        input_settings = self.build_section(InputSettings, draft.data["input"], "input")
        output_settings = self.build_section(
            OutputSettings, draft.data["output"], "output"
        )

        # 2. Builds the steps
        steps = self.build_steps(draft.data["steps"])
        pipeline = Pipeline(
            global_settings=global_settings,
            input_settings=input_settings,
            output_settings=output_settings,
            steps=steps,
        )

        # 3. Checks for step validity
        self.validate_pipeline(pipeline)

        return pipeline

    # ──────────────────────────────────────────────────────
    # 1.2 Subsection: Public Helper Functions
    # ──────────────────────────────────────────────────────
    def build_section(self, cls: Any, data: dict, section: str) -> Any:
        """Build a settings dataclass from one section of the pipeline data (dict from
        yaml).

        Args:
            cls: Dataclass to build.
            data: Raw mapping for this section, as loaded from the pipeline file.
            section: Section name, used only to prefix error messages.

        Raises:
            PipelineError: If a field without a default is missing, a key has no matching
                field, or a value has the wrong type.
        """
        try:
            return from_dict(cls, data, config=CONFIG)
        except DaciteError as e:
            raise PipelineError(f"[{section}] {e}") from e

    def build_steps(self, raw_steps: list[dict]) -> list[Step]:
        """Build each step from its registry `key` and the remaining keys as its fields.

        Raises:
            PipelineError: If a step has no `name`, the name is not registered, or its
                fields are missing, unknown or of the wrong type.
        """
        steps = []
        for i, raw in enumerate(raw_steps):
            # 1. Get the specific step draft params
            params = dict(raw)
            name = params.pop("name", None)

            _validate_step_name(i, name)

            # 2. Saves the steps into registry
            step_cls = StepRegistry.get_type(name)
            steps.append(self.build_section(step_cls, params, f"steps[{i}].{name}"))
        return steps

    def validate_pipeline(self, pipeline: Pipeline) -> None:
        """Check a Pipeline's steps and save points are consistent; `build` already
        calls it.

        Call it directly for a Pipeline constructed by hand, e.g. in tests.

        Raises:
            PipelineError: If a step's required steps do not appear earlier, a step's input
                type is not loaded or produced before it, or a save point names a missing
                step or an out-of-range occurrence.
        """
        _validate_step_order(pipeline.steps)
        _validate_save_points(pipeline)
        _validate_input_flow(pipeline)


# ──────────────────────────────────────────────────────
# 1.1 Subsection: Private Helper Functions
# ──────────────────────────────────────────────────────
def _validate_keys(data: dict) -> None:
    missing = KNOWN_SECTIONS - set(data)
    unknown = set(data) - KNOWN_SECTIONS

    if missing or unknown:
        raise PipelineError(
            f"Invalid pipeline sections. Missing: {sorted(missing) or 'none'}; "
            f"unknown: {sorted(unknown) or 'none'}. "
            f"Expected exactly: {sorted(KNOWN_SECTIONS)}"
        )


def _validate_step_name(pos: int, name: str | None) -> None:
    if name is None:
        raise PipelineError(f"[steps[{pos}]] missing 'name'")

    if not StepRegistry.has(name):
        raise PipelineError(
            f"[steps[{pos}]] unknown step {name!r}. Known: {sorted(StepRegistry.known_keys())}"
        )


def _validate_step_order(steps: list[Step]) -> None:
    seen: list[type[Step]] = []
    for i, step in enumerate(steps):
        if not set(seen) >= set(step.requires):
            missing = set(step.requires) - set(seen)
            raise PipelineError(
                f"[steps[{i}]] {StepRegistry.key_of(step)!r} {missing} earlier in the pipeline"
            )
        seen.append(type(step))


def _validate_input_flow(pipeline: Pipeline) -> None:
    """Check each step's input type is loaded or produced by an earlier step."""
    settings = pipeline.input_settings

    # 1. Actors loaded from the input sources
    available: list[str] = list(settings.load_as.values())
    for source in settings.sources:
        available.extend(source.load_as.values())

    # 2. Walk the steps, adding what each one produces
    for i, step in enumerate(pipeline.steps):
        needed = step.input_name
        produced = step.output_name
        if needed not in available:
            raise PipelineError(
                f"[steps[{i}]] {StepRegistry.key_of(step)!r} needs {needed}, "
                f"but only {available} are available at this point"
            )

        # 3. Removes inputs from consideration when mutable
        if step.mutable:
            available = [a for a in available if a != needed]

        available.append(produced)


def _validate_save_points(pipeline: Pipeline) -> None:
    names = pipeline.steps_names
    for i, point in enumerate(pipeline.output_settings.save_points):
        count = names.count(point.after)
        if count == 0:
            raise PipelineError(
                f"[output.save_points[{i}]] no step named {point.after!r}"
            )
        if not 1 <= point.occurrence <= count:
            raise PipelineError(
                f"[output.save_points[{i}]] {point.after!r} occurrence {point.occurrence} "
                f"out of range (1-{count})"
            )
