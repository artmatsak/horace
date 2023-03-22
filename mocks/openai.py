api_key = ""


class Completion():
    def __init__(self, choices):
        self.choices = choices

    @classmethod
    def create(cls, *args, **kwargs):
        # Not perfect but OK for manual testing
        response = kwargs["prompt"].split(":")[-2].strip()

        if "end" in response:
            text = "I'm sorry to part ways now. Goodbye! END"
        elif "code" in response:
            text = 'Did I hear "code"? I got some codez here. <script>{"command": "book_table", "params": {"name": "John Smith"}}</script>'
        else:
            text = "You got it!"

        return Completion([{"text": text}])
