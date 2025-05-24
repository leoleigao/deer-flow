# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import logging
from typing import Annotated
try:
    from langchain_core.tools import tool
except Exception:  # pragma: no cover - fallback if langchain_core missing
    def tool(func=None, *, name=None, description=None):
        def decorator(f):
            f.name = name or f.__name__
            f.description = description
            return f

        if func is not None:
            return decorator(func)
        return decorator

try:
    from langchain_experimental.utilities import PythonREPL
except Exception:  # pragma: no cover - fallback minimal REPL
    import contextlib
    import io

    class PythonREPL:
        def run(self, code: str):  # type: ignore[override]
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                try:
                    exec(code, {})
                except BaseException as e:
                    return f"{e.__class__.__name__}: {e}"
            return stdout.getvalue().strip()
from .decorators import log_io

# Initialize REPL and logger
repl = PythonREPL()
logger = logging.getLogger(__name__)


@tool
@log_io
def python_repl_tool(
    code: Annotated[
        str, "The python code to execute to do further analysis or calculation."
    ],
):
    """Use this to execute python code and do data analysis or calculation. If you want to see the output of a value,
    you should print it out with `print(...)`. This is visible to the user."""
    if not isinstance(code, str):
        error_msg = f"Invalid input: code must be a string, got {type(code)}"
        logger.error(error_msg)
        return f"Error executing code:\n```python\n{code}\n```\nError: {error_msg}"

    logger.info("Executing Python code")
    try:
        result = repl.run(code)
        # Check if the result is an error message by looking for typical error patterns
        if isinstance(result, str) and ("Error" in result or "Exception" in result):
            logger.error(result)
            return f"Error executing code:\n```python\n{code}\n```\nError: {result}"
        logger.info("Code execution successful")
    except BaseException as e:
        error_msg = repr(e)
        logger.error(error_msg)
        return f"Error executing code:\n```python\n{code}\n```\nError: {error_msg}"

    result_str = f"Successfully executed:\n```python\n{code}\n```\nStdout: {result}"
    return result_str
