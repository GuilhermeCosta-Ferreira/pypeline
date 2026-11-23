# ================================================================
# 0. Section: IMPORTS
# ================================================================
from dataclasses import replace, field, dataclass

from pypeline.types import FilesMap

from ..actor_io import ActorIORegistry
from ...domain.pipeline import InputSettings
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
        """Only the top level of each source is listed; files whose extension is not
        mapped are skipped."""
        files: FilesMap = []
        for source in input_settings.sources:
            # 1. Source entries override the global ones
            load_as = {**input_settings.load_as, **source.load_as}

            # 2. Keeps only files with a mapped extension
            for path in sorted(source.path.iterdir()):
                if path.is_file() and path.suffix in load_as:
                    files.append((load_as[path.suffix], path))
        return files
