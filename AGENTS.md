# Agent guide

## What this repository is

This is a deployment/demo repository, not the source tree for Praxis, vLLM, or
`llm-d-sc`. It wires those externally built images into one request path:

`client -> Praxis :8080 -> llm-d-sc :50051 -> CPU or GPU vLLM`

The semantic classifier labels each prompt. `SIMPLE` and `MEDIUM` use the CPU
model; `COMPLEX` and `REASONING` use the GPU model. If classification is
unavailable or overloaded, Praxis falls back to CPU.

## Repository map

- `README.md`: shortest local-compose quick start and smoke request.
- `podman-compose.yaml`: local Podman stack and model/image settings.
- `praxis.yaml`: local Praxis routing configuration.
- `.env.example`: local secrets/path template; `.env` is ignored.
- `openshift/`: Kustomize base plus the RHOAI overlay. Read its nested
  `AGENTS.md` before changing manifests.
- `openwebui/filters/`: response-attribution filter documentation. The
  canonical source is packaged under `openshift/base/openwebui/`; read its
  nested `AGENTS.md` before changing the integration.
- `architecture.html`: standalone architecture visualization.
- `imgs/`: README screenshots; treat as documentation assets.

There is no application build, package manager, or automated test suite in
this repository. Most changes should be validated as configuration or rendered
manifests.

## Common commands

Local stack (requires the model directory, image registry access, and a GPU):

```bash
cp .env.example .env
# Set LLM_D_SC_MODEL_DIR and, when needed, HF_TOKEN.
podman compose -f podman-compose.yaml config
podman compose -f podman-compose.yaml up -d
podman compose -f podman-compose.yaml logs -f praxis llm-d-sc
```

Fast validation that does not deploy anything:

```bash
podman compose -f podman-compose.yaml config
kustomize build openshift/overlays/rhoai >/tmp/praxis-rendered.yaml
python3 -m py_compile openshift/base/openwebui/from_model.py
git diff --check
```

The compose validation needs a value for the required path, for example:

```bash
LLM_D_SC_MODEL_DIR=/tmp/model podman compose -f podman-compose.yaml config
```

## Change rules and invariants

- Keep local and OpenShift routing policy aligned when changing classifier
  labels, default clusters, timeouts, or `emit_headers`. The files are
  `praxis.yaml` and `openshift/base/praxis.yaml`.
- Do not make the two Praxis configs byte-for-byte identical: compose uses
  service endpoints on port `8000`; OpenShift uses KServe predictor Services on
  port `80` and adds a loopback-only admin listener for probes.
- Preserve the classifier contract: gRPC on `50051`, classifier name
  `complexity`, and a model mounted at `/models`.
- Preserve the public API contract: OpenAI-compatible Chat Completions at
  `/v1/chat/completions` through Praxis port `8080`.
- Never commit `.env`, tokens, downloaded models, registry credentials, or
  generated Python caches.
- Images tagged `latest`, model names, runtime names, resource sizes, and the
  OpenShift route hostname are demo/environment choices. Call out intentional
  changes to them in documentation or the handoff.
- Keep edits narrow. Do not reformat all YAML around a functional change.

## Before handing off

Run the relevant fast validation above, then summarize what was and was not
tested. Full startup/deployment is environment-dependent and should not be
claimed unless the containers or OpenShift resources were actually exercised.
