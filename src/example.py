"""Example module demonstrating basic class and function patterns."""

from dataclasses import dataclass
import logging

from src.utils.config import Config

logger = logging.getLogger(__name__)


@dataclass
class ExampleProcessor:
    """Example processor class for data processing operations.

    Attributes:
        name: Identifier for this processor instance
        max_items: Maximum number of items to process
    """

    name: str
    max_items: int = 100

    def process_item(self, item: str) -> str:
        """Process a single item.

        Args:
            item: The item to process

        Returns:
            Processed item as a string
        """
        logger.debug("Processing item: %s", item)
        return f"Processed: {item}"

    def process_batch(self, items: list[str]) -> list[str]:
        """Process a batch of items.

        Args:
            items: List of items to process

        Returns:
            List of processed items
        """
        items_to_process = items[: self.max_items]
        logger.info("Processing batch of %d items", len(items_to_process))

        return [self.process_item(item) for item in items_to_process]


def run_example() -> None:
    """Function to demonstrate usage of ExampleProcessor."""
    # WARNING: Only log non-sensitive config values. Never log secrets (passwords, API keys, etc.)
    logger.info("Example processor sees config: %s", Config.example_config)
    processor_name = "DemoProcessor"
    processor_max_items = 10
    logger.info("Creating processor '%s' with max_items=%d", processor_name, processor_max_items)
    processor = ExampleProcessor(name=processor_name, max_items=processor_max_items)
    sample_items = [f"item_{i}" for i in range(15)]
    processed_items = processor.process_batch(sample_items)

    for item in processed_items:
        logger.info("%s", item)
