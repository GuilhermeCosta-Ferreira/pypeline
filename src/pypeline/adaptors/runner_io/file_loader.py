# ================================================================
# 0. Section: IMPORTS
# ================================================================
from pathlib import Path
from dataclasses import replace, field, dataclass

from pypeline.types import FilesMap

from ..actor_io import ActorIORegistry
from ...domain.pipeline import InputSettings, Source
from ..temporary_formats import PickleFormat, TempFileFormat
from ...domain.runner import Loader, ActorRecord, INPUT_STEP


# ================================================================
# 1. Section: Functions
# ================================================================
@dataclass
class FileLoader(Loader):
    """`Loader` that reads inputs through `ActorIORegistry` and temp files through
    `temp_fmt`.

    Attributes:
        temp_fmt: Must be the format the `FileTempStorage` writes with.
    """

    temp_fmt: TempFileFormat = field(default_factory=PickleFormat)

    def load(self, actor: ActorRecord) -> ActorRecord:
        if actor.path is None:
            raise ValueError(f"{actor.class_name} has no path to load from")

        if actor.step_idx == INPUT_STEP:
            io = ActorIORegistry.get(actor.class_name)
            obj = io.load(actor.path)
            return replace(actor, object=obj)

        obj = self.temp_fmt.read(actor.path)
        return replace(actor, object=obj)

    def files(self, input_settings: InputSettings) -> FilesMap:
        """Each source is listed down to its `depth`; files whose extension is not
        mapped are skipped."""
        files: FilesMap = []
        for source in input_settings.sources:
            # 1. Source entries override the global ones
            load_as = {**input_settings.load_as, **source.load_as}

            # 2. Keeps only files with a mapped extension
            for path in _list_files(source):
                if path.suffix in load_as:
                    files.append((load_as[path.suffix], path))
        return files


# ──────────────────────────────────────────────────────
# 1.1 Subsection: Private Helper Functions
# ──────────────────────────────────────────────────────
def _list_files(source: Source) -> list[Path]:
    files: list[Path] = []
    for root, dirs, names in source.path.walk():
        # 1. Stops descending once the depth limit is reached
        level = len(root.relative_to(source.path).parts) + 1
        if source.depth is not None and level >= source.depth:
            dirs.clear()

        # 2. Drops hidden entries; editing `dirs` in place prunes the walk
        if not source.include_hidden_folders:
            dirs[:] = [d for d in dirs if not d.startswith(".")]
        if not source.include_hidden_files:
            names = [n for n in names if not n.startswith(".")]

        files.extend(root / name for name in names)
    return sorted(files)
