# ================================================================
# 0. Section: IMPORTS
# ================================================================
from dataclasses import dataclass

from .source import Source, FormatsMap


# ================================================================
# 1. Section: Functions
# ================================================================
@dataclass(frozen=True)
class InputSettings:
    """The `input` section: where the input files are and which actor class each
    becomes.

    Each file becomes one actor, and its extension decides the actor class.

    Attributes:
        load_as: Extension to actor class name, for every source.
        sources: Folders to read input files from.
    """

    load_as: FormatsMap
    sources: list[Source]
