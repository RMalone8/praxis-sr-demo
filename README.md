# Praxis & llm-d-sc Demo

**Note**: images are currently local as quay remains read-only.

```bash
cp .env.example .env
# edit your variables
vi .env

podman compose -f podman-compose.yaml up -d
```

And then test the stack once it's all up:

```bash
curl -sS http://127.0.0.1:8080/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "router-test",
    "messages": [{"role": "user", "content": "What is the capital of France?"}],
    "max_tokens": 64
  }'
```

Praxis classifies the prompt with `llm-d-sc` and routes it to the CPU or GPU vLLM backend.

## Results

![Compose logs](imgs/compose-logs.png)
*Compose logs*

![Curl responses](imgs/curl-responses.png)
*Curl responses*
