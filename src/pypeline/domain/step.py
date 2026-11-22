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
    """One unit of work in a pipeline, with validation around it.

    Callers always go through ``apply``, which validates the input, runs the step and
    validates the output. Subclasses implement ``run`` and both validators, declare
    their settings as dataclass fields, and must not override ``apply``.

    Attributes:
        scope: ``"single"`` runs the step once per item; ``"global"`` runs it once on
            the whole collection, for steps that need every item at the same time
            (e.g. normalising against the dataset mean).
    """

    scope: ClassVar[StepScope] = "single"
    requires: ClassVar[list[type[Step]]] = []
    mutable: ClassVar[bool] = True # delets input

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
    def apply(self, data: InputClass) -> OutputClass:
        """Validate, run and validate again; the only entry point for callers."""
        self.validate_input(data)
        result = self.run(data)
        self.validate_output(result)
        return result

    @abstractmethod
    def run(self, data: InputClass) -> OutputClass:
        """Transform the input into the step's output."""
        raise NotImplementedError()

    @abstractmethod
    def validate_input(self, data: InputClass) -> None:
        """Check that the input is acceptable before ``run`` is called."""

    @abstractmethod
    def validate_output(self, output: OutputClass) -> None:
        """Check that ``run`` produced an acceptable result."""


    # ──────────────────────────────────────────────────────
    # 1.2 Subsection: Helper Functions
    # ──────────────────────────────────────────────────────
    def io_types(self) -> tuple[type, type]:
        for base in get_original_bases(type(self)):
            if get_origin(base) is Step:
                inp, out = get_args(base)
                return get_origin(inp) or inp, get_origin(out) or out
        raise PipelineError(
            f"{type(self).__name__} does not declare Step[InputClass, OutputClass]"
        )
