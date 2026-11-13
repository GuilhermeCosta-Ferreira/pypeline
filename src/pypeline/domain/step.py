# ================================================================
# 0. Section: IMPORTS
# ================================================================
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Literal, final, ClassVar

StepScope = Literal["single", "global"]


# ================================================================
# 1. Section: Functions
# ================================================================
@dataclass  # kept dataclass for params
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

    @final
    def apply(self, data: InputClass) -> OutputClass | list[OutputClass]:
        """Validate, run and validate again; the only entry point for callers."""
        self.validate_input(data)
        result = self.run(data)
        self.validate_output(result)
        return result

    @abstractmethod
    def run(self, data: InputClass) -> OutputClass | list[OutputClass]:
        """Transform the input into the step's output."""
        raise NotImplementedError()

    @abstractmethod
    def validate_input(self, data: InputClass) -> None:
        """Check that the input is acceptable before ``run`` is called."""

    @abstractmethod
    def validate_output(self, output: OutputClass | list[OutputClass]) -> None:
        """Check that ``run`` produced an acceptable result."""
