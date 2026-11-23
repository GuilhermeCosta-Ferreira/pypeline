# ================================================================
# 0. Section: IMPORTS
# ================================================================
from dataclasses import replace, field, dataclass

from pypeline.types import FilesMap

from ..formats import PickleFormat, TempFileFormat
from ...domain.pipeline import InputSettings
from ..actor_io import ActorIORegistry
from ...domain.runner import Loader, ActorRecord, INPUT_STEP


# ================================================================
# 1. Section: Functions
# ================================================================
@dataclass
class FileLoader(Loader):
    temp_fmt: TempFileFormat = field(default_factory=PickleFormat)

    def load(self, actor: ActorRecord) -> ActorRecord:
        if actor.path is None:
            raise ValueError(f"{actor.class_name} has no path to load from")

        if actor.step_idx == INPUT_STEP:
            io = ActorIORegistry.get(actor.class_name)
            object = io.load(actor.path)
            return replace(actor, object=object)

        object = self.temp_fmt.read(actor.path)
        return replace(actor, object=object)

    def files(self, input_settings: InputSettings) -> FilesMap:
        files: FilesMap = []
        for source in input_settings.sources:
            # 1. Source entries override the global ones
            load_as = {**input_settings.load_as, **source.load_as}

            # 2. Keeps only files with a mapped extension
            for path in sorted(source.path.iterdir()):
                if path.is_file() and path.suffix in load_as:
                    files.append((load_as[path.suffix], path))
        return files
