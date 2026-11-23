# ================================================================
# 0. Section: IMPORTS
# ================================================================
import shutil

from pathlib import Path
from dataclasses import dataclass, field

from .pickle_format import PickleFormat
from .temp_file_format import TempFileFormat
from ..domain.runner import ActorRecord, TempStorage



# ================================================================
# 1. Section: Functions
# ================================================================
@dataclass
class FileTempStorage(TempStorage):
    root: Path
    fmt: TempFileFormat = field(default_factory=PickleFormat)
    _count: int = field(default=0, init=False)

    def put(self, actor: ActorRecord) -> Path:
        self.root.mkdir(parents=True, exist_ok=True)
        path = self.root / f"{actor.step_idx}_{actor.class_name}_{self._count}{self.fmt.extension}"
        self._count += 1
        self.fmt.write(actor.object, path)
        return path

    def clear(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)
