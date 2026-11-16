# ================================================================
# 0. Section: IMPORTS
# ================================================================
from typing import Any
from pathlib import Path
from dataclasses import dataclass

from pypeline.types import FilesMap

from .wave import Wave
from .saver import Saver
from .loader import Loader
from .pipeline import Pipeline
from .temp_storage import TempStorage


# ================================================================
# 1. Section: Functions
# ================================================================
@dataclass
class Runner:
    loader: Loader
    saver: Saver
    temp_storage: TempStorage

    def run(self, pipeline: Pipeline) -> Any:
        files_map = self.loader.files(pipeline.input_settings)
        waves = pipeline.waves

        for wave, idx in enumerate(waves):
            ...

    def single_step_runner(self, wave: Wave, pipeline: Pipeline, files_map: FilesMap):
        is_first = wave.wave_number == 0

        for actor_type, path in files_map:
            data = self.fetch(wave, path, actor_type, is_first)

            for step in wave.single_steps:
                data = step.run(data)

            self.temp_storage.put(wave.wave_number, path, data)

        self.temp_storage.clear(wave.wave_number - 1)

    def global_step_runner(self, wave: Wave, pipeline: Pipeline, files_map: FilesMap):
        if wave.global_steps is None:
            return

        is_first = wave.wave_number == 0 and not wave.single_steps

        data = [self.fetch(wave, path, actor_type, is_first) for actor_type, path in files_map]

        for step in wave.global_steps:
            data = step.run(data)

        self.temp_storage.put(wave.wave_number, path, data)
        self.temp_storage.clear(wave.wave_number - 1)

    def fetch(self, wave: Wave, path: Path, actor_type: str, is_first: bool) -> Any:
        if is_first:
            return self.loader.load(path, actor_type)

        return self.temp_storage.get(wave.wave_number, path, actor_type)
