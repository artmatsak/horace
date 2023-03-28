import json
import requests
from urllib.parse import urlunsplit
from typing import List


class Router():
    def __init__(self, plugins: List[str]):
        self.registry = {}
        for netloc in plugins:
            manifest_url = urlunsplit(
                ('http', netloc, '/.well-known/ai-plugin.json', '', ''))
            response = requests.get(manifest_url)
            response.raise_for_status()
            manifest = json.loads(response.text)

            response = requests.get(manifest["api"]["url"])
            response.raise_for_status()
            openapi_spec = response.text

            self.registry[manifest["name_for_model"]] = {
                "manifest": manifest,
                "openapi_spec": openapi_spec
            }

    def eval(self, expression: str) -> str:
        if not expression.startswith("requests."):
            raise ValueError(
                f"Expecting a requests function call, for example requests.get()")

        r = eval(expression)
        return f"[HTTP {r.status_code}] Response body: {r.text}"
