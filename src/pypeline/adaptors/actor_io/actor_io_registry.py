# ================================================================
# 0. Section: IMPORTS
# ================================================================
from ...domain import Registry
from .actor_io import ActorIO


# ================================================================
# 1. Section: Functions
# ================================================================
class ActorIORegistry(Registry[ActorIO]):
    """Registry of `ActorIO` classes, by actor class name.

    Examples:
        >>> @ActorIORegistry.register("Image")
        ... class ImageIO(ActorIO):
        ...     readers = {".png": read_png}
        ...     writers = {".png": write_png}

        The key is the class name the formats maps point to:

            input:
              load_as: {".png": "Image"}
            output:
              fmts: {".png": "Image"}
    """
