"""
Main entry point for the AI Tool Verification Assistant.

This module serves as the application entry point and initializes
the necessary components for the verification assistant.
"""

from loguru import logger
import openai

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


    client = openai.OpenAI(
        api_key="sk-pjXWROx1o6pYvLXyiEJgkA",
        base_url="https://litellm.ai.paas.htec.rs"
    )

    response = client.chat.completions.create(
        model="l2-gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": "tell me a joke"
            }
        ]
    )

    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()
