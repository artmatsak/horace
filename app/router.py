import os
import yaml
import json
import aiohttp
import requests
from urllib.parse import urlunsplit
import openapi_core
from openapi_core.contrib.requests import RequestsOpenAPIRequest
from openapi_core.validation.request.exceptions import RequestValidationError
import logging
from typing import List, Dict, Optional


class Router():
    PLUGIN_AUTH_FILENAME = '.plugin_auth.json'

    AUTH_TYPE_NONE = "none"
    AUTH_TYPE_SERVICE_HTTP = "service_http"
    AUTH_TYPE_USER_HTTP = "user_http"

    MIME_TYPES_JSON = ["application/json"]
    MIME_TYPES_YAML = ["application/yaml",
                       "application/x-yaml", "text/yaml", "text/x-yaml"]

    def __init__(self, plugins: Optional[List[str]] = None):
        if os.path.isfile(self.PLUGIN_AUTH_FILENAME):
            with open(self.PLUGIN_AUTH_FILENAME, 'r') as f:
                plugin_auth = json.load(f)
        else:
            plugin_auth = {}

        logging.info("Loading plugins...")

        self.registry = {}
        plugin_auth_update = {}
        for netloc in list(dict.fromkeys(plugins or [])):
            try:
                manifest_url = urlunsplit(
                    ('http', netloc, '/.well-known/ai-plugin.json', '', ''))
                response = requests.get(manifest_url)
                response.raise_for_status()
                manifest = json.loads(response.text)
            except Exception as e:
                logging.info(
                    f'Unable to load manifest for {netloc}, skipping: {e}')
                continue

            if manifest["auth"]["type"] not in [self.AUTH_TYPE_NONE, self.AUTH_TYPE_SERVICE_HTTP, self.AUTH_TYPE_USER_HTTP]:
                logging.info(
                    f'Plugin {netloc} declares an unsupported auth type, skipping: {manifest["auth"]["type"]}')
                continue

            if netloc not in plugin_auth or manifest["auth"]["type"] != plugin_auth[netloc]["type"]:
                plugin_auth_update[netloc] = {
                    "type": manifest["auth"]["type"]
                }

                if manifest["auth"]["type"] in [self.AUTH_TYPE_SERVICE_HTTP, self.AUTH_TYPE_USER_HTTP]:
                    plugin_auth_update[netloc]["token"] = input(
                        f'Enter access token for {manifest["name_for_human"]}: ')
            else:
                plugin_auth_update[netloc] = plugin_auth[netloc].copy()

            try:
                response = requests.get(manifest["api"]["url"])
                response.raise_for_status()
            except Exception as e:
                logging.info(
                    f'Unable to fetch OpenAPI specification for {netloc}, skipping: {e}')
                continue

            content_type = response.headers.get('Content-Type')
            if not content_type:
                logging.info(
                    f'Unable to parse OpenAPI specification for {netloc}, skipping: No Content-Type header set')
                continue

            mime_type = content_type.split(';')[0].strip()
            if mime_type not in self.MIME_TYPES_JSON + self.MIME_TYPES_YAML:
                logging.info(
                    f'Unable to parse OpenAPI specification for {netloc}, skipping: Unsupported MIME type: {mime_type}')
                continue

            try:
                spec_dict = json.loads(
                    response.text) if mime_type in self.MIME_TYPES_JSON else yaml.safe_load(response.text)
            except Exception as e:
                logging.info(
                    f'Unable to parse OpenAPI specification for {netloc}, skipping: {e}')
                continue

            self.registry[manifest["name_for_model"]] = {
                "netloc": netloc,
                "manifest": manifest,
                "spec_dict": spec_dict,
                "auth": plugin_auth_update[netloc]
            }

            try:
                self.registry[manifest["name_for_model"]]["spec"] = openapi_core.Spec.create(
                    data=spec_dict)
            except Exception as e:
                logging.warn(
                    f"Warning: Invalid OpenAPI specification for {netloc}. Horace will be unable to validate LLM requests to this plugin against the spec. Invalid spec presented to LLM may also cause it to form incorrect requests.")

        with open(self.PLUGIN_AUTH_FILENAME, 'w') as f:
            json.dump(plugin_auth_update, f)

        if self.registry:
            logging.info("Plugins loaded: " +
                         ", ".join([p["netloc"] for p in self.registry.values()]))
        else:
            logging.info("No plugins loaded.")

    def prepare(self, plugin_name: str, request_params: Dict) -> Dict:
        if plugin_name not in self.registry:
            raise ValueError(f"Unknown plugin: {plugin_name}")

        # Add authorization headers, if any
        if self.registry[plugin_name]["auth"]["type"] == self.AUTH_TYPE_USER_HTTP:
            extra_headers = {
                'Authorization': f'Bearer {self.registry[plugin_name]["auth"]["token"]}'
            }
            if "headers" in request_params:
                request_params["headers"].update(extra_headers)
            else:
                request_params["headers"] = extra_headers

        request = requests.Request(**request_params)

        # Validate the request against the plugin's OpenAPI spec
        if "spec" in self.registry[plugin_name]:
            openapi_request = RequestsOpenAPIRequest(request)
            try:
                openapi_core.validate_request(
                    openapi_request, spec=self.registry[plugin_name]["spec"])
            except RequestValidationError as e:
                raise ValueError(
                    f"Error validating the request against the plugin's OpenAPI spec: {e}")

        # Prepare aiohttp request params
        return {key: request_params.get(key)
                for key in ['method', 'url', 'headers', 'params', 'data', 'json']}

    async def send(self, prepared_request_params: Dict) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.request(**prepared_request_params) as response:
                text = await response.text()

        return response.status, text
