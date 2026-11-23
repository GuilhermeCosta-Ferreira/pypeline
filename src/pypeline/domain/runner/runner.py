# ================================================================
# 0. Section: IMPORTS
# ================================================================
from typing import Any
from dataclasses import dataclass, replace

from pypeline.errors import RunnerError

from ..step import Step
from .saver import Saver
from .loader import Loader
from ..pipeline import Pipeline
from ..pipeline.wave import Wave
from .temp_storage import TempStorage
from .actors import ActorRecord, Actors


# ================================================================
# 1. Section: Functions
# ================================================================
@dataclass
class Runner:
    """Run a `Pipeline`, allowing for all optimizations and boilerplate code to be standardized across projects

    Attributes:
        loader: Lists input files and reads actors from disk.
        saver: Writes step outputs for each save point.
        temp_storage: Holds actors between phases; cleared when the run ends.
    """

    loader: Loader
    saver: Saver
    temp_storage: TempStorage

    def run(self, pipeline: Pipeline) -> None:
        """Run every step of `pipeline` on the input files, wave by wave.

        Each wave runs its single steps actor by actor, then its global steps on all
        actors at once. Outputs are written only where save points ask for them.

        Raises:
            RunnerError: If a global step finds no actor of its input class.
        """
        actors = Actors.from_files(self.loader.files(pipeline.input_settings))

        for wave in pipeline.waves:
            actors = self.run_singles(wave, actors, pipeline)
            actors = self.run_globals(wave, actors, pipeline)

        self.temp_storage.clear()

    # ================================================================
    # 2. Section: Singles and Globals
    # ================================================================
    def run_singles(self, wave: Wave, actors: Actors, pipeline: Pipeline) -> Actors:
        # 0. Makes sure we have singles to run
        if not wave.single_steps:
            return actors

        # 1. Runs for each actor all the steps
        next_actors = []
        for actor in actors:
            actors_out = self.run_item(wave, pipeline, actor)

            # 2. Saves all the temps
            for actor_out in actors_out:
                next_actors.append(self._store(actor_out))

        return Actors.from_records(next_actors)

    def run_globals(self, wave: Wave, actors: Actors, pipeline: Pipeline) -> Actors:
        if not wave.global_steps:
            return actors

        # 1. Gets all actors, but only records (initial state)
        live_actors = list(actors)

        for idx, step in wave.global_steps:
            # 2. Checks nothing broke
            targets = [a for a in live_actors if a.class_name == step.input_name]
            others = [a for a in live_actors if a.class_name != step.input_name]
            if not targets:
                raise RunnerError(
                    f"Global step {type(step).__name__} has no {step.input_name} to run on"
                )

            # 3. Builds a new record from loaded actors
            inputs = [self.loader.load(a) for a in targets]
            result_record = self._apply(pipeline, idx, step, [a.object for a in inputs])

            # 4. Updates the list
            live_actors = others if step.mutable else others + targets
            live_actors.append(self._store(result_record))

        return Actors.from_records(live_actors)

    # ──────────────────────────────────────────────────────
    # 1.1 Subsection: Singles main Foundation
    # ──────────────────────────────────────────────────────
    def run_item(
        self, wave: Wave, pipeline: Pipeline, actor: ActorRecord
    ) -> list[ActorRecord]:
        # 1. we start with only one actor, but we keep all of the actors
        live_actors = [self.loader.load(actor)]

        for idx, step in wave.single_steps:
            next_actors = []
            for live_actor in live_actors:
                if step.input_name != live_actor.class_name:
                    next_actors.append(live_actor)
                    continue

                result_record = self._apply(pipeline, idx, step, live_actor.object)

                if not step.mutable:
                    next_actors.append(live_actor)
                next_actors.append(result_record)
            live_actors = next_actors

        return live_actors

    # ──────────────────────────────────────────────────────
    # 1.2 Subsection: Helper Functions
    # ──────────────────────────────────────────────────────
    def _store(self, actor: ActorRecord) -> ActorRecord:
        if actor.path is not None:  # already on disk
            return actor
        return replace(actor, path=self.temp_storage.put(actor), object=None)

    def _apply(
        self, pipeline: Pipeline, idx: int, step: Step, data: Any
    ) -> ActorRecord:
        result_record = ActorRecord(
            path=None,
            step_idx=idx,
            class_name=step.output_name,
            object=step.apply(data),
        )

        for save_point in pipeline.get_save_points_after(idx):
            self.saver.save(result_record, save_point)

        return result_record
