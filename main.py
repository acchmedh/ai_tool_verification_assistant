"""
Main entry point for the AI Tool Verification Assistant.

This module serves as the application entry point and initializes
the necessary components for the verification assistant.
"""

from loguru import logger

from src.config import settings
from src.utils.logger import setup_logger


def main() -> None:
    """Main application entry point."""
    # Setup logging
    setup_logger()

    logger.info("AI Tool Verification Assistant")
    logger.info(f"Version: 0.1.0")
    logger.info("=" * 50)

    # Display configuration (without sensitive data)
    logger.info(f"Model: {settings.default_model}")
    logger.info(f"Embedding Model: {settings.embedding_model}")
    logger.info(f"Data Directory: {settings.data_dir}")
    logger.info(f"RAG Store: {settings.chroma_persist_directory}")

    logger.info("=" * 50)
    logger.info("Application initialized successfully")
    logger.info("Ready to process verification requests")

    # TODO: Implement main application logic
    # - Data ingestion pipeline
    # - RAG chatbot interface
    # - Evaluation framework
if __name__ == "__main__":
    main()
