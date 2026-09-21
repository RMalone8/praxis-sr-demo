"""Install and enable the Praxis attribution Filter in Open WebUI."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request


def request(
    base_url: str,
    path: str,
    method: str = "GET",
    payload: dict | None = None,
    token: str | None = None,
) -> tuple[int, dict | str]:
    body = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(
        f"{base_url.rstrip('/')}{path}",
        data=body,
        headers=headers,
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            raw = response.read().decode("utf-8")
            return response.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as error:
        raw = error.read().decode("utf-8")
        try:
            return error.code, json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            return error.code, raw
    except urllib.error.URLError as error:
        return 0, str(error)


def describe(value: dict | str) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, sort_keys=True)


def wait_for_openwebui(base_url: str) -> None:
    deadline = time.monotonic() + 900
    while time.monotonic() < deadline:
        status, _ = request(base_url, "/health")
        if status == 200:
            return
        time.sleep(3)
    raise RuntimeError("Open WebUI did not become healthy before the deadline")


def sign_in(base_url: str, email: str, password: str) -> str:
    status, response = request(
        base_url,
        "/api/v1/auths/signin",
        method="POST",
        payload={"email": email, "password": password},
    )
    if status != 200 or not isinstance(response, dict) or not response.get("token"):
        raise RuntimeError(f"Open WebUI sign-in failed ({status}): {describe(response)}")
    return response["token"]


def install_filter(base_url: str, token: str) -> None:
    filter_id = os.environ.get("FILTER_ID", "praxis_from_model")
    filter_name = os.environ.get("FILTER_NAME", "Praxis model attribution")
    filter_description = os.environ.get(
        "FILTER_DESCRIPTION",
        "Shows the vLLM model returned by Praxis above each response.",
    )
    source_path = os.environ.get("FILTER_SOURCE", "/bootstrap/from_model.py")
    source = open(source_path, encoding="utf-8").read()
    payload = {
        "id": filter_id,
        "name": filter_name,
        "content": source,
        "meta": {"description": filter_description},
    }

    status, response = request(
        base_url,
        f"/api/v1/functions/id/{filter_id}",
        token=token,
    )
    if status == 200:
        action = "update"
        status, response = request(
            base_url,
            f"/api/v1/functions/id/{filter_id}/update",
            method="POST",
            payload=payload,
            token=token,
        )
    elif status in (401, 404):
        action = "create"
        status, response = request(
            base_url,
            "/api/v1/functions/create",
            method="POST",
            payload=payload,
            token=token,
        )
    else:
        raise RuntimeError(f"Could not inspect Filter ({status}): {describe(response)}")

    if status != 200:
        raise RuntimeError(f"Could not {action} Filter ({status}): {describe(response)}")

    status, response = request(
        base_url,
        f"/api/v1/functions/id/{filter_id}",
        token=token,
    )
    if status != 200 or not isinstance(response, dict):
        raise RuntimeError(f"Could not read Filter after {action} ({status}): {describe(response)}")

    if not response.get("is_active"):
        status, response = request(
            base_url,
            f"/api/v1/functions/id/{filter_id}/toggle",
            method="POST",
            token=token,
        )
        if status != 200:
            raise RuntimeError(f"Could not activate Filter ({status}): {describe(response)}")

    if not response.get("is_global"):
        status, response = request(
            base_url,
            f"/api/v1/functions/id/{filter_id}/toggle/global",
            method="POST",
            token=token,
        )
        if status != 200:
            raise RuntimeError(f"Could not globalize Filter ({status}): {describe(response)}")


def main() -> None:
    base_url = os.environ["OPENWEBUI_URL"]
    # WEBUI_AUTH=false uses this built-in account for API requests.
    email = "admin@localhost"
    password = "admin"

    wait_for_openwebui(base_url)

    deadline = time.monotonic() + 900
    while time.monotonic() < deadline:
        try:
            token = sign_in(base_url, email, password)
            install_filter(base_url, token)
            filter_id = os.environ.get("FILTER_ID", "praxis_from_model")
            print(f"Open WebUI Filter {filter_id} is installed and global")
            return
        except RuntimeError as error:
            print(f"Bootstrap retry: {error}")
            time.sleep(5)

    raise RuntimeError("Open WebUI Filter bootstrap did not complete before the deadline")


if __name__ == "__main__":
    main()
