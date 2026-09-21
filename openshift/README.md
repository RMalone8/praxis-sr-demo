# OpenShift

Deploys Praxis, `llm-d-sc`, and CPU/GPU KServe vLLM backends with Kustomize.
Praxis classifies each request with `llm-d-sc` and routes it to the proper KServe
predictor Service.

## Prerequisites

- A project with KServe, CPU and CUDA ServingRuntimes. These manfiests refer to them as `vllm-cpu-x86-runtime` and
  `vllm-cuda-runtime` respectively.
- NVIDIA GPU capacity for the GPU backend.

## Deploy

```console
kustomize build openshift/overlays/rhoai
oc apply -k openshift/overlays/rhoai
```

The overlay includes Open WebUI, a small persistent volume claim for
`/app/backend/data`, and a bootstrap Job. Open WebUI auth is disabled for this
demo. The Job uses Open WebUI's built-in no-auth bootstrap account to create or
update `praxis_from_model` and enable it globally.

Get the UI route with:

```console
WEBUI_HOST=$(oc -n praxis-sr-demo get route openwebui -o jsonpath='{.spec.host}')
echo "https://${WEBUI_HOST}"
```

The Open WebUI image is pinned to `v0.11.1` in the base manifests. Override
that image in an environment-specific overlay when using another tested
version.

If the Filter source changes, update the ConfigMap and rerun the one-shot
bootstrap Job:

```console
oc -n praxis-sr-demo delete job openwebui-bootstrap --ignore-not-found
oc apply -k openshift/overlays/rhoai
```

The Open WebUI database remains in the `openwebui-data` PVC, so chats,
settings, and the installed Filter survive pod restarts.

KServe creates `vllm-cpu-predictor` and `vllm-gpu-predictor` Services in raw
deployment mode; the Praxis config uses those internal addresses.

## Test the CPU path

```console
HOST=$(oc -n praxis-sr-demo get route praxis -o jsonpath='{.spec.host}')

curl -sS "https://${HOST}/v1/chat/completions" \
  -H 'Content-Type: application/json' \
  -d '{
    "messages": [{"role": "user", "content": "What is the capital of France?"}],
    "max_tokens": 64
  }'
```
