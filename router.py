import os
import json
import requests
from urllib.parse import urlunsplit
import logging
from typing import List, Dict


class Router():
    PLUGIN_DB_FILENAME = '.plugin_db.json'
    AUTH_TYPE_NONE = "none"
    AUTH_TYPE_USER_HTTP = "user_http"

    def __init__(self, plugins: List[str]):
        mode = 'r+' if os.path.isfile(self.PLUGIN_DB_FILENAME) else 'w'
        with open(self.PLUGIN_DB_FILENAME, mode) as f:
            plugin_db = json.load(f) if f.readable() else {}

            self.registry = {}
            plugin_db_update = {}
            for netloc in set(plugins):
                logging.debug(f"Loading plugin: {netloc}")

                manifest_url = urlunsplit(
                    ('http', netloc, '/.well-known/ai-plugin.json', '', ''))
                response = requests.get(manifest_url)
                response.raise_for_status()
                manifest = json.loads(response.text)

                if manifest["auth"]["type"] not in [self.AUTH_TYPE_NONE, self.AUTH_TYPE_USER_HTTP]:
                    logging.debug(
                        f'Plugin auth type not yet supported, skipping: {manifest["auth"]["type"]}')
                    continue

                if netloc not in plugin_db or manifest["auth"]["type"] != plugin_db[netloc]["auth_type"]:
                    plugin_db_update[netloc] = {
                        "auth_type": manifest["auth"]["type"]
                    }

                    if manifest["auth"]["type"] == self.AUTH_TYPE_USER_HTTP:
                        plugin_db_update[netloc]["auth_token"] = input(
                            f'Enter access token for {manifest["name_for_human"]}: ')
                else:
                    plugin_db_update[netloc] = plugin_db[netloc].copy()

                response = requests.get(manifest["api"]["url"])
                response.raise_for_status()
                openapi_spec = response.text

                self.registry[manifest["name_for_model"]] = {
                    "manifest": manifest,
                    "openapi_spec": openapi_spec,
                    "db_info": plugin_db_update[netloc]
                }

            f.seek(0)
            json.dump(plugin_db_update, f)
            f.truncate()

    def call(self, plugin_name: str, request_object_params: Dict) -> str:
        if plugin_name not in self.registry:
            raise ValueError(f"Unknown plugin: {plugin_name}")

        if self.registry[plugin_name]["db_info"]["auth_type"] == self.AUTH_TYPE_USER_HTTP:
            extra_headers = {
                'Authorization': f'Bearer {self.registry[plugin_name]["db_info"]["auth_token"]}'
            }
            if "headers" in request_object_params:
                request_object_params["headers"].update(extra_headers)
            else:
                request_object_params["headers"] = extra_headers

        request = requests.Request(**request_object_params)
        prepared_request = request.prepare()
        response = requests.Session().send(prepared_request)

        result = [f"HTTP status code: {response.status_code}"]
        if response.status_code >= 200 and response.status_code < 300:
            result.append(f"response body: {response.text}")

        return ", ".join(result)
