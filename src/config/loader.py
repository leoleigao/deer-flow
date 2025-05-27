# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import os
import yaml
from typing import Dict, Any

# Try to load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv

    load_dotenv()  # Load .env file from current directory
except ImportError:
    # python-dotenv not installed, skip .env loading
    pass


def replace_env_vars(value: str) -> str:
    """Replace environment variables in string values."""
    if not isinstance(value, str):
        return value

    # Handle ${VAR} format
    if value.startswith("${") and value.endswith("}"):
        env_var = value[2:-1]
        # For USE_GLEAN_STUB, default to "true" if not set
        if env_var == "USE_GLEAN_STUB":
            return os.getenv(env_var, "true")
        return os.getenv(env_var, value)

    # Handle $VAR format
    if value.startswith("$"):
        env_var = value[1:]
        # For USE_GLEAN_STUB, default to "true" if not set
        if env_var == "USE_GLEAN_STUB":
            return os.getenv(env_var, "true")
        return os.getenv(env_var, value)

    return value


def process_dict(config: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively process dictionary to replace environment variables."""
    result = {}
    for key, value in config.items():
        if isinstance(value, dict):
            result[key] = process_dict(value)
        elif isinstance(value, str):
            result[key] = replace_env_vars(value)
        else:
            result[key] = value
    return result


_config_cache: Dict[str, Dict[str, Any]] = {}


def load_yaml_config(file_path: str) -> Dict[str, Any]:
    """Load and process YAML configuration file."""
    # 如果文件不存在，返回{}
    if not os.path.exists(file_path):
        return {}

    # 检查缓存中是否已存在配置
    if file_path in _config_cache:
        return _config_cache[file_path]

    # 如果缓存中不存在，则加载并处理配置
    with open(file_path, "r") as f:
        config = yaml.safe_load(f)
    processed_config = process_dict(config)

    # 将处理后的配置存入缓存
    _config_cache[file_path] = processed_config
    return processed_config
