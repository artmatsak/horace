import json
from inspect import Signature, signature


class Router():
    registry = {}

    def __init__(self):
        pass

    def command(self, desc: str, example_params: tuple):
        def decorator(func):
            # Remove "return" annotation from signature
            sig = signature(func).replace(return_annotation=Signature.empty)

            example_dict = {"command": func.__name__, "params": {}}
            for param_name, value in zip(sig.parameters.keys(), example_params):
                example_dict["params"][param_name] = value

            self.registry[func.__name__] = {
                "python_sig": f"{func.__name__}{sig}",
                "desc": desc,
                "example_json": json.dumps(example_dict),
                "func": func
            }

            return func

        return decorator

    def invoke(self, command_json: str):
        try:
            command_dict = json.loads(command_json)
        except json.decoder.JSONDecodeError:
            raise ValueError(f"Malformed JSON received: {repr(command_json)}")

        for key in ["command", "params"]:
            if key not in command_dict:
                raise ValueError(
                    f"Command JSON missing required key: {repr(key)}")

        if command_dict["command"] not in self.registry:
            raise ValueError(
                f"No such command: {repr(command_dict['command'])}")

        func = self.registry[command_dict["command"]]["func"]

        return func(**command_dict["params"])
