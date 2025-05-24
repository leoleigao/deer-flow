# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import os
import dataclasses
from datetime import datetime
try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape
except Exception:  # pragma: no cover - jinja2 unavailable in minimal env
    from pathlib import Path
    import re

    class _SimpleTemplate:
        def __init__(self, text: str):
            self.text = text

        def render(self, **kwargs):
            def repl(match):
                key = match.group(1).strip()
                return str(kwargs.get(key, match.group(0)))

            return re.sub(r"{{\s*(\w+)\s*}}", repl, self.text)

    class Environment:  # type: ignore
        def __init__(self, loader=None, autoescape=None, trim_blocks=False, lstrip_blocks=False):
            self.loader = loader

        def get_template(self, name: str):
            path = Path(self.loader.searchpath[0]) / name  # type: ignore[attr-defined]
            with open(path, "r", encoding="utf-8") as f:
                return _SimpleTemplate(f.read())

    class FileSystemLoader:  # type: ignore
        def __init__(self, searchpath: str):
            self.searchpath = [searchpath]

    def select_autoescape(*args, **kwargs):  # type: ignore
        return False
from langgraph.prebuilt.chat_agent_executor import AgentState
from src.config.configuration import Configuration

# Initialize Jinja2 environment
env = Environment(
    loader=FileSystemLoader(os.path.dirname(__file__)),
    autoescape=select_autoescape(),
    trim_blocks=True,
    lstrip_blocks=True,
)


def get_prompt_template(prompt_name: str) -> str:
    """
    Load and return a prompt template using Jinja2.

    Args:
        prompt_name: Name of the prompt template file (without .md extension)

    Returns:
        The template string with proper variable substitution syntax
    """
    try:
        template = env.get_template(f"{prompt_name}.md")
        return template.render()
    except Exception as e:
        raise ValueError(f"Error loading template {prompt_name}: {e}")


def apply_prompt_template(
    prompt_name: str, state: AgentState, configurable: Configuration = None
) -> list:
    """
    Apply template variables to a prompt template and return formatted messages.

    Args:
        prompt_name: Name of the prompt template to use
        state: Current agent state containing variables to substitute

    Returns:
        List of messages with the system prompt as the first message
    """
    # Convert state to dict for template rendering
    state_vars = {
        "CURRENT_TIME": datetime.now().strftime("%a %b %d %Y %H:%M:%S %z"),
        **state,
    }

    # Add configurable variables
    if configurable:
        state_vars.update(dataclasses.asdict(configurable))

    try:
        template = env.get_template(f"{prompt_name}.md")
        system_prompt = template.render(**state_vars)
        return [{"role": "system", "content": system_prompt}] + state["messages"]
    except Exception as e:
        raise ValueError(f"Error applying template {prompt_name}: {e}")
