class DummyAgent:
    def __init__(self, name, model, tools, prompt):
        self.name = name
        self.model = model
        self.tools = tools
        self.prompt = prompt

    def invoke(self, state):
        # Simply call the model.invoke if available
        if hasattr(self.model, "invoke"):
            return self.model.invoke(state)
        return ""


def create_react_agent(name, model, tools, prompt):
    return DummyAgent(name, model, tools, prompt)
