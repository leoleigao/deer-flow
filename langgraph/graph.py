class MessagesState(dict):
    def __init__(self, messages=None, **kwargs):
        super().__init__()
        if messages is None:
            messages = []
        self["messages"] = messages
        for k, v in kwargs.items():
            self[k] = v
