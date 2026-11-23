# ================================================================
# 0. Section: IMPORTS
# ================================================================
from ..domain.registries import Registry
from .actor_loader import ActorLoader



# ================================================================
# 1. Section: Functions
# ================================================================
class ActorLoaderRegistry(Registry[ActorLoader]): ...
