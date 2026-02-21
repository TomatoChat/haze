"""Public API for haze.routes — re-exports every route for convenient import."""

from haze.routes.align_agents import align_agents
from haze.routes.align_docs import align_docs

__all__ = [
    "align_agents",
    "align_docs",
]
