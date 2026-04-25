"""AI tool implementations.

Importing any submodule registers its tools via the ``@tool`` decorator into
the global registry in :mod:`app.services.ai.tools.registry`.
"""
from . import registry  # noqa: F401
