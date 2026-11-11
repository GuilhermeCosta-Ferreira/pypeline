# ================================================================
# 0. Section: IMPORTS
# ================================================================
from pathlib import Path
from types import get_original_bases
from pypeline.errors import ProtocolError
from typing import Any, get_args, get_origin
from dacite import Config, DaciteError, from_dict

from ..step import Step
from .protocol import Protocol
from ..registries import StepRegistry
from .protocol_draft import ProtocolDraft
from .settings import GlobalSettings, InputSettings, OutputSettings

KNOWN_SECTIONS: frozenset[str] = frozenset({"global", "input", "steps", "output"})
CONFIG = Config(strict=True, type_hooks={Path: Path})



# ================================================================
# 1. Section: Functions
# ================================================================
class ProtocolBuilder:
    """Turn an unchecked ProtocolDraft into a validated, ready-to-run Protocol."""

    def build(self, draft: ProtocolDraft) -> Protocol:
        """Build a Protocol from a draft and check it is runnable before returning it.

        Raises:
            ProtocolError: If a section, step or save point is invalid, or the steps
                cannot run in the given order.
                """
        _validate_keys(draft.data)

        # 1. Builds the settings
        global_settings = build_section(GlobalSettings, draft.data["global"], "global")
        input_settings = build_section(InputSettings, draft.data["input"], "input")
        output_settings = build_section(OutputSettings, draft.data["output"], "output")

        # 2. Builds the steps
        steps = build_steps(draft.data["steps"])
        protocol = Protocol(
            global_settings=global_settings,
            input_settings=input_settings,
            output_settings=output_settings,
            steps=steps
        )

        # 3. Checks for step validity
        validate_protocol(protocol)

        return protocol


# ──────────────────────────────────────────────────────
# 1.1 Subsection: Private Helper Functions
# ──────────────────────────────────────────────────────
def _validate_keys(data: dict) -> None:
    missing = KNOWN_SECTIONS - set(data)
    unknown = set(data) - KNOWN_SECTIONS

    if missing or unknown:
        raise ProtocolError(
            f"Invalid protocol sections. Missing: {sorted(missing) or 'none'}; "
            f"unknown: {sorted(unknown) or 'none'}. "
            f"Expected exactly: {sorted(KNOWN_SECTIONS)}"
        )

def _validate_step_name(pos: int, name: str | None) -> None:
    if name is None:
        raise ProtocolError(f"[steps[{pos}]] missing 'name'")

    if not StepRegistry.has(name):
        raise ProtocolError(
            f"[steps[{pos}]] unknown step {name!r}. Known: {sorted(StepRegistry.known_keys())}"
        )

def _validate_step_order(steps: list[Step]) -> None:
    seen: list[type[Step]] = []
    for i, step in enumerate(steps):
        if not set(seen) >= set(step.requires):
            missing = set(step.requires) - set(seen)
            raise ProtocolError(
                f"[steps[{i}]] {StepRegistry.key_of(step)!r} {missing} earlier in the pipeline"
            )
        seen.append(type(step))

def _validate_input_flow(protocol: Protocol) -> None:
    """Check each step's input type is loaded or produced by an earlier step."""
    settings = protocol.input_settings

    # 1. Actors loaded from the input sources
    available: list[str] = list(settings.load_as.values())
    for source in settings.sources:
        available.extend(source.load_as.values())

    # 2. Walk the steps, adding what each one produces
    for i, step in enumerate(protocol.steps):
        needed, produced = _io_types(type(step))
        if needed.__name__ not in available:
            raise ProtocolError(
                f"[steps[{i}]] {StepRegistry.key_of(step)!r} needs {needed.__name__}, "
                f"but only {available} are available at this point"
            )
        available.append(produced.__name__)

def _validate_save_points(protocol: Protocol) -> None:
    names = protocol.steps_names
    for i, point in enumerate(protocol.output_settings.save_points):
        count = names.count(point.after)
        if count == 0:
            raise ProtocolError(f"[output.save_points[{i}]] no step named {point.after!r}")
        if not 1 <= point.occurrence <= count:
            raise ProtocolError(
                f"[output.save_points[{i}]] {point.after!r} occurrence {point.occurrence} "
                f"out of range (1-{count})"
            )

def _io_types(step_cls: type[Step]) -> tuple[type, type]:
    """Read a step's input and output types from its direct `Step[InputClass, OutputClass]` base."""
    for base in get_original_bases(step_cls):
        if get_origin(base) is Step:
            inp, out = (get_origin(t) or t for t in get_args(base))
            return inp, out
    raise ProtocolError(f"{step_cls.__name__} does not declare Step[InputClass, OutputClass]")


# ──────────────────────────────────────────────────────
# 1.2 Subsection: Public Helper Functions
# ──────────────────────────────────────────────────────
def build_section(cls: Any, data: dict, section: str) -> Any:
    """Build a settings dataclass from one section of the protocol data (dict from yaml).

    Args:
        cls: Dataclass to build.
        data: Raw mapping for this section, as loaded from the protocol file.
        section: Section name, used only to prefix error messages.

    Raises:
        ProtocolError: If a field without a default is missing, a key has no matching
            field, or a value has the wrong type.
    """
    try:
        return from_dict(cls, data, config=CONFIG)
    except DaciteError as e:
        raise ProtocolError(f"[{section}] {e}") from e

def build_steps(raw_steps: list[dict]) -> list[Step]:
    """Build each step from its registry `key` and the remaining keys as its fields.

    Raises:
        ProtocolError: If a step has no `name`, the name is not registered, or its
            fields are missing, unknown or of the wrong type."""
    steps = []
    for i, raw in enumerate(raw_steps):
        # 1. Get the specific step draft params
        params = dict(raw)
        name = params.pop("name", None)

        _validate_step_name(i, name)

        # 2. Saves the steps into registry
        step_cls = StepRegistry.get_type(name)
        steps.append(build_section(step_cls, params, f"steps[{i}].{name}"))
    return steps

def validate_protocol(protocol: Protocol) -> None:
    """Check a Protocol's steps and save points are consistent; `build` already calls it.

    Call it directly for a Protocol constructed by hand, e.g. in tests.

    Raises:
        ProtocolError: If a step's required steps do not appear earlier, a step's input
            type is not loaded or produced before it, or a save point names a missing
            step or an out-of-range occurrence.
    """
    _validate_step_order(protocol.steps)
    _validate_save_points(protocol)
    _validate_input_flow(protocol)
