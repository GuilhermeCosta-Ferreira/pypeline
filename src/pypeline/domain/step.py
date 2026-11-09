# ================================================================
# 0. Section: IMPORTS
# ================================================================
from typing import final
from dataclasses import dataclass
from abc import ABC, abstractmethod


# ================================================================
# 1. Section: Functions
# ================================================================
@dataclass  # kept dataclass for params
class Step[InputClass, OutputClass](ABC):
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
    def validate_input(self, input: InputClass) -> None:
        """Check that the input is acceptable before ``run`` is called."""

    @abstractmethod
    def validate_output(self, output: OutputClass) -> None:
        """Check that ``run`` produced an acceptable result."""
