# Open WebUI integration guide

This directory contains Open WebUI integration documentation. The canonical
Filter source is packaged by the OpenShift deployment at
`../openshift/base/openwebui/from_model.py` and is pasted into Open WebUI as a
global or model-scoped Filter for standalone installs.

## Filter contract

- The filter targets streamed OpenAI Chat Completions responses.
- It reads `model` from the upstream response, never from the request, because
  the request may contain a router alias rather than the vLLM model used.
- It prefixes only the first visible assistant text chunk and stores per-turn
  state in `__metadata__`.
- It accepts top-level response events and common `data`/`response` wrappers,
  plus both `choices[].delta.content` and `choices[].text` text shapes.
- If no response model is present, the event must pass through unchanged.

Keep installation/user-facing behavior synchronized with
`filters/README.md`. Avoid OpenWebUI internals that are not part of the Filter
hook inputs already used here.

## Validation

There is no committed test harness. At minimum run:

```bash
python3 -m py_compile openshift/base/openwebui/from_model.py
```

Do not commit `__pycache__/` or `.pyc` files. For behavior changes, exercise
synthetic streamed events for wrapped/unwrapped model metadata, empty chunks,
`delta.content`, and `choices[].text`; state should reset in `inlet` for every
turn.
