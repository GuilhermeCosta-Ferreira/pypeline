# ================================================================
# 0. Section: IMPORTS
# ================================================================
from dataclasses import dataclass

from pypeline.errors import RunnerError

from .wave import Wave
from .saver import Saver
from .loader import Loader
from .pipeline import Pipeline
from .temp_storage import TempStorage
from .actors import ActorRecord, Actors


# ================================================================
# 1. Section: Functions
# ================================================================
@dataclass
class Runner:
    loader: Loader
    saver: Saver
    temp_storage: TempStorage

    def run(self, pipeline: Pipeline) -> None:
        actors = Actors.from_files(self.loader.files(pipeline.input_settings))

        for wave in pipeline.waves:
            # 1. Single steps, then every global step of the wave
            actors = self.run_singles(wave, actors, pipeline)

            # 2. Now runs the global steps
            actors = self.run_globals(wave, actors, pipeline)

        self.temp_storage.clear()

    def run_singles(self, wave: Wave, actors: Actors, pipeline: Pipeline) -> Actors:
        if wave.single_steps:
            next_actors = []
            for actor in actors:
                actors_out = self.run_item(wave, pipeline, actor)

                # 1. Saves all the temps
                [self.temp_storage.put(actor) for actor in actors_out]

                next_actors.extend(actors_out)

            return Actors.from_records(next_actors)

        return actors

    def run_globals(self, wave: Wave, actors: Actors, pipeline: Pipeline) -> Actors:
        if wave.global_steps:
            next_actors = []
            for idx, step in zip(wave.global_idx, wave.global_steps):
                live_actors = [
                    self.loader.load(actor) for actor in actors if actor.class_name == step.input_name
                ]

                if not live_actors:
                    raise RunnerError(f"Global step {type(step).__name__} has no {step.input_name} to run on")

                result = step.apply([a.object for a in live_actors])
                result_record = ActorRecord(
                    path = None,
                    step_idx = idx,
                    class_name = step.output_name,
                    object = result
                )

                for save_point in pipeline.get_save_points_after(idx):
                    self.saver.save(result_record, save_point)

                if not step.mutable:
                    next_actors.extend(live_actors)
                next_actors.append(result_record)

            return Actors.from_records(next_actors)
        return actors


    # ──────────────────────────────────────────────────────
    # 1.1 Subsection: Helper Functions
    # ──────────────────────────────────────────────────────
    def run_item(self, wave: Wave, pipeline: Pipeline, actor: ActorRecord) -> list[ActorRecord]:
        # 1. we start with only one actor, but we keep all of the actors
        # that will be used for future steps in this phase
        live_actors = [self.loader.load(actor)]

        for idx, step in zip(wave.single_idx, wave.single_steps):
            next_actors = []
            for live_actor in live_actors:
                if step.input_name != live_actor.class_name:
                    next_actors.append(live_actor)
                    continue

                result = step.apply(live_actor.object)
                result_record = ActorRecord(
                    path = None,
                    step_idx = idx,
                    class_name = step.output_name,
                    object = result
                )

                for save_point in pipeline.get_save_points_after(idx):
                    self.saver.save(result_record, save_point)

                if not step.mutable:
                    next_actors.append(live_actor)
                next_actors.append(result_record)
            live_actors = next_actors

        return live_actors
