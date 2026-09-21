# OpenShift manifest guide

This directory deploys the same logical stack as the root compose file using
Kustomize, OpenShift Routes, KServe `InferenceService` resources, and a
ModelCar init container.

## Layout and ownership

- `base/`: reusable Praxis and classifier Deployments/Services/Route.
- `base/praxis.yaml`: Praxis config embedded into a generated ConfigMap by
  `base/kustomization.yaml`.
- `overlays/rhoai/`: deployable environment overlay, including Namespace,
  route hostname, and CPU/GPU KServe backends.
- `README.md`: prerequisites, deploy command, and smoke test.

Make reusable changes in `base/`; keep cluster-specific values in an overlay.
The current overlay targets namespace `praxis-sr-demo`. Although the base names
`praxis-demo`, the overlay namespace wins in the rendered output.

## Runtime relationships to preserve

- Praxis loads `/etc/praxis/config.yaml` from the generated `praxis-config`
  ConfigMap and exposes only HTTP `8080` through its Service and Route.
- Praxis admin port `9901` stays Pod-local and supplies readiness/liveness
  endpoints.
- `llm-d-sc` receives its model through the ModelCar init container and serves
  gRPC on `50051`.
- RawDeployment KServe creates `vllm-cpu-predictor` and
  `vllm-gpu-predictor`; `base/praxis.yaml` routes to those names on port `80`.
- Both `InferenceService` resources depend on cluster-provided runtime names.
  Do not assume those names are portable to another cluster.

## Validation

Render before applying:

```bash
kustomize build openshift/overlays/rhoai >/tmp/praxis-rendered.yaml
oc apply --dry-run=client -f /tmp/praxis-rendered.yaml
```

For an actual deployment, follow `openshift/README.md`. Do not run `oc apply`
or mutate a cluster merely to validate a manifest unless the user explicitly
asked for deployment.

When changing image names, route hostnames, namespaces, runtime names, model
URIs, or resource requests, treat them as environment-specific choices and
update the README when operator action is required.

