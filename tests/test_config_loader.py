"""Tests for configuration loader with environment variable support."""

import os
import tempfile
import pytest
from src.config.loader import load_yaml_config, replace_env_vars


def test_replace_env_vars_with_dollar_brace_format():
    """Test ${VAR} format environment variable replacement."""
    os.environ["TEST_VAR"] = "test_value"
    assert replace_env_vars("${TEST_VAR}") == "test_value"
    assert replace_env_vars("${NONEXISTENT}") == "${NONEXISTENT}"
    del os.environ["TEST_VAR"]


def test_replace_env_vars_with_dollar_format():
    """Test $VAR format environment variable replacement."""
    os.environ["TEST_VAR"] = "test_value"
    assert replace_env_vars("$TEST_VAR") == "test_value"
    assert replace_env_vars("$NONEXISTENT") == "$NONEXISTENT"
    del os.environ["TEST_VAR"]


def test_use_glean_stub_default():
    """Test USE_GLEAN_STUB defaults to 'true' when not set."""
    # Ensure USE_GLEAN_STUB is not set
    if "USE_GLEAN_STUB" in os.environ:
        del os.environ["USE_GLEAN_STUB"]

    assert replace_env_vars("${USE_GLEAN_STUB}") == "true"
    assert replace_env_vars("$USE_GLEAN_STUB") == "true"


def test_use_glean_stub_override():
    """Test USE_GLEAN_STUB can be overridden."""
    os.environ["USE_GLEAN_STUB"] = "false"
    assert replace_env_vars("${USE_GLEAN_STUB}") == "false"
    del os.environ["USE_GLEAN_STUB"]


def test_load_yaml_with_env_vars():
    """Test loading YAML config with environment variable substitution."""
    # Create a temporary YAML file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(
            """
test_config:
  env_var: ${TEST_ENV_VAR}
  stub_mode: ${USE_GLEAN_STUB}
  literal: "literal_value"
"""
        )
        temp_path = f.name

    try:
        os.environ["TEST_ENV_VAR"] = "from_env"
        config = load_yaml_config(temp_path)

        assert config["test_config"]["env_var"] == "from_env"
        assert config["test_config"]["stub_mode"] == "true"  # default value
        assert config["test_config"]["literal"] == "literal_value"
    finally:
        os.unlink(temp_path)
        if "TEST_ENV_VAR" in os.environ:
            del os.environ["TEST_ENV_VAR"]


def test_load_nonexistent_yaml():
    """Test loading non-existent YAML returns empty dict."""
    config = load_yaml_config("nonexistent/file.yaml")
    assert config == {}
