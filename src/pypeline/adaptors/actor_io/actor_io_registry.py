# ================================================================
# 0. Section: IMPORTS
# ================================================================
from collections.abc import Mapping

from pypeline.types import Reader, Writer

from .actor_io import ActorIO
from ...domain import Registry


# ================================================================
# 1. Section: Functions
# ================================================================
class ActorIORegistry(Registry[ActorIO]):
    """Registry of `ActorIO` classes, by actor class name.

    Examples:
        >>> ActorIORegistry.add("Image", readers={".png": read_png})

        A hand-written subclass works too; annotate both maps with `ClassVar` so ruff
        does not flag them (RUF012):

        >>> @ActorIORegistry.register("Image")
        ... class ImageIO(ActorIO):
        ...     readers: ClassVar[dict[str, Reader]] = {".png": read_png}
        ...     writers: ClassVar[dict[str, Writer]] = {".png": write_png}

        The key is the class name the formats maps point to:

            input:
              load_as: {".png": "Image"}
            output:
              fmts: {".png": "Image"}
    """

    @classmethod
    def add(
        cls,
        key: str,
        readers: Mapping[str, Reader] | None = None,
        writers: Mapping[str, Writer] | None = None,
    ) -> None:
        """Register how the actor class `key` is read and written, without writing an
        `ActorIO` subclass.

        Args:
            key: The actor class name the pipeline file uses.
            readers: Extension to a function that reads a file into an actor. Leave it
                out for an actor that is never loaded from an input file.
            writers: Extension to a function that writes an actor to a file. Leave it
                out for an actor that is never saved.

        Raises:
            ValueError: If `key` is already registered.

        Examples:
            >>> ActorIORegistry.add(
            ...     "Image",
            ...     readers={".png": read_png},
            ...     writers={".png": write_png, ".jpg": write_jpg},
            ... )
        """
        # 1. Builds the subclass the user would otherwise write by hand
        io_cls = type(
            f"{key}IO",
            (ActorIO,),
            {"readers": dict(readers or {}), "writers": dict(writers or {})},
        )

        # 2. Registers it like any other `ActorIO` subclass
        cls.register(key)(io_cls)
