"""Pydantic → JSON-schema conversion for tool function definitions.

The OpenAI ``tools`` field expects a flat draft-7-ish object schema. Pydantic v2
``model_json_schema()`` produces draft-2020 with ``$defs`` / ``$ref`` and
``title`` everywhere; some local model APIs choke on those. This module flattens
the output so it works across OpenAI, OpenRouter, Ollama, Groq, etc.
"""
from copy import deepcopy
from typing import Any, Dict, Type

from pydantic import BaseModel


def _resolve_refs(node: Any, defs: Dict[str, Any]) -> Any:
    """Recursively inline ``$ref``-pointed definitions into the schema."""
    if isinstance(node, dict):
        if "$ref" in node:
            ref = node["$ref"]
            if ref.startswith("#/$defs/"):
                key = ref[len("#/$defs/"):]
                replacement = deepcopy(defs.get(key, {}))
                # Merge any sibling keys (rare but legal).
                for k, v in node.items():
                    if k != "$ref":
                        replacement[k] = v
                return _resolve_refs(replacement, defs)
        return {k: _resolve_refs(v, defs) for k, v in node.items()}
    if isinstance(node, list):
        return [_resolve_refs(item, defs) for item in node]
    return node


def _strip_keys(node: Any, keys: tuple[str, ...]) -> Any:
    if isinstance(node, dict):
        return {k: _strip_keys(v, keys) for k, v in node.items() if k not in keys}
    if isinstance(node, list):
        return [_strip_keys(item, keys) for item in node]
    return node


def pydantic_to_openai_schema(model: Type[BaseModel]) -> Dict[str, Any]:
    """Convert a Pydantic model to a tool-call-ready JSON schema.

    The returned schema has ``$defs`` / ``$ref`` / ``title`` removed and is
    safe to drop into ``tools[i].function.parameters``.
    """
    raw = model.model_json_schema()
    defs = raw.pop("$defs", {})
    resolved = _resolve_refs(raw, defs)
    cleaned = _strip_keys(resolved, ("title",))
    if isinstance(cleaned, dict):
        # OpenAI structured-outputs strict mode prefers explicit
        # ``additionalProperties: false`` — for non-strict it's tolerated.
        cleaned.setdefault("type", "object")
        cleaned.setdefault("additionalProperties", False)
    return cleaned
