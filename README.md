<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/images/banner_dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="docs/images/banner_light.svg">
    <img alt="Pypeline logo" src="docs/images/banner_light.svg" width="300px">
  </picture>
</div>

<h1 align='center'>
    Pypeline: Boilerplate-free pipelines in pure Python
</h1>

<div align="center">
    <img src="https://shields.io/badge/python-3.14-blue?logo=python&style=flat" alt="Python">
    <img src="https://shields.io/badge/latest-v0.1.0-blue?&style=flat" alt="Version">
    <img src="https://shields.io/badge/license-AGPL--3.0-blue?&style=flat" alt="License">
    <img src="https://shields.io/badge/Package_Manager-poetry-green?logo=poetry&style=flat" alt="Poetry">
    <img src="https://shields.io/badge/code_style-black-black?&style=flat" alt="Formatter">
    <img src="https://shields.io/badge/linting-pylint-yellow?&style=flat" alt="Linter">
</div>

---

# Introduction

Did you ever need to make a pipeline project for your master thesis, side-hustle or any other project? Most of the time pipelines are straight forward: data comes as input and steps will be applied in succession and you get an output. However, most of the time you code one, after 2 months of changes you need help from AI or god to just make a change your suppervisor asked for. You just wish you had made it easier to work with. If this is you now, or soon, this is the package for you. All the boilerplate code you need is imported from here and you just need to focus on implementing the steps and data actors you need. Optimizations? We got you!

# Setup

## Install

Pypeline is not on PyPI yet, so install it from the GitHub repository.

With pip:

```bash
pip install git+https://github.com/GuilhermeCosta-Ferreira/pypeline.git
```

With Poetry, inside your own project:

```bash
poetry add git+https://github.com/GuilhermeCosta-Ferreira/pypeline.git
```

Add `@<branch, tag or commit>` at the end of the URL to pin a version.

## Develop

To work on Pypeline itself, clone it and install it with its dev tools using [Poetry](https://python-poetry.org/docs/#installation):

```bash
git clone https://github.com/GuilhermeCosta-Ferreira/pypeline.git
cd pypeline
poetry install
```

`make dev` formats, lints, type checks and tests the code (see [CONTRIBUTING.md](CONTRIBUTING.md)). `make diagram` also needs [PlantUML](https://plantuml.com/download) on your `PATH`.

# Usage

You write three things:

1. **Actors**: the data types that flow through the pipeline. Any Python class works, including ones you do not own (`numpy.ndarray`, a polars `DataFrame`).
2. **Steps and actor I/O**: what each step does, and how each actor is read from and written to files.
3. **A pipeline file**: a YAML file saying where the input files are, which steps run in which order with which settings, and what gets saved.

Pypeline handles loading, validation, execution order, intermediate files and saving.

The example below uppercases text files one by one, then counts the words across all of them. Its layout:

```
my_project/
├── actors.py
├── actor_io.py
├── steps.py
├── pipeline.yaml
├── main.py
└── data/
    ├── batch_1/   a.txt, b.txt
    └── batch_2/   c.txt
```

## 1. Actors

```python
# actors.py
from dataclasses import dataclass


@dataclass
class Text:
    content: str


@dataclass
class TextStats:
    n_texts: int
    n_words: int
```

An actor is identified by its class name (`"Text"`), which is the name the pipeline file uses.

## 2. Actor I/O: reading and writing actors

Call `ActorIORegistry.add` once per actor class, with the class name as the key. `readers` and `writers` map a file extension to a function. Fill only the side you need: an actor that is only produced never needs a reader, and one that is never saved needs no writer.

```python
# actor_io.py
import json
from pathlib import Path

from pypeline import ActorIORegistry

from actors import Text, TextStats


def read_txt(path: Path) -> Text:
    return Text(path.read_text())


def write_txt(text: Text, path: Path) -> None:
    path.write_text(text.content)


def write_json(stats: TextStats, path: Path) -> None:
    path.write_text(json.dumps(vars(stats)))


ActorIORegistry.add("Text", readers={".txt": read_txt}, writers={".txt": write_txt})
ActorIORegistry.add("TextStats", writers={".json": write_json})
```

If you prefer a named class, subclass `ActorIO` and register it with the decorator instead. Annotate `readers` and `writers` with `ClassVar`, or ruff flags them (RUF012):

```python
from typing import ClassVar

from pypeline import ActorIO, ActorIORegistry
from pypeline.types import Reader, Writer


@ActorIORegistry.register("Text")
class TextIO(ActorIO):
    readers: ClassVar[dict[str, Reader]] = {".txt": read_txt}
    writers: ClassVar[dict[str, Writer]] = {".txt": write_txt}
```

## 3. Steps

A step is a dataclass that subclasses `Step[InputClass, OutputClass]`: exactly one input class in, one output out. Its dataclass fields are its settings, filled from the pipeline file. Implement `run`, `validate_input` and `validate_output` (raise to reject, return to accept), and register it in `StepRegistry` under the name the pipeline file uses. Never override `apply`: the runner calls it to validate, run and validate again.

Three class variables control how a step runs:

| Variable | Default | Meaning |
|---|---|---|
| `scope` | `"single"` | `"single"` runs once per actor of the input class. `"global"` runs once on the list of all of them; declare the input as `list[X]`. |
| `mutable` | `True` | `True` consumes the input: only the output continues. `False` keeps the input next to the output. |
| `requires` | `[]` | Step classes that must appear earlier in the pipeline. |

```python
# steps.py
from dataclasses import dataclass

from pypeline import Step, StepRegistry

from actors import Text, TextStats


@StepRegistry.register("shout")
@dataclass
class Shout(Step[Text, Text]):
    suffix: str = "!"

    def run(self, data: Text) -> Text:
        return Text(data.content.strip().upper() + self.suffix)

    def validate_input(self, data: Text) -> None:
        if not data.content.strip():
            raise ValueError("empty text")

    def validate_output(self, output: Text) -> None: ...


@StepRegistry.register("count_words")
@dataclass
class CountWords(Step[list[Text], TextStats]):
    scope = "global"
    mutable = False

    def run(self, data: list[Text]) -> TextStats:
        return TextStats(len(data), sum(len(t.content.split()) for t in data))

    def validate_input(self, data: list[Text]) -> None: ...

    def validate_output(self, output: TextStats) -> None: ...
```

To try a step on its own, outside a pipeline, call `apply`:

```python
>>> Shout(suffix="?").apply(Text("hi"))
Text(content='HI?')
```

## 4. The pipeline file

```yaml
# pipeline.yaml
global:
  pipeline_name: shout_and_count
  check_scope: true             # not used yet, but required

input:
  load_as: {".txt": "Text"}     # extension -> actor class, for every source
  sources:
    - path: data/batch_1        # always a folder; only its top level is read
    - path: data/batch_2
      # load_as: {".json": "Labels"}  # extra mappings for this folder only

steps:
  - name: shout                 # StepRegistry key
    suffix: "!!"                # step field
  - name: count_words

output:
  out_dir: results
  fmts: {".txt": "Text", ".json": "TextStats"}  # extension -> actor class
  save_all_intermediates: false # not used yet, but required
  save_points:
    - after: shout              # save this step's output
      subdir: shouted           # inside out_dir
    - after: count_words
```

- Each input file becomes one actor. Its extension decides the class; files with an unmapped extension are skipped.
- Formats maps always go from extension to class name, in `input` and in `output` alike. One class can have several extensions; on output, it is saved once per extension.
- A save point's own `fmts` override `output.fmts`. A step used more than once is picked with `occurrence` (counting from 1).
- Only save points are written to `out_dir`, as `{class name}_{n}{extension}`. Everything in between lives in temporary files that are deleted when the run ends.

## 5. Run it

```python
# main.py
from pathlib import Path
from pypeline import Pypeline

PROTOCOL_PATH: Path = Path("pipeline.yaml")

pypeline = Pypeline(PROTOCOL_PATH, packages=["actor_io", "steps"])
pypeline.run()
```

Steps and actor I/O are registered when their module is imported. `packages` lists those modules by name, and `Pypeline` imports them before it reads the pipeline file, so you never import them yourself. A name can also be a package: every module inside it is imported too, so new steps are picked up without touching any `__init__.py`. Point it at the package that holds your steps and actor I/O, not at your whole project, or scripts like this `main.py` get imported (and run) as well.

The pipeline file is checked as soon as the `Pypeline` is created: unknown sections or keys, unknown step names, a step whose input class is not available at that point, or a save point naming a missing step all raise `PipelineError` before anything runs. Relative paths in the file are resolved from the current working directory.

The result:

```
results/
├── TextStats_3.json     {"n_texts": 3, "n_words": 9}
└── shouted/
    ├── Text_0.txt       HELLO WORLD!!
    ├── Text_1.txt       THE QUICK BROWN FOX!!
    └── Text_2.txt       PIPELINES ARE FUN!!
```

## How steps are scheduled

Single steps run actor by actor; global steps need every actor at once. Pypeline cuts the steps into waves: a run of single steps, then the global steps after them. Within a wave each actor goes through all the single steps before the next one is loaded, then the global steps run. Step order is never changed, and single steps keep only one input actor in memory at a time.

## Temporary files

Intermediate actors are written to a temporary folder with pickle, so by default every actor must be picklable. To use another format, pass any object with an `extension` class variable and `write(obj, path)` / `read(path)` methods, where `read` returns what `write` was given:

```python
import gzip
import pickle
from pathlib import Path
from typing import Any, ClassVar
from dataclasses import dataclass


@dataclass(frozen=True)
class GzipPickleFormat:
    extension: ClassVar[str] = ".pkl.gz"

    def write(self, obj: Any, path: Path) -> None:
        with gzip.open(path, "wb") as f:
            pickle.dump(obj, f)

    def read(self, path: Path) -> Any:
        with gzip.open(path, "rb") as f:
            return pickle.load(f)


Pypeline(Path("pipeline.yaml"), temp_fmt=GzipPickleFormat()).run()
```

`temp_root` sets the folder the per-run temporary folder is created in (the system default otherwise). Pypeline only deletes the per-run folder, never `temp_root` itself.

# License

Pypeline is licensed under the [GNU Affero General Public License v3.0](LICENSE).
