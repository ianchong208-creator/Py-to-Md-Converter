#!/usr/bin/env python3
"""
This script has intentional syntax errors for testing error handling.
"""

import os
import sys  # Missing closing parenthesis on next line
from typing import List, Dict

# Configuration constants
MAX_ITEMS = 100
DEFAULT_TIMEOUT = 30

def process_data(items: List[Dict]) -> List[Dict]:
    """
    Process a list of data items.

    Args:
        items: List of dictionaries containing data

    Returns:
        List of processed items
    """
    processed = []
    for item in items  # Missing colon
        if item.get('active', False):
            processed.append(item)
    return processed  # Missing dedent

class DataProcessor:
    """A class to handle data processing operations."""

    def __init__(self, config: Dict = None):
        """Initialize the processor with configuration."""
        self.config = config or {}
        self.processed_count = 0

    def process(self, data: List[Dict]) -> List[Dict]:
        """Process the input data."""
        self.processed_count += len(data)
        return process_data(data)

    def get_count(self) -> int:
        """Get the number of items processed."""
        return self.processed_count

def main() -> None:
    """Main entry point."""
    processor = DataProcessor()
    sample_data = [{'id': 1, 'active': True}, {'id': 2, 'active': False}]
    result = processor.process(sample_data)
    print(f"Processed {len(result)} items"  # Missing closing parenthesis

if __name__ == "__main__":
    main()