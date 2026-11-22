# ================================================================
# 0. Section: IMPORTS
# ================================================================
from typing import Protocol

from pypeline.types import FilesMap

from .actors import ActorRecord
from .pipeline.settings import InputSettings



# ================================================================
# 1. Section: Functions
# ================================================================
class Loader(Protocol):
    def load(self, actor: ActorRecord) -> ActorRecord: ...
    def files(self, input_settings: InputSettings) -> FilesMap: ...
