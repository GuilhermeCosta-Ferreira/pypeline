# ================================================================
# 0. Section: IMPORTS
# ================================================================
from dataclasses import dataclass
from abc import ABC, abstractmethod
from types import get_original_bases
from typing import Literal, final, ClassVar, get_args, get_origin

from pypeline.errors import PipelineError

StepScope = Literal["single", "global"]


# ================================================================
# 1. Section: Functions
# ================================================================
@dataclass
class Step[InputClass, OutputClass](ABC):
    """One operation of a pipeline: takes one input and returns one output.

    Subclass it with the input and output classes as type parameters, declare the step's
    settings as dataclass fields, implement `run`, `validate_input` and `validate_output`,
    and register it in `StepRegistry` so a pipeline file can name it. Never override
    `apply`: the runner calls it to validate, run and validate again.

    A step runs on every actor whose class name matches its input class. A mutable
    step can drop an actor by returning `None` from `run`: nothing is saved for it and
    later steps never see it. Keep `Step[Image, Image]` as the type parameters and
    annotate only `run` as returning `Image | None`.

    Attributes:
        scope: `"single"` runs the step once per actor of its input class. `"global"` runs
            it once on the list of all of them; declare the input as `list[X]`.
        requires: Step classes that must appear earlier in the pipeline.
        mutable: If True (default), the step consumes its input: the actors it ran on are
            dropped and only its output continues. If False, they are kept next to it.

    Examples:
        A single step, run once per `Image`:

        >>> @StepRegistry.register("blur")
        ... @dataclass
        ... class Blur(Step[Image, Image]):
        ...     radius: int = 2
        ...
        ...     def run(self, data: Image) -> Image:
        ...         return data.blur(self.radius)
        ...
        ...     def validate_input(self, data: Image) -> None: ...
        ...     def validate_output(self, output: Image) -> None: ...

        A filter that drops dark images and keeps the rest:

        >>> @StepRegistry.register("drop_dark")
        ... @dataclass
        ... class DropDark(Step[Image, Image]):
        ...     def run(self, data: Image) -> Image | None:
        ...         return data if data.brightness > 0.2 else None
        ...     ...

        A global step, run once on every `Image` at the same time, keeping them:

        >>> @StepRegistry.register("stats")
        ... @dataclass
        ... class Stats(Step[list[Image], ImageStats]):
        ...     scope = "global"
        ...     mutable = False
        ...     ...
    """

    scope: ClassVar[StepScope] = "single"
    requires: ClassVar[list[type[Step]]] = []
    mutable: ClassVar[bool] = True

    @property
    def input_type(self) -> type:
        return self.io_types()[0]

    @property
    def input_name(self) -> str:
        return self.io_types()[0].__name__

    @property
    def output_type(self) -> type:
        return self.io_types()[1]

    @property
    def output_name(self) -> str:
        return self.io_types()[1].__name__

    # ──────────────────────────────────────────────────────
    # 1.1 Subsection: Main Functions
    # ──────────────────────────────────────────────────────
    @final
    def apply(self, data: InputClass) -> OutputClass | None:
        """Validate the input, run the step and validate the output.

        The runner calls this; call it yourself only to try a step outside a pipeline.

        Args:
            data: One actor for a single step; the list of all actors of the input
                class for a global step.

        Returns:
            The step's output, already validated, or `None` if the step dropped the
            actor (`validate_output` is then skipped).
        """
        self.validate_input(data)
        result = self.run(data)
        if result is not None:
            self.validate_output(result)
        return result

    @abstractmethod
    def run(self, data: InputClass) -> OutputClass | None:
        """Transform the input into the step's output.

        Args:
            data: Input that already passed `validate_input`.

        Returns:
            The output, or `None` to drop the actor so it goes no further.
        """
        raise NotImplementedError()

    @abstractmethod
    def validate_input(self, data: InputClass) -> None:
        """Raise an exception if `run` cannot handle `data`; return to accept it."""

    @abstractmethod
    def validate_output(self, output: OutputClass) -> None:
        """Raise an exception if `run` returned an unacceptable `output`; return to
        accept it."""

    # ──────────────────────────────────────────────────────
    # 1.2 Subsection: Helper Functions
    # ──────────────────────────────────────────────────────
    def io_types(self) -> tuple[type, type]:
        for base in get_original_bases(type(self)):
            if get_origin(base) is Step:
                inp, out = get_args(base)
                if (
                    get_origin(inp) is list
                ):  # global steps take a list of one actor class
                    inp = get_args(inp)[0]
                return get_origin(inp) or inp, get_origin(out) or out
        raise PipelineError(
            f"{type(self).__name__} does not declare Step[InputClass, OutputClass]"
        )
