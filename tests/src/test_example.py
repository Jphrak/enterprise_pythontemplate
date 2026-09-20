"""Tests for src.example module."""

import logging

import pytest

from src.example import ExampleProcessor, run_example


def test_example_processor_default_values() -> None:
    """Test ExampleProcessor dataclass default values."""
    processor = ExampleProcessor(name="test")

    assert processor.name == "test"
    assert processor.max_items == 100


def test_example_processor_custom_values() -> None:
    """Test ExampleProcessor dataclass with custom values."""
    processor = ExampleProcessor(name="custom", max_items=50)

    assert processor.name == "custom"
    assert processor.max_items == 50


def test_process_item() -> None:
    """Test process_item returns formatted string."""
    processor = ExampleProcessor(name="test")

    result = processor.process_item("sample")

    assert result == "Processed: sample"


def test_process_item_logs_debug(caplog: pytest.LogCaptureFixture) -> None:
    """Test process_item logs debug message."""
    processor = ExampleProcessor(name="test")

    with caplog.at_level(logging.DEBUG):
        processor.process_item("sample")

    assert "Processing item: sample" in caplog.text


def test_process_batch_returns_processed_items() -> None:
    """Test process_batch returns list of processed items."""
    processor = ExampleProcessor(name="test", max_items=5)
    items = ["item1", "item2", "item3"]

    result = processor.process_batch(items)

    assert result == ["Processed: item1", "Processed: item2", "Processed: item3"]


def test_process_batch_respects_max_items() -> None:
    """Test process_batch only processes up to max_items."""
    processor = ExampleProcessor(name="test", max_items=3)
    items = ["item1", "item2", "item3", "item4", "item5"]

    result = processor.process_batch(items)

    assert len(result) == 3
    assert result == ["Processed: item1", "Processed: item2", "Processed: item3"]


def test_process_batch_logs_info(caplog: pytest.LogCaptureFixture) -> None:
    """Test process_batch logs info message with batch size."""
    processor = ExampleProcessor(name="test", max_items=5)
    items = ["item1", "item2"]

    with caplog.at_level(logging.INFO):
        processor.process_batch(items)

    assert "Processing batch of 2 items" in caplog.text


def test_process_batch_empty_list() -> None:
    """Test process_batch handles empty list."""
    processor = ExampleProcessor(name="test")

    result = processor.process_batch([])

    assert result == []


def test_run_example_full_workflow(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """Test run_example creates processor and processes batch correctly."""
    # Mock Config to avoid dependency on actual config file
    from src.utils import config

    mock_config = config._Config(example_config="test_config_value", example_uninitialized=42)
    # Patch Config in src.example module where it's imported and used
    monkeypatch.setattr("src.example.Config", mock_config)

    with caplog.at_level(logging.INFO):
        run_example()

    # Verify processor creation
    assert "Example processor sees config: test_config_value" in caplog.text
    assert "Creating processor 'DemoProcessor' with max_items=10" in caplog.text

    # Verify batch processing (should process 10 items from 15 generated)
    assert "Processing batch of 10 items" in caplog.text
    assert "Processed: item_0" in caplog.text
    assert "Processed: item_9" in caplog.text
