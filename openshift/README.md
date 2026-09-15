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
