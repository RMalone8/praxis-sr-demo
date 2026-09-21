# Open WebUI model attribution filter

The canonical Filter source is
[`openshift/base/openwebui/from_model.py`](../../openshift/base/openwebui/from_model.py).
The OpenShift bootstrap Job loads that same file into Open WebUI. For a
standalone Open WebUI installation, paste the contents of that file into a
Filter.

`from_model.py` adds a line such as this to the beginning of each streamed
assistant response:

```text
From qwen2.5-7b
```

The filter reads the `model` field from the upstream Chat Completions response.
It does not use the request's `model` field, because Praxis may receive a
logical router alias while vLLM returns the model that actually served the
request.

## Install

1. Open **Admin Panel → Functions** in Open WebUI.
2. Create a new Function and select **Filter**.
3. Paste the contents of `from_model.py`.
4. Activate it globally, or attach it to the Praxis router model.
5. Keep the OpenAI-compatible connection configured for **Chat Completions**.

The filter leaves a response unchanged if Praxis or the upstream provider does
not return a `model` value. The `prefix_template` valve can be changed from
`From {model}` to another format if desired.

## OpenShift deployment

The `openwebui-bootstrap` Job imports the canonical source into the persistent
Open WebUI database and enables it globally, so the Admin Panel steps above are
only needed for standalone Open WebUI installs.
