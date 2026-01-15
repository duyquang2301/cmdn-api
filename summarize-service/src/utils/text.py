"""Text processing utilities."""


class TextChunker:
    """Text chunker."""

    def should_chunk(self, text: str, max_size: int) -> bool:
        """Check if text needs chunking."""
        return len(text) > max_size

    def chunk(self, text: str, max_size: int) -> list[str]:
        """Split text into chunks."""
        return [text[i : i + max_size] for i in range(0, len(text), max_size)]
