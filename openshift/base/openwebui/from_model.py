"""Open WebUI Filter: show the serving model above each assistant reply.

This filter is intended for an OpenAI Chat Completions connection. It reads the
`model` field from the provider's streamed response chunks and prefixes the
first visible assistant text chunk with `From <model>`.

It deliberately does not fall back to the request's `model` field: with the
Praxis router, that value can be a logical alias rather than the model that
actually served the response.
"""

from typing import Any, Optional

from pydantic import BaseModel, Field


class Filter:
    """Prefix each streamed assistant response with the provider model name."""

    class Valves(BaseModel):
        prefix_template: str = Field(
            default="From {model}\n\n",
            description=(
                "Prefix applied before the first assistant text chunk. "
                "Use {model} for the provider model name."
            ),
        )

    def __init__(self):
        self.valves = self.Valves()

    async def inlet(
        self,
        body: dict,
        __metadata__: Optional[dict] = None,
    ) -> dict:
        """Reset per-turn state without changing the request sent to Praxis."""

        if __metadata__ is not None:
            __metadata__.pop("_praxis_from_model", None)
            __metadata__.pop("_praxis_from_model_prefixed", None)
        return body

    @staticmethod
    def _response_model(event: dict) -> Optional[str]:
        """Read a model name from common Chat Completions event shapes."""

        candidates: list[Any] = [event]
        seen: set[int] = set()

        while candidates:
            candidate = candidates.pop(0)
            if not isinstance(candidate, dict) or id(candidate) in seen:
                continue
            seen.add(id(candidate))

            model = candidate.get("model")
            if isinstance(model, str) and model.strip():
                return model.strip()

            for key in ("data", "response"):
                nested = candidate.get(key)
                if isinstance(nested, dict):
                    candidates.append(nested)

        return None

    def _prefix_first_text(self, event: dict, prefix: str) -> bool:
        """Prefix the first non-empty Chat Completions text delta."""

        for choice in event.get("choices") or []:
            if not isinstance(choice, dict):
                continue

            delta = choice.get("delta")
            if isinstance(delta, dict):
                content = delta.get("content")
                if isinstance(content, str) and content:
                    delta["content"] = prefix + content
                    return True

            # Some OpenAI-compatible providers use `text` instead of `delta`.
            text = choice.get("text")
            if isinstance(text, str) and text:
                choice["text"] = prefix + text
                return True

        return False

    async def stream(
        self,
        event: dict,
        __metadata__: Optional[dict] = None,
    ) -> dict:
        """Add the attribution to the first visible streamed text chunk."""

        if __metadata__ is None or not isinstance(event, dict):
            return event

        model = self._response_model(event)
        if model:
            # A later provider call in a tool loop may supply the final model.
            # Keep the newest observed value until text is actually emitted.
            __metadata__["_praxis_from_model"] = model

        if __metadata__.get("_praxis_from_model_prefixed"):
            return event

        model = __metadata__.get("_praxis_from_model")
        if not isinstance(model, str) or not model:
            return event

        prefix = self.valves.prefix_template.format(model=model)
        if self._prefix_first_text(event, prefix):
            __metadata__["_praxis_from_model_prefixed"] = True

        return event
