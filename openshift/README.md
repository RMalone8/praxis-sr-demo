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

The overlay includes Open WebUI and a small persistent volume claim for
`/app/backend/data`. Open WebUI auth is disabled for this demo. It discovers
the single logical model `Semantic-Qwen` from Praxis's `/v1/models` response
and sends that value in completion requests. Praxis routes the request based on
prompt complexity. Completion responses may report a physical serving-model
name; Open WebUI does not display or use it for routing.

Get the UI route with:

```console
WEBUI_HOST=$(oc -n praxis-sr-demo get route openwebui -o jsonpath='{.spec.host}')
echo "https://${WEBUI_HOST}"
```

The Open WebUI image is pinned to `v0.11.1` in the base manifests. Override
that image in an environment-specific overlay when using another tested
version.

The Open WebUI database remains in the `openwebui-data` PVC, so chats and
settings survive pod restarts.

KServe creates `vllm-cpu-predictor` and `vllm-gpu-predictor` headless Services in
raw deployment mode; the Praxis config targets their vLLM listener on port
`8080`.

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
